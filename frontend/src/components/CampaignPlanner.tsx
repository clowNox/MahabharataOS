"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Calendar, Sparkles, Send, Loader2, ChevronRight, LayoutGrid, Clock, CheckCircle2 } from "lucide-react";
import { fetchWithTimeout } from "@/lib/fetchWithTimeout";

interface CampaignDay {
  day: number;
  title: string;
  prompt: string;
  status?: "pending" | "generating" | "completed";
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function CampaignPlanner({ onExecuteDay }: { onExecuteDay: (prompt: string) => void }) {
  const [theme, setTheme] = useState("");
  const [days, setDays] = useState(7);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isScheduling, setIsScheduling] = useState(false);
  const [scheduledId, setScheduledId] = useState<string | null>(null);
  const [plan, setPlan] = useState<CampaignDay[]>([]);

  const handleScheduleCampaign = async (campaignId: string) => {
    setIsScheduling(true);
    try {
      const res = await fetch(`${API_BASE}/campaigns/${campaignId}/schedule`, {
        method: "POST"
      });
      if (res.ok) {
        setScheduledId(campaignId);
        setTimeout(() => setScheduledId(null), 5000);
      }
    } catch (e) {
      console.error("Scheduling failed", e);
    } finally {
      setIsScheduling(false);
    }
  };

  const handleGeneratePlan = async () => {
    if (!theme) return;
    setIsGenerating(true);
    setPlan([]);
    
    try {
      const response = await fetchWithTimeout(`${API_BASE}/campaigns/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-openai-key": localStorage.getItem("OPENAI_API_KEY") || "",
        },
        body: JSON.stringify({ theme, duration_days: days }),
      });
      
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const data = await response.json();
      if (data.status === "success") {
        setPlan(data.plan);
        // We need the campaign_id to schedule it
        localStorage.setItem("LAST_CAMPAIGN_ID", data.campaign_id);
      }
    } catch (error) {
      console.error("Failed to generate campaign:", error);
      alert("Failed to generate campaign: " + (error instanceof Error ? error.message : String(error)));
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Card className="border-primary/20 bg-card/40 backdrop-blur-xl shadow-2xl shadow-primary/5 overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary/10 via-primary to-primary/10" />
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Calendar className="h-6 w-6 text-primary" />
            </div>
            <div>
              <CardTitle className="text-2xl font-bold tracking-tight">Campaign Architect</CardTitle>
              <CardDescription>Design multi-day content strategies in seconds</CardDescription>
            </div>
          </div>
          {plan.length > 0 && (
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                disabled={isScheduling || scheduledId !== null}
                onClick={() => {
                  const campaignId = localStorage.getItem("LAST_CAMPAIGN_ID");
                  if (campaignId) handleScheduleCampaign(campaignId);
                }} 
                className={`transition-all ${scheduledId ? 'bg-green-500/10 text-green-500 border-green-500/20' : 'text-primary hover:bg-primary/20 border-primary/20'}`}
              >
                {isScheduling ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : scheduledId ? <CheckCircle2 className="h-4 w-4 mr-2" /> : <Clock className="h-4 w-4 mr-2" />}
                {scheduledId ? "Scheduled" : "Schedule Autonomous Campaign"}
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => {
                  const content = `# MahabharataOS Campaign Strategy\n\n**Theme:** ${theme}\n**Duration:** ${days} Days\n\n---\n\n` + 
                    plan.map(d => `## Day ${d.day}: ${d.title}\n\n**Prompt:**\n${d.prompt}\n\n---\n`).join("\n");
                  
                  const blob = new Blob([content], { type: "text/markdown" });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `campaign_strategy_${theme.toLowerCase().replace(/ /g, "_")}.md`;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  URL.revokeObjectURL(url);
                }} 
                className="text-primary hover:text-primary-foreground hover:bg-primary/20 border-primary/20"
              >
                Export Strategy (.md)
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setPlan([])} className="text-muted-foreground hover:text-foreground">
                Reset Plan
              </Button>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {plan.length === 0 ? (
          <div className="flex flex-col md:flex-row gap-4 animate-in fade-in slide-in-from-top-2">
            <div className="flex-1 space-y-2">
              <label className="text-xs font-bold uppercase tracking-tighter text-muted-foreground ml-1">Campaign Theme</label>
              <Input 
                placeholder="e.g. 10 Years of India's Energy Transformation" 
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
                className="bg-background/50 border-primary/20 focus:border-primary/50 transition-all h-12"
              />
            </div>
            <div className="w-full md:w-32 space-y-2">
              <label className="text-xs font-bold uppercase tracking-tighter text-muted-foreground ml-1">Duration (Days)</label>
              <Input 
                type="number" 
                min={1} 
                max={30} 
                value={days}
                onChange={(e) => setDays(Math.max(1, parseInt(e.target.value) || 1))}
                className="bg-background/50 border-primary/20 h-12"
              />
            </div>
            <Button 
              onClick={handleGeneratePlan} 
              disabled={isGenerating || !theme}
              className="md:mt-6 h-12 px-8 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/20"
            >
              {isGenerating ? <Loader2 className="h-5 w-5 animate-spin" /> : <Sparkles className="h-5 w-5 mr-2" />}
              Generate Strategy
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-in zoom-in-95 duration-500">
            {plan.map((item, index) => (
              <Card 
                key={`campaign-day-${item.day}-${index}`} 
                className="group border-border/40 bg-background/40 hover:border-primary/50 transition-all cursor-pointer relative overflow-hidden"
                onClick={() => onExecuteDay(item.prompt)}
              >
                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Send className="h-4 w-4 text-primary" />
                </div>
                <CardHeader className="p-4">
                  <Badge variant="outline" className="w-fit mb-2 border-primary/30 text-primary bg-primary/5">Day {item.day}</Badge>
                  <CardTitle className="text-sm font-bold line-clamp-1 group-hover:text-primary transition-colors">
                    {item.title}
                  </CardTitle>
                </CardHeader>
                <CardContent className="px-4 pb-4 pt-0">
                  <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">
                    {item.prompt}
                  </p>
                </CardContent>
                <div className="absolute bottom-0 left-0 w-full h-0.5 bg-primary transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left" />
              </Card>
            ))}
            
            <Card className="border-dashed border-primary/20 bg-transparent flex items-center justify-center p-6 group hover:border-primary/40 transition-colors">
              <Button variant="ghost" className="text-muted-foreground group-hover:text-primary transition-colors flex flex-col gap-2">
                <LayoutGrid className="h-6 w-6" />
                <span className="text-xs font-medium">Add Day</span>
              </Button>
            </Card>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
