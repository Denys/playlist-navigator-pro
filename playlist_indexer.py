#!/usr/bin/env python3
"""
YouTube Playlist Indexer
Automates the creation of interactive and expandable documents for YouTube playlists
with descriptions, hyperlinks, and tags.
"""

import os
import re
import json
import argparse
from markdown_it import MarkdownIt
from datetime import datetime
from typing import List, Dict, Any, Optional

from execution.io_utils import clean_secret_value, get_env_secret


def resolve_youtube_api_key(config: Dict[str, Any], config_file_path: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(config_file_path))
    env_key = get_env_secret(base_dir, "PLAYLIST_INDEXER_YOUTUBE_API_KEY", "YOUTUBE_API_KEY")
    if env_key:
        return env_key
    return clean_secret_value(config.get("youtube_api_key", ""))

class PlaylistIndexer:
    def __init__(self, config_file: str = "config.json"):
        """Initialize the playlist indexer with configuration."""
        self.config_file_path = os.path.abspath(config_file)
        self.config = self.load_config(self.config_file_path)
        self.video_data = []
        self.categories = {}
        self.tags = set()
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        default_config = {
            "output_dir": "output",
            "generate_html": True,
            "generate_pdf": True,
            "color_scheme": "purple",
            "auto_categorize": True,
            "tag_suggestions": True
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return default_config
        else:
            # Create default config file
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def extract_video_info(self, video_title: str, video_url: str, channel: str = "") -> Dict[str, Any]:
        """Extract and process video information."""
        # Generate description based on title
        description = self.generate_description(video_title)
        
        # Generate tags based on title and description
        tags = self.generate_tags(video_title, description)
        
        # Determine category
        category = self.categorize_video(video_title, description, tags)
        
        return {
            "title": video_title,
            "url": video_url,
            "channel": channel,
            "description": description,
            "tags": tags,
            "category": category
        }
    
    def generate_description(self, title: str) -> str:
        """Generate a concise description based on the video title."""
        # Common patterns and their descriptions
        patterns = {
            r'(?i)build|diy|make|create': 'tutorial on building',
            r'(?i)review|test': 'review and analysis of',
            r'(?i)tutorial|guide|how to': 'step-by-step guide for',
            r'(?i)demo|demonstration': 'demonstration of',
            r'(?i)comparison|vs|versus': 'comparison between',
            r'(?i)part \d+': 'part of a series on',
            r'(?i)workshop|masterclass': 'workshop covering',
            r'(?i)live|stream': 'live session about',
            r'(?i)beginner|intro|introduction': 'beginner-friendly introduction to',
            r'(?i)advanced|expert': 'advanced techniques for',
            r'(?i)tips|tricks': 'tips and tricks for',
            r'(?i)setup|install|configure': 'setup and configuration guide for'
        }
        
        description_start = "Comprehensive overview of"
        
        for pattern, desc_template in patterns.items():
            if re.search(pattern, title):
                description_start = desc_template.capitalize()
                break
        
        # Extract key terms from title
        key_terms = self.extract_key_terms(title)
        
        if key_terms:
            return f"{description_start} {' and '.join(key_terms[:3])}."
        else:
            return f"{description_start} the content presented in this video."
    
    def extract_key_terms(self, title: str) -> List[str]:
        """Extract key technical terms from the title."""
        # Common technical terms and their variations
        tech_terms = {
            'teensy': ['Teensy', 'microcontroller'],
            'arduino': ['Arduino', 'microcontroller'],
            'daisy': ['Daisy', 'audio platform'],
            'midi': ['MIDI', 'protocol'],
            'synth': ['synthesizer', 'synthesis'],
            'dsp': ['DSP', 'signal processing'],
            'filter': ['filter', 'audio processing'],
            'oscillator': ['oscillator', 'waveform generation'],
            'sequencer': ['sequencer', 'pattern programming'],
            'controller': ['controller', 'interface'],
            'audio': ['audio', 'sound'],
            'programming': ['programming', 'coding'],
            'electronics': ['electronics', 'hardware'],
            'diy': ['DIY', 'do-it-yourself'],
            'pcb': ['PCB', 'circuit board'],
            'firmware': ['firmware', 'embedded software']
        }
        
        found_terms = []
        title_lower = title.lower()
        
        for term, variations in tech_terms.items():
            if term in title_lower:
                found_terms.append(variations[0])
        
        return found_terms
    
    def generate_tags(self, title: str, description: str) -> List[str]:
        """Generate relevant tags based on title and description."""
        tags = []
        text = f"{title} {description}".lower()
        
        # Hardware tags
        hardware_tags = {
            'teensy': '#Teensy',
            'arduino': '#Arduino',
            'daisy': '#DaisySeed',
            'raspberry': '#RaspberryPi',
            'esp32': '#ESP32',
            'microcontroller': '#Microcontroller',
            'pcb': '#PCB',
            'hardware': '#Hardware',
            'electronics': '#Electronics'
        }
        
        # Audio tags
        audio_tags = {
            'synth': '#Synthesizer',
            'midi': '#MIDI',
            'audio': '#Audio',
            'dsp': '#DSP',
            'filter': '#Filter',
            'oscillator': '#Oscillator',
            'sequencer': '#Sequencer',
            'sampler': '#Sampler',
            'effects': '#Effects',
            'reverb': '#Reverb',
            'delay': '#Delay',
            'distortion': '#Distortion'
        }
        
        # Project tags
        project_tags = {
            'diy': '#DIY',
            'build': '#BuildGuide',
            'tutorial': '#Tutorial',
            'guide': '#Guide',
            'workshop': '#Workshop',
            'demo': '#Demo',
            'review': '#Review',
            'comparison': '#Comparison',
            'beginner': '#Beginner',
            'advanced': '#Advanced'
        }
        
        # Programming tags
        programming_tags = {
            'programming': '#Programming',
            'code': '#Coding',
            'firmware': '#Firmware',
            'software': '#Software',
            'library': '#Library',
            'api': '#API'
        }
        
        all_tag_groups = [hardware_tags, audio_tags, project_tags, programming_tags]
        
        for tag_group in all_tag_groups:
            for keyword, tag in tag_group.items():
                if keyword in text and tag not in tags:
                    tags.append(tag)
        
        # Limit to 5 most relevant tags
        return tags[:5]
    
    def categorize_video(self, title: str, description: str, tags: List[str]) -> str:
        """Automatically categorize the video based on content."""
        text = f"{title} {description}".lower()
        tag_text = " ".join(tags).lower()
        
        categories = {
            "Hardware Projects": ["teensy", "arduino", "diy", "build", "pcb", "electronics", "hardware"],
            "Audio Development": ["audio", "dsp", "library", "programming", "software", "api"],
            "Synthesizer Projects": ["synth", "oscillator", "filter", "effects", "analog"],
            "MIDI Controllers": ["midi", "controller", "interface", "input"],
            "Tutorials and Guides": ["tutorial", "guide", "workshop", "beginner", "how to"],
            "Reviews and Comparisons": ["review", "comparison", "vs", "test", "analysis"],
            "Live Sessions": ["live", "stream", "workshop", "masterclass"],
            "Advanced Techniques": ["advanced", "expert", "professional", "complex"]
        }
        
        category_scores = {}
        
        for category, keywords in categories.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 2
                if keyword in tag_text:
                    score += 1
            category_scores[category] = score
        
        # Return category with highest score, or default
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        return "General Projects"
    
    def process_playlist_data(self, playlist_data: List[Dict[str, str]]) -> None:
        """Process a list of video data from a playlist."""
        self.video_data = []
        self.categories = {}
        
        for video in playlist_data:
            video_info = self.extract_video_info(
                video.get('title', ''),
                video.get('url', ''),
                video.get('channel', '')
            )
            
            self.video_data.append(video_info)
            
            # Group by category
            category = video_info['category']
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(video_info)
            
            # Collect all tags
            self.tags.update(video_info['tags'])
    
    def extract_from_youtube_url(self, playlist_url: str, use_api: bool = True) -> List[Dict[str, str]]:
        """
        Extract playlist data directly from YouTube URL.
        
        Tries YouTube API first (if configured), falls back to browser automation.
        
        Args:
            playlist_url: YouTube playlist URL
            use_api: Whether to attempt API extraction (default: True)
            
        Returns:
            List of video dictionaries
            
        Raises:
            Exception: If extraction fails with all methods
        """
        api_key = resolve_youtube_api_key(self.config, self.config_file_path)
        
        # Method 1: Try YouTube API if key is available and user wants it
        if use_api and api_key:
            try:
                print("Attempting to extract playlist using YouTube Data API...")
                from youtube_api_extractor import YouTubeAPIExtractor
                
                api_extractor = YouTubeAPIExtractor(api_key)
                playlist_id = api_extractor.extract_playlist_id(playlist_url)
                
                # Get playlist info
                playlist_info = api_extractor.get_playlist_info(playlist_id)
                if playlist_info:
                    print(f"  Playlist: {playlist_info.get('title', 'Unknown')}")
                    print(f"  Videos: {playlist_info.get('video_count', 0)}")
                
                # Fetch videos with full descriptions
                videos = api_extractor.get_playlist_videos(
                    playlist_id,
                    include_descriptions=True
                )
                
                print(f"✓ Successfully extracted {len(videos)} videos via API")
                return videos
                
            except ImportError:
                print("⚠ YouTube API client not installed. Falling back to browser automation.")
                print("  To use API, install: pip install google-api-python-client")
            except Exception as e:
                print(f"⚠ API extraction failed: {e}")
                print("  Falling back to browser automation...")
        
        # Method 2: Browser automation fallback
        print("\nExtracting playlist using browser automation...")
        print("⚠ Note: This method doesn't provide video descriptions.")
        print("  For better quality, configure YouTube API key in config.json\n")
        
        # This would require browser automation implementation
        # For now, we'll raise an error to indicate it needs implementation
        raise NotImplementedError(
            "Browser automation fallback not yet implemented.\n"
            "Please set YOUTUBE_API_KEY (or PLAYLIST_INDEXER_YOUTUBE_API_KEY) or use --input-file method.\n"
            "\n"
            "To set up YouTube API:\n"
            "  1. Get API key from Google Cloud Console\n"
            "  2. Set environment variable: YOUTUBE_API_KEY=YOUR_KEY_HERE\n"
            "  3. Run: pip install google-api-python-client"
        )
    

    def generate_markdown(self, playlist_name: str) -> str:
        """Generate the markdown content for the playlist index."""
        md_content = f"# {playlist_name} Playlist Video Index\n\n"
        md_content += "This interactive document contains an index of all videos in the playlist with descriptions, hyperlinks, and tags.\n\n"
        
        # Table of Contents
        md_content += "## Table of Contents\n"
        for category in sorted(self.categories.keys()):
            anchor = category.lower().replace(' ', '-').replace('&', 'and')
            md_content += f"- [{category}](#{anchor})\n"
        md_content += "\n"
        
        # Video sections by category
        for category in sorted(self.categories.keys()):
            md_content += f"## {category}\n\n"
            
            for i, video in enumerate(self.categories[category], 1):
                md_content += f"{i}. [{video['title']}]({video['url']})  \n"
                md_content += f"   {video['description']}  \n"
                md_content += f"   {' '.join(video['tags'])}\n\n"
        
        # Tag Index
        md_content += "## Tag Index\n\n"
        md_content += "This section allows you to quickly find videos by their tags:\n\n"
        
        # Group tags by type
        tag_groups = {
            "Hardware Tags": [],
            "Audio Tags": [],
            "Project Tags": [],
            "Content Tags": []
        }
        
        for tag in sorted(self.tags):
            if any(hw in tag.lower() for hw in ['teensy', 'arduino', 'daisy', 'hardware', 'pcb', 'electronics']):
                tag_groups["Hardware Tags"].append(tag)
            elif any(audio in tag.lower() for audio in ['audio', 'midi', 'synth', 'dsp', 'filter']):
                tag_groups["Audio Tags"].append(tag)
            elif any(proj in tag.lower() for proj in ['diy', 'build', 'tutorial', 'guide']):
                tag_groups["Project Tags"].append(tag)
            else:
                tag_groups["Content Tags"].append(tag)
        
        for group_name, tags in tag_groups.items():
            if tags:
                md_content += f"### {group_name}\n"
                for tag in tags:
                    md_content += f"- {tag}\n"
                md_content += "\n"
        
        # Usage instructions
        md_content += self.get_usage_instructions()
        
        return md_content
    
    def get_usage_instructions(self) -> str:
        """Get the usage instructions section."""
        return """## How to Use This Document

### Navigation
1. Use the **Table of Contents** to browse videos by category
2. Use the **Tag Index** to find videos by specific tags
3. Use your browser's search function (Ctrl+F or Cmd+F) to search for specific keywords
4. Click on video titles to open them directly on YouTube

### Expanding This Document
This document is designed to be expandable. To add new videos:

1. **Add a new video entry** in the appropriate category section following this format:
   ```markdown
   [Video Title](YouTube URL)  
   Short one-sentence description of the video content.  
   #Tag1 #Tag2 #Tag3 #Tag4 #Tag5
   ```

2. **Update the Tag Index** if you add new tags that don't exist yet

3. **Create new categories** if needed by adding a new section

4. **Update the Table of Contents** to include any new categories

---

*This document was created using the YouTube Playlist Indexer automation script.*
"""
    
    def generate_html(self, markdown_content: str, playlist_name: str, color_scheme: str = "purple") -> str:
        """Generate HTML content from markdown with styling and interactivity."""
        md = MarkdownIt()
        html_body = md.render(markdown_content)
        
        color_schemes = {
            "purple": {"primary": "#7e57c2", "secondary": "#5e35b1", "bg": "#f3e5f5"},
            "teal": {"primary": "#00897b", "secondary": "#00695c", "bg": "#e0f2f1"},
            "blue": {"primary": "#1976d2", "secondary": "#1565c0", "bg": "#e3f2fd"},
            "green": {"primary": "#388e3c", "secondary": "#2e7d32", "bg": "#e8f5e9"}
        }
        
        colors = color_schemes.get(color_scheme, color_schemes["purple"])
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{playlist_name} Playlist Video Index</title>
    <style>
        {self.get_css_styles(colors)}
    </style>
</head>
<body>
{html_body}
<script>
{self.get_javascript()}
</script>
</body>
</html>"""
        
        return html_template
    
    def get_css_styles(self, colors: Dict[str, str]) -> str:
        """Get CSS styles with the specified color scheme."""
        return f"""
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        
        h1 {{
            color: {colors['primary']};
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 30px;
            border-bottom: 2px solid {colors['primary']};
            padding-bottom: 10px;
        }}
        
        h2 {{
            color: {colors['primary']};
            font-size: 1.8em;
            margin-top: 40px;
            border-left: 5px solid {colors['primary']};
            padding-left: 15px;
            background-color: {colors['bg']};
            padding: 10px 15px;
            border-radius: 0 5px 5px 0;
        }}
        
        h3 {{
            color: {colors['secondary']};
            font-size: 1.4em;
            margin-top: 30px;
        }}
        
        a {{
            color: {colors['primary']};
            text-decoration: none;
            transition: color 0.3s;
        }}
        
        a:hover {{
            color: {colors['secondary']};
            text-decoration: underline;
        }}
        
        .toggle-btn {{
            background: none;
            border: none;
            font-size: 1.2em;
            cursor: pointer;
            margin-right: 10px;
            color: {colors['primary']};
        }}
        
        #search-container {{
            margin: 20px 0;
            padding: 15px;
            background-color: {colors['bg']};
            border-radius: 5px;
        }}
        
        #search-box {{
            padding: 8px;
            width: 70%;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 16px;
        }}
        
        #search-btn {{
            padding: 8px 15px;
            background-color: {colors['primary']};
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-left: 10px;
        }}
        
        #back-to-top {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: {colors['primary']};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 15px;
            cursor: pointer;
            display: none;
            z-index: 1000;
        }}
        
        .highlight {{
            background-color: {colors['bg']};
            border-radius: 3px;
            padding: 2px 5px;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ background-color: {colors['bg']}; }}
            50% {{ background-color: {colors['secondary']}33; }}
            100% {{ background-color: {colors['bg']}; }}
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            h1 {{ font-size: 2em; }}
            h2 {{ font-size: 1.5em; }}
        }}
        """
    
    def get_javascript(self) -> str:
        """Get JavaScript for interactive functionality."""
        return """
        document.addEventListener('DOMContentLoaded', function() {
            // Add collapsible sections
            const headings = document.querySelectorAll('h2');
            
            headings.forEach(heading => {
                const toggleBtn = document.createElement('button');
                toggleBtn.innerHTML = '−';
                toggleBtn.className = 'toggle-btn';
                toggleBtn.setAttribute('aria-label', 'Toggle section');
                heading.prepend(toggleBtn);
                
                let content = [];
                let nextEl = heading.nextElementSibling;
                
                while (nextEl && !['H1', 'H2'].includes(nextEl.tagName)) {
                    content.push(nextEl);
                    nextEl = nextEl.nextElementSibling;
                }
                
                toggleBtn.addEventListener('click', () => {
                    content.forEach(el => {
                        el.style.display = el.style.display === 'none' ? '' : 'none';
                    });
                    toggleBtn.innerHTML = toggleBtn.innerHTML === '−' ? '+' : '−';
                });
            });
            
            // Add search functionality
            const searchBox = document.createElement('input');
            searchBox.type = 'text';
            searchBox.placeholder = 'Search videos...';
            searchBox.id = 'search-box';
            
            const searchBtn = document.createElement('button');
            searchBtn.textContent = 'Search';
            searchBtn.id = 'search-btn';
            
            const searchResults = document.createElement('div');
            searchResults.id = 'search-results';
            
            const searchContainer = document.createElement('div');
            searchContainer.id = 'search-container';
            searchContainer.appendChild(searchBox);
            searchContainer.appendChild(searchBtn);
            searchContainer.appendChild(searchResults);
            
            document.querySelector('h1').after(searchContainer);
            
            function performSearch() {
                const query = searchBox.value.toLowerCase();
                if (query.length < 2) {
                    searchResults.innerHTML = '';
                    return;
                }
                
                const videoEntries = document.querySelectorAll('p a');
                let results = [];
                
                videoEntries.forEach(entry => {
                    const title = entry.textContent.toLowerCase();
                    const description = entry.parentElement.nextElementSibling ? 
                                       entry.parentElement.nextElementSibling.textContent.toLowerCase() : '';
                    
                    if (title.includes(query) || description.includes(query)) {
                        results.push({
                            element: entry.parentElement,
                            title: entry.textContent
                        });
                    }
                });
                
                searchResults.innerHTML = '';
                if (results.length === 0) {
                    searchResults.innerHTML = '<p>No results found</p>';
                } else {
                    const resultsList = document.createElement('ul');
                    results.forEach(result => {
                        const li = document.createElement('li');
                        const link = document.createElement('a');
                        link.href = '#';
                        link.textContent = result.title;
                        link.addEventListener('click', (e) => {
                            e.preventDefault();
                            result.element.scrollIntoView({ behavior: 'smooth' });
                            result.element.classList.add('highlight');
                            setTimeout(() => {
                                result.element.classList.remove('highlight');
                            }, 2000);
                        });
                        li.appendChild(link);
                        resultsList.appendChild(li);
                    });
                    searchResults.appendChild(resultsList);
                }
            }
            
            searchBtn.addEventListener('click', performSearch);
            searchBox.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    performSearch();
                }
            });
            
            // Add "Back to Top" button
            const backToTopBtn = document.createElement('button');
            backToTopBtn.textContent = '↑ Top';
            backToTopBtn.id = 'back-to-top';
            backToTopBtn.addEventListener('click', () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
            document.body.appendChild(backToTopBtn);
            
            window.addEventListener('scroll', () => {
                if (window.scrollY > 300) {
                    backToTopBtn.style.display = 'block';
                } else {
                    backToTopBtn.style.display = 'none';
                }
            });
        });
        """
    
    def create_output_directory(self, playlist_name: str) -> str:
        """Create output directory for the playlist."""
        safe_name = re.sub(r'[^\w\s-]', '', playlist_name).strip()
        safe_name = re.sub(r'[-\s]+', '_', safe_name).lower()
        
        output_base = self.config['output_dir']
        
        # If output_dir is relative, make it relative to the config file (app root)
        if not os.path.isabs(output_base):
            output_base = os.path.join(os.path.dirname(self.config_file_path), output_base)
            
        output_dir = os.path.join(output_base, safe_name)
        os.makedirs(output_dir, exist_ok=True)
        
        return output_dir
    
    def generate_files(self, playlist_name: str, playlist_data: List[Dict[str, str]]) -> str:
        """Generate all output files for the playlist."""
        # Process the playlist data
        self.process_playlist_data(playlist_data)
        
        # Create output directory
        output_dir = self.create_output_directory(playlist_name)
        
        # Generate markdown content
        markdown_content = self.generate_markdown(playlist_name)
        
        # Write markdown file
        md_file = os.path.join(output_dir, f"{playlist_name.lower().replace(' ', '_')}_index.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        generated_files = [md_file]
        
        # Generate HTML if requested
        if self.config.get('generate_html', True):
            html_content = self.generate_html(
                markdown_content, 
                playlist_name, 
                self.config.get('color_scheme', 'purple')
            )
            html_file = os.path.join(output_dir, f"{playlist_name.lower().replace(' ', '_')}_index.html")
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            generated_files.append(html_file)
        
        # Generate PDF if requested
        if self.config.get('generate_pdf', True):
            pdf_file = os.path.join(output_dir, f"{playlist_name.lower().replace(' ', '_')}_index.pdf")
            try:
                os.system(f"manus-md-to-pdf '{md_file}' '{pdf_file}'")
                if os.path.exists(pdf_file):
                    generated_files.append(pdf_file)
            except Exception as e:
                print(f"Warning: Could not generate PDF: {e}")
        
        return output_dir, generated_files


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='YouTube Playlist Indexer',
        epilog='Examples:\n'
               '  # Direct URL (with API):\n'
               '  python playlist_indexer.py --playlist-url "https://youtube.com/playlist?list=..." --name "MyPlaylist"\n\n'
               '  # Legacy JSON file method:\n'
               '  python playlist_indexer.py --playlist-name "MyPlaylist" --input-file data.json\n',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Method 1: Direct URL input (NEW)
    parser.add_argument('--playlist-url', 
                       help='YouTube playlist URL (automatically extracts video data)')
    parser.add_argument('--name', 
                       help='Playlist name (required when using --playlist-url)')
    
    # Method 2: JSON file input (LEGACY)
    parser.add_argument('--playlist-name', 
                       help='Name of the playlist (legacy method)')
    parser.add_argument('--input-file', 
                       help='JSON file with playlist data (legacy method)')
    
    # Common options
    parser.add_argument('--config', default='config.json', 
                       help='Configuration file (default: config.json)')
    parser.add_argument('--color-scheme', 
                       choices=['purple', 'teal', 'blue', 'green'], 
                       help='Color scheme for HTML output')
    parser.add_argument('--no-api', action='store_true',
                       help='Skip YouTube API and use browser automation (when using --playlist-url)')
    
    args = parser.parse_args()
    
    # Initialize indexer
    indexer = PlaylistIndexer(args.config)
    
    # Override color scheme if specified
    if args.color_scheme:
        indexer.config['color_scheme'] = args.color_scheme
    
    # Determine which method to use
    if args.playlist_url:
        # Method 1: Direct URL extraction
        if not args.name:
            print("Error: --name is required when using --playlist-url")
            return 1
        
        playlist_name = args.name
        
        # Try to extract data from YouTube
        try:
            playlist_data = indexer.extract_from_youtube_url(
                args.playlist_url, 
                use_api=not args.no_api
            )
            
            if not playlist_data:
                print("Error: No videos found in playlist")
                return 1
                
        except Exception as e:
            print(f"Error extracting playlist data: {e}")
            return 1
            
    elif args.playlist_name and args.input_file:
        # Method 2: Legacy JSON file input
        playlist_name = args.playlist_name
        
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                playlist_data = json.load(f)
        except Exception as e:
            print(f"Error loading playlist data: {e}")
            return 1
    else:
        print("Error: Must provide either:")
        print("  1. --playlist-url and --name, OR")
        print("  2. --playlist-name and --input-file")
        parser.print_help()
        return 1
    
    # Generate files
    try:
        output_dir, generated_files = indexer.generate_files(playlist_name, playlist_data)
        
        print(f"\n✓ Successfully generated playlist index for '{playlist_name}'")
        print(f"  Output directory: {output_dir}")
        print(f"  Generated files:")
        for file in generated_files:
            print(f"    - {file}")
        
        return 0
    except Exception as e:
        print(f"Error generating files: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
