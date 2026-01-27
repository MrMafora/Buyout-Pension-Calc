import { motion } from "framer-motion";
import { 
  DollarSign, 
  TrendingUp, 
  Briefcase, 
  AlertCircle,
  PiggyBank,
  ArrowRight
} from "lucide-react";
import type { CalculationResult } from "@shared/schema";
import { cn } from "@/lib/utils";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

interface ResultsCardProps {
  result: CalculationResult | null;
  isLoading: boolean;
}

const formatCurrency = (val: number) => 
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

export function ResultsCard({ result, isLoading }: ResultsCardProps) {
  if (isLoading) {
    return (
      <div className="h-full min-h-[400px] flex flex-col items-center justify-center p-8 bg-white rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50">
        <div className="w-16 h-16 border-4 border-primary/30 border-t-primary rounded-full animate-spin mb-6" />
        <p className="text-slate-500 font-medium animate-pulse">Crunching the federal numbers...</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="h-full min-h-[400px] flex flex-col items-center justify-center p-8 bg-slate-50 rounded-3xl border border-dashed border-slate-200 text-center">
        <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mb-4 text-slate-400">
          <DollarSign className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-bold text-slate-700">Ready to Estimate</h3>
        <p className="text-slate-500 mt-2 max-w-xs">
          Enter your service details on the left to see your potential buyout vs. pension comparison.
        </p>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-3xl border border-slate-100 shadow-2xl shadow-slate-200/50 overflow-hidden sticky top-8"
    >
      {/* Header Result */}
      <div className="bg-gradient-to-br from-slate-900 to-slate-800 p-8 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 p-32 bg-white/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
        
        <div className="relative z-10">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-xs font-medium text-white/80 border border-white/10 mb-4">
            <TrendingUp className="w-3 h-3" /> Estimate
          </span>
          
          <div className="space-y-1">
            <p className="text-slate-400 text-sm font-medium uppercase tracking-wider">Estimated Net Buyout</p>
            <h2 className="text-5xl font-bold tracking-tight text-white">
              {formatCurrency(result.buyout.net)}
            </h2>
            <p className="text-slate-400 text-sm mt-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              After est. taxes of {formatCurrency(result.buyout.taxes.totalTax)}
            </p>
          </div>
        </div>
      </div>

      <div className="p-8 space-y-8">
        {/* Pension Comparison */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <PiggyBank className="w-5 h-5 text-primary" />
              Vs. Pension Income
            </h3>
            <span className="text-sm text-muted-foreground">FERS Annuity</span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
              <p className="text-xs font-medium text-muted-foreground uppercase mb-1">Monthly</p>
              <p className="text-2xl font-bold text-slate-900">{formatCurrency(result.pension.monthly)}</p>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
              <p className="text-xs font-medium text-muted-foreground uppercase mb-1">Annual</p>
              <p className="text-2xl font-bold text-slate-900">{formatCurrency(result.pension.annual)}</p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-amber-50 border border-amber-100 text-amber-900 text-sm flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <p>
              <span className="font-bold block text-amber-800 mb-1">Break-Even Analysis</span>
              It would take about <strong className="text-amber-700">{result.comparison.breakEvenYears.toFixed(1)} years</strong> of pension payments to equal this net buyout amount.
            </p>
          </div>
        </div>

        {/* Breakdown Accordion */}
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="taxes" className="border-b-0 mb-2">
            <AccordionTrigger className="hover:no-underline py-3 px-4 bg-slate-50 rounded-xl data-[state=open]:rounded-b-none data-[state=open]:bg-slate-100 transition-colors">
              <span className="font-semibold text-slate-700">Tax Breakdown</span>
            </AccordionTrigger>
            <AccordionContent className="px-4 py-4 bg-slate-50 rounded-b-xl border-t border-slate-200/50">
              <div className="space-y-3 text-sm">
                <div className="flex justify-between text-slate-600">
                  <span>Gross Amount</span>
                  <span className="font-mono font-medium">{formatCurrency(result.buyout.gross)}</span>
                </div>
                <div className="h-px bg-slate-200 my-2" />
                <div className="flex justify-between text-red-500">
                  <span>Federal (22%)</span>
                  <span className="font-mono">-{formatCurrency(result.buyout.taxes.federal)}</span>
                </div>
                <div className="flex justify-between text-red-500">
                  <span>Social Security (6.2%)</span>
                  <span className="font-mono">-{formatCurrency(result.buyout.taxes.socialSecurity)}</span>
                </div>
                <div className="flex justify-between text-red-500">
                  <span>Medicare (1.45%)</span>
                  <span className="font-mono">-{formatCurrency(result.buyout.taxes.medicare)}</span>
                </div>
                <div className="flex justify-between text-red-500">
                  <span>State Tax (Est.)</span>
                  <span className="font-mono">-{formatCurrency(result.buyout.taxes.state)}</span>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="formula" className="border-b-0">
            <AccordionTrigger className="hover:no-underline py-3 px-4 bg-slate-50 rounded-xl data-[state=open]:rounded-b-none data-[state=open]:bg-slate-100 transition-colors">
              <span className="font-semibold text-slate-700">Formula Details</span>
            </AccordionTrigger>
            <AccordionContent className="px-4 py-4 bg-slate-50 rounded-b-xl border-t border-slate-200/50">
              <div className="space-y-3 text-sm text-slate-600">
                <div className="flex justify-between">
                  <span>Weekly Base Rate</span>
                  <span className="font-mono">{formatCurrency(result.severance.weeklyRate)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Credited Weeks</span>
                  <span className="font-mono">{result.severance.basicWeeks.toFixed(1)} weeks</span>
                </div>
                {result.severance.ageAdjustmentFactor > 1 && (
                  <div className="p-2 bg-blue-50 text-blue-800 rounded text-xs mt-2">
                    <strong>Age Bonus Active:</strong> Your severance was multiplied by {result.severance.ageAdjustmentFactor.toFixed(2)}x because you are over 40.
                  </div>
                )}
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </motion.div>
  );
}
