"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Sword, Users, CalendarDays, Terminal } from "lucide-react";
import SettingsModal from "@/components/SettingsModal";

const NAV_LINKS = [
  { href: "/", label: "Command Desk", icon: <Terminal className="h-4 w-4" /> },
  { href: "/characters", label: "Characters", icon: <Users className="h-4 w-4" /> },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between gap-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 flex-shrink-0 group">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/25 group-hover:shadow-amber-500/40 transition-shadow">
            <Sword className="h-3.5 w-3.5 text-white" />
          </div>
          <span className="font-semibold text-sm tracking-tight text-white">
            Mahabharata<span className="text-amber-400">OS</span>
          </span>
        </Link>

        {/* Nav links */}
        <nav className="flex items-center gap-1">
          {NAV_LINKS.map(({ href, label, icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                id={`nav-${label.toLowerCase().replace(/\s+/g, "-")}`}
                className={`
                  flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                  transition-all duration-150
                  ${active
                    ? "bg-white/10 text-white"
                    : "text-slate-400 hover:text-white hover:bg-white/6"
                  }
                `}
              >
                {icon}
                <span className="hidden sm:inline">{label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Settings */}
        <div className="flex-shrink-0">
          <SettingsModal />
        </div>
      </div>
    </header>
  );
}
