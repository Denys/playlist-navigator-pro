# Playlist Navigator Pro

A Python automation script that creates interactive and expandable documents for YouTube playlists with descriptions, hyperlinks, and tags.

## Features

- **Automatic categorization** of videos based on content analysis
- **Smart tag generation** from video titles and descriptions
- **Multiple output formats**: Markdown, HTML, and PDF
- **Interactive HTML** with search functionality and collapsible sections
- **Configurable color schemes** for different content types
- **Template-based approach** for easy customization
- **Expandable documents** with clear instructions for adding new content

## Quick Start

1. **Prepare your playlist data** in JSON format:
   ```json
   [
     {
       "title": "Video Title",
       "url": "https://www.youtube.com/watch?v=VIDEO_ID",
       "channel": "Channel Name"
     }
   ]
   ```

2. **Run the indexer**:
   ```bash
   python3 playlist_indexer.py --playlist-name "My Playlist" --input-file my_playlist.json
   ```

3. **Find your generated files** in the `output/` directory

## Installation

### Prerequisites

- Python 3.6 or higher
- `markdown` library for HTML generation
- `manus-md-to-pdf` utility for PDF generation (pre-installed in sandbox)

### Install Python dependencies

```bash
pip3 install markdown
```

## Usage

### Basic Usage

```bash
python3 playlist_indexer.py --playlist-name "TEENSY Projects" --input-file teensy_videos.json
```

### Advanced Usage

```bash
python3 playlist_indexer.py \
  --playlist-name "Audio Development" \
  --input-file audio_videos.json \
  --color-scheme teal \
  --config custom_config.json
```

### Command Line Options

- `--playlist-name`: Name of the playlist (required)
- `--input-file`: JSON file with video data (required)
- `--config`: Configuration file (default: config.json)
- `--color-scheme`: Color scheme for HTML output (purple, teal, blue, green)

## Getting Playlist Data

### Method 1: Manual Entry Helper

Use the included helper script for interactive data entry:

```bash
python3 extract_playlist_data.py --interactive --output my_playlist.json
```

### Method 2: Copy-Paste from YouTube

1. Go to your YouTube playlist
2. Copy the video titles and channel names
3. Use the extraction helper:

```bash
python3 extract_playlist_data.py --input-file copied_content.txt --output my_playlist.json
```

### Method 3: Manual JSON Creation

Create a JSON file with this structure:

```json
[
  {
    "title": "Build a Teensy Stand-Alone Filter for Synths",
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "channel": "Notes and Volts"
  }
]
```

## Configuration

The `config.json` file allows you to customize the behavior:

```json
{
  "output_dir": "output",
  "generate_html": true,
  "generate_pdf": true,
  "color_scheme": "purple",
  "auto_categorize": true,
  "tag_suggestions": true
}
```

### Color Schemes

- **Purple**: Good for general tech content
- **Teal**: Good for audio/hardware content  
- **Blue**: Good for programming content
- **Green**: Good for educational content

## Output Files

For each playlist, the script generates:

1. **Markdown file** (`.md`) - Source document with all content
2. **HTML file** (`.html`) - Interactive web version with search and navigation
3. **PDF file** (`.pdf`) - Print-friendly version

### HTML Features

- **Search functionality**: Find videos by title, description, or tags
- **Collapsible sections**: Click +/- to expand/collapse categories
- **Responsive design**: Works on desktop and mobile
- **Back to top button**: Easy navigation
- **Tag highlighting**: Visual feedback for searches

## Automatic Features

### Video Categorization

Videos are automatically sorted into categories:

- **Hardware Projects**: Teensy, Arduino, DIY builds
- **Audio Development**: DSP, audio libraries, programming
- **Synthesizer Projects**: Synth builds, oscillators, filters
- **MIDI Controllers**: MIDI interfaces and controllers
- **Tutorials and Guides**: Educational content
- **Reviews and Comparisons**: Product reviews and comparisons
- **Live Sessions**: Workshops and live streams
- **Advanced Techniques**: Expert-level content

### Tag Generation

Tags are automatically generated based on content:

- **Hardware tags**: #Teensy, #Arduino, #DaisySeed, #Hardware
- **Audio tags**: #Synthesizer, #MIDI, #Audio, #DSP, #Filter
- **Project tags**: #DIY, #BuildGuide, #Tutorial, #Workshop
- **Content tags**: #Beginner, #Advanced, #Review, #Demo

## Examples

### Example 1: TEENSY Playlist

```bash
# Create playlist data
python3 extract_playlist_data.py --interactive --output teensy_videos.json

# Generate index with teal color scheme
python3 playlist_indexer.py \
  --playlist-name "TEENSY Projects" \
  --input-file teensy_videos.json \
  --color-scheme teal
```

### Example 2: MIDI Controllers

```bash
# Generate index with blue color scheme
python3 playlist_indexer.py \
  --playlist-name "MIDI Controllers" \
  --input-file midi_videos.json \
  --color-scheme blue
```

## Customization

### Adding New Categories

Edit the `categorize_video()` method in `playlist_indexer.py`:

```python
categories = {
    "Your New Category": ["keyword1", "keyword2", "keyword3"],
    # ... existing categories
}
```

### Adding New Tags

Edit the `generate_tags()` method to include new tag patterns:

```python
your_tags = {
    'keyword': '#YourTag',
    # ... existing tags
}
```

### Custom Color Schemes

Add new color schemes to `config.json`:

```json
{
  "color_schemes": {
    "your_scheme": {
      "primary": "#your_color",
      "secondary": "#your_secondary",
      "background": "#your_background"
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **"No module named 'markdown'"**
   ```bash
   pip3 install markdown
   ```

2. **PDF generation fails**
   - Ensure `manus-md-to-pdf` is available
   - Check file permissions in output directory

3. **Empty or incorrect categorization**
   - Check your video titles for recognizable keywords
   - Customize the categorization rules in the script

4. **HTML not displaying correctly**
   - Ensure all files (HTML, CSS, JS) are in the same directory
   - Check browser console for JavaScript errors

### Getting Help

1. Check the example files in the repository
2. Review the configuration options
3. Test with the provided example data first
4. Ensure your input JSON format matches the expected structure

## File Structure

```
playlist_indexer/
├── playlist_indexer.py          # Main script
├── extract_playlist_data.py     # Data extraction helper
├── config.json                  # Configuration file
├── example_playlist_data.json   # Example input data
├── README.md                    # This documentation
├── requirements.txt             # Python dependencies
└── output/                      # Generated files directory
    └── playlist_name/
        ├── playlist_index.md    # Markdown output
        ├── playlist_index.html  # HTML output
        └── playlist_index.pdf   # PDF output
```

## License

This script is provided as-is for educational and personal use. Feel free to modify and adapt it for your needs.

---

*Created as part of the Playlist Navigator Pro project for organizing and indexing video content.*

