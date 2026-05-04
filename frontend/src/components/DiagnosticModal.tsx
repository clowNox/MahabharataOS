"use client";

import { useState } from "react";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription, 
  DialogFooter 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Bug, Copy, Check, Terminal } from "lucide-react";

interface DiagnosticData {
  taskId?: string;
  runId?: string;
  timestamp: string;
  errors: any[];
  logs: string[];
  environment: {
    os: string;
    browser: string;
    version: string;
  };
}

export default function DiagnosticModal({ 
  isOpen, 
  onClose, 
  data 
}: { 
  isOpen: boolean; 
  onClose: () => void; 
  data: Partial<DiagnosticData> 
}) {
  const [copied, setCopied] = useState(false);

  const report = JSON.stringify({
    title: "MahabharataOS Dharma Analysis Report",
    ...data,
    timestamp: new Date().toISOString(),
    environment: {
      os: typeof window !== "undefined" ? navigator.platform : "unknown",
      browser: typeof window !== "undefined" ? navigator.userAgent : "unknown",
      version: "0.1.0-alpha"
    }
  }, null, 2);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl bg-slate-950 border-white/10 text-white">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Bug className="h-5 w-5 text-red-500" />
            Dharma Analysis Report
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            Compile system diagnostics for external debugging or peer review.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 my-4">
          <div className="flex gap-2">
            <Badge variant="outline" className="bg-red-500/10 text-red-400 border-red-500/20">
              {data.errors?.length || 0} Issues Detected
            </Badge>
            <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/20">
              System: Stable
            </Badge>
          </div>

          <div className="relative group">
            <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
              <Button size="sm" variant="secondary" onClick={copyToClipboard} className="h-8 gap-2">
                {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                {copied ? "Copied" : "Copy JSON"}
              </Button>
            </div>
            <pre className="bg-slate-900 border border-white/5 p-4 rounded-lg text-xs font-mono text-slate-300 max-h-64 overflow-y-auto overflow-x-hidden whitespace-pre-wrap">
              {report}
            </pre>
          </div>

          <div className="bg-amber-500/5 border border-amber-500/10 p-3 rounded-lg flex gap-3">
            <Terminal className="h-5 w-5 text-amber-500 shrink-0" />
            <p className="text-[10px] text-amber-200/70 leading-relaxed">
              <span className="font-bold block mb-1 uppercase tracking-tighter">Usage Note:</span>
              This report contains transient identifiers. Paste this into your debugging tool or share it with the technical council (Developers) for rapid resolution.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="ghost" onClick={onClose} className="text-slate-400 hover:text-white">
            Close
          </Button>
          <Button onClick={copyToClipboard} className="bg-primary hover:bg-primary/90 text-primary-foreground">
            Copy Report
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
