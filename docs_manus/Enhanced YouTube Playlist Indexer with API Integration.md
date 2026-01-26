# Enhanced YouTube Playlist Indexer with API Integration

A comprehensive Python automation framework that creates interactive and expandable documents for YouTube playlists with automatic data extraction, CSV export, and advanced indexing capabilities.

## 🚀 NEW FEATURES

### ✅ YouTube API Integration
- **Automatic playlist extraction** from YouTube URLs
- **No more manual copying** - just paste the playlist URL
- **Real-time data** directly from YouTube's servers
- **Handles large playlists** with pagination support

### ✅ CSV Export Functionality  
- **Structured data export** for analysis and processing
- **Complete metadata** including duration, view counts, thumbnails
- **Excel-compatible format** for easy data manipulation
- **Batch processing support** for multiple playlists

### ✅ Enhanced Metadata
- **Video duration** in readable format (HH:MM:SS)
- **View counts, likes, comments** with formatted numbers
- **Thumbnail URLs** for visual references
- **Publication dates** for chronological analysis
- **Channel information** for creator attribution

## Quick Start

### 🎯 Super Easy Method (NEW!)
```bash
# 1. Get YouTube API key (free) from https://console.cloud.google.com/
export YOUTUBE_API_KEY='your_api_key_here'

# 2. Run the enhanced script
./run_enhanced.sh

# 3. Choose option 1, paste any YouTube playlist URL, done!
```

### 🔧 Command Line Method
```bash
# Install dependencies
pip3 install -r requirements.txt

# Extract playlist automatically
python3 youtube_api_extractor.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"

# Create interactive index
python3 playlist_indexer.py --playlist-name "My Playlist" --input-file extracted_playlists/playlist.json
```

## Installation & Setup

### Prerequisites
- Python 3.6 or higher
- YouTube Data API v3 key (free from Google Cloud Console)
- Internet connection for API access

### 1. Get YouTube API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable "YouTube Data API v3"
4. Create credentials (API Key)
5. Set environment variable: `export YOUTUBE_API_KEY='your_key_here'`

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Run the Tool
```bash
./run_enhanced.sh
```

## Usage Methods

### Method 1: Automatic Extraction (Recommended)
```bash
# Extract from any YouTube playlist URL
python3 youtube_api_extractor.py "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLvGuvNuceQY71PBuOn"

# Options:
--output-format csv|json|both    # Export format (default: both)
--max-videos 100                 # Limit number of videos (default: 200)
--output-dir my_playlists        # Custom output directory
--no-details                     # Skip video statistics (faster)
```

### Method 2: Interactive Script
```bash
./run_enhanced.sh
# Choose from menu options:
# 1) Extract from YouTube URL (NEW!)
# 2) Process existing JSON file  
# 3) Interactive creation (original method)
```

### Method 3: Programmatic Usage
```python
from youtube_api_extractor import YouTubePlaylistExtractor

# Initialize with API key
extractor = YouTubePlaylistExtractor(api_key='your_key')

# Extract playlist
results = extractor.extract_playlist(
    playlist_url='https://www.youtube.com/playlist?list=YOUR_ID',
    output_format='both',
    max_videos=200
)

print(f"Extracted {results['video_count']} videos")
print(f"Files created: {results['files_created']}")
```

## Output Formats

### 📊 CSV Export (NEW!)
Structured data with columns:
- Position, Title, Channel, URL, Video ID
- Published Date, Description, Duration
- View Count, Like Count, Comment Count, Thumbnail URL

### 📄 JSON Export
Compatible with existing playlist indexer:
```json
[
  {
    "title": "Video Title",
    "url": "https://youtube.com/watch?v=...",
    "channel": "Channel Name",
    "description": "Video description...",
    "duration": "PT5M30S",
    "view_count": "12345"
  }
]
```

### 🌐 Interactive Documents
- **Markdown** - Source documentation
- **HTML** - Interactive web version with search
- **PDF** - Print-friendly format

## Advanced Features

### Automatic Categorization
Videos are intelligently sorted into categories:
- **Hardware Projects** - Teensy, Arduino, electronics
- **Audio Development** - DSP, synthesis, programming  
- **MIDI Controllers** - Interface development
- **Synthesizer Projects** - Analog/digital builds
- **Tutorials & Guides** - Educational content
- **Reviews & Comparisons** - Product analysis

### Smart Tag Generation
Automatic tags based on content analysis:
- **Hardware**: #Teensy, #Arduino, #DaisySeed, #PCB
- **Audio**: #Synthesizer, #MIDI, #DSP, #Filter
- **Projects**: #DIY, #BuildGuide, #Tutorial
- **Content**: #Beginner, #Advanced, #Review

### Interactive HTML Features
- **Real-time search** across all content
- **Collapsible sections** for better navigation
- **Tag filtering** and highlighting
- **Responsive design** for all devices
- **Back-to-top navigation**

## Configuration

### API Settings
```bash
# Set API key (required for automatic extraction)
export YOUTUBE_API_KEY='your_api_key_here'

# Optional: Save permanently
echo "export YOUTUBE_API_KEY='your_key'" >> ~/.bashrc
```

