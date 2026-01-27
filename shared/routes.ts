import { z } from 'zod';
import { calculateInputSchema, calculationResultSchema, emailSignupSchema } from './schema';

export const errorSchemas = {
  validation: z.object({
    message: z.string(),
    field: z.string().optional(),
  }),
  internal: z.object({
    message: z.string(),
  }),
};

export const api = {
  calculator: {
    calculate: {
      method: 'POST' as const,
      path: '/api/calculate',
      input: calculateInputSchema,
      responses: {
        200: calculationResultSchema,
        400: errorSchemas.validation,
      },
    },
  },
  newsletter: {
    signup: {
      method: 'POST' as const,
      path: '/api/newsletter/signup',
      input: emailSignupSchema,
      responses: {
        200: z.object({ success: z.boolean(), message: z.string() }),
        400: errorSchemas.validation,
      },
    },
  },
};

export function buildUrl(path: string, params?: Record<string, string | number>): string {
  let url = path;
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (url.includes(`:${key}`)) {
        url = url.replace(`:${key}`, String(value));
      }
    });
  }
  return url;
}

// Type exports
export type CalculateInput = z.infer<typeof api.calculator.calculate.input>;
export type CalculationResponse = z.infer<typeof api.calculator.calculate.responses[200]>;
export type EmailSignupInput = z.infer<typeof api.newsletter.signup.input>;
