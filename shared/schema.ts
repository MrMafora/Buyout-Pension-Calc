import { pgTable, text, serial, integer, boolean, timestamp, numeric } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// We don't need a database for this logic-only app, but we'll keep the structure
// in case we want to save calculations later.
export const calculations = pgTable("calculations", {
  id: serial("id").primaryKey(),
  salary: integer("salary").notNull(),
  yearsOfService: integer("years_of_service").notNull(),
  age: integer("age").notNull(),
  buyoutOffer: integer("buyout_offer"), // User provided fixed amount
  createdAt: timestamp("created_at").defaultNow(),
});

export const insertCalculationSchema = createInsertSchema(calculations).pick({
  salary: true,
  yearsOfService: true,
  age: true,
  buyoutOffer: true,
});

// === API CONTRACT TYPES ===

export const calculateInputSchema = z.object({
  currentSalary: z.number().min(1, "Salary is required"),
  yearsOfService: z.number().min(0, "Years of service is required"),
  age: z.number().min(18, "Age must be 18+"),
  buyoutMode: z.enum(["custom", "8month", "severance"]).default("8month"),
  customBuyoutAmount: z.number().optional(),
  stateTaxRate: z.number().min(0).max(100).default(0),
});

export type CalculateInput = z.infer<typeof calculateInputSchema>;

export const taxBreakdownSchema = z.object({
  federal: z.number(),
  socialSecurity: z.number(),
  medicare: z.number(),
  state: z.number(),
  totalTax: z.number(),
});

export const calculationResultSchema = z.object({
  pension: z.object({
    annual: z.number(),
    monthly: z.number(),
    multiplier: z.number(), // 1.0 or 1.1
    high3: z.number(), // Assumed same as current for simplicity, or we could ask
  }),
  severance: z.object({
    weeklyRate: z.number(),
    basicWeeks: z.number(),
    basicAmount: z.number(),
    ageAdjustmentFactor: z.number(),
    ageAdjustmentAmount: z.number(),
    totalGross: z.number(),
  }),
  buyout: z.object({
    gross: z.number(),
    net: z.number(),
    taxes: taxBreakdownSchema,
  }),
  comparison: z.object({
    breakEvenYears: z.number(), // Buyout Net / Pension Annual
    difference5Year: z.number(), // (Pension * 5) - Buyout Net
  })
});

export type CalculationResult = z.infer<typeof calculationResultSchema>;
