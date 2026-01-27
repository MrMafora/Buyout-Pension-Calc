import { pgTable, text, serial, integer, boolean, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// We don't need a database for this logic-only app, but we'll keep the structure
export const calculations = pgTable("calculations", {
  id: serial("id").primaryKey(),
  salary: integer("salary").notNull(),
  yearsOfService: integer("years_of_service").notNull(),
  age: integer("age").notNull(),
  buyoutOffer: integer("buyout_offer"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const insertCalculationSchema = createInsertSchema(calculations).pick({
  salary: true,
  yearsOfService: true,
  age: true,
  buyoutOffer: true,
});

// === API CONTRACT TYPES ===

export const retirementSystemSchema = z.enum(["fers", "csrs"]);
export type RetirementSystem = z.infer<typeof retirementSystemSchema>;

export const survivorBenefitSchema = z.enum(["none", "partial", "full"]);
export type SurvivorBenefit = z.infer<typeof survivorBenefitSchema>;

export const calculateInputSchema = z.object({
  currentSalary: z.number().min(1, "Salary is required"),
  yearsOfService: z.number().min(0, "Years of service is required"),
  age: z.number().min(18, "Age must be 18+"),
  retirementSystem: retirementSystemSchema.default("fers"),
  
  // Special provisions (LEO, firefighters, ATC)
  isSpecialProvisions: z.boolean().default(false),
  
  // Military buyback
  militaryYears: z.number().min(0).max(40).default(0),
  
  // Deferred retirement
  isDeferredRetirement: z.boolean().default(false),
  
  // Early retirement
  isEarlyRetirement: z.boolean().default(false),
  minimumRetirementAge: z.number().min(55).max(57).default(57), // MRA varies by birth year
  
  // Survivor benefits
  survivorBenefit: survivorBenefitSchema.default("none"),
  
  // Buyout options
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
    annualGross: z.number(),
    annualNet: z.number(), // After survivor benefit reduction
    monthly: z.number(),
    multiplier: z.number(),
    high3: z.number(),
    totalYearsOfService: z.number(), // Including military buyback
    militaryYearsAdded: z.number(),
    isSpecialProvisions: z.boolean(),
    earlyRetirementPenalty: z.number(), // Percentage reduction
    earlyRetirementReduction: z.number(), // Dollar amount
    survivorBenefitReduction: z.number(), // Percentage
    survivorBenefitAmount: z.number(), // Dollar reduction
    retirementSystem: z.string(),
    deferredPensionAt62: z.number().optional(), // Annual pension if deferred
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
    breakEvenYears: z.number(),
    difference5Year: z.number(),
    difference10Year: z.number(),
    recommendation: z.string(),
  })
});

export type CalculationResult = z.infer<typeof calculationResultSchema>;

// Email signup schema
export const emailSignupSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
});

export type EmailSignup = z.infer<typeof emailSignupSchema>;
