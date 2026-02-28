import React, { useState } from 'react';
import { TabId, TabConfig } from './types';
import { GlassCard, GlassInput, GlassButton, GlassSelect } from './components/GlassUI';
import { IconDownload, IconLibrary, IconSearch, IconVideo, IconStore, IconBrain, IconLink, IconPlay } from './components/Icons';
import { mockPlaylists, mockVideos } from './services/mockData';
import MindMap from './components/MindMap';

// --- Sub-Components for specific tabs ---

const IndexerTab = () => {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setProgress(0);
    
    // Simulate progress
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 100) {
          clearInterval(interval);
          setLoading(false);
          return 100;
        }
        return p + 5;
      });
    }, 100);
  };

  return (
    <GlassCard title="Index YouTube Playlist" className="max-w-2xl mx-auto">
      <p className="text-white/70 mb-8">Extract and index playlist videos with descriptions and metadata into your local library.</p>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <GlassInput 
          label="Playlist URL" 
          placeholder="https://youtube.com/playlist?list=..." 
          icon={<IconLink />}
        />
        
        <GlassInput 
          label="Playlist Name" 
          placeholder="e.g. My Study Mix" 
          icon={<span className="text-lg">📝</span>}
        />

        <div className="mb-6">
            <label className="block text-sm font-medium text-white/80 mb-2 ml-1">Color Scheme</label>
            <div className="flex gap-3">
                {['bg-purple-500', 'bg-teal-500', 'bg-blue-500', 'bg-green-500'].map((color, i) => (
                    <button 
                        key={i}
                        type="button"
                        className={`w-10 h-10 rounded-full ${color} shadow-lg border-2 border-white/20 hover:scale-110 transition-transform ${i === 0 ? 'ring-2 ring-white ring-offset-2 ring-offset-transparent' : ''}`} 
                    />
                ))}
            </div>
        </div>

        <GlassButton type="submit" className="w-full">
            <IconDownload />
            {loading ? 'Indexing...' : 'Index Playlist'}
        </GlassButton>
      </form>

      {loading && (
        <div className="mt-8 bg-black/20 rounded-xl p-4 border border-white/10">
            <div className="flex justify-between text-sm text-white/80 mb-2">
                <span>Processing videos...</span>
                <span>{progress}%</span>
            </div>
            <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                <div 
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300"
                    style={{ width: `${progress}%` }}
                ></div>
            </div>
        </div>
      )}
    </GlassCard>
  );
};

const PlaylistsTab = () => (
  <div className="space-y-6">
     <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/60">Your Playlists</h2>
        <GlassButton variant="secondary" className="!py-2">Export All</GlassButton>
     </div>
      
     <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockPlaylists.map(playlist => (
            <GlassCard
              key={playlist.id}
              className="cursor-pointer hover:bg-white/15 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-300/70 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900"
              role="link"
              tabIndex={0}
              aria-label={`Open playlist ${playlist.name}`}
              onClick={() => window.open(playlist.url, '_blank', 'noopener,noreferrer')}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault();
                  window.open(playlist.url, '_blank', 'noopener,noreferrer');
                }
              }}
            >
                <div className={`h-32 -mx-6 -mt-6 mb-4 relative overflow-hidden`}>
                    <div className={`absolute inset-0 bg-gradient-to-br ${
                        playlist.color === 'purple' ? 'from-purple-600 to-indigo-800' :
                        playlist.color === 'teal' ? 'from-teal-500 to-emerald-700' :
                        playlist.color === 'blue' ? 'from-blue-500 to-sky-700' :
                        'from-green-500 to-lime-700'
                    } opacity-80`}></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-6xl opacity-20">📚</span>
                    </div>
                </div>
                <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-bold text-white truncate pr-4">{playlist.name}</h3>
                </div>
                <div className="flex justify-between items-center text-sm text-white/60">
                    <span>{playlist.videoCount} videos</span>
                    <span>{playlist.lastUpdated}</span>
                </div>
            </GlassCard>
        ))}
     </div>
  </div>
);

const GalleryTab = ({ isStore = false }: { isStore?: boolean }) => (
    <div className="space-y-6">
       <div className="flex flex-col md:flex-row gap-4 mb-6 sticky top-24 z-20 bg-slate-900/10 backdrop-blur-md p-4 rounded-2xl border border-white/5">
          <GlassInput placeholder="Search..." className="!mb-0" />
          <div className="flex gap-2 min-w-[300px]">
             <GlassSelect className="!mb-0">
                <option>Newest First</option>
                <option>Oldest First</option>
             </GlassSelect>
             {isStore && (
                <GlassSelect className="!mb-0">
                    <option>All Genres</option>
                    <option>Education</option>
                    <option>Music</option>
                </GlassSelect>
             )}
          </div>
       </div>
       
       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {mockVideos.map(video => (
              <GlassCard key={video.id} className="group !p-0 overflow-hidden border-none bg-black/20 hover:bg-black/40">
                  <div className="relative aspect-video">
                      <img src={video.thumbnail} alt={video.title} className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
                      <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40 backdrop-blur-[2px]">
                         <div className="bg-white/20 p-3 rounded-full backdrop-blur-md border border-white/30 text-white">
                             <IconPlay />
                         </div>
                      </div>
                      <span className="absolute bottom-2 right-2 bg-black/60 text-xs px-2 py-1 rounded text-white backdrop-blur-sm">{video.duration}</span>
                  </div>
                  <div className="p-4">
                      <h4 className="font-semibold text-white mb-1 line-clamp-2 leading-tight">{video.title}</h4>
                      <div className="flex justify-between text-xs text-white/60 mt-2">
                          <span>{video.channel}</span>
                          <span>{video.views} views</span>
                      </div>
                      {isStore && (
                          <GlassButton className="w-full mt-4 text-sm !py-2" variant="secondary">Add to Library</GlassButton>
                      )}
                  </div>
              </GlassCard>
          ))}
       </div>
    </div>
);

