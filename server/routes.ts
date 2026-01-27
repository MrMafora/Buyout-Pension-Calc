import type { Express } from "express";
import type { Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { CALCULATOR_CONFIG } from "@shared/config";
import { z } from "zod";

// In-memory email storage (for demo - in production use a real database)
const emailSubscribers: Set<string> = new Set();

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {

  app.post(api.calculator.calculate.path, (req, res) => {
    try {
      const input = api.calculator.calculate.input.parse(req.body);
      
      const { 
        currentSalary, 
        yearsOfService, 
        age, 
        retirementSystem,
        isEarlyRetirement,
        minimumRetirementAge,
        survivorBenefit,
        buyoutMode, 
        customBuyoutAmount, 
        stateTaxRate 
      } = input;

      // ========================================
      // 1. Calculate Pension
      // ========================================
      
      const { fers, csrs, taxes, earlyRetirement: earlyRetConfig } = CALCULATOR_CONFIG;
      let multiplier: number;
      
      if (retirementSystem === "csrs") {
        // CSRS: Tiered multipliers from config
        if (yearsOfService <= csrs.tier1Years) {
          multiplier = csrs.tier1Multiplier;
        } else if (yearsOfService <= csrs.tier1Years + csrs.tier2Years) {
          multiplier = (csrs.tier1Years * csrs.tier1Multiplier + (yearsOfService - csrs.tier1Years) * csrs.tier2Multiplier) / yearsOfService;
        } else {
          const first5 = csrs.tier1Years * csrs.tier1Multiplier;
          const next5 = csrs.tier2Years * csrs.tier2Multiplier;
          const rest = (yearsOfService - csrs.tier1Years - csrs.tier2Years) * csrs.tier3Multiplier;
          multiplier = (first5 + next5 + rest) / yearsOfService;
        }
      } else {
        // FERS: Multipliers from config
        multiplier = (age >= fers.bonusAgeRequirement && yearsOfService >= fers.bonusYearsRequirement) 
          ? fers.bonusMultiplier 
          : fers.standardMultiplier;
      }

      let annualPensionGross = currentSalary * yearsOfService * multiplier;
      
      // Apply CSRS max benefit cap
      if (retirementSystem === "csrs") {
        const maxPension = currentSalary * csrs.maxBenefitPercent;
        if (annualPensionGross > maxPension) {
          annualPensionGross = maxPension;
        }
      }

      // ========================================
      // 2. Early Retirement Penalty
      // ========================================
      
      let earlyRetirementPenalty = 0;
      let earlyRetirementReduction = 0;
      
      if (isEarlyRetirement && age < minimumRetirementAge) {
        // Reduction per year under MRA from config
        const yearsUnderMRA = minimumRetirementAge - age;
        earlyRetirementPenalty = yearsUnderMRA * (earlyRetConfig.penaltyPerYear * 100); // Percentage
        earlyRetirementReduction = annualPensionGross * (earlyRetirementPenalty / 100);
        annualPensionGross -= earlyRetirementReduction;
      }

      // ========================================
      // 3. Survivor Benefit Reduction
      // ========================================
      
      let survivorBenefitReduction = 0;
      let survivorBenefitAmount = 0;
      
      const { survivorBenefit: survivorConfig } = CALCULATOR_CONFIG;
      if (survivorBenefit === "full") {
        survivorBenefitReduction = survivorConfig.full * 100;
        survivorBenefitAmount = annualPensionGross * survivorConfig.full;
      } else if (survivorBenefit === "partial") {
        survivorBenefitReduction = survivorConfig.partial * 100;
        survivorBenefitAmount = annualPensionGross * survivorConfig.partial;
      }
      
      const annualPensionNet = annualPensionGross - survivorBenefitAmount;
      const monthlyPension = annualPensionNet / 12;

      // ========================================
      // 4. Calculate Severance Pay (OPM Formula)
      // ========================================
      
      const { severance: sevConfig, buyout: buyoutConfig } = CALCULATOR_CONFIG;
      
      // Weekly Rate = (Annual / hoursPerYear) * hoursPerWeek
      const weeklyRate = (currentSalary / sevConfig.hoursPerYear) * sevConfig.hoursPerWeek;

      // Basic Allowance: tier1 weeks per year (first tier1Years), tier2 weeks per year thereafter
      let basicWeeks = 0;
      if (yearsOfService <= sevConfig.tier1Years) {
        basicWeeks = yearsOfService * sevConfig.tier1WeeksPerYear;
      } else {
        basicWeeks = (sevConfig.tier1Years * sevConfig.tier1WeeksPerYear) + 
                     ((yearsOfService - sevConfig.tier1Years) * sevConfig.tier2WeeksPerYear);
      }

      const basicSeverance = basicWeeks * weeklyRate;

      // Age Adjustment: adjustment per quarter over base age
      let ageAdjustmentFactor = 1.0;
      let ageAdjustmentAmount = 0;

      if (age > sevConfig.ageAdjustmentBase) {
        const quartersOverBase = (age - sevConfig.ageAdjustmentBase) * 4;
        const increasePercent = quartersOverBase * sevConfig.ageAdjustmentPerQuarter;
        ageAdjustmentFactor = 1 + increasePercent;
      }

      let totalSeverance = basicSeverance * ageAdjustmentFactor;
      ageAdjustmentAmount = totalSeverance - basicSeverance;

      // Cap at maxYearsSalary * annual salary
      const severanceCap = currentSalary * sevConfig.maxYearsSalary;
      if (totalSeverance > severanceCap) {
        totalSeverance = severanceCap;
      }
      
      // ========================================
      // 5. Determine Gross Buyout Amount
      // ========================================
      
      let grossBuyout = 0;
      if (buyoutMode === 'custom' && customBuyoutAmount) {
        grossBuyout = customBuyoutAmount;
      } else if (buyoutMode === 'severance') {
        grossBuyout = totalSeverance;
      } else {
        // Default buyout (months from config)
        grossBuyout = (currentSalary / 12) * buyoutConfig.defaultMonths;
      }

      // ========================================
      // 6. Calculate Taxes on Buyout
      // ========================================
      
      // Federal: From config (supplemental wage rate)
      const fedTax = grossBuyout * taxes.federal.rate;
      
      // Social Security: From config (up to wage base - simplified)
      const ssTax = grossBuyout * taxes.socialSecurity.rate;

      // Medicare: From config
      const medTax = grossBuyout * taxes.medicare.rate;

      // State Tax
      const stateTax = grossBuyout * (stateTaxRate / 100);

      const totalTax = fedTax + ssTax + medTax + stateTax;
      const netBuyout = grossBuyout - totalTax;

      // ========================================
      // 7. Comparison Analysis
      // ========================================
      
      // Break-even: How many years of pension equals net buyout?
      const breakEvenYears = annualPensionNet > 0 ? (netBuyout / annualPensionNet) : 0;
      
      // 5-year and 10-year comparison
      const difference5Year = (annualPensionNet * 5) - netBuyout;
      const difference10Year = (annualPensionNet * 10) - netBuyout;

      // Generate recommendation
      let recommendation = "";
      if (breakEvenYears <= 3) {
        recommendation = "The buyout may be attractive if you have immediate financial needs or private sector opportunities. Your pension would exceed the buyout value within 3 years.";
      } else if (breakEvenYears <= 5) {
        recommendation = "Consider your job prospects carefully. The pension catches up to the buyout within 5 years, making it valuable long-term.";
      } else if (breakEvenYears <= 10) {
        recommendation = "The buyout offers significant upfront value. If you're confident in private sector earnings or have other retirement savings, it could be worthwhile.";
      } else {
        recommendation = "The buyout is very attractive financially. Your pension would take over 10 years to match it. Consider your career plans and financial situation.";
      }

      const result = {
        pension: {
          annualGross: Number(annualPensionGross.toFixed(2)),
          annualNet: Number(annualPensionNet.toFixed(2)),
          monthly: Number(monthlyPension.toFixed(2)),
          multiplier,
          high3: currentSalary,
          earlyRetirementPenalty,
          earlyRetirementReduction: Number(earlyRetirementReduction.toFixed(2)),
          survivorBenefitReduction,
          survivorBenefitAmount: Number(survivorBenefitAmount.toFixed(2)),
          retirementSystem: retirementSystem.toUpperCase(),
        },
        severance: {
          weeklyRate: Number(weeklyRate.toFixed(2)),
          basicWeeks,
          basicAmount: Number(basicSeverance.toFixed(2)),
          ageAdjustmentFactor,
          ageAdjustmentAmount: Number(ageAdjustmentAmount.toFixed(2)),
          totalGross: Number(totalSeverance.toFixed(2)),
        },
        buyout: {
          gross: Number(grossBuyout.toFixed(2)),
          net: Number(netBuyout.toFixed(2)),
          taxes: {
            federal: Number(fedTax.toFixed(2)),
            socialSecurity: Number(ssTax.toFixed(2)),
            medicare: Number(medTax.toFixed(2)),
            state: Number(stateTax.toFixed(2)),
            totalTax: Number(totalTax.toFixed(2)),
          },
        },
        comparison: {
          breakEvenYears: Number(breakEvenYears.toFixed(2)),
          difference5Year: Number(difference5Year.toFixed(2)),
          difference10Year: Number(difference10Year.toFixed(2)),
          recommendation,
        }
      };

      res.json(result);

    } catch (err) {
      if (err instanceof z.ZodError) {
        res.status(400).json({
          message: err.errors[0].message,
          field: err.errors[0].path.join('.'),
        });
      } else {
        console.error(err);
        res.status(500).json({ message: "Internal Server Error" });
      }
    }
  });

  // Newsletter signup endpoint
  app.post(api.newsletter.signup.path, (req, res) => {
    try {
      const input = api.newsletter.signup.input.parse(req.body);
      
      if (emailSubscribers.has(input.email)) {
        return res.json({ 
          success: true, 
          message: "You're already subscribed! We'll keep you updated." 
        });
      }
      
      emailSubscribers.add(input.email);
      console.log(`New subscriber: ${input.email}`);
      
      res.json({ 
        success: true, 
        message: "Thanks for subscribing! You'll receive updates on federal buyout news." 
      });

    } catch (err) {
      if (err instanceof z.ZodError) {
        res.status(400).json({
          message: err.errors[0].message,
          field: err.errors[0].path.join('.'),
        });
      } else {
        console.error(err);
        res.status(500).json({ message: "Internal Server Error" });
      }
    }
  });

  return httpServer;
}
