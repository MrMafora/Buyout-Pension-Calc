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
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { Calculator, ChevronRight, ChevronDown, AlertTriangle, Info } from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

interface CalculatorFormProps {
  onSubmit: (data: CalculateInput) => void;
  isLoading: boolean;
}

export function CalculatorForm({ onSubmit, isLoading }: CalculatorFormProps) {
  const [earlyRetirementOpen, setEarlyRetirementOpen] = useState(false);
  
  const form = useForm<CalculateInput>({
    resolver: zodResolver(calculateInputSchema),
    defaultValues: {
      currentSalary: 85000,
      yearsOfService: 15,
      age: 50,
      retirementSystem: "fers",
      isEarlyRetirement: false,
      minimumRetirementAge: 57,
      survivorBenefit: "none",
      buyoutMode: "8month",
      stateTaxRate: 5.0,
      customBuyoutAmount: 25000,
    },
  });

  const buyoutMode = form.watch("buyoutMode");
  const isEarlyRetirement = form.watch("isEarlyRetirement");
  const retirementSystem = form.watch("retirementSystem");

  return (
    <div className="bg-white rounded-3xl p-8 border border-slate-100 shadow-xl shadow-slate-200/40">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900 font-display">Your Details</h2>
        <p className="text-slate-500">Enter your current federal service information.</p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Basic Info */}
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
                      data-testid="input-salary"
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
                      data-testid="input-years"
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
                      data-testid="input-age"
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
                      data-testid="input-state-tax"
                      {...field}
                      onChange={e => field.onChange(Number(e.target.value))}
                      className="text-lg font-mono"
                    />
                  </FormControl>
                  <FormDescription className="text-xs">
                    CA: 13.3% | NY: 10.9% | TX/FL: 0%
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          {/* Retirement System Toggle */}
          <div className="pt-6 border-t border-slate-100">
            <FormField
              control={form.control}
              name="retirementSystem"
              render={({ field }) => (
                <FormItem className="space-y-3">
                  <FormLabel className="text-base font-semibold flex items-center gap-2">
                    Retirement System
                    <span className="text-xs font-normal text-muted-foreground">(affects pension calculation)</span>
                  </FormLabel>
                  <FormControl>
                    <RadioGroup
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      className="grid grid-cols-2 gap-3"
                    >
                      <FormItem className={cn(
                        "flex items-center space-x-3 space-y-0 rounded-xl border p-4 transition-all cursor-pointer",
                        field.value === "fers" ? "border-primary bg-primary/5 ring-1 ring-primary" : "border-slate-200 hover:border-slate-300"
                      )}>
                        <FormControl>
                          <RadioGroupItem value="fers" data-testid="radio-fers" />
                        </FormControl>
                        <FormLabel className="font-normal cursor-pointer flex-1">
                          <span className="font-semibold block text-slate-900">FERS</span>
                          <span className="text-slate-500 text-xs">1.0-1.1% multiplier</span>
                        </FormLabel>
                      </FormItem>
                      
                      <FormItem className={cn(
                        "flex items-center space-x-3 space-y-0 rounded-xl border p-4 transition-all cursor-pointer",
                        field.value === "csrs" ? "border-primary bg-primary/5 ring-1 ring-primary" : "border-slate-200 hover:border-slate-300"
                      )}>
                        <FormControl>
                          <RadioGroupItem value="csrs" data-testid="radio-csrs" />
                        </FormControl>
                        <FormLabel className="font-normal cursor-pointer flex-1">
                          <span className="font-semibold block text-slate-900">CSRS</span>
                          <span className="text-slate-500 text-xs">1.5-2.0% multiplier</span>
                        </FormLabel>
                      </FormItem>
                    </RadioGroup>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          {/* Early Retirement Section */}
          <div className="space-y-4">
            <Button 
              type="button" 
              variant="ghost" 
              onClick={() => setEarlyRetirementOpen(!earlyRetirementOpen)}
              className="w-full justify-between p-4 h-auto bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-xl"
              data-testid="button-early-retirement-toggle"
            >
              <div className="flex items-center gap-2 text-amber-800">
                <AlertTriangle className="w-4 h-4" />
                <span className="font-semibold">Early Retirement Options</span>
              </div>
              <ChevronDown className={cn("w-4 h-4 text-amber-600 transition-transform", earlyRetirementOpen && "rotate-180")} />
            </Button>
            
            {earlyRetirementOpen && (
              <div className="space-y-4 animate-in fade-in slide-in-from-top-2">
                <FormField
                  control={form.control}
                  name="isEarlyRetirement"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border border-slate-200 p-4">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                          data-testid="checkbox-early-retirement"
                        />
                      </FormControl>
                      <div className="space-y-1 leading-none">
                        <FormLabel>I am considering early retirement (before MRA)</FormLabel>
                        <FormDescription>
                          Your pension will be reduced by 5% for each year you are under your Minimum Retirement Age.
                        </FormDescription>
                      </div>
                    </FormItem>
                  )}
                />

                {isEarlyRetirement && (
                  <FormField
                    control={form.control}
                    name="minimumRetirementAge"
                    render={({ field }) => (
                      <FormItem className="animate-in fade-in slide-in-from-top-2">
                        <FormLabel>Your Minimum Retirement Age (MRA): {field.value}</FormLabel>
                        <FormControl>
                          <Slider
                            min={55}
                            max={57}
                            step={1}
                            value={[field.value]}
                            onValueChange={(vals) => field.onChange(vals[0])}
                            className="py-4"
                            data-testid="slider-mra"
                          />
                        </FormControl>
                        <FormDescription className="text-xs">
                          MRA varies by birth year: Born before 1948 = 55, 1953-1964 = 56, 1970+ = 57
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                )}
              </div>
            )}
          </div>

          {/* Survivor Benefits */}
          <div className="pt-4">
            <FormField
              control={form.control}
              name="survivorBenefit"
              render={({ field }) => (
                <FormItem className="space-y-3">
                  <FormLabel className="text-base font-semibold flex items-center gap-2">
                    Survivor Benefit Election
                    <Info className="w-4 h-4 text-muted-foreground" />
                  </FormLabel>
                  <FormDescription className="text-xs -mt-1">
                    Providing for a spouse reduces your pension but gives them income after you pass.
                  </FormDescription>
                  <FormControl>
                    <RadioGroup
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      className="grid grid-cols-1 gap-2"
                    >
                      <FormItem className={cn(
                        "flex items-center space-x-3 space-y-0 rounded-lg border p-3 transition-all cursor-pointer",
                        field.value === "none" ? "border-primary bg-primary/5" : "border-slate-200 hover:border-slate-300"
                      )}>
                        <FormControl>
                          <RadioGroupItem value="none" data-testid="radio-survivor-none" />
                        </FormControl>
                        <FormLabel className="font-normal cursor-pointer flex-1 text-sm">
                          <span className="font-medium">None</span>
                          <span className="text-slate-500 ml-2">Full pension for you</span>
                        </FormLabel>
                      </FormItem>
                      
                      <FormItem className={cn(
                        "flex items-center space-x-3 space-y-0 rounded-lg border p-3 transition-all cursor-pointer",
                        field.value === "partial" ? "border-primary bg-primary/5" : "border-slate-200 hover:border-slate-300"
                      )}>
                        <FormControl>
                          <RadioGroupItem value="partial" data-testid="radio-survivor-partial" />
                        </FormControl>
                        <FormLabel className="font-normal cursor-pointer flex-1 text-sm">
                          <span className="font-medium">Partial (25% to survivor)</span>
                          <span className="text-amber-600 ml-2">-5% pension</span>
                        </FormLabel>
                      </FormItem>

                      <FormItem className={cn(
                        "flex items-center space-x-3 space-y-0 rounded-lg border p-3 transition-all cursor-pointer",
                        field.value === "full" ? "border-primary bg-primary/5" : "border-slate-200 hover:border-slate-300"
                      )}>
                        <FormControl>
                          <RadioGroupItem value="full" data-testid="radio-survivor-full" />
                        </FormControl>
                        <FormLabel className="font-normal cursor-pointer flex-1 text-sm">
                          <span className="font-medium">Full (50% to survivor)</span>
                          <span className="text-amber-600 ml-2">-10% pension</span>
                        </FormLabel>
                      </FormItem>
                    </RadioGroup>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          {/* Buyout Type */}
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
                          <RadioGroupItem value="8month" data-testid="radio-8month" />
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
                          <RadioGroupItem value="severance" data-testid="radio-severance" />
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
                          <RadioGroupItem value="custom" data-testid="radio-custom" />
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
                      data-testid="input-custom-amount"
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
            data-testid="button-calculate"
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
