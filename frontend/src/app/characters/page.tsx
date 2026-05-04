"use client";

import { useEffect, useMemo, useState } from "react";
import { Search, Users, Loader2, AlertCircle } from "lucide-react";
import CharacterCard from "@/components/CharacterCard";
import { fetchWithTimeout } from "@/lib/fetchWithTimeout";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

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

const SIDE_FILTERS = ["All", "Pandava", "Kaurava", "Neutral"] as const;
type SideFilter = (typeof SIDE_FILTERS)[number];

export default function CharactersPage() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [side, setSide] = useState<SideFilter>("All");
  const [total, setTotal] = useState(0);

  // Fetch all characters on mount
  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const [listRes, countRes] = await Promise.all([
          fetchWithTimeout(`${API_BASE}/characters/`, {}, 10000),
          fetchWithTimeout(`${API_BASE}/characters/count`, {}, 10000),
        ]);
        if (!listRes.ok) throw new Error(`HTTP ${listRes.status}`);
        if (!countRes.ok) throw new Error(`Count endpoint failed: HTTP ${countRes.status}`);
        const list: Character[] = await listRes.json();
        const { count } = await countRes.json();
        setCharacters(list);
        setTotal(count);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Client-side search + filter
  const filtered = useMemo(() => {
    let result = characters;
    if (query.trim()) {
      const q = query.toLowerCase();
      result = result.filter(
        (c) =>
          c.name.toLowerCase().includes(q) ||
          c.description?.toLowerCase().includes(q) ||
          c.weapon?.toLowerCase().includes(q)
      );
    }
    if (side !== "All") {
      result = result.filter((c) => c.side === side);
    }
    return result;
  }, [characters, query, side]);

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* Hero header */}
      <div className="relative overflow-hidden border-b border-white/10 bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900">
        {/* Decorative glows */}
        <div className="absolute top-0 left-1/4 -translate-x-1/2 w-96 h-96 rounded-full bg-blue-600/10 blur-3xl pointer-events-none" />
        <div className="absolute top-0 right-1/4 translate-x-1/2 w-96 h-96 rounded-full bg-rose-600/10 blur-3xl pointer-events-none" />

        <div className="relative max-w-6xl mx-auto px-6 py-14">
          <div className="flex items-center gap-3 mb-3">
            <Users className="h-8 w-8 text-amber-400" />
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-amber-300 via-white to-amber-300 bg-clip-text text-transparent">
              Characters of the Mahabharata
            </h1>
          </div>
          <p className="text-slate-400 text-sm max-w-lg">
            {total > 0
              ? `${total} characters — warriors, sages, kings, and divine beings from the great epic.`
              : "Loading the great warriors..."}
          </p>
        </div>
      </div>

      {/* Controls bar */}
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur-md border-b border-white/8">
        <div className="max-w-6xl mx-auto px-6 py-3 flex flex-col sm:flex-row gap-3 items-center">
          {/* Search */}
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <input
              id="character-search"
              type="text"
              placeholder="Search by name, description, or weapon…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-800/60 border border-white/10 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/40 transition"
            />
          </div>

          {/* Side filter tabs */}
          <div className="flex gap-1.5 flex-shrink-0">
            {SIDE_FILTERS.map((s) => (
              <button
                key={s}
                id={`filter-${s.toLowerCase()}`}
                onClick={() => setSide(s)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  side === s
                    ? s === "Pandava"
                      ? "bg-blue-600 text-white shadow-lg shadow-blue-600/25"
                      : s === "Kaurava"
                      ? "bg-rose-600 text-white shadow-lg shadow-rose-600/25"
                      : "bg-amber-500 text-slate-900 shadow-lg shadow-amber-500/25"
                    : "bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white"
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-3 text-slate-500">
            <Loader2 className="h-8 w-8 animate-spin text-amber-400" />
            <span className="text-sm">Summoning the warriors…</span>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-3 p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-300 text-sm max-w-lg mx-auto">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
            <div>
              <p className="font-medium">Failed to load characters</p>
              <p className="text-red-400/70 text-xs mt-0.5">{error} — is the backend running?</p>
            </div>
          </div>
        )}

        {!loading && !error && filtered.length === 0 && (
          <div className="text-center py-20 text-slate-500 text-sm">
            No characters found for <span className="text-white">&quot;{query}&quot;</span>
            {side !== "All" && (
              <span>
                {" "}on the <span className="text-white">{side}</span> side
              </span>
            )}
            .
          </div>
        )}

        {!loading && !error && filtered.length > 0 && (
          <>
            <p className="text-xs text-slate-500 mb-5">
              Showing {filtered.length} of {total} characters
              {side !== "All" && ` · ${side} side`}
              {query && ` · matching "${query}"`}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filtered.map((c) => (
                <CharacterCard key={c.id} character={c} />
              ))}
            </div>
          </>
        )}
      </div>
    </main>
  );
}
