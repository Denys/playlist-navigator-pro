import React from 'react';

export function GalleryTab() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-6">Video Gallery</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="col-span-full text-center py-20">
          <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-emerald-600/10 flex items-center justify-center text-5xl">
            🎬
          </div>
          <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">No videos yet</h3>
          <p className="text-slate-500 dark:text-white/60">Index a playlist to see your videos here</p>
        </div>
      </div>
    </div>
  );
}
