import React from 'react';

export interface Video {
  id: string;
  title: string;
  thumbnail: string;
  channel: string;
  duration: string;
  views: string;
  playlistId: string;
}

export interface Playlist {
  id: string;
  name: string;
  videoCount: number;
  color: 'purple' | 'teal' | 'blue' | 'green' | 'pink';
  url: string;
  lastUpdated: string;
}

export type TabId = 'indexer' | 'playlists' | 'search' | 'gallery' | 'store' | 'mindmap';

export interface TabConfig {
  id: TabId;
  label: string;
  icon: React.ReactNode;
}