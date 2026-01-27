import { motion } from "framer-motion";
import { 
  DollarSign, 
  TrendingUp, 
  AlertCircle,
  PiggyBank,
  Share2,
  Copy,
  Check,
  Lightbulb,
  Mail,
  User,
  Phone,
  Send
} from "lucide-react";
import { SiX, SiFacebook, SiLinkedin } from "react-icons/si";
import type { CalculationResult, CalculateInput } from "@shared/schema";
import { cn } from "@/lib/utils";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { useMutation } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";

interface ResultsCardProps {
  result: CalculationResult | null;
  isLoading: boolean;
  inputData?: CalculateInput;
}

const formatCurrency = (val: number) => 
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

export function ResultsCard({ result, isLoading, inputData }: ResultsCardProps) {
  const [copied, setCopied] = useState(false);
  const [emailDialogOpen, setEmailDialogOpen] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [saved, setSaved] = useState(false);
  const { toast } = useToast();

  const saveResultsMutation = useMutation({
    mutationFn: async (data: { name: string; email: string; phone?: string }) => {
      if (!result || !inputData) throw new Error("No results to save");
      const response = await apiRequest("POST", "/api/save-results", {
        name: data.name,
        email: data.email,
        phone: data.phone || undefined,
        calculationData: {
          salary: inputData.currentSalary,
          yearsOfService: inputData.yearsOfService,
          age: inputData.age,
          retirementSystem: inputData.retirementSystem,
          monthlyPension: result.pension.monthly,
          netBuyout: result.buyout.net,
          breakEvenYears: result.comparison.breakEvenYears,
        },
      });
      return response.json();
    },
    onSuccess: () => {
      setSaved(true);
      setEmailDialogOpen(false);
      toast({
        title: "Results Saved!",
        description: "Your calculation has been saved. We'll be in touch soon!",
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to save results. Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleSaveResults = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email) return;
    saveResultsMutation.mutate({ name, email, phone });
  };

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      toast({ title: "Link copied!", description: "Share it with fellow feds." });
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast({ title: "Failed to copy", variant: "destructive" });
    }
  };

  const shareText = "Considering a federal buyout? Use this calculator to compare your options:";
  const shareUrl = typeof window !== "undefined" ? window.location.href : "";

  const handleShare = (platform: string) => {
    const urls: Record<string, string> = {
      twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`,
    };
    window.open(urls[platform], "_blank", "width=600,height=400");
  };

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
        <h3 className="text-xl font-bold text-slate-700" data-testid="text-ready">Ready to Estimate</h3>
        <p className="text-slate-500 mt-2 max-w-xs">
          Enter your service details on the left to see your potential buyout vs. pension comparison.
        </p>
      </div>
    );
  }

  // Color code break-even
  const breakEvenColor = result.comparison.breakEvenYears > 5 
    ? "text-emerald-600 bg-emerald-50 border-emerald-200" 
    : result.comparison.breakEvenYears > 3 
    ? "text-amber-600 bg-amber-50 border-amber-200" 
    : "text-red-600 bg-red-50 border-red-200";

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
            <TrendingUp className="w-3 h-3" /> {result.pension.retirementSystem} Estimate
          </span>
          
          <div className="space-y-1">
            <p className="text-slate-400 text-sm font-medium uppercase tracking-wider">Estimated Net Buyout</p>
            <h2 className="text-5xl font-bold tracking-tight text-white" data-testid="text-net-buyout">
              {formatCurrency(result.buyout.net)}
            </h2>
            <p className="text-slate-400 text-sm mt-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              After est. taxes of {formatCurrency(result.buyout.taxes.totalTax)}
            </p>
          </div>
        </div>
      </div>

      <div className="p-8 space-y-6">
        {/* Pension Comparison */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <PiggyBank className="w-5 h-5 text-primary" />
              Vs. Pension Income
            </h3>
            <span className="text-sm text-muted-foreground">{result.pension.retirementSystem} Annuity</span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
              <p className="text-xs font-medium text-muted-foreground uppercase mb-1">Monthly</p>
              <p className="text-2xl font-bold text-slate-900" data-testid="text-monthly-pension">{formatCurrency(result.pension.monthly)}</p>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100">
              <p className="text-xs font-medium text-muted-foreground uppercase mb-1">Annual (Net)</p>
              <p className="text-2xl font-bold text-slate-900" data-testid="text-annual-pension">{formatCurrency(result.pension.annualNet)}</p>
            </div>
          </div>

          {/* Pension Adjustments */}
          {(result.pension.militaryYearsAdded > 0 || result.pension.isSpecialProvisions || result.pension.earlyRetirementPenalty > 0 || result.pension.survivorBenefitReduction > 0 || result.pension.deferredPensionAt62) && (
            <div className="space-y-2">
              {result.pension.isSpecialProvisions && (
                <div className="flex justify-between text-sm p-2 bg-blue-50 rounded-lg border border-blue-100">
                  <span className="text-blue-700">Special Provisions (LEO/FF/ATC)</span>
                  <span className="font-mono text-blue-600">1.7% multiplier</span>
                </div>
              )}
              {result.pension.militaryYearsAdded > 0 && (
                <div className="flex justify-between text-sm p-2 bg-green-50 rounded-lg border border-green-100">
                  <span className="text-green-700">Military Buyback Years Added</span>
                  <span className="font-mono text-green-600">+{result.pension.militaryYearsAdded} years</span>
                </div>
              )}
              {result.pension.deferredPensionAt62 && (
                <div className="flex justify-between text-sm p-2 bg-indigo-50 rounded-lg border border-indigo-100">
                  <span className="text-indigo-700">Deferred Pension (at age 62)</span>
                  <span className="font-mono text-indigo-600">{formatCurrency(result.pension.deferredPensionAt62)}/yr</span>
                </div>
              )}
              {result.pension.earlyRetirementPenalty > 0 && (
                <div className="flex justify-between text-sm p-2 bg-red-50 rounded-lg border border-red-100">
                  <span className="text-red-700">Early Retirement Penalty ({result.pension.earlyRetirementPenalty}%)</span>
                  <span className="font-mono text-red-600">-{formatCurrency(result.pension.earlyRetirementReduction)}/yr</span>
                </div>
              )}
              {result.pension.survivorBenefitReduction > 0 && (
                <div className="flex justify-between text-sm p-2 bg-amber-50 rounded-lg border border-amber-100">
                  <span className="text-amber-700">Survivor Benefit ({result.pension.survivorBenefitReduction}%)</span>
                  <span className="font-mono text-amber-600">-{formatCurrency(result.pension.survivorBenefitAmount)}/yr</span>
                </div>
              )}
            </div>
          )}

          {/* Break Even */}
          <div className={cn("p-4 rounded-xl border text-sm flex items-start gap-3", breakEvenColor)}>
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <p>
              <span className="font-bold block mb-1">Break-Even Analysis</span>
              It would take about <strong>{result.comparison.breakEvenYears.toFixed(1)} years</strong> of pension payments to equal this net buyout amount.
            </p>
          </div>

          {/* Recommendation */}
          <div className="p-4 rounded-xl bg-blue-50 border border-blue-100 text-blue-900 text-sm flex items-start gap-3">
            <Lightbulb className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
            <p>{result.comparison.recommendation}</p>
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

          <AccordionItem value="pension" className="border-b-0 mb-2">
            <AccordionTrigger className="hover:no-underline py-3 px-4 bg-slate-50 rounded-xl data-[state=open]:rounded-b-none data-[state=open]:bg-slate-100 transition-colors">
              <span className="font-semibold text-slate-700">Pension Calculation</span>
            </AccordionTrigger>
            <AccordionContent className="px-4 py-4 bg-slate-50 rounded-b-xl border-t border-slate-200/50">
              <div className="space-y-3 text-sm text-slate-600">
                <div className="flex justify-between">
                  <span>High-3 Salary</span>
                  <span className="font-mono">{formatCurrency(result.pension.high3)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Multiplier ({result.pension.retirementSystem})</span>
                  <span className="font-mono">{(result.pension.multiplier * 100).toFixed(2)}%</span>
                </div>
                <div className="flex justify-between font-medium">
                  <span>Gross Annual</span>
                  <span className="font-mono">{formatCurrency(result.pension.annualGross)}</span>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="formula" className="border-b-0">
            <AccordionTrigger className="hover:no-underline py-3 px-4 bg-slate-50 rounded-xl data-[state=open]:rounded-b-none data-[state=open]:bg-slate-100 transition-colors">
              <span className="font-semibold text-slate-700">Severance Formula</span>
            </AccordionTrigger>
            <AccordionContent className="px-4 py-4 bg-slate-50 rounded-b-xl border-t border-slate-200/50">
              <div className="space-y-3 text-sm text-slate-600">
                <div className="flex justify-between">
                  <span>Weekly Base Rate</span>
                  <span className="font-mono">{formatCurrency(result.severance.weeklyRate)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Credited Weeks</span>
                  <span className="font-mono">{result.severance.basicWeeks.toFixed(0)} weeks</span>
                </div>
                <div className="flex justify-between">
                  <span>Basic Severance</span>
                  <span className="font-mono">{formatCurrency(result.severance.basicAmount)}</span>
                </div>
                {result.severance.ageAdjustmentFactor > 1 && (
                  <div className="p-2 bg-blue-50 text-blue-800 rounded text-xs mt-2">
                    <strong>Age Bonus Active:</strong> Your severance was multiplied by {result.severance.ageAdjustmentFactor.toFixed(2)}x (+{formatCurrency(result.severance.ageAdjustmentAmount)}) because you are over 40.
                  </div>
                )}
                <div className="flex justify-between font-medium pt-2 border-t border-slate-200">
                  <span>Total Severance (if applicable)</span>
                  <span className="font-mono">{formatCurrency(result.severance.totalGross)}</span>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>

        {/* Email My Results Section */}
        <div className="pt-4 border-t border-slate-100">
          <Dialog open={emailDialogOpen} onOpenChange={setEmailDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                className="w-full gap-2" 
                size="lg"
                disabled={saved}
                data-testid="button-email-results"
              >
                {saved ? (
                  <>
                    <Check className="w-5 h-5" />
                    Results Saved!
                  </>
                ) : (
                  <>
                    <Mail className="w-5 h-5" />
                    Email My Results
                  </>
                )}
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <Mail className="w-5 h-5 text-primary" />
                  Save Your Results
                </DialogTitle>
                <DialogDescription>
                  Save your calculation so you can review it later with your family or financial advisor.
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSaveResults} className="space-y-4 mt-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center gap-2">
                    <User className="w-4 h-4 text-slate-400" />
                    Your Name
                  </label>
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="John Smith"
                    required
                    data-testid="input-save-name"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center gap-2">
                    <Mail className="w-4 h-4 text-slate-400" />
                    Email Address
                  </label>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="john@example.com"
                    required
                    data-testid="input-save-email"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium flex items-center gap-2">
                    <Phone className="w-4 h-4 text-slate-400" />
                    Phone (optional)
                  </label>
                  <Input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="(555) 123-4567"
                    data-testid="input-save-phone"
                  />
                </div>
                <Button 
                  type="submit" 
                  className="w-full gap-2"
                  disabled={saveResultsMutation.isPending || !name || !email}
                  data-testid="button-save-submit"
                >
                  {saveResultsMutation.isPending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Send My Results
                    </>
                  )}
                </Button>
                <p className="text-xs text-slate-500 text-center">
                  We respect your privacy and won't spam you.
                </p>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Share Section */}
        <div className="pt-4 border-t border-slate-100">
          <p className="text-sm font-medium text-slate-700 mb-3 flex items-center gap-2">
            <Share2 className="w-4 h-4" /> Share with fellow feds
          </p>
          <div className="flex gap-2 flex-wrap">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => handleShare("twitter")}
              data-testid="button-share-twitter"
              className="gap-2"
            >
              <SiX className="w-4 h-4" /> X
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => handleShare("facebook")}
              data-testid="button-share-facebook"
              className="gap-2"
            >
              <SiFacebook className="w-4 h-4" /> Facebook
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => handleShare("linkedin")}
              data-testid="button-share-linkedin"
              className="gap-2"
            >
              <SiLinkedin className="w-4 h-4" /> LinkedIn
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleCopyLink}
              data-testid="button-copy-link"
              className="gap-2"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              {copied ? "Copied!" : "Copy Link"}
            </Button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
