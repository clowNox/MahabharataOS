"use client";

import { useState, useRef } from "react";
import CommandDesk from "@/components/CommandDesk";
import CampaignPlanner from "@/components/CampaignPlanner";
import CharacterBios from "@/components/CharacterBios";
import LiveStatusFeed from "@/components/LiveStatusFeed";
import DiagnosticModal from "@/components/DiagnosticModal";
import SettingsModal from "@/components/SettingsModal";
import ChronicleView from "@/components/ChronicleView";
import ExecutionStepper, { DelegationNodeData } from "@/components/ExecutionStepper";
import OutputWorkspace, { OutputsData } from "@/components/OutputWorkspace";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui";
import { Zap, Calendar, Bug, Users, Settings, Shield, History } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Home() {
  const [delegationNodes, setDelegationNodes] = useState<DelegationNodeData[]>([]);
  const [outputs, setOutputs] = useState<OutputsData | null>(null);
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [activeMode, setActiveMode] = useState<"single" | "campaign" | "characters" | "chronicle">("single");
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentPrompt, setCurrentPrompt] = useState("");
  const [isDiagnosticOpen, setIsDiagnosticOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [sessionErrors, setSessionErrors] = useState<any[]>([]);

  const commandDeskRef = useRef<any>(null);

  const handleExecution = (nodes: any, taskOutputs: any, taskId?: string, isFinal: boolean = true) => {
    setDelegationNodes(nodes as DelegationNodeData[]);
    setOutputs(taskOutputs as OutputsData ?? null);
    setActiveTaskId(taskId ?? (nodes as DelegationNodeData[])[0]?.task_id ?? null);
    if (isFinal) setIsExecuting(false);
    
    setTimeout(() => {
       window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }, 100);
  };

  const handleCampaignDayExecute = (prompt: string) => {
    setActiveMode("single");
    setCurrentPrompt(prompt);
    setIsExecuting(true);
    setDelegationNodes([]);
    setOutputs(null);

    if (commandDeskRef.current) {
      commandDeskRef.current.executePrompt(prompt);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/5 via-slate-950 to-slate-950 selection:bg-primary/20">
      <div className="container mx-auto px-4 py-12 md:py-16 space-y-8 max-w-6xl">
        
        <div className="flex justify-between items-center mb-4">
          <div className="w-10 h-10" /> {/* Spacer */}
          <Tabs value={activeMode} onValueChange={(val: string) => setActiveMode(val as any)} className="w-full max-w-[600px]">
            <TabsList className="grid w-full grid-cols-4 bg-slate-900/50 border border-white/5 backdrop-blur-md">
              <TabsTrigger value="single" className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary flex items-center gap-2">
                <Zap className="h-4 w-4" />
                <span className="hidden sm:inline">Quick Task</span>
              </TabsTrigger>
              <TabsTrigger value="campaign" className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <span className="hidden sm:inline">Architect</span>
              </TabsTrigger>
              <TabsTrigger value="chronicle" className="data-[state=active]:bg-amber-500/20 data-[state=active]:text-amber-500 flex items-center gap-2">
                <History className="h-4 w-4" />
                <span className="hidden sm:inline">Chronicle</span>
              </TabsTrigger>
              <TabsTrigger value="characters" className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary flex items-center gap-2">
                <Users className="h-4 w-4" />
                <span className="hidden sm:inline">Council</span>
              </TabsTrigger>
            </TabsList>
          </Tabs>
          <Button 
            onClick={() => setIsSettingsOpen(true)}
            variant="ghost" 
            size="icon" 
            className="rounded-full h-10 w-10 text-slate-400 hover:text-primary hover:bg-primary/10 transition-all"
          >
            <Shield className="h-5 w-5" />
          </Button>
        </div>

        <div className="transition-all duration-500 ease-in-out">
          {activeMode === "single" ? (
            <div className="space-y-8">
              <CommandDesk 
                ref={commandDeskRef}
                onTaskExecute={handleExecution} 
              />
              <LiveStatusFeed isRunning={isExecuting} currentTask={currentPrompt} />
            </div>
          ) : activeMode === "campaign" ? (
            <div className="space-y-12">
              <CampaignPlanner onExecuteDay={handleCampaignDayExecute} />
            </div>
          ) : activeMode === "chronicle" ? (
            <div className="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <ChronicleView />
            </div>
          ) : (
            <div className="space-y-12 animate-in fade-in slide-in-from-top-4 duration-500">
              <CharacterBios />
            </div>
          )}
        </div>

        <div className="space-y-12">
          {delegationNodes.length > 0 && (
            <ExecutionStepper 
              key={activeTaskId || "execution-stepper"} 
              dataNodes={delegationNodes} 
            />
          )}
          {outputs && (
            <OutputWorkspace
              key={activeTaskId || "output-workspace"}
              outputs={outputs}
              taskId={activeTaskId ?? undefined}
              onComplete={() => {
                setDelegationNodes([]);
                setOutputs(null);
                setActiveTaskId(null);
              }}
            />
          )}
        </div>

        {/* Floating Debug Button */}
        <div className="fixed bottom-6 right-6 z-50">
          <Button 
            onClick={() => setIsDiagnosticOpen(true)}
            variant="outline" 
            size="icon" 
            className="rounded-full h-12 w-12 bg-slate-900 border-white/10 shadow-2xl hover:bg-slate-800 transition-all hover:scale-110"
          >
            <Bug className="h-5 w-5 text-red-500" />
          </Button>
        </div>

        <DiagnosticModal 
          isOpen={isDiagnosticOpen} 
          onClose={() => setIsDiagnosticOpen(false)} 
          data={{
            taskId: activeTaskId || delegationNodes[0]?.task_id,
            errors: sessionErrors,
            logs: ["Divine Transmission Feed active", "Vyūha stabilized", ...(outputs?.media?.reasoning ? [outputs.media.reasoning] : [])],
            environment: {
              os: "MahabharataOS-v0.1",
              browser: "Chronicle-Ready",
              version: "Phase-3"
            }
          }}
        />

        <SettingsModal 
          isOpen={isSettingsOpen} 
          onClose={() => setIsSettingsOpen(false)} 
        />
      </div>
    </main>
  );
}
