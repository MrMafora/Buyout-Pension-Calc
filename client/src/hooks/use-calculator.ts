import { useMutation } from "@tanstack/react-query";
import { api } from "@shared/routes";
import type { CalculateInput, EmailSignup } from "@shared/schema";
import { useToast } from "@/hooks/use-toast";

export function useCalculate() {
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (data: CalculateInput) => {
      const validated = api.calculator.calculate.input.parse(data);
      
      const res = await fetch(api.calculator.calculate.path, {
        method: api.calculator.calculate.method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(validated),
      });

      if (!res.ok) {
        if (res.status === 400) {
          const error = api.calculator.calculate.responses[400].parse(await res.json());
          throw new Error(error.message || "Validation failed");
        }
        throw new Error("Failed to calculate results");
      }

      return api.calculator.calculate.responses[200].parse(await res.json());
    },
    onError: (error) => {
      toast({
        title: "Calculation Error",
        description: error.message,
        variant: "destructive",
      });
    }
  });
}

export function useNewsletterSignup() {
  return useMutation({
    mutationFn: async (data: EmailSignup) => {
      const validated = api.newsletter.signup.input.parse(data);
      
      const res = await fetch(api.newsletter.signup.path, {
        method: api.newsletter.signup.method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(validated),
      });

      if (!res.ok) {
        if (res.status === 400) {
          const error = api.newsletter.signup.responses[400].parse(await res.json());
          throw new Error(error.message || "Invalid email");
        }
        throw new Error("Failed to subscribe");
      }

      return api.newsletter.signup.responses[200].parse(await res.json());
    },
  });
}
