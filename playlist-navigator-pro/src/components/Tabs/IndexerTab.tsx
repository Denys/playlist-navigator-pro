import React, { useState } from 'react';
import { PlaySquare } from 'lucide-react';

export function IndexerTab() {
  const [url, setUrl] = useState('');
  const [name, setName] = useState('');
  const [color, setColor] = useState('emerald');

  const colorSchemes = [
    { id: 'emerald', label: 'Generic', gradient: 'from-emerald-500 to-emerald-700', shadow: 'shadow-emerald-600/25 hover:shadow-emerald-600/40' },
    { id: 'violet', label: 'AI/ML/LLM', gradient: 'from-violet-500 to-purple-600', shadow: 'shadow-violet-600/25 hover:shadow-violet-600/40' },
    { id: 'amber', label: 'Electronics', gradient: 'from-amber-400 to-orange-500', shadow: 'shadow-amber-500/25 hover:shadow-amber-500/40' },
    { id: 'blue', label: 'Firmware', gradient: 'from-blue-500 to-indigo-600', shadow: 'shadow-blue-500/25 hover:shadow-blue-500/40' },
    { id: 'rose', label: 'Audio HW', gradient: 'from-rose-500 to-red-600', shadow: 'shadow-rose-500/25 hover:shadow-rose-500/40' },
    { id: 'fuchsia', label: 'Composing', gradient: 'from-fuchsia-500 to-pink-600', shadow: 'shadow-fuchsia-500/25 hover:shadow-fuchsia-500/40' },
    { id: 'cyan', label: 'Playlists', gradient: 'from-cyan-400 to-blue-500', shadow: 'shadow-cyan-400/25 hover:shadow-cyan-400/40' },
    { id: 'slate', label: 'Other', gradient: 'from-slate-500 to-slate-700', shadow: 'shadow-slate-500/25 hover:shadow-slate-500/40' },
  ];

  const selectedScheme = colorSchemes.find(s => s.id === color) || colorSchemes[0];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle indexing logic
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="liquid-glass rounded-3xl p-8">
        <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Index YouTube Playlist</h2>
        <p className="text-slate-600 dark:text-white/70 mb-8">Extract and index playlist videos with descriptions and metadata.</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-white/80 mb-2">Playlist URL</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full px-4 py-3 liquid-glass-sm border-0 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-emerald-600/50"
              placeholder="https://youtube.com/playlist?list=..."
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-white/80 mb-2">Playlist Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 liquid-glass-sm border-0 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-emerald-600/50"
              placeholder="My Study Mix"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-white/80 mb-3">Color Scheme</label>
            <div className="grid grid-cols-4 sm:grid-cols-8 gap-3">
              {colorSchemes.map((scheme) => (
                <div key={scheme.id} className="flex flex-col items-center gap-2 group">
                  <button
                    type="button"
                    onClick={() => setColor(scheme.id)}
                    className={`w-10 h-10 rounded-full bg-gradient-to-br border-2 transition-all ${scheme.gradient} ${
                      color === scheme.id
                        ? 'border-emerald-900 dark:border-white shadow-lg ring-2 ring-emerald-900 dark:ring-white ring-offset-2 ring-offset-emerald-50 dark:ring-offset-[#0a1a12] opacity-100 scale-110'
                        : 'border-transparent opacity-60 hover:opacity-100 hover:scale-105'
                    }`}
                    title={scheme.label}
                  />
                  <span className={`text-[10px] font-medium transition-colors text-center ${
                    color === scheme.id 
                      ? 'text-slate-900 dark:text-white' 
                      : 'text-slate-500 dark:text-white/40 group-hover:text-slate-700 dark:group-hover:text-white/70'
                  }`}>
                    {scheme.label}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <button
            type="submit"
            className={`w-full py-3 px-6 bg-gradient-to-r ${selectedScheme.gradient} rounded-xl font-semibold text-white shadow-lg ${selectedScheme.shadow} hover:scale-[1.02] transition-all flex items-center justify-center gap-2`}
          >
            <PlaySquare size={20} />
            Index Playlist
          </button>
        </form>
      </div>
    </div>
  );
}
