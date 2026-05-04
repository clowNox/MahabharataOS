"use client";

import { Shield, Sword, Crown, Flame, Star, User } from "lucide-react";

interface Character {
  id: string;
  name: string;
  role?: string;
  side?: string;
  description?: string;
  weapon?: string;
  lineage?: string;
  avatar_url?: string;
}

const ROLE_CONFIG: Record<string, { icon: React.ReactNode; color: string }> = {
  Warrior: {
    icon: <Sword className="h-3 w-3" />,
    color: "bg-red-500/20 text-red-300 border-red-500/30",
  },
  Sage: {
    icon: <Star className="h-3 w-3" />,
    color: "bg-violet-500/20 text-violet-300 border-violet-500/30",
  },
  King: {
    icon: <Crown className="h-3 w-3" />,
    color: "bg-amber-500/20 text-amber-300 border-amber-500/30",
  },
  Queen: {
    icon: <Crown className="h-3 w-3" />,
    color: "bg-pink-500/20 text-pink-300 border-pink-500/30",
  },
  "Avatar / Divine": {
    icon: <Flame className="h-3 w-3" />,
    color: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
  },
  "Demon / Asura": {
    icon: <Shield className="h-3 w-3" />,
    color: "bg-orange-500/20 text-orange-300 border-orange-500/30",
  },
  Other: {
    icon: <User className="h-3 w-3" />,
    color: "bg-slate-500/20 text-slate-300 border-slate-500/30",
  },
};

const SIDE_CONFIG: Record<string, string> = {
  Pandava: "bg-blue-500/15 text-blue-300 border-blue-500/25",
  Kaurava: "bg-rose-500/15 text-rose-300 border-rose-500/25",
  Neutral: "bg-slate-500/15 text-slate-300 border-slate-500/25",
};

const AVATAR_INITIALS = (name: string) =>
  name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

const SIDE_BG: Record<string, string> = {
  Pandava: "from-blue-900/40 to-slate-900",
  Kaurava: "from-rose-900/40 to-slate-900",
  Neutral: "from-slate-800/60 to-slate-900",
};

export default function CharacterCard({ character }: { character: Character }) {
  const roleConf = ROLE_CONFIG[character.role ?? "Other"] ?? ROLE_CONFIG["Other"];
  const sideClass = SIDE_CONFIG[character.side ?? "Neutral"] ?? SIDE_CONFIG["Neutral"];
  const sideBg = SIDE_BG[character.side ?? "Neutral"] ?? SIDE_BG["Neutral"];

  return (
    <div
      className={`
        group relative flex flex-col overflow-hidden rounded-2xl border border-white/10
        bg-gradient-to-b ${sideBg}
        shadow-lg transition-all duration-300
        hover:-translate-y-1 hover:shadow-xl hover:border-white/20
        cursor-pointer
      `}
    >
      {/* Top accent stripe by side */}
      <div
        className={`h-1 w-full ${
          character.side === "Pandava"
            ? "bg-gradient-to-r from-blue-500 to-indigo-500"
            : character.side === "Kaurava"
            ? "bg-gradient-to-r from-rose-500 to-red-600"
            : "bg-gradient-to-r from-slate-500 to-slate-400"
        }`}
      />

      <div className="p-5 flex flex-col gap-4 flex-1">
        {/* Header row */}
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div
            className={`
              flex-shrink-0 h-14 w-14 rounded-xl flex items-center justify-center
              text-lg font-bold tracking-wide text-white shadow-inner
              ${
                character.side === "Pandava"
                  ? "bg-blue-600/50"
                  : character.side === "Kaurava"
                  ? "bg-rose-600/50"
                  : "bg-slate-600/50"
              }
            `}
          >
            {AVATAR_INITIALS(character.name)}
          </div>

          {/* Name + badges */}
          <div className="flex-1 min-w-0">
            <h3 className="text-base font-semibold text-white truncate">
              {character.name}
            </h3>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {character.role && (
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border font-medium ${roleConf.color}`}
                >
                  {roleConf.icon}
                  {character.role}
                </span>
              )}
              {character.side && (
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs border font-medium ${sideClass}`}
                >
                  {character.side}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Description */}
        {character.description && (
          <p className="text-sm text-slate-300 leading-relaxed line-clamp-3">
            {character.description}
          </p>
        )}

        {/* Footer — weapon + lineage */}
        <div className="mt-auto space-y-1.5 border-t border-white/10 pt-3">
          {character.weapon && (
            <div className="flex items-start gap-2 text-xs text-slate-400">
              <Sword className="h-3.5 w-3.5 mt-0.5 flex-shrink-0 text-amber-400/70" />
              <span className="truncate">{character.weapon}</span>
            </div>
          )}
          {character.lineage && (
            <div className="flex items-start gap-2 text-xs text-slate-400">
              <Star className="h-3.5 w-3.5 mt-0.5 flex-shrink-0 text-violet-400/70" />
              <span className="truncate">{character.lineage}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
