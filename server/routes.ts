import type { Express } from "express";
import type { Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { z } from "zod";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {

  app.post(api.calculator.calculate.path, (req, res) => {
    try {
      const input = api.calculator.calculate.input.parse(req.body);
      
      const { currentSalary, yearsOfService, age, buyoutMode, customBuyoutAmount, stateTaxRate } = input;

      // 1. Calculate Pension (FERS)
      // Multiplier: 1.1% if Age >= 62 AND Years >= 20, else 1.0%
      const multiplier = (age >= 62 && yearsOfService >= 20) ? 0.011 : 0.010;
      const annualPension = currentSalary * yearsOfService * multiplier;
      const monthlyPension = annualPension / 12;

      // 2. Calculate Severance Pay (OPM Formula)
      // Weekly Rate
      const weeklyRate = (currentSalary / 2087) * 40;

      // Basic Allowance Weeks
      let basicWeeks = 0;
      if (yearsOfService <= 10) {
        basicWeeks = yearsOfService * 1;
      } else {
        basicWeeks = 10 + (yearsOfService - 10) * 2;
      }

      const basicSeverance = basicWeeks * weeklyRate;

      // Age Adjustment
      // 2.5% for each full quarter year over 40
      let ageAdjustmentFactor = 1.0;
      let ageAdjustmentAmount = 0;

      if (age > 40) {
        const quartersOver40 = (age - 40) * 4; // Assuming integer age input implies full years
        const increasePercent = quartersOver40 * 0.025;
        ageAdjustmentFactor = 1 + increasePercent;
      }

      let totalSeverance = basicSeverance * ageAdjustmentFactor;
      ageAdjustmentAmount = totalSeverance - basicSeverance;

      // Cap at 1 year salary
      if (totalSeverance > currentSalary) {
        totalSeverance = currentSalary;
      }
      
      // 3. Determine Gross Buyout Amount
      let grossBuyout = 0;
      if (buyoutMode === 'custom' && customBuyoutAmount) {
        grossBuyout = customBuyoutAmount;
      } else if (buyoutMode === 'severance') {
        grossBuyout = totalSeverance;
      } else {
        // Default: 8 Month Buyout (Fixed 8 months of salary)
        grossBuyout = (currentSalary / 12) * 8;
      }

      // 4. Calculate Taxes
      // Federal: Flat 22% on supplemental wages
      const fedTax = grossBuyout * 0.22;
      
      // Social Security: 6.2% (Technically capped at $176,100 wage base, simplified here to flat 6.2%)
      // We assume the buyout is subject to SS. 
      const ssTax = grossBuyout * 0.062;

      // Medicare: 1.45%
      const medTax = grossBuyout * 0.0145;

      // State Tax: User input %
      const stateTax = grossBuyout * (stateTaxRate / 100);

      const totalTax = fedTax + ssTax + medTax + stateTax;
      const netBuyout = grossBuyout - totalTax;

      // 5. Comparison
      // Break Even Years: How many years of pension does it take to equal the Net Buyout?
      const breakEvenYears = annualPension > 0 ? (netBuyout / annualPension) : 0;
      
      // 5 Year Difference: (Pension * 5) - Net Buyout
      const difference5Year = (annualPension * 5) - netBuyout;

      const result = {
        pension: {
          annual: Number(annualPension.toFixed(2)),
          monthly: Number(monthlyPension.toFixed(2)),
          multiplier,
          high3: currentSalary, // Simplified
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

  return httpServer;
}
