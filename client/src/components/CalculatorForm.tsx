import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { calculateInputSchema, type CalculateInput } from "@shared/schema";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";
import { Calculator, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface CalculatorFormProps {
  onSubmit: (data: CalculateInput) => void;
  isLoading: boolean;
}

export function CalculatorForm({ onSubmit, isLoading }: CalculatorFormProps) {
  const form = useForm<CalculateInput>({
    resolver: zodResolver(calculateInputSchema),
    defaultValues: {
      currentSalary: 75000,
      yearsOfService: 10,
      age: 45,
      buyoutMode: "8month",
      stateTaxRate: 5.0,
      customBuyoutAmount: 25000,
    },
  });

  const buyoutMode = form.watch("buyoutMode");

  return (
    <div className="bg-white rounded-3xl p-8 border border-slate-100 shadow-xl shadow-slate-200/40">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900 font-display">Your Details</h2>
        <p className="text-slate-500">Enter your current federal service information.</p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormField
              control={form.control}
              name="currentSalary"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Current Annual Salary ($)</FormLabel>
                  <FormControl>
                    <Input 
                      type="number" 
                      placeholder="85000" 
                      {...field} 
                      onChange={e => field.onChange(Number(e.target.value))}
                      className="text-lg font-mono"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="yearsOfService"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Years of Service</FormLabel>
                  <FormControl>
                    <Input 
                      type="number" 
                      {...field}
                      onChange={e => field.onChange(Number(e.target.value))}
                      className="text-lg font-mono"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="age"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Your Age</FormLabel>
                  <FormControl>
                    <Input 
                      type="number" 
                      {...field}
                      onChange={e => field.onChange(Number(e.target.value))}
                      className="text-lg font-mono"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="stateTaxRate"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>State Tax Rate (%)</FormLabel>
                  <FormControl>
                    <Input 
                      type="number" 
                      step="0.1" 
                      {...field}
                      onChange={e => field.onChange(Number(e.target.value))}
                      className="text-lg font-mono"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="pt-6 border-t border-slate-100">
            <FormField
              control={form.control}
              name="buyoutMode"
              render={({ field }) => (
                <FormItem className="space-y-3">
                  <FormLabel className="text-base font-semibold">Buyout Type to Estimate</FormLabel>
                  <FormControl>
                    <RadioGroup
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      className="grid grid-cols-1 gap-3"
                    >
                      <FormItem className={cn(
                        "flex items-center space-x-3 space-y-0 rounded-xl border p-4 transition-all cursor-pointer",
                        field.value === "8month" ? "border-primary bg-primary/5 ring-1 ring-primary" : "border-slate-200 hover:border-slate-300"
                      )}>
                        <FormControl>
                          <RadioGroupItem value="8month" />
                        </FormControl>
                        <FormLabel className="font-normal cursor-pointer flex-1">
                          <span className="font-semibold block text-slate-900">8-Month Buyout (Proposed)</span>
                          <span className="text-slate-500 text-sm">Full 8 months of your basic pay</span>
                        </FormLabel>
                      </FormItem>
                      
                      <FormItem className={cn(
                        "flex items-center space-x-3 space-y-0 rounded-xl border p-4 transition-all cursor-pointer",
                        field.value === "severance" ? "border-primary bg-primary/5 ring-1 ring-primary" : "border-slate-200 hover:border-slate-300"
                      )}>
                        <FormControl>
                          <RadioGroupItem value="severance" />
                        </FormControl>
                        <FormLabel className="font-normal cursor-pointer flex-1">
                          <span className="font-semibold block text-slate-900">Standard Severance</span>
                          <span className="text-slate-500 text-sm">Based on years of service + age adjustment</span>
                        </FormLabel>
                      </FormItem>

                      <FormItem className={cn(
                        "flex items-center space-x-3 space-y-0 rounded-xl border p-4 transition-all cursor-pointer",
                        field.value === "custom" ? "border-primary bg-primary/5 ring-1 ring-primary" : "border-slate-200 hover:border-slate-300"
                      )}>
                        <FormControl>
                          <RadioGroupItem value="custom" />
                        </FormControl>
                        <FormLabel className="font-normal cursor-pointer flex-1">
                          <span className="font-semibold block text-slate-900">Custom Amount</span>
                          <span className="text-slate-500 text-sm">Enter a specific buyout offer amount</span>
                        </FormLabel>
                      </FormItem>
                    </RadioGroup>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          {buyoutMode === "custom" && (
            <FormField
              control={form.control}
              name="customBuyoutAmount"
              render={({ field }) => (
                <FormItem className="animate-in fade-in slide-in-from-top-2">
                  <FormLabel>Custom Amount ($)</FormLabel>
                  <FormControl>
                    <Input 
                      type="number" 
                      {...field}
                      onChange={e => field.onChange(Number(e.target.value))}
                      className="text-lg font-mono"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          )}

          <Button 
            type="submit" 
            size="lg" 
            className="w-full text-lg h-14 mt-4" 
            disabled={isLoading}
          >
            {isLoading ? (
              "Calculating..." 
            ) : (
              <>
                <Calculator className="mr-2 h-5 w-5" /> Calculate Payout
                <ChevronRight className="ml-2 h-5 w-5 opacity-50" />
              </>
            )}
          </Button>
        </form>
      </Form>
    </div>
  );
}
