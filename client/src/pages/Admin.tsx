import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Users, Mail, TrendingUp, Lock, LogOut, Calendar, Send } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Link } from "wouter";

interface AdminStats {
  totalSubscribers: number;
  subscribersToday: number;
  totalLeads: number;
  leadsToday: number;
}

interface Subscriber {
  id: number;
  email: string;
  source: string;
  createdAt: string;
}

interface Lead {
  id: number;
  name: string;
  email: string;
  phone: string | null;
  salary: number | null;
  yearsOfService: number | null;
  age: number | null;
  retirementSystem: string | null;
  monthlyPension: number | null;
  netBuyout: number | null;
  breakEvenYears: string | null;
  createdAt: string;
}

function LoginForm({ onLogin }: { onLogin: (token: string) => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();
      if (data.success) {
        localStorage.setItem("adminToken", data.token);
        onLogin(data.token);
      } else {
        setError("Invalid credentials");
      }
    } catch {
      setError("Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
            <Lock className="w-6 h-6 text-primary" />
          </div>
          <CardTitle>Admin Dashboard</CardTitle>
          <p className="text-muted-foreground text-sm">Enter your credentials to continue</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                data-testid="input-admin-username"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                data-testid="input-admin-password"
              />
            </div>
            {error && (
              <p className="text-sm text-destructive" data-testid="text-login-error">{error}</p>
            )}
            <Button 
              type="submit" 
              className="w-full" 
              disabled={loading}
              data-testid="button-admin-login"
            >
              {loading ? "Logging in..." : "Login"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

function Dashboard({ token, onLogout }: { token: string; onLogout: () => void }) {
  const { toast } = useToast();
  const [sendingAnalytics, setSendingAnalytics] = useState(false);
  
  const authHeaders = {
    Authorization: `Bearer ${token}`,
  };

  const handleSendAnalytics = async () => {
    setSendingAnalytics(true);
    try {
      const res = await fetch("/api/admin/send-analytics", {
        method: "POST",
        headers: authHeaders,
      });
      const data = await res.json();
      if (res.ok) {
        toast({ title: "Analytics email sent!", description: "Check your inbox." });
      } else {
        toast({ title: "Failed to send", description: data.message, variant: "destructive" });
      }
    } catch {
      toast({ title: "Error", description: "Failed to send analytics email", variant: "destructive" });
    } finally {
      setSendingAnalytics(false);
    }
  };

  const { data: stats, isLoading: statsLoading } = useQuery<AdminStats>({
    queryKey: ["/api/admin/stats"],
    queryFn: async () => {
      const res = await fetch("/api/admin/stats", { headers: authHeaders });
      if (!res.ok) throw new Error("Failed to fetch stats");
      return res.json();
    },
  });

  const { data: subscribers, isLoading: subscribersLoading } = useQuery<Subscriber[]>({
    queryKey: ["/api/admin/subscribers"],
    queryFn: async () => {
      const res = await fetch("/api/admin/subscribers", { headers: authHeaders });
      if (!res.ok) throw new Error("Failed to fetch subscribers");
      return res.json();
    },
  });

  const { data: leads, isLoading: leadsLoading } = useQuery<Lead[]>({
    queryKey: ["/api/admin/leads"],
    queryFn: async () => {
      const res = await fetch("/api/admin/leads", { headers: authHeaders });
      if (!res.ok) throw new Error("Failed to fetch leads");
      return res.json();
    },
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatCurrency = (amount: number | null) => {
    if (amount === null) return "—";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <span className="text-xl font-bold text-primary cursor-pointer" data-testid="link-home">
                FedBuyout
              </span>
            </Link>
            <span className="text-slate-400">/</span>
            <span className="font-semibold text-slate-700">Admin Dashboard</span>
          </div>
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              onClick={handleSendAnalytics} 
              disabled={sendingAnalytics}
              data-testid="button-send-analytics"
            >
              <Send className="w-4 h-4 mr-2" />
              {sendingAnalytics ? "Sending..." : "Send Analytics"}
            </Button>
            <Button variant="outline" onClick={onLogout} data-testid="button-logout">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Subscribers</p>
                  <p className="text-3xl font-bold" data-testid="text-total-subscribers">
                    {statsLoading ? "—" : stats?.totalSubscribers || 0}
                  </p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <Mail className="w-6 h-6 text-blue-600" />
                </div>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                <span className="text-green-600 font-medium">+{stats?.subscribersToday || 0}</span> today
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Leads</p>
                  <p className="text-3xl font-bold" data-testid="text-total-leads">
                    {statsLoading ? "—" : stats?.totalLeads || 0}
                  </p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <Users className="w-6 h-6 text-green-600" />
                </div>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                <span className="text-green-600 font-medium">+{stats?.leadsToday || 0}</span> today
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Subscribers Today</p>
                  <p className="text-3xl font-bold" data-testid="text-subscribers-today">
                    {statsLoading ? "—" : stats?.subscribersToday || 0}
                  </p>
                </div>
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                  <Calendar className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Leads Today</p>
                  <p className="text-3xl font-bold" data-testid="text-leads-today">
                    {statsLoading ? "—" : stats?.leadsToday || 0}
                  </p>
                </div>
                <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="subscribers" className="space-y-4">
          <TabsList>
            <TabsTrigger value="subscribers" data-testid="tab-subscribers">
              Subscribers ({subscribers?.length || 0})
            </TabsTrigger>
            <TabsTrigger value="leads" data-testid="tab-leads">
              Leads ({leads?.length || 0})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="subscribers">
            <Card>
              <CardHeader>
                <CardTitle>Newsletter Subscribers</CardTitle>
              </CardHeader>
              <CardContent>
                {subscribersLoading ? (
                  <p className="text-muted-foreground">Loading...</p>
                ) : subscribers && subscribers.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Email</TableHead>
                        <TableHead>Source</TableHead>
                        <TableHead>Signed Up</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {subscribers.map((sub) => (
                        <TableRow key={sub.id} data-testid={`row-subscriber-${sub.id}`}>
                          <TableCell className="font-medium">{sub.email}</TableCell>
                          <TableCell>
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              sub.source === "calculator" 
                                ? "bg-blue-100 text-blue-700" 
                                : "bg-green-100 text-green-700"
                            }`}>
                              {sub.source}
                            </span>
                          </TableCell>
                          <TableCell className="text-muted-foreground">
                            {formatDate(sub.createdAt)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <p className="text-muted-foreground text-center py-8">No subscribers yet</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="leads">
            <Card>
              <CardHeader>
                <CardTitle>Captured Leads</CardTitle>
              </CardHeader>
              <CardContent>
                {leadsLoading ? (
                  <p className="text-muted-foreground">Loading...</p>
                ) : leads && leads.length > 0 ? (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Name</TableHead>
                          <TableHead>Email</TableHead>
                          <TableHead>Phone</TableHead>
                          <TableHead>System</TableHead>
                          <TableHead>Salary</TableHead>
                          <TableHead>Monthly Pension</TableHead>
                          <TableHead>Net Buyout</TableHead>
                          <TableHead>Break-even</TableHead>
                          <TableHead>Date</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {leads.map((lead) => (
                          <TableRow key={lead.id} data-testid={`row-lead-${lead.id}`}>
                            <TableCell className="font-medium">{lead.name}</TableCell>
                            <TableCell>{lead.email}</TableCell>
                            <TableCell>{lead.phone || "—"}</TableCell>
                            <TableCell>
                              <span className="px-2 py-1 rounded-full text-xs bg-slate-100 text-slate-700">
                                {lead.retirementSystem?.toUpperCase() || "—"}
                              </span>
                            </TableCell>
                            <TableCell>{formatCurrency(lead.salary)}</TableCell>
                            <TableCell>{formatCurrency(lead.monthlyPension)}</TableCell>
                            <TableCell>{formatCurrency(lead.netBuyout)}</TableCell>
                            <TableCell>{lead.breakEvenYears ? `${lead.breakEvenYears} yrs` : "—"}</TableCell>
                            <TableCell className="text-muted-foreground">
                              {formatDate(lead.createdAt)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <p className="text-muted-foreground text-center py-8">No leads captured yet</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

export default function Admin() {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const savedToken = localStorage.getItem("adminToken");
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  const handleLogin = (newToken: string) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem("adminToken");
    setToken(null);
  };

  if (!token) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return <Dashboard token={token} onLogout={handleLogout} />;
}
