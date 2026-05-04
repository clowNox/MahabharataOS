"use client";

import { useState, forwardRef, useImperativeHandle, useEffect, useCallback } from "react";
import { Sparkles, Loader2, ListTodo, Clock, CheckCircle2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { fetchWithTimeout } from "@/lib/fetchWithTimeout";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface DelegationNode { id: string; task_id?: string; [key: string]: unknown; }
interface TaskOutputs { [key: string]: unknown; }

interface ActiveTask {
  id: string;
  title: string;
  original_prompt: string;
  status: "pending" | "pending_review" | "in_progress";
  created_at: string;
  last_run_at?: string;
}

type FilterType = "All" | "Pending Review" | "In Progress";

const STATUS_CONFIG: Record<ActiveTask["status"], { label: string; icon: React.ReactNode; badge: string }> = {
  pending: {
    label: "Pending",
    icon: <Clock className="h-3 w-3" />,
    badge: "bg-slate-500/20 text-slate-400 border-slate-500/30",
  },
  pending_review: {
    label: "Pending Review",
    icon: <AlertCircle className="h-3 w-3" />,
    badge: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  },
  in_progress: {
    label: "In Progress",
    icon: <CheckCircle2 className="h-3 w-3" />,
    badge: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  },
};

const CommandDesk = forwardRef(({ onTaskExecute }: { onTaskExecute?: (nodes: DelegationNode[], outputs?: TaskOutputs, taskId?: string, isFinal?: boolean) => void }, ref) => {
  const [prompt, setPrompt] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [tasks, setTasks] = useState<ActiveTask[]>([]);
  const [filter, setFilter] = useState<FilterType>("All");
  const [tasksLoading, setTasksLoading] = useState(false);

  const fetchTasks = useCallback(async () => {
    setTasksLoading(true);
    try {
      const res = await fetchWithTimeout(`${API_BASE}/tasks?limit=20`, {}, 8000);
      if (!res.ok) return;
      const data: ActiveTask[] = await res.json();
      setTasks(data);
    } catch {
      // silently fail — task list is non-critical
    } finally {
      setTasksLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  useImperativeHandle(ref, () => ({
    executePrompt: (overridePrompt: string) => {
      setPrompt(overridePrompt);
      handleSubmit(overridePrompt);
    }
  }));

  const handleSubmit = async (overridePrompt?: string) => {
    const finalPrompt = overridePrompt || prompt;
    if (!finalPrompt.trim()) return;
    setIsSubmitting(true);

    try {
      const openaiKey = localStorage.getItem("OPENAI_API_KEY") || "";
      const anthropicKey = localStorage.getItem("ANTHROPIC_API_KEY") || "";
      const tavilyKey = localStorage.getItem("TAVILY_API_KEY") || "";
      const geminiKey = localStorage.getItem("GEMINI_API_KEY") || "";

      const headers = {
        "Content-Type": "application/json",
        "x-openai-key": openaiKey,
        "x-anthropic-key": anthropicKey,
        "x-tavily-key": tavilyKey,
        "x-gemini-key": geminiKey
      };

      const riskParams = JSON.parse(localStorage.getItem("CHARACTER_RISK_PARAMS") || "{}");

      // 1. Create the task
      const createRes = await fetchWithTimeout(`${API_BASE}/tasks`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          project_id: "DC-P001",
          title: finalPrompt.length > 50 ? finalPrompt.substring(0, 50) + "..." : finalPrompt,
          original_prompt: finalPrompt,
          context: { character_risk_params: riskParams }
        })
      }, 60000);
      if (!createRes.ok) throw new Error(`Task creation failed: HTTP ${createRes.status}`);
      const task = await createRes.json();

      // 2. Execute the task
      const executeRes = await fetchWithTimeout(`${API_BASE}/tasks/${task.id}/execute`, {
        method: "POST",
        headers
      }, 120000); // 2 minute timeout for long streams
      
      if (!executeRes.ok || !executeRes.body) throw new Error(`Task execution failed: HTTP ${executeRes.status}`);

      const reader = executeRes.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      let currentNodes: any[] = [];
      let currentOutputs: any = {};

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || !trimmed.startsWith("data: ")) continue;
          
          try {
            const jsonStr = trimmed.replace(/^data:\s*/, "");
            const data = JSON.parse(jsonStr);
            
            if (data.step === "interpretation") {
              const virtualId = "virtual-interpretation";
              if (!currentNodes.some(n => n.id === virtualId)) {
                const virtualNode = {
                  id: virtualId,
                  department: "Interpretation Engine",
                  objective: "Extracting user intent...",
                  message: data.result.user_intent,
                  task_id: task.id
                };
                currentNodes = [virtualNode];
                if (onTaskExecute) onTaskExecute(currentNodes, currentOutputs, task.id, false);
              }
            } else if (data.step === "classification") {
              const virtualId = "virtual-classification";
              if (!currentNodes.some(n => n.id === virtualId)) {
                const virtualNode = {
                  id: virtualId,
                  department: "Strategic Classification",
                  objective: `Classifying task as ${data.result.task_type}...`,
                  message: `Primary Department: ${data.result.primary_department}`,
                  task_id: task.id
                };
                currentNodes = [...currentNodes, virtualNode];
                if (onTaskExecute) onTaskExecute(currentNodes, currentOutputs, task.id, false);
              }
            } else if (data.step === "ceo") {
              // Replace virtual nodes with the actual plan, but preserve progress if possible
              currentNodes = (data.result.delegation_plan || []).map((node: any) => ({
                ...node,
                task_id: task.id
              }));
              if (onTaskExecute) onTaskExecute(currentNodes, currentOutputs, task.id, false);
            } else if (data.step === "media" || data.step === "research" || data.step === "finance") {
              currentOutputs[data.step] = data.output;
              if (onTaskExecute) onTaskExecute(currentNodes, { ...currentOutputs }, task.id, false);
            } else if (data.step.startsWith("vidura_")) {
              const dept = data.step.replace("vidura_", "");
              currentOutputs["vidura_audit"] = currentOutputs["vidura_audit"] || {};
              currentOutputs["vidura_audit"][dept] = data.audit;
              if (onTaskExecute) onTaskExecute(currentNodes, { ...currentOutputs }, task.id, false);
            } else if (data.step === "final") {
              if (onTaskExecute) onTaskExecute(
                data.result.delegation_chain || currentNodes, 
                data.result.outputs || currentOutputs, 
                task.id,
                true
              );
            }
          } catch (e) {
            console.error("Failed to parse SSE chunk:", trimmed, e);
          }
        }
      }

      if (!overridePrompt) setPrompt("");
      fetchTasks(); // refresh task list after execution

    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      console.error(e);
      alert("API Error: " + msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredTasks = tasks.filter((t) => {
    if (filter === "Pending Review") return t.status === "pending_review";
    if (filter === "In Progress") return t.status === "in_progress";
    return true;
  });

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="border-primary/20 text-primary bg-primary/5">
            CEO Office
          </Badge>
          <span className="text-sm text-muted-foreground font-mono">mahabharataOS v0.1.0</span>
        </div>
        <h1 className="text-4xl font-semibold tracking-tight text-foreground">
          Command Desk
        </h1>
        <p className="text-muted-foreground text-lg">
          Enter an objective. The AI orchestrator will plan, delegate, and execute.
        </p>
      </div>

      {/* Input Area */}
      <Card className="border-border/50 bg-card/50 backdrop-blur-xl shadow-2xl overflow-hidden transition-all duration-500 hover:shadow-primary/5 focus-within:ring-1 focus-within:ring-primary/20">
        <CardContent className="p-0 relative">
          <Textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., Draft a LinkedIn post about how 80% of our startup success comes from AI execution..."
            className="min-h-[150px] w-full resize-none border-0 bg-transparent p-6 text-lg placeholder:text-muted-foreground/60 focus-visible:ring-0 focus-visible:ring-offset-0"
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                handleSubmit();
              }
            }}
          />

          <div className="absolute bottom-4 right-4 flex items-center gap-4">
            <span className="text-xs text-muted-foreground font-medium flex items-center gap-1 hidden sm:flex">
              <kbd className="rounded-md border bg-muted px-1.5 py-0.5 font-sans text-[10px]">⌘</kbd>
              <kbd className="rounded-md border bg-muted px-1.5 py-0.5 font-sans text-[10px]">Enter</kbd>
              to orchestrate
            </span>
            <Button
              size="lg"
              className="gap-2 shadow-lg shadow-primary/20 transition-all duration-300 hover:shadow-primary/40"
              onClick={() => handleSubmit()}
              disabled={isSubmitting || !prompt.trim()}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Orchestrating...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Execute Objective
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Active Tasks */}
      <div className="pt-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-medium flex items-center gap-2 text-foreground/80">
            <ListTodo className="h-5 w-5" />
            Active Tasks
            {tasks.length > 0 && (
              <span className="text-sm text-muted-foreground font-normal">({tasks.length})</span>
            )}
          </h2>
          <div className="flex gap-2">
            {(["All", "Pending Review", "In Progress"] as FilterType[]).map((f) => (
              <Badge
                key={f}
                variant={filter === f ? "default" : "outline"}
                className={`cursor-pointer transition-colors ${
                  filter === f
                    ? "bg-primary/20 text-primary border-primary/30 hover:bg-primary/30"
                    : "hover:bg-muted"
                }`}
                onClick={() => setFilter(f)}
              >
                {f}
              </Badge>
            ))}
          </div>
        </div>

        {tasksLoading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground py-6">
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            Loading tasks...
          </div>
        )}

        {!tasksLoading && filteredTasks.length === 0 && (
          <div className="text-sm text-muted-foreground py-6 text-center border border-dashed border-border/50 rounded-xl">
            {filter === "All"
              ? "No tasks yet — execute an objective above to get started."
              : `No tasks with status "${filter}".`}
          </div>
        )}

        {!tasksLoading && filteredTasks.length > 0 && (
          <div className="space-y-3">
            {filteredTasks.map((task) => {
              const conf = STATUS_CONFIG[task.status];
              return (
                <Card
                  key={task.id}
                  className="border-border/40 bg-card/30 hover:bg-card/60 transition-colors"
                >
                  <CardContent className="p-4 flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm text-foreground truncate">{task.title}</p>
                      <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">
                        {task.original_prompt}
                      </p>
                      {task.last_run_at && (
                        <p className="text-[10px] text-muted-foreground/50 mt-1 font-mono">
                          Last run: {new Date(task.last_run_at).toLocaleString()}
                        </p>
                      )}
                    </div>
                    <Badge
                      variant="outline"
                      className={`shrink-0 flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider ${conf.badge}`}
                    >
                      {conf.icon}
                      {conf.label}
                    </Badge>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
});

CommandDesk.displayName = "CommandDesk";
export default CommandDesk;
