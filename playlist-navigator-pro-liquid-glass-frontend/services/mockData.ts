import { Playlist, Video } from '../types';

export const mockPlaylists: Playlist[] = [
  { id: '1', name: 'Web Dev Essentials', videoCount: 142, color: 'purple', url: '#', lastUpdated: '2 days ago' },
  { id: '2', name: 'Liquid Drum & Bass', videoCount: 56, color: 'teal', url: '#', lastUpdated: '1 week ago' },
  { id: '3', name: 'React Conference 2024', videoCount: 24, color: 'blue', url: '#', lastUpdated: '3 weeks ago' },
  { id: '4', name: 'Nature Documentaries', videoCount: 12, color: 'green', url: '#', lastUpdated: '1 month ago' },
];

export const mockVideos: Video[] = [
  { id: '101', title: 'Advanced React Patterns', thumbnail: 'https://picsum.photos/320/180?random=1', channel: 'Frontend Masters', duration: '45:20', views: '12K', playlistId: '1' },
  { id: '102', title: 'Understanding CSS Grid', thumbnail: 'https://picsum.photos/320/180?random=2', channel: 'CSS Tricks', duration: '12:05', views: '8.5K', playlistId: '1' },
  { id: '103', title: 'Atmospheric Jungle Mix', thumbnail: 'https://picsum.photos/320/180?random=3', channel: 'Liquid City', duration: '1:02:30', views: '45K', playlistId: '2' },
  { id: '104', title: 'Keynote: The Future of UI', thumbnail: 'https://picsum.photos/320/180?random=4', channel: 'React Conf', duration: '30:15', views: '150K', playlistId: '3' },
  { id: '105', title: 'Deep Sea Creatures', thumbnail: 'https://picsum.photos/320/180?random=5', channel: 'Nat Geo', duration: '48:10', views: '2.1M', playlistId: '4' },
  { id: '106', title: 'TypeScript for Beginners', thumbnail: 'https://picsum.photos/320/180?random=6', channel: 'Programming with Mosh', duration: '1:15:00', views: '500K', playlistId: '1' },
  { id: '107', title: 'Lo-Fi Beats to Relax To', thumbnail: 'https://picsum.photos/320/180?random=7', channel: 'Lofi Girl', duration: 'Live', views: '24K', playlistId: '2' },
  { id: '108', title: 'Mountain Climbing 101', thumbnail: 'https://picsum.photos/320/180?random=8', channel: 'Outdoor Life', duration: '22:45', views: '12K', playlistId: '4' },
];