export const CALCULATOR_CONFIG = {
  lastUpdated: "January 27, 2026",
  dataYear: 2026,
  
  taxes: {
    federal: {
      rate: 0.22,
      description: "22% flat rate (simplified)",
    },
    socialSecurity: {
      rate: 0.062,
      wageBase: 184500,
      description: "6.2% on first $184,500",
    },
    medicare: {
      rate: 0.0145,
      description: "1.45% on all earnings",
    },
  },
  
  fers: {
    standardMultiplier: 0.01,
    bonusMultiplier: 0.011,
    bonusAgeRequirement: 62,
    bonusYearsRequirement: 20,
    description: "1.0% standard, 1.1% if age 62+ with 20+ years",
  },
  
  csrs: {
    tier1Multiplier: 0.015,
    tier1Years: 5,
    tier2Multiplier: 0.0175,
    tier2Years: 5,
    tier3Multiplier: 0.02,
    maxBenefitPercent: 0.80,
    description: "1.5% first 5 years, 1.75% next 5, 2.0% thereafter (max 80%)",
  },
  
  earlyRetirement: {
    penaltyPerYear: 0.05,
    description: "5% reduction per year under MRA",
  },
  
  survivorBenefit: {
    partial: 0.05,
    full: 0.10,
    description: "Partial: 5% reduction, Full: 10% reduction",
  },
  
  severance: {
    hoursPerYear: 2087,
    hoursPerWeek: 40,
    tier1WeeksPerYear: 1,
    tier1Years: 10,
    tier2WeeksPerYear: 2,
    ageAdjustmentBase: 40,
    ageAdjustmentPerQuarter: 0.025,
    maxYearsSalary: 1,
    description: "One week per year (first 10), two weeks thereafter + 2.5% per quarter over age 40, max 1 year salary",
  },
  
  buyout: {
    defaultMonths: 8,
    description: "Standard buyout is 8 months of salary",
  },
  
  cola: {
    fers2026: 0.02,
    csrs2026: 0.028,
    description: "FERS: 2.0%, CSRS: 2.8% for 2026",
  },
  
  sources: [
    {
      name: "OPM Retirement Center",
      url: "https://www.opm.gov/retirement-center/",
      description: "Official FERS/CSRS computation rules",
    },
    {
      name: "IRS Tax Brackets 2026",
      url: "https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026",
      description: "Federal income tax rates and brackets",
    },
    {
      name: "Social Security Wage Base",
      url: "https://www.ssa.gov/oact/cola/cbb.html",
      description: "Social Security contribution limits",
    },
    {
      name: "CSRS/FERS Handbook",
      url: "https://www.opm.gov/retirement-center/publications-forms/csrsfers-handbook/",
      description: "Complete retirement computation guide",
    },
  ],
} as const;

export type CalculatorConfig = typeof CALCULATOR_CONFIG;
