import { useState } from "react";
import { useCalculate, useNewsletterSignup } from "@/hooks/use-calculator";
import { CalculatorForm } from "@/components/CalculatorForm";
import { ResultsCard } from "@/components/ResultsCard";
import type { CalculationResult } from "@shared/schema";
import { 
  BadgeCheck, 
  Info, 
  ShieldCheck, 
  Scale, 
  FileText, 
  AlertTriangle,
  Clock,
  Users,
  Mail,
  ArrowRight
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

export default function Home() {
  const [result, setResult] = useState<CalculationResult | null>(null);
  const [email, setEmail] = useState("");
  const calculateMutation = useCalculate();
  const newsletterMutation = useNewsletterSignup();
  const { toast } = useToast();

  const handleCalculate = (data: any) => {
    calculateMutation.mutate(data, {
      onSuccess: (data) => setResult(data),
    });
  };

  const handleNewsletterSignup = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    
    newsletterMutation.mutate({ email }, {
      onSuccess: (data) => {
        toast({ title: "Subscribed!", description: data.message });
        setEmail("");
      },
      onError: () => {
        toast({ title: "Error", description: "Please enter a valid email.", variant: "destructive" });
      }
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
            <a href="#calculator" className="hover:text-primary transition-colors">Calculator</a>
            <a href="#info" className="hover:text-primary transition-colors">Info</a>
            <a href="#disclaimer" className="hover:text-primary transition-colors">Disclaimer</a>
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
          <div className="flex flex-wrap justify-center gap-3 text-sm">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100">
              <BadgeCheck className="w-4 h-4" /> FERS & CSRS Supported
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-purple-50 text-purple-700 border border-purple-100">
              <Clock className="w-4 h-4" /> Early Retirement Penalties
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-50 text-amber-700 border border-amber-100">
              <Users className="w-4 h-4" /> Survivor Benefits
            </span>
          </div>
        </div>

        {/* Calculator Section */}
        <div id="calculator" className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start">
          <div className="lg:col-span-7">
            <CalculatorForm 
              onSubmit={handleCalculate} 
              isLoading={calculateMutation.isPending} 
            />
          </div>

          <div className="lg:col-span-5 relative">
            <ResultsCard 
              result={result} 
              isLoading={calculateMutation.isPending} 
            />
          </div>
        </div>

        {/* Did You Know Section */}
        <div id="info" className="mt-16 pt-12 border-t border-slate-200">
          <h2 className="text-2xl font-bold text-slate-900 text-center mb-8">Did You Know?</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
              <div className="flex items-start gap-3">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <Info className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-900">CSRS Multipliers</h4>
                  <p className="text-sm text-slate-500 mt-1">
                    CSRS employees get higher multipliers: 1.5% (years 1-5), 1.75% (6-10), and 2% (11+).
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
              <div className="flex items-start gap-3">
                <div className="bg-emerald-100 p-2 rounded-lg">
                  <BadgeCheck className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-900">Age Adjustment</h4>
                  <p className="text-sm text-slate-500 mt-1">
                    Over 40? Severance gets a 2.5% boost for every quarter-year over age 40.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
              <div className="flex items-start gap-3">
                <div className="bg-purple-100 p-2 rounded-lg">
                  <Clock className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-900">FERS 1.1% Bonus</h4>
                  <p className="text-sm text-slate-500 mt-1">
                    If you are 62+ with 20+ years, your multiplier increases from 1.0% to 1.1%.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
              <div className="flex items-start gap-3">
                <div className="bg-amber-100 p-2 rounded-lg">
                  <AlertTriangle className="w-5 h-5 text-amber-600" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-900">Early Penalty</h4>
                  <p className="text-sm text-slate-500 mt-1">
                    Retiring before MRA? Your pension is reduced by 5% for each year early.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Email Signup Section */}
        <div className="mt-16 bg-gradient-to-br from-primary to-blue-700 rounded-3xl p-8 md:p-12 text-white text-center">
          <Mail className="w-12 h-12 mx-auto mb-4 opacity-80" />
          <h2 className="text-2xl md:text-3xl font-bold mb-3">Stay Updated on Federal Buyout News</h2>
          <p className="text-blue-100 mb-6 max-w-lg mx-auto">
            Get updates when buyout offers change, new calculators are added, or important deadlines approach.
          </p>
          <form onSubmit={handleNewsletterSignup} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <Input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-white/10 border-white/20 text-white placeholder:text-white/60 flex-1"
              data-testid="input-newsletter-email"
            />
            <Button 
              type="submit" 
              variant="secondary" 
              disabled={newsletterMutation.isPending}
              data-testid="button-subscribe"
              className="gap-2"
            >
              {newsletterMutation.isPending ? "Subscribing..." : (
                <>Subscribe <ArrowRight className="w-4 h-4" /></>
              )}
            </Button>
          </form>
        </div>

        {/* Disclaimer Section */}
        <div id="disclaimer" className="mt-16 bg-amber-50 border-2 border-amber-200 rounded-2xl p-6 md:p-8">
          <div className="flex items-start gap-4">
            <div className="bg-amber-100 p-3 rounded-xl shrink-0">
              <AlertTriangle className="w-6 h-6 text-amber-700" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-amber-900 mb-2">Important Disclaimer</h3>
              <p className="text-amber-800 text-sm leading-relaxed">
                This calculator provides <strong>estimates only</strong> and is <strong>not a substitute</strong> for official OPM guidance or personalized financial advice. The calculations are based on general formulas and may not account for all individual circumstances including:
              </p>
              <ul className="list-disc list-inside text-amber-800 text-sm mt-3 space-y-1">
                <li>Special retirement provisions (law enforcement, firefighters, air traffic controllers)</li>
                <li>Military buyback credits</li>
                <li>Disability retirement considerations</li>
                <li>Deferred retirement options</li>
                <li>FEHB health insurance continuation rules</li>
                <li>TSP (Thrift Savings Plan) implications</li>
              </ul>
              <p className="text-amber-800 text-sm mt-4 font-medium">
                Always consult with your agency HR office and consider speaking with a qualified financial advisor before making any decisions about your federal career. <strong>This tool is not affiliated with or endorsed by OPM or any government agency.</strong>
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t border-slate-200 text-center">
          <div className="flex justify-center gap-6 text-sm text-slate-500 mb-4">
            <a href="#" className="hover:text-primary transition-colors">About</a>
            <a href="#" className="hover:text-primary transition-colors">Privacy</a>
            <a href="#" className="hover:text-primary transition-colors">Contact</a>
          </div>
          <p className="text-sm text-slate-400 flex items-center justify-center gap-2">
            <FileText className="w-4 h-4" />
            Calculations based on standard OPM formulas and 2025 tax brackets.
          </p>
          <p className="text-xs text-slate-300 mt-2">
            FedBuyout.com - For estimation purposes only.
          </p>
        </footer>
      </main>
    </div>
  );
}
