import { useMutation } from "@tanstack/react-query";
import { api, type CalculateInput, type CalculationResult } from "@shared/routes";
import { useToast } from "@/hooks/use-toast";
import { z } from "zod";

export function useCalculate() {
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (data: CalculateInput) => {
      // Validate locally first (good practice)
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