const SearchTab = () => (
    <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
            <h2 className="text-4xl font-bold text-white mb-2">Master Search</h2>
            <p className="text-white/60">Deep search across tags, descriptions, and transcripts.</p>
        </div>
        
        <div className="relative mb-12">
            <input 
                type="text" 
                placeholder="What are you looking for?" 
                className="w-full h-16 pl-8 pr-32 rounded-full bg-white/10 backdrop-blur-xl border border-white/20 text-xl text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-400/50 shadow-[0_0_30px_rgba(139,92,246,0.3)]"
            />
            <div className="absolute right-2 top-2 h-12 w-12 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center shadow-lg cursor-pointer hover:scale-105 transition-transform">
                <IconSearch />
            </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
             {/* Mock search results placeholder */}
             <div className="text-center py-10 text-white/30 border-2 border-dashed border-white/10 rounded-3xl">
                 Start typing to see magic results...
             </div>
        </div>
    </div>
);

// --- Main App Component ---

const App = () => {
  const [activeTab, setActiveTab] = useState<TabId>('indexer');

  const tabs: TabConfig[] = [
    { id: 'indexer', label: 'Indexer', icon: <IconDownload /> },
    { id: 'playlists', label: 'Playlists', icon: <IconLibrary /> },
    { id: 'search', label: 'Search', icon: <IconSearch /> },
    { id: 'gallery', label: 'Gallery', icon: <IconVideo /> },
    { id: 'store', label: 'Store', icon: <IconStore /> },
    { id: 'mindmap', label: 'Mind Map', icon: <IconBrain /> },
  ];

  return (
    <div className="min-h-screen relative overflow-hidden font-sans text-slate-100 selection:bg-purple-500/50">
      
      {/* Dynamic Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-slate-900" />
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-700/30 blur-[100px] animate-float" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-700/20 blur-[120px] animate-float-delayed" />
        <div className="absolute top-[40%] left-[40%] w-[30%] h-[30%] rounded-full bg-pink-600/20 blur-[90px] animate-float" />
      </div>

      {/* Main Content Wrapper */}
      <div className="relative z-10 flex flex-col min-h-screen">
        
        {/* Header */}
        <header className="sticky top-0 z-50 backdrop-blur-md bg-slate-900/30 border-b border-white/10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-20">
              <div className="flex items-center gap-3">
                 <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/20">
                    <span className="text-2xl">🎬</span>
                 </div>
                 <h1 className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-purple-200">
                   Playlist Navigator <span className="font-light opacity-70">Pro</span>
                 </h1>
              </div>

              {/* Desktop Nav */}
              <nav className="hidden md:flex gap-1 p-1 bg-white/5 rounded-full border border-white/10 backdrop-blur-sm">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      relative px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 flex items-center gap-2
                      ${activeTab === tab.id ? 'text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}
                    `}
                  >
                    {activeTab === tab.id && (
                        <span className="absolute inset-0 bg-white/10 rounded-full shadow-[0_0_10px_rgba(255,255,255,0.1)] border border-white/10"></span>
                    )}
                    <span className="relative z-10 flex items-center gap-2">
                        {tab.icon} {tab.label}
                    </span>
                  </button>
                ))}
              </nav>
            </div>
          </div>
          
          {/* Mobile Nav Scroller (Optional implementation simplified) */}
          <div className="md:hidden overflow-x-auto pb-3 px-4 flex gap-2 no-scrollbar">
             {tabs.map(tab => (
                 <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`whitespace-nowrap px-4 py-2 rounded-full text-sm font-medium border transition-colors ${activeTab === tab.id ? 'bg-white/20 border-white/30 text-white' : 'bg-transparent border-transparent text-white/60'}`}
                 >
                     {tab.label}
                 </button>
             ))}
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            {activeTab === 'indexer' && <IndexerTab />}
            {activeTab === 'playlists' && <PlaylistsTab />}
            {activeTab === 'search' && <SearchTab />}
            {activeTab === 'gallery' && <GalleryTab />}
            {activeTab === 'store' && <GalleryTab isStore={true} />}
            {activeTab === 'mindmap' && <MindMap />}
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t border-white/10 bg-black/20 backdrop-blur-md py-6">
          <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center text-sm text-white/50">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
                <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></span>
                <span>API Quota: <strong>4,230</strong> / 10,000</span>
            </div>
            <div className="flex gap-6">
                <a href="#" className="hover:text-white transition-colors">Privacy</a>
                <a href="#" className="hover:text-white transition-colors">Terms</a>
                <span>v2.4.0 (Liquid)</span>
            </div>
          </div>
        </footer>

      </div>
    </div>
  );
};

export default App;
