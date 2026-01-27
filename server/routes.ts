import type { Express } from "express";
import type { Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
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
      
      let multiplier: number;
      
      if (retirementSystem === "csrs") {
        // CSRS: 1.5% for first 5 years, 1.75% for years 5-10, 2% thereafter
        // Simplified: We'll use weighted average based on years
        if (yearsOfService <= 5) {
          multiplier = 0.015;
        } else if (yearsOfService <= 10) {
          // Average of 1.5% and 1.75%
          multiplier = (5 * 0.015 + (yearsOfService - 5) * 0.0175) / yearsOfService;
        } else {
          // Full calculation
          const first5 = 5 * 0.015;
          const next5 = 5 * 0.0175;
          const rest = (yearsOfService - 10) * 0.02;
          multiplier = (first5 + next5 + rest) / yearsOfService;
        }
      } else {
        // FERS: 1.0% normally, 1.1% if age 62+ with 20+ years
        multiplier = (age >= 62 && yearsOfService >= 20) ? 0.011 : 0.010;
      }

      let annualPensionGross = currentSalary * yearsOfService * multiplier;

      // ========================================
      // 2. Early Retirement Penalty
      // ========================================
      
      let earlyRetirementPenalty = 0;
      let earlyRetirementReduction = 0;
      
      if (isEarlyRetirement && age < minimumRetirementAge) {
        // 5% reduction for each year under MRA
        const yearsUnderMRA = minimumRetirementAge - age;
        earlyRetirementPenalty = yearsUnderMRA * 5; // Percentage
        earlyRetirementReduction = annualPensionGross * (earlyRetirementPenalty / 100);
        annualPensionGross -= earlyRetirementReduction;
      }

      // ========================================
      // 3. Survivor Benefit Reduction
      // ========================================
      
      let survivorBenefitReduction = 0;
      let survivorBenefitAmount = 0;
      
      if (survivorBenefit === "full") {
        // Full survivor benefit: 10% reduction for 50% survivor annuity
        survivorBenefitReduction = 10;
        survivorBenefitAmount = annualPensionGross * 0.10;
      } else if (survivorBenefit === "partial") {
        // Partial survivor benefit: 5% reduction for 25% survivor annuity
        survivorBenefitReduction = 5;
        survivorBenefitAmount = annualPensionGross * 0.05;
      }
      
      const annualPensionNet = annualPensionGross - survivorBenefitAmount;
      const monthlyPension = annualPensionNet / 12;

      // ========================================
      // 4. Calculate Severance Pay (OPM Formula)
      // ========================================
      
      // Weekly Rate = (Annual / 2087) * 40
      const weeklyRate = (currentSalary / 2087) * 40;

      // Basic Allowance: 1 week per year (first 10), 2 weeks per year (11+)
      let basicWeeks = 0;
      if (yearsOfService <= 10) {
        basicWeeks = yearsOfService * 1;
      } else {
        basicWeeks = 10 + (yearsOfService - 10) * 2;
      }

      const basicSeverance = basicWeeks * weeklyRate;

      // Age Adjustment: 2.5% for each quarter-year over age 40
      let ageAdjustmentFactor = 1.0;
      let ageAdjustmentAmount = 0;

      if (age > 40) {
        const quartersOver40 = (age - 40) * 4;
        const increasePercent = quartersOver40 * 0.025;
        ageAdjustmentFactor = 1 + increasePercent;
      }

      let totalSeverance = basicSeverance * ageAdjustmentFactor;
      ageAdjustmentAmount = totalSeverance - basicSeverance;

      // Cap at 1 year salary
      if (totalSeverance > currentSalary) {
        totalSeverance = currentSalary;
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
        // 8-Month Buyout
        grossBuyout = (currentSalary / 12) * 8;
      }

      // ========================================
      // 6. Calculate Taxes on Buyout
      // ========================================
      
      // Federal: Flat 22% on supplemental wages
      const fedTax = grossBuyout * 0.22;
      
      // Social Security: 6.2% (up to wage base - simplified)
      const ssTax = grossBuyout * 0.062;

      // Medicare: 1.45%
      const medTax = grossBuyout * 0.0145;

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
