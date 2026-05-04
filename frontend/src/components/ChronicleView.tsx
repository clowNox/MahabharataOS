"use client";

import { useState, useEffect } from "react";
import { History, Search, Cpu, Database, ChevronRight, Zap, Filter } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface MemoryEntry {
  type: string;
  task_id: string;
  text_snippet: string;
  character?: string;
  dept?: string;
  timestamp: string;
  score?: number;
}

export default function ChronicleView() {
  const [entries, setEntries] = useState<MemoryEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const fetchEntries = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/chronicle/list?limit=15`);
      if (res.ok) {
        const data = await res.json();
        setEntries(data);
      }
    } catch (e) {
      console.error("Failed to fetch chronicle", e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchEntries();
      return;
    }
    setIsSearching(true);
    try {
      const openaiKey = localStorage.getItem("x-openai-key");
      const res = await fetch(`${API_BASE}/chronicle/search?query=${encodeURIComponent(searchQuery)}`, {
        headers: { "x-openai-key": openaiKey || "" }
      });
      if (res.ok) {
        const data = await res.json();
        // search returns [{score, metadata}]
        setEntries(data.map((d: any) => ({ ...d.metadata, score: d.score })));
      }
    } catch (e) {
      console.error("Search failed", e);
    } finally {
      setIsSearching(false);
    }
  };

  useEffect(() => {
    fetchEntries();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between border-b border-white/5 pb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <History className="h-6 w-6 text-amber-500" />
          </div>
          <div>
            <h2 className="text-2xl font-bold tracking-tight">The Chronicle</h2>
            <p className="text-sm text-slate-400 font-medium">Temporal Memory & Semantic Ledger</p>
          </div>
        </div>

        <div className="flex w-full md:w-auto gap-2">
          <div className="relative w-full md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <Input 
              placeholder="Search past wisdom..." 
              className="pl-10 bg-slate-900/50 border-white/10 focus:border-amber-500/50 transition-all"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
          </div>
          <Button 
            variant="secondary" 
            className="bg-amber-500/10 hover:bg-amber-500/20 text-amber-500 border border-amber-500/20"
            onClick={handleSearch}
            disabled={isSearching}
          >
            {isSearching ? <Zap className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {isLoading ? (
          <div className="py-20 text-center text-slate-500 animate-pulse font-mono uppercase tracking-widest text-xs">
            Consulting the Oracle...
          </div>
        ) : entries.length === 0 ? (
          <div className="py-20 text-center text-slate-500 bg-slate-900/20 border border-dashed border-white/5 rounded-2xl">
            <Database className="h-8 w-8 mx-auto mb-4 opacity-20" />
            <p className="text-sm">No transmissions recorded in the Chronicle yet.</p>
          </div>
        ) : (
          entries.map((entry, i) => (
            <Card key={i} className="bg-slate-900/40 border-white/5 hover:bg-slate-900/60 transition-all group overflow-hidden">
              <CardContent className="p-0">
                <div className="flex flex-col md:flex-row">
                  <div className={`w-full md:w-48 p-4 border-b md:border-b-0 md:border-r border-white/5 flex flex-col justify-between gap-4 ${
                    entry.type === 'strategy' ? 'bg-blue-500/5' : 
                    entry.type === 'audit' ? 'bg-amber-500/5' : 'bg-emerald-500/5'
                  }`}>
                    <div className="space-y-2">
                      <Badge variant="outline" className={`uppercase text-[9px] tracking-widest ${
                        entry.type === 'strategy' ? 'border-blue-500/30 text-blue-400' : 
                        entry.type === 'audit' ? 'border-amber-500/30 text-amber-400' : 'border-emerald-500/30 text-emerald-400'
                      }`}>
                        {entry.type}
                      </Badge>
                      <div className="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                        <Cpu className="h-3 w-3" />
                        {entry.character || entry.dept || "System"}
                      </div>
                    </div>
                    {entry.score !== undefined && (
                      <div className="text-xs font-black text-amber-500/50">
                        Match: {(entry.score * 100).toFixed(0)}%
                      </div>
                    )}
                  </div>
                  <div className="flex-1 p-4 relative">
                    <p className="text-xs text-slate-300 leading-relaxed italic line-clamp-3">
                      "{entry.text_snippet}..."
                    </p>
                    <div className="mt-4 flex items-center justify-between">
                      <span className="text-[9px] text-slate-600 font-mono uppercase tracking-tighter">TASK: {entry.task_id.split('-')[0]}</span>
                      <Button variant="ghost" size="sm" className="h-7 text-[10px] gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        View Context <ChevronRight className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
