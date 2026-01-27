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
        isSpecialProvisions,
        militaryYears,
        isDeferredRetirement,
        isEarlyRetirement,
        minimumRetirementAge,
        survivorBenefit,
        buyoutMode, 
        customBuyoutAmount, 
        stateTaxRate 
      } = input;

      // ========================================
      // 1. Calculate Pension (with military buyback)
      // ========================================
      
      const { fers, csrs, specialProvisions, taxes, earlyRetirement: earlyRetConfig } = CALCULATOR_CONFIG;
      
      // Add military buyback years to total service
      const totalYearsOfService = yearsOfService + (militaryYears || 0);
      
      let multiplier: number;
      
      if (isSpecialProvisions && retirementSystem === "fers") {
        // Special provisions (LEO, firefighters, ATC): 1.7% for first 20 years, 1.0% thereafter
        if (totalYearsOfService <= 20) {
          multiplier = specialProvisions.first20YearsMultiplier;
        } else {
          const first20 = 20 * specialProvisions.first20YearsMultiplier;
          const after20 = (totalYearsOfService - 20) * specialProvisions.after20YearsMultiplier;
          multiplier = (first20 + after20) / totalYearsOfService;
        }
      } else if (retirementSystem === "csrs") {
        // CSRS: Tiered multipliers from config
        if (totalYearsOfService <= csrs.tier1Years) {
          multiplier = csrs.tier1Multiplier;
        } else if (totalYearsOfService <= csrs.tier1Years + csrs.tier2Years) {
          multiplier = (csrs.tier1Years * csrs.tier1Multiplier + (totalYearsOfService - csrs.tier1Years) * csrs.tier2Multiplier) / totalYearsOfService;
        } else {
          const first5 = csrs.tier1Years * csrs.tier1Multiplier;
          const next5 = csrs.tier2Years * csrs.tier2Multiplier;
          const rest = (totalYearsOfService - csrs.tier1Years - csrs.tier2Years) * csrs.tier3Multiplier;
          multiplier = (first5 + next5 + rest) / totalYearsOfService;
        }
      } else {
        // FERS: Multipliers from config
        multiplier = (age >= fers.bonusAgeRequirement && totalYearsOfService >= fers.bonusYearsRequirement) 
          ? fers.bonusMultiplier 
          : fers.standardMultiplier;
      }

      let annualPensionGross = currentSalary * totalYearsOfService * multiplier;
      
      // Calculate deferred pension at age 62 (if applicable)
      let deferredPensionAt62: number | undefined;
      if (isDeferredRetirement && age < 62) {
        // Deferred retirement: pension calculated at current service, payable at 62
        // Uses the 1.0% multiplier (not 1.1% bonus since service ends before 62)
        deferredPensionAt62 = currentSalary * totalYearsOfService * fers.standardMultiplier;
      }
      
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
          totalYearsOfService,
          militaryYearsAdded: militaryYears || 0,
          isSpecialProvisions: isSpecialProvisions || false,
          earlyRetirementPenalty,
          earlyRetirementReduction: Number(earlyRetirementReduction.toFixed(2)),
          survivorBenefitReduction,
          survivorBenefitAmount: Number(survivorBenefitAmount.toFixed(2)),
          retirementSystem: isSpecialProvisions ? `${retirementSystem.toUpperCase()} (Special)` : retirementSystem.toUpperCase(),
          deferredPensionAt62: deferredPensionAt62 ? Number(deferredPensionAt62.toFixed(2)) : undefined,
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

  // Save results / Lead capture endpoint
  app.post("/api/save-results", async (req, res) => {
    try {
      const { saveResultsSchema } = await import("@shared/schema");
      const { db } = await import("./db");
      const { leads } = await import("@shared/schema");
      
      const input = saveResultsSchema.parse(req.body);
      
      // Insert lead into database
      const [lead] = await db.insert(leads).values({
        name: input.name,
        email: input.email,
        phone: input.phone || null,
        salary: Math.round(input.calculationData.salary),
        yearsOfService: input.calculationData.yearsOfService,
        age: input.calculationData.age,
        retirementSystem: input.calculationData.retirementSystem,
        monthlyPension: Math.round(input.calculationData.monthlyPension),
        netBuyout: Math.round(input.calculationData.netBuyout),
        breakEvenYears: input.calculationData.breakEvenYears.toFixed(1),
      }).returning();
      
      console.log("=== NEW LEAD CAPTURED ===");
      console.log(`Name: ${input.name}`);
      console.log(`Email: ${input.email}`);
      console.log(`Phone: ${input.phone || 'Not provided'}`);
      console.log(`Monthly Pension: $${input.calculationData.monthlyPension}`);
      console.log(`Net Buyout: $${input.calculationData.netBuyout}`);
      console.log("=========================");

      res.json({ 
        success: true, 
        message: "Your results have been saved! We'll be in touch soon.",
        leadId: lead.id
      });

    } catch (err) {
      if (err instanceof z.ZodError) {
        res.status(400).json({
          message: err.errors[0].message,
          field: err.errors[0].path.join('.'),
        });
      } else {
        console.error(err);
        res.status(500).json({ message: "Failed to save results. Please try again." });
      }
    }
  });

  // Contact form endpoint
  app.post("/api/contact", (req, res) => {
    try {
      const contactSchema = z.object({
        name: z.string().min(2),
        email: z.string().email(),
        subject: z.string().min(3),
        message: z.string().min(10),
      });

      const input = contactSchema.parse(req.body);
      
      // Log the contact form submission
      console.log("=== NEW CONTACT FORM SUBMISSION ===");
      console.log(`From: ${input.name} <${input.email}>`);
      console.log(`Subject: ${input.subject}`);
      console.log(`Message: ${input.message}`);
      console.log("To: support@fedbuyout.com");
      console.log("===================================");

      // TODO: Integrate with email service (Resend/SendGrid) to actually send emails
      // For now, we log the submission and return success
      
      res.json({ 
        success: true, 
        message: "Your message has been received. We'll respond within 1-2 business days." 
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
