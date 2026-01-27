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
  
  stateTaxRates: [
    { state: "Alabama", abbrev: "AL", rate: 5.0 },
    { state: "Alaska", abbrev: "AK", rate: 0 },
    { state: "Arizona", abbrev: "AZ", rate: 2.5 },
    { state: "Arkansas", abbrev: "AR", rate: 4.4 },
    { state: "California", abbrev: "CA", rate: 13.3 },
    { state: "Colorado", abbrev: "CO", rate: 4.4 },
    { state: "Connecticut", abbrev: "CT", rate: 6.99 },
    { state: "Delaware", abbrev: "DE", rate: 6.6 },
    { state: "Florida", abbrev: "FL", rate: 0 },
    { state: "Georgia", abbrev: "GA", rate: 5.09 },
    { state: "Hawaii", abbrev: "HI", rate: 11.0 },
    { state: "Idaho", abbrev: "ID", rate: 5.8 },
    { state: "Illinois", abbrev: "IL", rate: 4.95 },
    { state: "Indiana", abbrev: "IN", rate: 2.95 },
    { state: "Iowa", abbrev: "IA", rate: 3.8 },
    { state: "Kansas", abbrev: "KS", rate: 5.58 },
    { state: "Kentucky", abbrev: "KY", rate: 3.5 },
    { state: "Louisiana", abbrev: "LA", rate: 3.0 },
    { state: "Maine", abbrev: "ME", rate: 7.15 },
    { state: "Maryland", abbrev: "MD", rate: 5.75 },
    { state: "Massachusetts", abbrev: "MA", rate: 5.0 },
    { state: "Michigan", abbrev: "MI", rate: 4.25 },
    { state: "Minnesota", abbrev: "MN", rate: 9.85 },
    { state: "Mississippi", abbrev: "MS", rate: 4.0 },
    { state: "Missouri", abbrev: "MO", rate: 4.7 },
    { state: "Montana", abbrev: "MT", rate: 5.65 },
    { state: "Nebraska", abbrev: "NE", rate: 4.55 },
    { state: "Nevada", abbrev: "NV", rate: 0 },
    { state: "New Hampshire", abbrev: "NH", rate: 0 },
    { state: "New Jersey", abbrev: "NJ", rate: 10.75 },
    { state: "New Mexico", abbrev: "NM", rate: 5.9 },
    { state: "New York", abbrev: "NY", rate: 10.9 },
    { state: "North Carolina", abbrev: "NC", rate: 3.99 },
    { state: "North Dakota", abbrev: "ND", rate: 2.5 },
    { state: "Ohio", abbrev: "OH", rate: 2.75 },
    { state: "Oklahoma", abbrev: "OK", rate: 4.5 },
    { state: "Oregon", abbrev: "OR", rate: 9.9 },
    { state: "Pennsylvania", abbrev: "PA", rate: 3.07 },
    { state: "Rhode Island", abbrev: "RI", rate: 5.99 },
    { state: "South Carolina", abbrev: "SC", rate: 6.2 },
    { state: "South Dakota", abbrev: "SD", rate: 0 },
    { state: "Tennessee", abbrev: "TN", rate: 0 },
    { state: "Texas", abbrev: "TX", rate: 0 },
    { state: "Utah", abbrev: "UT", rate: 4.55 },
    { state: "Vermont", abbrev: "VT", rate: 8.75 },
    { state: "Virginia", abbrev: "VA", rate: 5.75 },
    { state: "Washington", abbrev: "WA", rate: 0 },
    { state: "Washington DC", abbrev: "DC", rate: 10.75 },
    { state: "West Virginia", abbrev: "WV", rate: 5.12 },
    { state: "Wisconsin", abbrev: "WI", rate: 7.65 },
    { state: "Wyoming", abbrev: "WY", rate: 0 },
  ],
  
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
