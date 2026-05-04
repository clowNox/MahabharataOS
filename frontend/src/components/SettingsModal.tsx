"use client";

import { useState, useEffect } from "react";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription, 
  DialogFooter 
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Shield, Lock, Key, Loader2, CheckCircle2, AlertCircle } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function SettingsModal({ 
  isOpen, 
  onClose 
}: { 
  isOpen: boolean; 
  onClose: () => void; 
}) {
  const [vaultStatus, setVaultStatus] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<Record<string, 'idle' | 'success' | 'error'>>({});
  
  const apiKeys = [
    { id: "openai", name: "OpenAI API Key", icon: <Zap className="h-4 w-4" /> },
    { id: "anthropic", name: "Anthropic API Key", icon: <Cpu className="h-4 w-4" /> },
    { id: "tavily", name: "Tavily Search Key", icon: <Wifi className="h-4 w-4" /> },
    { id: "gemini", name: "Google Gemini Key", icon: <Sparkles className="h-4 w-4" /> },
  ];

  const fetchVaultStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/vault/status`);
      if (res.ok) {
        const data = await res.json();
        setVaultStatus(data.keys || []);
      }
    } catch (e) {
      console.error("Failed to fetch vault status", e);
    }
  };

  useEffect(() => {
    if (isOpen) fetchVaultStatus();
  }, [isOpen]);

  const handleSaveSecret = async (key: string, value: string) => {
    if (!value) return;
    setIsSaving(key);
    setSaveStatus(prev => ({ ...prev, [key]: 'idle' }));
    
    try {
      const res = await fetch(`${API_BASE}/vault/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key, value }),
      });
      
      if (res.ok) {
        setSaveStatus(prev => ({ ...prev, [key]: 'success' }));
        fetchVaultStatus();
        // Clear value from input if needed (usually handled by local state in parent)
      } else {
        setSaveStatus(prev => ({ ...prev, [key]: 'error' }));
      }
    } catch (e) {
      setSaveStatus(prev => ({ ...prev, [key]: 'error' }));
    } finally {
      setIsSaving(null);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-xl bg-slate-950 border-white/10 text-white backdrop-blur-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl">
            <Shield className="h-5 w-5 text-primary" />
            Strategic Vault
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            Securely persist API keys to the server-side vault for autonomous campaign execution.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 my-4">
          <div className="bg-primary/5 border border-primary/20 p-3 rounded-lg flex gap-3">
            <Lock className="h-5 w-5 text-primary shrink-0" />
            <p className="text-[10px] text-primary/70 leading-relaxed">
              <span className="font-bold block mb-1 uppercase tracking-tighter">Encrypted Storage</span>
              Keys are encrypted using AES-256 (Fernet) and never stored in plain text. They are only decrypted in-memory during autonomous background runs.
            </p>
          </div>

          <div className="space-y-4">
            {apiKeys.map((key) => {
              const isStored = vaultStatus.includes(key.id);
              const status = saveStatus[key.id] || 'idle';
              
              return (
                <div key={key.id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                      <Key className="h-3 w-3" />
                      {key.name}
                    </label>
                    {isStored && (
                      <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/20 text-[9px] uppercase">
                        Securely Persisted
                      </Badge>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Input 
                      type="password"
                      placeholder={isStored ? "••••••••••••••••" : "Enter key..."}
                      className="bg-slate-900 border-white/5 focus:border-primary/50 transition-all text-xs"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleSaveSecret(key.id, (e.target as HTMLInputElement).value);
                          (e.target as HTMLInputElement).value = "";
                        }
                      }}
                    />
                    <Button 
                      size="sm" 
                      disabled={isSaving === key.id}
                      onClick={(e) => {
                        const input = (e.currentTarget.previousSibling as HTMLInputElement);
                        handleSaveSecret(key.id, input.value);
                        input.value = "";
                      }}
                      className="shrink-0"
                    >
                      {isSaving === key.id ? <Loader2 className="h-4 w-4 animate-spin" /> : "Store"}
                    </Button>
                  </div>
                  {status === 'success' && (
                    <p className="text-[9px] text-green-500 flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3" /> Key secured in vault.
                    </p>
                  )}
                  {status === 'error' && (
                    <p className="text-[9px] text-red-400 flex items-center gap-1">
                      <AlertCircle className="h-3 w-3" /> Failed to store key.
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <DialogFooter className="border-t border-white/5 pt-4">
          <Button variant="ghost" onClick={onClose} className="text-slate-400 hover:text-white">
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Sub-icons for the keys (placeholders for lucide components)
function Zap(props: any) { return <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 14.71 11 3l1.5 8h7.5L13 21l-1.5-8z"/></svg> }
function Cpu(props: any) { return <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg> }
function Wifi(props: any) { return <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.58 16.11a7 7 0 0 1 6.84 0"/><path d="M12 20h.01"/></svg> }
function Sparkles(props: any) { return <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg> }
