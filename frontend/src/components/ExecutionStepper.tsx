"use client";

import { AlertCircle, CheckCircle2, Circle, Loader2, Play, RotateCcw, Quote } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useEffect, useRef, useState } from "react";
import { fetchWithTimeout } from "@/lib/fetchWithTimeout";
import { getCharacterByDept } from "@/lib/characters";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface DelegationNodeData {
  id: string;
  task_id?: string;
  department?: string;
  receiver?: string;
  message?: string;
  objective?: string;
  reason?: string;
  model_choice?: string;
  estimated_time_minutes?: number;
  dependency_ids?: string[];
}

interface LatestRun {
  id: string;
  task_id: string;
  next_action?: string;
  delegation_chain?: DelegationNodeData[];
  outputs?: Record<string, unknown>;
  created_at?: string;
}

export default function ExecutionStepper({ dataNodes }: { dataNodes: DelegationNodeData[] }) {
  const [visibleCount, setVisibleCount] = useState(0);
  const [latestRun, setLatestRun] = useState<LatestRun | null>(null);
  const [latestRunLoading, setLatestRunLoading] = useState(false);
  const [latestRunError, setLatestRunError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const taskId = dataNodes.find((node) => node.task_id)?.task_id;

  useEffect(() => {
    if (!dataNodes || dataNodes.length === 0) {
      const resetTimer = setTimeout(() => {
        setVisibleCount(0);
        setLatestRun(null);
        setLatestRunError(null);
      }, 0);

      return () => clearTimeout(resetTimer);
    }

    const resetTimer = setTimeout(() => {
      setVisibleCount(0);
      setLatestRun(null);
      setLatestRunError(null);
    }, 0);

    const intervalTimer = setTimeout(() => {
      // Fast stagger effect since the backend already finished
      intervalRef.current = setInterval(() => {
        setVisibleCount(prev => {
          const next = prev + 1;
          if (next >= dataNodes.length && intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
          return next;
        });
      }, 250);
    }, 0);

    return () => {
      clearTimeout(resetTimer);
      clearTimeout(intervalTimer);
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [dataNodes]);

  useEffect(() => {
    if (!taskId || dataNodes.length === 0 || visibleCount < dataNodes.length) return;

    (async () => {
      try {
        setLatestRunLoading(true);
        setLatestRunError(null);
        const response = await fetchWithTimeout(`${API_BASE}/tasks/${taskId}/latest_run`, {}, 10000);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const run: LatestRun = await response.json();
        setLatestRun(run);
      } catch (e: unknown) {
        setLatestRun(null);
        setLatestRunError(e instanceof Error ? e.message : "Unknown error");
      } finally {
        setLatestRunLoading(false);
      }
    })();
  }, [taskId, dataNodes.length, visibleCount]);

  if (!dataNodes || dataNodes.length === 0) return null;

  return (
    <div className="w-full max-w-4xl mx-auto my-12 animate-in fade-in zoom-in-95 duration-700">
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-xl font-semibold text-foreground flex items-center gap-3">
          <div className="p-2 rounded-full bg-primary/10 border border-primary/20">
            <Play className="h-5 w-5 text-primary" />
          </div>
          Execution Pipeline
        </h3>
        <Badge variant="outline" className="font-mono text-[10px] border-white/5 bg-slate-900/50">
          Vyūha Formation active
        </Badge>
      </div>

      {taskId && visibleCount >= dataNodes.length && (
        <div className="mb-10 rounded-2xl border border-white/5 bg-slate-900/30 backdrop-blur-xl p-6 shadow-2xl transition-all hover:bg-slate-900/40">
          <div className="flex items-center justify-between gap-3 mb-4">
            <div className="flex items-center gap-2 font-medium text-foreground">
              <RotateCcw className="h-4 w-4 text-primary" />
              Intelligence Recall
            </div>
            {latestRun?.created_at && (
              <span className="text-[10px] font-mono text-muted-foreground bg-slate-950 px-2 py-1 rounded border border-white/5">
                {new Date(latestRun.created_at).toLocaleString()}
              </span>
            )}
          </div>

          {latestRunLoading && (
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
              Sifting through the cosmic records...
            </div>
          )}

          {latestRunError && (
            <div className="flex items-center gap-3 text-sm text-red-400">
              <AlertCircle className="h-4 w-4" />
              Recall failed: {latestRunError}
            </div>
          )}

          {latestRun && !latestRunLoading && (
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-xl border border-white/5 bg-slate-950/40 p-4">
                <div className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground mb-1">Session</div>
                <div className="truncate font-mono text-xs text-foreground/80">{latestRun.id}</div>
              </div>
              <div className="rounded-xl border border-white/5 bg-slate-950/40 p-4">
                <div className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground mb-1">Next Action</div>
                <div className="truncate text-xs text-primary font-bold">{latestRun.next_action || "Complete"}</div>
              </div>
              <div className="rounded-xl border border-white/5 bg-slate-950/40 p-4">
                <div className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground mb-1">Artifacts</div>
                <div className="text-xs text-foreground/80 font-medium">
                  {Object.keys(latestRun.outputs || {}).length} generated
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      
      <div className="space-y-0 relative">
        {/* Continuous Vertical line */}
        <div className="absolute left-[23px] top-6 bottom-6 w-[1px] bg-gradient-to-b from-primary/50 via-primary/20 to-transparent z-0" />
        
        {dataNodes.slice(0, visibleCount).map((node, index) => {
          const dept = node.receiver || node.department || "CEO Office";
          const char = getCharacterByDept(dept);
          const isCompleted = true; 
          
          return (
            <div key={`pipeline-step-${node.id || index}`} className="relative z-10 flex gap-8 items-start pb-10 animate-in slide-in-from-top-4 fade-in duration-500">
              {/* Step Marker */}
              <div className="mt-1 flex-shrink-0 relative">
                <div className={`h-12 w-12 rounded-2xl flex items-center justify-center border-2 transition-all duration-500 ${char ? char.color : 'border-border bg-card'}`}>
                  {char ? char.icon : <Circle className="h-6 w-6 text-muted-foreground" />}
                </div>
                {isCompleted && (
                  <div className="absolute -right-1 -bottom-1 bg-primary rounded-full p-1 border-2 border-slate-950">
                    <CheckCircle2 className="h-3 w-3 text-white" />
                  </div>
                )}
              </div>
              
              <div className="flex-1 bg-slate-900/40 backdrop-blur-md border border-white/5 hover:bg-slate-900/60 transition-all duration-300 rounded-2xl p-6 shadow-xl group">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="font-bold text-lg text-foreground tracking-tight group-hover:text-primary transition-colors">
                      {dept}
                    </h4>
                    {char && (
                      <p className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground mt-1 font-semibold">
                        Lead Sage: <span className="text-primary/70">{char.name}</span>
                      </p>
                    )}
                  </div>
                  <Badge variant="outline" className="font-mono text-[10px] border-white/10 bg-slate-950 text-muted-foreground">
                    {node.model_choice || "system"}
                  </Badge>
                </div>
                
                <div className="relative">
                  <Quote className="absolute -left-2 -top-2 h-8 w-8 text-white/5 z-0" />
                  <p className="text-sm text-foreground/80 leading-relaxed relative z-10 pl-2">
                    {node.message || node.objective}
                  </p>
                </div>
                
                {node.reason && (
                  <div className="mt-4 flex items-start gap-2 text-xs font-mono text-muted-foreground/50 border-t border-white/5 pt-4 italic">
                    <span className="text-primary/40">Rationale:</span>
                    <span>{node.reason}</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
