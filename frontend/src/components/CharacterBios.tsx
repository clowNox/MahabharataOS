import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui";
import { Loader2, AlertCircle, Sparkles } from "lucide-react";
import { fetchWithTimeout } from "@/lib/fetchWithTimeout";
import { CHARACTER_DATA } from "@/lib/characters";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface Character {
  id: string;
  name: string;
  role?: string;
  side?: string;
  description?: string;
  weapon?: string;
  lineage?: string;
}

export default function CharacterBios() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [riskParams, setRiskParams] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetchWithTimeout(`${API_BASE}/characters/?limit=100`, {}, 10000);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const list: Character[] = await response.json();
        setCharacters(list);

        let savedParams: Record<string, number> = {};
        try {
          const saved = localStorage.getItem("CHARACTER_RISK_PARAMS");
          savedParams = saved ? JSON.parse(saved) : {};
        } catch {
          savedParams = {};
        }
        const defaults = list.reduce(
          (acc, char) => ({ ...acc, [char.name.toLowerCase()]: savedParams[char.name.toLowerCase()] ?? 50 }),
          {} as Record<string, number>
        );
        setRiskParams(defaults);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleRiskChange = (id: string, value: number[]) => {
    const newParams = { ...riskParams, [id]: value[0] };
    setRiskParams(newParams);
    localStorage.setItem("CHARACTER_RISK_PARAMS", JSON.stringify(newParams));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center gap-2 py-12 text-sm text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin text-primary" />
        Loading character bios...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
        <AlertCircle className="h-5 w-5 flex-shrink-0" />
        <div>
          <p className="font-medium">Failed to load character bios</p>
          <p className="text-xs text-red-400/70">{error} - is the backend running?</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold flex items-center gap-2 text-foreground">
          <Sparkles className="h-6 w-6 text-primary" />
          The Council of Sages
        </h2>
        <p className="text-sm text-muted-foreground">Adjust risk tolerance to influence AI behavior.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {characters.map((char) => {
          const charKey = char.name.toLowerCase();
          const style = CHARACTER_DATA[charKey] || { 
            icon: <Sparkles className="h-5 w-5 text-primary" />, 
            color: "border-primary/20 bg-primary/5" 
          };
          const specialty = char.weapon || char.lineage || char.side || "Epic counsel";

          return (
            <Card 
              key={char.id} 
              className={`relative overflow-hidden border-0 bg-slate-900/40 backdrop-blur-md transition-all duration-500 hover:scale-[1.02] hover:bg-slate-900/60 group`}
            >
              {/* Animated Gradient Border */}
              <div className={`absolute inset-0 border-2 rounded-xl opacity-20 group-hover:opacity-100 transition-opacity duration-500 ${style.color.split(" ")[0]}`} />
              
              <CardHeader className="pb-2 relative z-10">
                <div className="flex items-center gap-2 mb-2">
                  <div className={`p-2 rounded-lg bg-slate-950/50 border border-white/5 shadow-inner`}>
                    {style.icon}
                  </div>
                  <CardTitle className="text-sm font-bold tracking-tight">{char.name}</CardTitle>
                </div>
                <Badge variant="outline" className="w-fit border-white/10 text-[9px] h-4 bg-slate-950/50 backdrop-blur-sm">
                  {char.role || "Other"}{char.side ? ` - ${char.side}` : ""}
                </Badge>
              </CardHeader>
              
              <CardContent className="space-y-4 relative z-10">
                <p className="text-[10px] text-muted-foreground leading-tight italic line-clamp-2 min-h-[2.5em]">
                  {char.description || "A recorded figure from the Mahabharata archive."}
                </p>
                
                <div className="space-y-3 pt-3 border-t border-white/5">
                  <div className="flex justify-between items-center">
                    <span className="text-[9px] uppercase font-bold text-muted-foreground tracking-widest">Risk Factor</span>
                    <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded bg-slate-950 border border-white/5 ${
                      (riskParams[charKey] ?? 50) > 70 ? "text-red-400" :
                      (riskParams[charKey] ?? 50) < 30 ? "text-green-400" : "text-amber-400"
                    }`}>
                      {riskParams[charKey] ?? 50}%
                    </span>
                  </div>
                  <Slider
                    value={[riskParams[charKey] ?? 50]}
                    onValueChange={(val: number[]) => handleRiskChange(charKey, val)}
                    max={100}
                    step={1}
                    className="cursor-pointer"
                  />
                </div>

                <div className="text-[8px] uppercase tracking-[0.2em] font-bold text-foreground/30 pt-1">
                  {specialty}
                </div>
              </CardContent>

              {/* Decorative Background Element */}
              <div className={`absolute -right-4 -bottom-4 h-16 w-16 opacity-[0.03] group-hover:opacity-[0.07] transition-opacity duration-500`}>
                {style.icon}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
