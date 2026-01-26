#!/usr/bin/env python3
"""
YouTube Playlist Data Extractor
Helper script to extract video information from YouTube playlists
for use with the Playlist Indexer.
"""

import json
import re
import argparse
from typing import List, Dict, Any

class PlaylistDataExtractor:
    def __init__(self):
        """Initialize the playlist data extractor."""
        pass
    
    def extract_from_manual_input(self, videos_text: str) -> List[Dict[str, Any]]:
        """Extract video data from manually copied playlist text."""
        videos = []
        lines = videos_text.strip().split('\n')
        
        current_video = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for video titles (usually longer lines without timestamps)
            if len(line) > 20 and not re.match(r'^\d+:\d+', line):
                # This might be a title
                if 'title' in current_video:
                    # Save previous video and start new one
                    if self.is_valid_video(current_video):
                        videos.append(current_video)
                    current_video = {}
                
                current_video['title'] = line
            
            # Look for channel names (usually shorter, after titles)
            elif 'title' in current_video and 'channel' not in current_video:
                if len(line) < 50 and not re.match(r'^\d+:\d+', line):
                    current_video['channel'] = line
        
        # Don't forget the last video
        if self.is_valid_video(current_video):
            videos.append(current_video)
        
        return videos
    
    def is_valid_video(self, video: Dict[str, Any]) -> bool:
        """Check if a video entry has the minimum required information."""
        return 'title' in video and len(video['title']) > 5
    
    def create_playlist_data(self, videos: List[Dict[str, Any]], base_url: str = "") -> List[Dict[str, Any]]:
        """Create properly formatted playlist data."""
        playlist_data = []
        
        for i, video in enumerate(videos):
            # Generate a placeholder URL if not provided
            url = video.get('url', f"{base_url}?v=video_{i+1}")
            
            playlist_data.append({
                "title": video['title'],
                "url": url,
                "channel": video.get('channel', 'Unknown Channel')
            })
        
        return playlist_data
    
    def interactive_input(self) -> List[Dict[str, Any]]:
        """Interactive mode for manual video entry."""
        print("Interactive Playlist Data Entry")
        print("=" * 40)
        print("Enter video information. Press Enter twice to finish.")
        print()
        
        videos = []
        while True:
            print(f"Video #{len(videos) + 1}:")
            title = input("Title: ").strip()
            if not title:
                break
            
            url = input("URL (optional): ").strip()
            if not url:
                url = f"https://www.youtube.com/watch?v=placeholder_{len(videos) + 1}"
            
            channel = input("Channel (optional): ").strip()
            if not channel:
                channel = "Unknown Channel"
            
            videos.append({
                "title": title,
                "url": url,
                "channel": channel
            })
            
            print()
            continue_input = input("Add another video? (y/n): ").strip().lower()
            if continue_input != 'y':
                break
            print()
        
        return videos

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='YouTube Playlist Data Extractor')
    parser.add_argument('--output', '-o', default='playlist_data.json', 
                       help='Output JSON file (default: playlist_data.json)')
    parser.add_argument('--input-file', '-i', 
                       help='Text file with copied playlist content')
    parser.add_argument('--interactive', action='store_true',
                       help='Use interactive mode for manual entry')
    parser.add_argument('--base-url', default='https://www.youtube.com/watch',
                       help='Base URL for generated video links')
    
    args = parser.parse_args()
    
    extractor = PlaylistDataExtractor()
    
    if args.interactive:
        # Interactive mode
        videos = extractor.interactive_input()
    elif args.input_file:
        # File input mode
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            videos = extractor.extract_from_manual_input(content)
        except Exception as e:
            print(f"Error reading input file: {e}")
            return 1
    else:
        # Manual paste mode
        print("Paste your playlist content (video titles and channels):")
        print("Press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) when done:")
        print()
        
        try:
            content = ""
            while True:
                try:
                    line = input()
                    content += line + "\n"
                except EOFError:
                    break
            
            videos = extractor.extract_from_manual_input(content)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return 1
    
    if not videos:
        print("No videos found or extracted.")
        return 1
    
    # Create properly formatted playlist data
    playlist_data = extractor.create_playlist_data(videos, args.base_url)
    
    # Save to JSON file
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(playlist_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully extracted {len(playlist_data)} videos")
        print(f"Saved to: {args.output}")
        print("\nExtracted videos:")
        for i, video in enumerate(playlist_data, 1):
            print(f"  {i}. {video['title']} - {video['channel']}")
        
        return 0
    except Exception as e:
        print(f"Error saving output file: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

