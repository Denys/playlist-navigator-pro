import React from 'react';

export function MindMapTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">🧠 Knowledge Graph</h2>
      <p className="text-slate-500 dark:text-white/60 mb-6">Visualize connections between videos based on tags and channels</p>
      <div className="liquid-glass rounded-3xl p-4 h-[600px]">
        <div className="w-full h-full flex items-center justify-center text-slate-400 dark:text-white/40">
          Mind map visualization will appear here when you have indexed playlists
        </div>
      </div>
    </div>
  );
}
