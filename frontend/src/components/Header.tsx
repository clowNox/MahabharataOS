'use client';

import Link from 'next/link';
import { useState } from 'react';

export function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="border-b bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">M</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">MahabharataOS</h1>
          </Link>

          <nav className="hidden md:flex gap-8">
            <Link href="/" className="text-gray-600 hover:text-gray-900 font-medium">
              Dashboard
            </Link>
            <Link href="/tasks" className="text-gray-600 hover:text-gray-900 font-medium">
              Tasks
            </Link>
            <Link href="/campaigns" className="text-gray-600 hover:text-gray-900 font-medium">
              Campaigns
            </Link>
            <Link href="/settings" className="text-gray-600 hover:text-gray-900 font-medium">
              Settings
            </Link>
          </nav>

          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden p-2 hover:bg-gray-100 rounded-lg"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>

        {menuOpen && (
          <nav className="md:hidden mt-4 space-y-2 border-t pt-4">
            <Link
              href="/"
              className="block text-gray-600 hover:text-gray-900 font-medium py-2"
              onClick={() => setMenuOpen(false)}
            >
              Dashboard
            </Link>
            <Link
              href="/tasks"
              className="block text-gray-600 hover:text-gray-900 font-medium py-2"
              onClick={() => setMenuOpen(false)}
            >
              Tasks
            </Link>
            <Link
              href="/campaigns"
              className="block text-gray-600 hover:text-gray-900 font-medium py-2"
              onClick={() => setMenuOpen(false)}
            >
              Campaigns
            </Link>
            <Link
              href="/settings"
              className="block text-gray-600 hover:text-gray-900 font-medium py-2"
              onClick={() => setMenuOpen(false)}
            >
              Settings
            </Link>
          </nav>
        )}
      </div>
    </header>
  );
}
