import { ReactNode } from "react";
import { Shield, Zap, BookOpen, Crown, Target, Scale, PenTool, BarChart3, Sword, Users as UsersIcon } from "lucide-react";

export interface CharacterStyle {
  icon: ReactNode;
  color: string;
  name: string;
  department: string;
}

export const CHARACTER_DATA: Record<string, CharacterStyle> = {
  krishna: { 
    name: "Krishna",
    department: "CEO Office",
    icon: <Crown className="h-5 w-5 text-yellow-500" />, 
    color: "border-yellow-500/20 bg-yellow-500/5 text-yellow-500" 
  },
  bhishma: { 
    name: "Bhishma",
    department: "Legal / Compliance",
    icon: <BookOpen className="h-5 w-5 text-blue-500" />, 
    color: "border-blue-500/20 bg-blue-500/5 text-blue-500" 
  },
  arjuna: { 
    name: "Arjuna",
    department: "Media Department",
    icon: <Zap className="h-5 w-5 text-purple-500" />, 
    color: "border-purple-500/20 bg-purple-500/5 text-purple-500" 
  },
  vidura: { 
    name: "Vidura",
    department: "Integrity / Citation",
    icon: <Shield className="h-5 w-5 text-emerald-500" />, 
    color: "border-emerald-500/20 bg-emerald-500/5 text-emerald-500" 
  },
  karna: { 
    name: "Karna",
    department: "Strategy",
    icon: <Target className="h-5 w-5 text-red-500" />, 
    color: "border-red-500/20 bg-red-500/5 text-red-500" 
  },
  yudhisthira: { 
    name: "Yudhisthira",
    department: "Policy",
    icon: <Scale className="h-5 w-5 text-slate-400" />, 
    color: "border-slate-500/20 bg-slate-500/5 text-slate-400" 
  },
  drona: { 
    name: "Drona",
    department: "Research Department",
    icon: <PenTool className="h-5 w-5 text-amber-600" />, 
    color: "border-amber-500/20 bg-amber-500/5 text-amber-600" 
  },
  sahadeva: { 
    name: "Sahadeva",
    department: "Finance & Capital",
    icon: <BarChart3 className="h-5 w-5 text-cyan-500" />, 
    color: "border-cyan-500/20 bg-cyan-500/5 text-cyan-500" 
  },
  draupadi: { 
    name: "Draupadi",
    department: "Stakeholder Relations",
    icon: <UsersIcon className="h-5 w-5 text-rose-500" />, 
    color: "border-rose-500/20 bg-rose-500/5 text-rose-500" 
  },
  duryodhana: { 
    name: "Duryodhana",
    department: "Competition Analysis",
    icon: <Sword className="h-5 w-5 text-red-700" />, 
    color: "border-red-700/20 bg-red-700/5 text-red-700" 
  },
};

export function getCharacterByDept(dept: string): CharacterStyle | null {
  const normalized = dept.toLowerCase();
  
  // CEO Office / Core Logic
  if (
    normalized.includes("ceo") || 
    normalized.includes("interpretation") || 
    normalized.includes("classification") || 
    normalized.includes("strategic") ||
    normalized.includes("office")
  ) {
    return CHARACTER_DATA.krishna;
  }
  
  // Media / Content
  if (normalized.includes("media") || normalized.includes("post") || normalized.includes("content")) {
    return CHARACTER_DATA.arjuna;
  }
  
  // Research / Intelligence
  if (normalized.includes("research") || normalized.includes("gather") || normalized.includes("findings")) {
    return CHARACTER_DATA.drona;
  }
  
  // Finance / Capital
  if (
    normalized.includes("finance") || 
    normalized.includes("capital") || 
    normalized.includes("budget") || 
    normalized.includes("cost") ||
    normalized.includes("financial")
  ) {
    return CHARACTER_DATA.sahadeva;
  }
  
  // Integrity / Citation / Audit
  if (
    normalized.includes("citation") || 
    normalized.includes("integrity") || 
    normalized.includes("audit") || 
    normalized.includes("verification")
  ) {
    return CHARACTER_DATA.vidura;
  }
  
  // Legal / Compliance / QA
  if (
    normalized.includes("legal") || 
    normalized.includes("compliance") || 
    normalized.includes("qa") || 
    normalized.includes("quality") ||
    normalized.includes("refine")
  ) {
    return CHARACTER_DATA.bhishma;
  }
  
  // Output / Deployment
  if (normalized.includes("output") || normalized.includes("workspace") || normalized.includes("deploy")) {
    return CHARACTER_DATA.yudhisthira;
  }

  // Fallback to Krishna if it's some unknown system step
  return CHARACTER_DATA.krishna;
}
