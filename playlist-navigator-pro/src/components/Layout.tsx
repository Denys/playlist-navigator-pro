import React from 'react';
import { PlaySquare, ListVideo, Search, Image as ImageIcon, Store, BrainCircuit, Bot, Sun, Moon } from 'lucide-react';
import { TabType } from '../App';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
}

export function Layout({ children, activeTab, setActiveTab }: LayoutProps) {
  const [isDark, setIsDark] = React.useState(true);

  React.useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);
  const navItems = [
    { id: 'indexer', label: 'Indexer', icon: PlaySquare },
    { id: 'playlists', label: 'Playlists', icon: ListVideo },
    { id: 'search', label: 'Search', icon: Search },
    { id: 'gallery', label: 'Gallery', icon: ImageIcon },
    { id: 'store', label: 'Store', icon: Store },
    { id: 'mindmap', label: 'Mind Map', icon: BrainCircuit },
  ] as const;

  return (
    <div className="min-h-screen relative bg-emerald-50 dark:bg-[#0a1a12] text-slate-900 dark:text-white overflow-x-hidden font-sans transition-colors duration-500">
      {/* Animated Background */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        {/* Pine Green */}
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-emerald-500/30 dark:bg-emerald-800/30 blur-[120px] animate-float"></div>
        {/* River Blue */}
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-sky-400/30 dark:bg-sky-800/30 blur-[120px] animate-float-delayed"></div>
        {/* Tree Trunk Brown */}
        <div className="absolute top-[40%] left-[40%] w-[30%] h-[30%] rounded-full bg-amber-600/20 dark:bg-amber-900/20 blur-[100px] animate-float-slow"></div>
        {/* Rock Grey */}
        <div className="absolute top-[20%] right-[20%] w-[25%] h-[25%] rounded-full bg-slate-400/20 dark:bg-slate-700/20 blur-[100px] animate-float"></div>
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 liquid-glass border-b-0 hidden md:block">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-sky-500 flex items-center justify-center shadow-lg shadow-emerald-600/20">
                <span className="text-2xl">🌲</span>
              </div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-800 to-sky-700 dark:from-emerald-200 dark:to-sky-200">
                Playlist Navigator <span className="font-light opacity-70">Pro</span>
              </h1>
            </div>

            <nav className="flex gap-1 p-1 liquid-glass-sm rounded-full border-0">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`px-4 py-2 rounded-full text-sm font-medium flex items-center gap-2 transition-all ${
                    activeTab === item.id
                      ? 'liquid-glass-sm shadow-[0_0_20px_rgba(16,185,129,0.1)] text-emerald-900 dark:text-white border-0'
                      : 'text-slate-600 hover:text-slate-900 dark:text-white/70 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/10'
                  }`}
                >
                  <item.icon size={16} />
                  {item.label}
                </button>
              ))}
              <button
                onClick={() => setActiveTab('assistant')}
                className={`px-4 py-2 rounded-full text-sm font-medium flex items-center gap-2 transition-all ${
                  activeTab === 'assistant'
                    ? 'bg-gradient-to-r from-emerald-600/40 to-sky-500/40 text-emerald-900 dark:text-white border border-emerald-600/80 shadow-[0_0_20px_rgba(5,150,105,0.3)]'
                    : 'bg-gradient-to-r from-emerald-600/10 to-sky-500/10 dark:from-emerald-600/20 dark:to-sky-500/20 text-emerald-800 dark:text-white border border-emerald-600/30 hover:border-emerald-600/60 shadow-[0_0_15px_rgba(5,150,105,0.15)]'
                }`}
              >
                <Bot size={16} />
                Assistant
              </button>
              <button
                onClick={() => setIsDark(!isDark)}
                className="ml-2 p-2 rounded-full text-slate-600 hover:text-slate-900 dark:text-white/70 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
                aria-label="Toggle theme"
              >
                {isDark ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Mobile Header */}
      <header className="sticky top-0 z-50 liquid-glass border-b-0 md:hidden pt-[env(safe-area-inset-top)]">
        <div className="px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-600 to-sky-500 flex items-center justify-center shadow-lg shadow-emerald-600/20">
              <span className="text-xl">🌲</span>
            </div>
            <h1 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-800 to-sky-700 dark:from-emerald-200 dark:to-sky-200">
              Playlist Nav
            </h1>
          </div>
          <button
            onClick={() => setIsDark(!isDark)}
            className="p-2 rounded-full text-slate-600 hover:text-slate-900 dark:text-white/70 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
          >
            {isDark ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-24 md:pb-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        {children}
      </main>

      {/* Mobile Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden liquid-glass border-t border-white/10 pb-[env(safe-area-inset-bottom)]">
        <div className="flex justify-around items-center h-16 px-2">
          {navItems.slice(0, 5).map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex flex-col items-center justify-center w-full h-full gap-1 ${
                activeTab === item.id
                  ? 'text-emerald-600 dark:text-emerald-400'
                  : 'text-slate-500 dark:text-white/50'
              }`}
            >
              <item.icon size={20} strokeWidth={activeTab === item.id ? 2.5 : 2} />
              <span className="text-[10px] font-medium">{item.label}</span>
            </button>
          ))}
          <button
            onClick={() => setActiveTab('assistant')}
            className={`flex flex-col items-center justify-center w-full h-full gap-1 ${
              activeTab === 'assistant'
                ? 'text-emerald-600 dark:text-emerald-400'
                : 'text-slate-500 dark:text-white/50'
            }`}
          >
            <Bot size={20} strokeWidth={activeTab === 'assistant' ? 2.5 : 2} />
            <span className="text-[10px] font-medium">Assistant</span>
          </button>
        </div>
      </nav>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-200 dark:border-white/10 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center text-sm text-slate-500 dark:text-white/50">
          <div className="flex items-center gap-2 mb-4 md:mb-0">
            <span className="w-2 h-2 rounded-full bg-emerald-600 shadow-[0_0_8px_rgba(5,150,105,0.6)]"></span>
            <span>API Quota: <strong className="text-slate-900 dark:text-white">4,230</strong> / 10,000</span>
          </div>
          <div>40 playlists | 1684 videos</div>
          <div className="flex gap-6">
            <a href="#" className="hover:text-slate-900 dark:hover:text-white transition-colors">Privacy</a>
            <a href="#" className="hover:text-slate-900 dark:hover:text-white transition-colors">Terms</a>
            <span>v2.5.0 (Liquid Glass)</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
