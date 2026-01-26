# Directive: YouTube Playlist Indexing Workflow

## Purpose
Index a YouTube playlist to create searchable, categorized documentation with multiple output formats.

## Inputs
- **Required**: YouTube playlist URL OR JSON file with video data
- **Optional**: Playlist name, color scheme (purple/teal/blue/green)

## Tools/Scripts
- `playlist_indexer.py` - Main indexing script
- `youtube_api_extractor.py` - YouTube API integration
- `web_app.py` - Web interface (alternative to CLI)

## Workflow

### Option A: Web Interface (Recommended)
1. Start server: `python web_app.py`
2. Open http://localhost:5000
3. Go to "YouTube Indexer" tab
4. Paste playlist URL, enter name, select color scheme
5. Click "Start Indexing"
6. Wait for progress to complete
7. Find files in `output/{playlist_name}/`

### Option B: Command Line
```bash
python playlist_indexer.py \
  --playlist-name "My Playlist" \
  --playlist-url "https://www.youtube.com/playlist?list=PLxxx..."
```

### Option C: Local JSON Data
```bash
python playlist_indexer.py \
  --playlist-name "My Playlist" \
  --input-file my_videos.json
```

## Outputs
- `{name}_index.md` - Markdown source
- `{name}_index.html` - Interactive HTML with search
- `{name}_index.pdf` - Print-friendly PDF
- `{name}_data.json` - Raw video data for API

## Edge Cases

### API Quota Exceeded
- YouTube API has 10,000 units/day limit
- ~100 units per 100-video playlist
- Wait 24 hours for quota reset (midnight Pacific)
- Or use your own API key in `.env`

### Private/Deleted Videos
- Script skips unavailable videos
- Check logs for skipped count

### Large Playlists (500+ videos)
- May take 5-10 minutes
- Progress shown in web UI
- Consider splitting into multiple smaller playlists

## Learnings
- *Add discoveries here as you encounter edge cases*
