import React, { useState } from 'react';
import { Layout } from './components/Layout';
import { IndexerTab } from './components/Tabs/IndexerTab';
import { PlaylistsTab } from './components/Tabs/PlaylistsTab';
import { SearchTab } from './components/Tabs/SearchTab';
import { GalleryTab } from './components/Tabs/GalleryTab';
import { StoreTab } from './components/Tabs/StoreTab';
import { MindMapTab } from './components/Tabs/MindMapTab';
import { AssistantTab } from './components/Tabs/AssistantTab';
import { AIChatWidget } from './components/AIChatWidget';

export type TabType = 'indexer' | 'playlists' | 'search' | 'gallery' | 'store' | 'mindmap' | 'assistant';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('indexer');

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {activeTab === 'indexer' && <IndexerTab />}
      {activeTab === 'playlists' && <PlaylistsTab />}
      {activeTab === 'search' && <SearchTab />}
      {activeTab === 'gallery' && <GalleryTab />}
      {activeTab === 'store' && <StoreTab />}
      {activeTab === 'mindmap' && <MindMapTab />}
      {activeTab === 'assistant' && <AssistantTab />}
      
      <AIChatWidget />
    </Layout>
  );
}
