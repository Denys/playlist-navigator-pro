import React from 'react';

export function StoreTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-6">Video Store</h2>
      <div className="flex gap-4 mb-6 overflow-x-auto pb-2">
        <button className="px-6 py-3 rounded-xl liquid-glass-sm text-slate-900 dark:text-white font-medium whitespace-nowrap border-0">
          All
        </button>
        <button className="px-6 py-3 rounded-xl liquid-glass-sm text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white whitespace-nowrap border-0">
          Education
        </button>
        <button className="px-6 py-3 rounded-xl liquid-glass-sm text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white whitespace-nowrap border-0">
          Music
        </button>
        <button className="px-6 py-3 rounded-xl liquid-glass-sm text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white whitespace-nowrap border-0">
          Tech
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="col-span-full text-center py-20">
          <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-emerald-600/10 flex items-center justify-center text-5xl">
            🏪
          </div>
          <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">Store is empty</h3>
          <p className="text-slate-500 dark:text-white/60">Add videos to your collection to see them here</p>
        </div>
      </div>
    </div>
  );
}
