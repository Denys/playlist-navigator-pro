import React from 'react';
import { ListVideo } from 'lucide-react';

export function PlaylistsTab() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Your Playlists</h2>
        <button className="px-4 py-2 liquid-glass-sm rounded-lg text-sm hover:text-slate-900 dark:hover:text-white transition-colors border-0">
          Export All
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="col-span-full text-center py-20">
          <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-emerald-600/10 flex items-center justify-center text-5xl">
            📚
          </div>
          <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">No playlists yet</h3>
          <p className="text-slate-500 dark:text-white/60">Start by indexing your first YouTube playlist</p>
        </div>
      </div>
    </div>
  );
}
