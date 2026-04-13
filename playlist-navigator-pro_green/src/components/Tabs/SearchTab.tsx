import React, { useState } from 'react';
import { Search } from 'lucide-react';

export function SearchTab() {
  const [query, setQuery] = useState('');

  return (
    <div className="max-w-4xl mx-auto text-center">
      <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-2">Master Search</h2>
      <p className="text-slate-500 dark:text-white/60 mb-8">Deep search across tags, descriptions, and transcripts</p>

      <div className="relative mb-8">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full h-16 pl-6 pr-16 rounded-full liquid-glass-sm border-0 text-xl text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-emerald-600/50 shadow-[0_0_30px_rgba(5,150,105,0.2)]"
          placeholder="What are you looking for?"
        />
        <button className="absolute right-2 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-gradient-to-r from-emerald-600 to-sky-500 flex items-center justify-center shadow-lg hover:scale-105 transition-transform">
          <Search size={20} className="text-white" strokeWidth={3} />
        </button>
      </div>

      <div className="text-left">
        <div className="text-center py-12 text-slate-400 dark:text-white/40">
          Start typing to search across all your indexed content
        </div>
      </div>
    </div>
  );
}
