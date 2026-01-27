import { useState } from "react";
import { useCalculate } from "@/hooks/use-calculator";
import { CalculatorForm } from "@/components/CalculatorForm";
import { ResultsCard } from "@/components/ResultsCard";
import type { CalculationResult } from "@shared/schema";
import { BadgeCheck, Info, ShieldCheck, Scale, FileText } from "lucide-react";

export default function Home() {
  const [result, setResult] = useState<CalculationResult | null>(null);
  const calculateMutation = useCalculate();

  const handleCalculate = (data: any) => {
    calculateMutation.mutate(data, {
      onSuccess: (data) => setResult(data),
    });
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      {/* Navbar */}
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-primary/10 p-2 rounded-lg">
              <Scale className="w-6 h-6 text-primary" />
            </div>
            <span className="font-display font-bold text-xl tracking-tight text-slate-900">
              Fed<span className="text-primary">Buyout</span>.com
            </span>
          </div>
          <div className="hidden sm:flex items-center gap-6 text-sm font-medium text-slate-600">
            <a href="#how-it-works" className="hover:text-primary transition-colors">How it Works</a>
            <a href="#about" className="hover:text-primary transition-colors">About</a>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-sm font-medium mb-6 border border-blue-100">
            <ShieldCheck className="w-4 h-4" /> Unofficial Estimation Tool
          </span>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 mb-6 tracking-tight leading-tight">
            Should you take the <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-600">Buyout or Stay?</span>
          </h1>
          <p className="text-lg text-slate-600 mb-8 max-w-2xl mx-auto leading-relaxed">
            Federal employees are facing tough decisions. Compare your potential severance or buyout offer against the pension value you might be leaving behind.
          </p>
        </div>

        {/* Calculator Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start">
          <div className="lg:col-span-7">
            <CalculatorForm 
              onSubmit={handleCalculate} 
              isLoading={calculateMutation.isPending} 
            />
            
            {/* Info Cards - Mobile/Desktop placement */}
            <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
                <div className="flex items-start gap-3">
                  <BadgeCheck className="w-5 h-5 text-emerald-500 mt-1" />
                  <div>
                    <h4 className="font-bold text-slate-900">Age Adjustment</h4>
                    <p className="text-sm text-slate-500 mt-1">
                      If you are over 40, severance pay increases by 2.5% for every quarter-year over age 40. This can significantly boost your payout.
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-blue-500 mt-1" />
                  <div>
                    <h4 className="font-bold text-slate-900">FERS Calculation</h4>
                    <p className="text-sm text-slate-500 mt-1">
                      Pension is calculated as High-3 Salary × Years × 1% (or 1.1% if age 62+ with 20+ years).
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5 relative">
            <ResultsCard 
              result={result} 
              isLoading={calculateMutation.isPending} 
            />
          </div>
        </div>

        {/* Footer Disclaimer */}
        <div className="mt-24 pt-8 border-t border-slate-200 text-center">
          <p className="text-sm text-slate-400 flex items-center justify-center gap-2">
            <FileText className="w-4 h-4" />
            Disclaimer: This tool is for estimation purposes only. Not official OPM advice. 
            Consult with a financial advisor before making career decisions.
          </p>
          <p className="text-xs text-slate-300 mt-2">
            Calculations based on standard OPM formulas and 2024 tax brackets.
          </p>
        </div>
      </main>
    </div>
  );
}
