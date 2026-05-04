"use client";

import { useState, useEffect, useRef } from "react";
import { Terminal, Cpu, Wifi } from "lucide-react";

interface StatusMessage {
  id: string;
  sender: "KRISHNA" | "BHISHMA" | "ARJUNA" | "VIDURA" | "SYSTEM";
  text: string;
  timestamp: string;
}

export default function LiveStatusFeed({ isRunning, currentTask }: { isRunning: boolean, currentTask?: string }) {
  const [messages, setMessages] = useState<StatusMessage[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isRunning) {
      setMessages([{
        id: "1",
        sender: "SYSTEM",
        text: `Initializing mission: ${currentTask?.substring(0, 30) || "Objective"}...`,
        timestamp: new Date().toLocaleTimeString()
      }]);

      const sequence = [
        { sender: "KRISHNA", text: "Analyzing the Vyūha... Strategic alignment confirmed.", delay: 1500 },
        { sender: "BHISHMA", text: "Scanning the divine scrolls of knowledge (Web Search active).", delay: 3500 },
        { sender: "BHISHMA", text: "Synthesis complete. Core truths extracted.", delay: 5500 },
        { sender: "ARJUNA", text: "Target locked. Manifesting creative assets.", delay: 7500 },
        { sender: "VIDURA", text: "Dharma check: Risk assessment and financial integrity verified.", delay: 9500 },
        { sender: "SYSTEM", text: "Mission accomplished. Output workspace ready.", delay: 11000 },
      ];

      const timers = sequence.map((step, index) => {
        return setTimeout(() => {
          setMessages(prev => [...prev, {
            id: `msg-${step.sender}-${index}`,
            sender: step.sender as any,
            text: step.text,
            timestamp: new Date().toLocaleTimeString()
          }]);
        }, step.delay);
      });

      return () => timers.forEach(clearTimeout);
    } else {
      setMessages([]);
    }
  }, [isRunning, currentTask]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  if (!isRunning && messages.length === 0) return null;

  return (
    <div className="w-full max-w-4xl mx-auto bg-slate-900 border border-white/5 rounded-lg overflow-hidden shadow-2xl animate-in slide-in-from-bottom-4 duration-500">
      <div className="bg-slate-800/50 px-4 py-2 border-b border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="h-4 w-4 text-primary" />
          <span className="text-xs font-mono font-bold tracking-widest text-muted-foreground uppercase">Divine Transmission Feed</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <Cpu className="h-3 w-3 text-emerald-500 animate-pulse" />
            <span className="text-[10px] font-mono text-emerald-500/80">CORE_SYNC</span>
          </div>
          <div className="flex items-center gap-1">
            <Wifi className="h-3 w-3 text-blue-500 animate-pulse" />
            <span className="text-[10px] font-mono text-blue-500/80">ENCRYPTED</span>
          </div>
        </div>
      </div>
      
      <div 
        ref={scrollRef}
        className="h-48 overflow-y-auto p-4 font-mono text-sm space-y-2 scroll-smooth"
      >
        {messages.map((msg) => (
          <div key={msg.id} className="flex gap-3 animate-in fade-in slide-in-from-left-1 duration-300">
            <span className="text-muted-foreground/40 shrink-0">[{msg.timestamp}]</span>
            <span className={`font-bold shrink-0 ${
              msg.sender === "KRISHNA" ? "text-yellow-500" :
              msg.sender === "BHISHMA" ? "text-blue-500" :
              msg.sender === "ARJUNA" ? "text-purple-500" :
              msg.sender === "VIDURA" ? "text-emerald-500" :
              "text-white"
            }`}>
              {msg.sender}:
            </span>
            <span className="text-foreground/90">{msg.text}</span>
          </div>
        ))}
        {isRunning && (
          <div className="flex gap-2 items-center text-primary/60">
            <div className="h-1 w-1 bg-primary rounded-full animate-ping" />
            <span className="text-xs italic">Awaiting further transmission...</span>
          </div>
        )}
      </div>
    </div>
  );
}
