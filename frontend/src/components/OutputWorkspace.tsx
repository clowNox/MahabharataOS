import { useState, useRef } from "react";
import { CheckCircle2, Sparkles, AlertCircle, Loader2, Shield, Pencil, X, Quote } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CHARACTER_DATA, getCharacterByDept } from "@/lib/characters";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface MediaOutput {
  needs_human_approval: boolean;
  recommendation?: {
    reason?: string;
    recommended_post?: string;
    recommended_index?: number;
  };
  draft_options?: Array<{
    hook?: string;
    combined_post?: string;
    [key: string]: unknown;
  }>;
  visual_asset?: {
    type: string;
    prompt: string;
  };
  reasoning?: string;
}

export interface AuditResult {
  integrity_score: number;
  assessment: string;
  warnings: string[];
  is_safe_to_deploy: boolean;
}

export interface OutputsData {
  media?: MediaOutput;
  research?: { 
    findings: string; 
    needs_human_approval: boolean; 
    raw_model_used: string;
    search_query?: string;
    results_count?: number;
  };
  finance?: { 
    financial_breakdown: string; 
    needs_human_approval: boolean; 
    raw_model_used: string;
    structured_data?: {
      line_items: Array<{ item: string; amount: number; category: string }>;
      totals: { total_cost: number; projected_revenue: number };
      risk_factors: string[];
    };
  };
  general?: { message: string; status: string; needs_human_approval: boolean };
  vidura_audit?: Record<string, AuditResult> | AuditResult;
  [key: string]: unknown;
}