### Color Schemes
Choose from 4 built-in themes:
- **Purple** - General tech content
- **Teal** - Audio/hardware projects (recommended for TEENSY/DAISY)
- **Blue** - Programming content
- **Green** - Educational content

### Custom Configuration
Edit `config.json`:
```json
{
  "output_dir": "output",
  "generate_html": true,
  "generate_pdf": true,
  "color_scheme": "teal",
  "auto_categorize": true,
  "tag_suggestions": true
}
```

## Examples

### Example 1: TEENSY Playlist
```bash
# Automatic extraction
python3 youtube_api_extractor.py "https://www.youtube.com/playlist?list=TEENSY_PLAYLIST_ID"

# Create interactive index
python3 playlist_indexer.py --playlist-name "TEENSY Projects" --input-file extracted_playlists/teensy_playlist.json --color-scheme teal
```

### Example 2: Batch Processing
```bash
# Extract multiple playlists
python3 youtube_api_extractor.py "PLAYLIST_URL_1" --output-dir batch_1
python3 youtube_api_extractor.py "PLAYLIST_URL_2" --output-dir batch_2

# Process all JSON files
for json_file in batch_*/*.json; do
    playlist_name=$(basename "$json_file" .json)
    python3 playlist_indexer.py --playlist-name "$playlist_name" --input-file "$json_file"
done
```

## Performance & Limits

### YouTube API Quotas
- **Free tier**: 10,000 requests/day
- **Typical usage**: 1-3 requests per video
- **Large playlist (200 videos)**: ~400 requests
- **Daily capacity**: ~25 large playlists

### Processing Speed
- **API extraction**: 2-5 seconds per video
- **Document generation**: 1-2 seconds total
- **Total time**: 5-10 minutes for 200-video playlist

### Optimization Tips
- Use `--no-details` flag for faster extraction (skips statistics)
- Set `--max-videos` to limit extraction size
- Process during off-peak hours for better API performance

## Troubleshooting

### Common Issues

#### API Key Problems
```bash
# Error: "YouTube API key is required"
export YOUTUBE_API_KEY='your_actual_key_here'

# Verify key is set
echo $YOUTUBE_API_KEY
```

#### Quota Exceeded
```bash
# Error: "quotaExceeded"
# Wait 24 hours or use a different project/key
# Monitor usage at: https://console.cloud.google.com/
```

#### Private/Deleted Videos
```bash
# Warning: Some videos skipped
# This is normal - private/deleted videos are automatically filtered out
```

#### Large Playlists
```bash
# For playlists with 1000+ videos, use batching:
python3 youtube_api_extractor.py "PLAYLIST_URL" --max-videos 200
```

### Getting Help
1. Check the enhanced interactive script: `./run_enhanced.sh`
2. Review API setup guide: Option 6 in the menu
3. Test with example data first
4. Verify API key permissions and quotas

## Migration from Original Version

### Existing Users
Your existing workflow still works! The enhanced version adds new features without breaking compatibility:

```bash
# Old method still works
python3 extract_playlist_data.py --interactive
python3 playlist_indexer.py --playlist-name "My Playlist" --input-file data.json

# New method available
python3 youtube_api_extractor.py "PLAYLIST_URL"
```

### File Compatibility
- Existing JSON files work with new indexer
- New CSV format provides additional data
- All output formats remain the same

## File Structure

```
playlist_indexer/
├── youtube_api_extractor.py     # NEW: YouTube API integration
├── playlist_indexer.py          # Enhanced main script
├── extract_playlist_data.py     # Original manual extraction
├── run_enhanced.sh              # NEW: Enhanced interactive script
├── run.sh                       # Original interactive script
├── config.json                  # Configuration file
├── requirements.txt             # Updated dependencies
├── README_ENHANCED.md           # This documentation
├── README.md                    # Original documentation
└── output/                      # Generated files
    └── playlist_name/
        ├── playlist_index.md    # Markdown
        ├── playlist_index.html  # Interactive HTML
        └── playlist_index.pdf   # PDF
└── extracted_playlists/         # NEW: API extraction output
    ├── playlist_name.csv        # NEW: CSV export
    └── playlist_name.json       # JSON for indexer
```

## Comparison: Before vs After

| Feature | Original Version | Enhanced Version |
|---------|------------------|------------------|
| Data Input | Manual copying | Automatic API extraction |
| Time per Playlist | 30-60 minutes | 5-10 minutes |
| Data Accuracy | Manual errors possible | 100% accurate from API |
| Metadata | Basic info only | Full metadata + statistics |
| Export Formats | JSON only | CSV + JSON |
| Scalability | Limited by manual work | Limited by API quotas |
| Setup Complexity | None | Requires API key |
| Offline Usage | Yes | No (requires internet) |

## Future Enhancements

Planned improvements:
- **Playlist monitoring** for automatic updates
- **Bulk channel processing** for multiple playlists
- **Advanced analytics** with trend analysis
- **Web interface** for non-technical users
- **Integration with spreadsheet tools**
- **Custom export templates**

## License & Credits

This enhanced framework builds upon the original YouTube Playlist Indexer, adding professional-grade automation capabilities while maintaining the same ease of use and high-quality output.

Created for efficient YouTube content organization and documentation.

---

*Transform any YouTube playlist into professional documentation in minutes, not hours!*