export default function OutputWorkspace({ outputs, taskId, onComplete }: { outputs: OutputsData, taskId?: string, onComplete?: () => void }) {
  const [isApproving, setIsApproving] = useState(false);
  const [isApproved, setIsApproved] = useState(false);
  const [approveError, setApproveError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedPost, setEditedPost] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleApprove = async () => {
    setIsApproving(true);
    setApproveError(null);
    try {
      if (taskId) {
        const res = await fetch(`${API_BASE}/tasks/${taskId}/status`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: "approved" }),
        });
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
      }
      setIsApproved(true);
      if (onComplete) {
        setTimeout(() => {
          setIsApproved(false);
          onComplete();
        }, 2500);
      }
    } catch (e: unknown) {
      setApproveError(e instanceof Error ? e.message : "Approval failed");
    } finally {
      setIsApproving(false);
    }
  };

  if (!outputs || Object.keys(outputs).length === 0) return null;

  const { media, research, finance, general } = outputs;
  
  // Find if any output requires approval
  const needsApproval = 
    (media?.needs_human_approval) || 
    (research?.needs_human_approval) || 
    (finance?.needs_human_approval) || 
    (general?.needs_human_approval) || false;
  const recommended = media?.recommendation;
  const drafts = media?.draft_options || [];

  const renderAudits = () => {
    if (!outputs.vidura_audit) return null;
    
    // Handle both old single-audit format and new multi-audit dictionary
    const audits = ("integrity_score" in outputs.vidura_audit) 
      ? { "General": outputs.vidura_audit as AuditResult }
      : outputs.vidura_audit as Record<string, AuditResult>;

    return (
      <div className="lg:col-span-3 space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <Shield className="h-5 w-5 text-amber-500" />
          <h3 className="text-sm font-bold uppercase tracking-[0.2em] text-amber-500/80">Vidura Integrity Reviews</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(audits).map(([dept, audit]) => {
            const char = getCharacterByDept(dept);
            return (
              <Card key={dept} className="border-amber-500/30 bg-amber-500/5 backdrop-blur-xl relative overflow-hidden transition-all hover:bg-amber-500/10 group">
                <div className="absolute top-0 left-0 w-1 h-full bg-amber-500/50 group-hover:bg-amber-500" />
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`p-1.5 rounded-lg bg-slate-950/50 border border-white/5`}>
                        {char?.icon || <Shield className="h-4 w-4 text-amber-500" />}
                      </div>
                      <div>
                        <CardTitle className="text-sm font-bold">{dept} Audit</CardTitle>
                        <CardDescription className="text-[10px] uppercase tracking-wider font-mono">Verified by Vidura</CardDescription>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-xl font-black ${(audit.integrity_score ?? 0) > 80 ? "text-green-500" : (audit.integrity_score ?? 0) > 50 ? "text-amber-500" : "text-red-500"}`}>
                        {audit.integrity_score}%
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="relative">
                    <Quote className="absolute -left-2 -top-2 h-6 w-6 text-white/5" />
                    <p className="text-xs text-foreground/80 italic pl-2 leading-relaxed">
                      "{audit.assessment}"
                    </p>
                  </div>
                  
                  {audit.warnings && audit.warnings.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-2">
                      {audit.warnings.map((warning, i) => (
                        <Badge key={`${dept}-warning-${i}`} variant="outline" className="text-[9px] bg-red-500/5 border-red-500/20 text-red-300 font-mono">
                          {warning}
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="w-full space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {approveError && (
        <div className="flex items-center gap-3 p-3 rounded-lg border border-red-500/30 bg-red-500/10 text-red-300 text-sm">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          Approval failed: {approveError}
        </div>
      )}
      
      <div className="flex items-center justify-between border-b border-white/5 pb-6">
        <div className="space-y-1">
          <h2 className="text-3xl font-bold text-foreground flex items-center gap-3">
            <Sparkles className="h-6 w-6 text-primary animate-pulse" />
            Strategic Artifacts
          </h2>
          <p className="text-sm text-muted-foreground">Synthesized wisdom ready for deployment.</p>
        </div>
        <div className="flex items-center gap-4">
          {needsApproval && !isApproved && (
            <Badge variant="destructive" className="animate-pulse flex items-center gap-2 px-3 py-1 shadow-lg shadow-destructive/20 border-destructive/50">
              <AlertCircle className="h-3 w-3" />
              Awaiting Human Approval
            </Badge>
          )}
          {isApproved && (
            <Badge variant="default" className="bg-green-500/10 text-green-500 flex items-center gap-2 px-3 py-1 border-green-500/20">
              <CheckCircle2 className="h-3 w-3" />
              Vyuha Stabilized
            </Badge>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Media Output rendering */}
        {media && (
          <>
            <Card className="lg:col-span-2 border-primary/40 shadow-2xl shadow-primary/5 relative overflow-hidden bg-slate-900/40 backdrop-blur-2xl group">
          <div className="absolute top-0 left-0 w-1.5 h-full bg-primary/40 group-hover:bg-primary transition-colors" />
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl font-bold tracking-tight">Lead Post Option</CardTitle>
                <CardDescription className="mt-2 text-primary/80 font-medium italic">&quot;{recommended?.reason || "Best overall fit for target audience."}&quot;</CardDescription>
              </div>
              <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
                <Sparkles className="h-5 w-5 text-primary" />
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {isEditing ? (
              <textarea
                ref={textareaRef}
                className="w-full min-h-[250px] p-6 bg-slate-950/80 rounded-xl border border-primary/30 font-medium text-foreground/90 resize-y focus:outline-none focus:ring-2 focus:ring-primary/20 text-sm leading-relaxed shadow-inner"
                value={editedPost ?? recommended?.recommended_post ?? ""}
                onChange={(e) => setEditedPost(e.target.value)}
              />
            ) : (
              <div className="p-6 bg-slate-950/50 rounded-xl border border-white/5 whitespace-pre-wrap font-medium text-foreground/90 text-sm leading-relaxed shadow-inner relative">
                <Quote className="absolute right-4 top-4 h-12 w-12 text-white/5 pointer-events-none" />
                {editedPost ?? recommended?.recommended_post ?? "No recommendation provided."}
              </div>
            )}

            {media.visual_asset && (
              <div className="p-5 bg-gradient-to-br from-primary/10 to-transparent rounded-xl border border-primary/20 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-[10px] font-black uppercase tracking-widest text-primary/80">Directed Visual Prompt</h4>
                  <Badge variant="outline" className="text-[9px] bg-slate-950 border-white/10 uppercase">{media.visual_asset.type}</Badge>
                </div>
                <p className="text-sm text-foreground/70 italic leading-relaxed">
                  &quot;{media.visual_asset.prompt}&quot;
                </p>
              </div>
            )}
          </CardContent>
          <CardFooter className="flex justify-end gap-3 bg-slate-950/40 border-t border-white/5 p-4">
            {!isApproved && !isEditing && (
              <Button
                variant="outline"
                className="border-white/10 bg-slate-900 hover:bg-slate-800 gap-2 transition-all hover:scale-105"
                onClick={() => {
                  setEditedPost(editedPost ?? recommended?.recommended_post ?? "");
                  setIsEditing(true);
                  setTimeout(() => textareaRef.current?.focus(), 50);
                }}
              >
                <Pencil className="h-3.5 w-3.5" />
                Edit Guidance
              </Button>
            )}
            {isEditing && (
              <>
                <Button
                  variant="ghost"
                  className="gap-2 text-muted-foreground hover:text-foreground"
                  onClick={() => setIsEditing(false)}
                >
                  <X className="h-3.5 w-3.5" />
                  Cancel
                </Button>
                <Button
                  variant="outline"
                  className="gap-2 border-primary/30 text-primary hover:bg-primary/10"
                  onClick={() => setIsEditing(false)}
                >
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  Apply Edits
                </Button>
              </>
            )}
            {!isEditing && (
              <ApproveButton isApproving={isApproving} isApproved={isApproved} onClick={handleApprove} />
            )}
          </CardFooter>
        </Card>

        {/* Alternative Drafts */}
        <div className="space-y-4 lg:col-span-1">
          <h3 className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em] mb-4">Strategic Hooks</h3>
          {drafts.map((draft, index: number) => {
            if (index === recommended?.recommended_index) return null;
            return (
              <Card key={`draft-${index}`} className="border-white/5 bg-slate-900/40 hover:bg-slate-900/60 transition-all cursor-pointer group hover:border-primary/20">
                <CardHeader className="p-5">
                  <Badge variant="outline" className="w-fit mb-3 text-[9px] uppercase tracking-widest border-white/10 bg-slate-950">Option {index + 1}</Badge>
                  <CardDescription className="text-foreground/80 font-medium italic group-hover:text-primary/90 transition-colors">
                    "{draft.hook}"
                  </CardDescription>
                </CardHeader>
              </Card>
            );
          })}
        </div>
          </>
        )}

        {/* Research Output rendering */}
        {research && (
          <Card className="lg:col-span-3 border-blue-500/30 shadow-2xl shadow-blue-500/5 relative overflow-hidden bg-slate-900/40 backdrop-blur-2xl">
            <div className="absolute top-0 left-0 w-1.5 h-full bg-blue-500/50" />
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl font-bold tracking-tight">Intelligence Synthesis</CardTitle>
                  {research.search_query && (
                    <div className="mt-3 flex items-center gap-3">
                      <Badge variant="outline" className="text-[9px] uppercase font-black tracking-widest bg-blue-500/5 border-blue-500/20 text-blue-400 px-2 py-1">
                        Query: {research.search_query}
                      </Badge>
                      <span className="text-[10px] text-muted-foreground font-mono uppercase tracking-widest">{research.results_count || 0} Oracle Sources</span>
                    </div>
                  )}
                </div>
                <Badge variant="outline" className="bg-slate-950 border-white/10 text-blue-400/80 font-mono text-[10px]">{research.raw_model_used}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="p-6 bg-slate-950/50 rounded-xl border border-white/5 whitespace-pre-wrap font-medium text-foreground/90 text-sm leading-relaxed shadow-inner">
                {research.findings}
              </div>
            </CardContent>
            <CardFooter className="flex justify-end gap-3 bg-slate-950/40 border-t border-white/5 p-4">
              <ApproveButton isApproving={isApproving} isApproved={isApproved} onClick={handleApprove} />
            </CardFooter>
          </Card>
        )}

        {/* Finance Output rendering */}
        {finance && (
          <Card className="lg:col-span-3 border-emerald-500/30 shadow-2xl shadow-emerald-500/5 relative overflow-hidden bg-slate-900/40 backdrop-blur-2xl">
            <div className="absolute top-0 left-0 w-1.5 h-full bg-emerald-500/50" />
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl font-bold tracking-tight">Financial Projections</CardTitle>
                  <CardDescription className="mt-2 text-emerald-400/60 font-mono text-[10px] uppercase tracking-widest">Sahadeva's Strategic Ledger</CardDescription>
                </div>
                <Badge variant="outline" className="bg-slate-950 border-white/10 text-emerald-400/80 font-mono text-[10px]">{finance.raw_model_used}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-8">
              <div className="p-6 bg-slate-950/50 rounded-xl border border-white/5 whitespace-pre-wrap font-medium text-foreground/90 text-sm leading-relaxed shadow-inner">
                {finance.financial_breakdown}
              </div>

              {finance.structured_data && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-4">
                    <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-emerald-500/80 flex items-center gap-2">
                      <div className="h-1 w-1 rounded-full bg-emerald-500" />
                      Capital Allocation
                    </h4>
                    <div className="rounded-xl border border-white/5 bg-slate-950/50 overflow-hidden shadow-2xl">
                      <table className="w-full text-xs">
                        <thead className="bg-slate-900/80 border-b border-white/5">
                          <tr className="text-left">
                            <th className="p-3 font-bold uppercase tracking-widest text-[9px] text-muted-foreground">Line Item</th>
                            <th className="p-3 font-bold uppercase tracking-widest text-[9px] text-muted-foreground text-right">Magnitude</th>
                          </tr>
                        </thead>
                        <tbody>
                          {finance.structured_data.line_items.map((item, i) => (
                            <tr key={`line-item-${i}`} className="border-t border-white/5 hover:bg-white/[0.02] transition-colors">
                              <td className="p-3 text-foreground/80 font-medium">{item.item}</td>
                              <td className="p-3 text-right font-mono text-emerald-400 font-bold">${item.amount.toLocaleString()}</td>
                            </tr>
                          ))}
                          <tr className="border-t border-emerald-500/20 bg-emerald-500/5 font-black text-sm">
                            <td className="p-3 text-emerald-100">Projected Burn/Cost</td>
                            <td className="p-3 text-right text-emerald-400 font-mono">${finance.structured_data.totals.total_cost.toLocaleString()}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-red-400/80 flex items-center gap-2">
                      <AlertCircle className="h-4 w-4" />
                      Risk Scrutiny
                    </h4>
                    <div className="space-y-3">
                      {finance.structured_data.risk_factors.map((risk, i) => (
                        <div key={`risk-${i}`} className="p-4 bg-red-500/5 border border-red-500/20 rounded-xl text-xs text-foreground/80 flex items-start gap-3 shadow-inner">
                          <div className="h-1.5 w-1.5 rounded-full bg-red-500 mt-1 shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
                          <span className="leading-relaxed font-medium">{risk}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
            <CardFooter className="flex justify-end gap-3 bg-slate-950/40 border-t border-white/5 p-4">
              <ApproveButton isApproving={isApproving} isApproved={isApproved} onClick={handleApprove} />
            </CardFooter>
          </Card>
        )}

        {/* General Output rendering */}
        {general && !media && !research && !finance && (
          <Card className="lg:col-span-3 border-white/10 bg-slate-900/40 backdrop-blur-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1.5 h-full bg-slate-500/50" />
            <CardHeader>
              <CardTitle className="text-xl font-bold">Divine Resolution</CardTitle>
              <CardDescription className="text-[10px] uppercase tracking-widest">Orchestrated Fulfillment</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-6 bg-slate-950/50 rounded-xl border border-white/5 text-foreground/90 text-sm leading-relaxed shadow-inner">
                {general.message}
              </div>
            </CardContent>
            {general.needs_human_approval && (
              <CardFooter className="flex justify-end gap-3 bg-slate-950/40 border-t border-white/5 p-4">
                <ApproveButton isApproving={isApproving} isApproved={isApproved} onClick={handleApprove} />
              </CardFooter>
            )}
          </Card>
        )}

        {/* Vidura Integrity Audit rendering */}
        {renderAudits()}

      </div>
    </div>
  );
}

// Helper component for the Approval button
function ApproveButton({ isApproving, isApproved, onClick }: { isApproving: boolean, isApproved: boolean, onClick: () => void }) {
  return (
    <Button 
      size="lg"
      className={`gap-3 transition-all duration-500 px-8 py-6 rounded-xl font-bold tracking-tight shadow-xl ${
        isApproved 
          ? 'bg-green-600 hover:bg-green-700 text-white shadow-green-500/20' 
          : 'bg-primary hover:bg-primary/90 text-primary-foreground shadow-primary/20 hover:scale-105 active:scale-95'
      }`}
      disabled={isApproving || isApproved}
      onClick={onClick}
    >
      {isApproving ? (
        <>
          <Loader2 className="h-5 w-5 animate-spin" />
          Deploying Vyuha...
        </>
      ) : isApproved ? (
        <>
          <CheckCircle2 className="h-5 w-5" />
          Dharma Upheld
        </>
      ) : (
        <>
          <CheckCircle2 className="h-5 w-5" />
          Approve & Deploy
        </>
      )}
    </Button>
  );
}
