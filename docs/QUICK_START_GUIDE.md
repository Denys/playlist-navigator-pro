# 🚀 Quick Start Guide

**Playlist Navigator Pro** - Index and search YouTube playlists with ease!

---

## ⚡ 3-Minute Setup

### 🚀 Option A: Standalone Executable (Windows) - No Setup Required!

1.  **Locate the Folder**: Go to `dist/PlaylistIndexer/`.
2.  **Run**: Double-click `PlaylistIndexer.exe` inside that folder.
3.  **Browse**: Open `http://localhost:5000` in your web browser.

*That's it! No Python installation required. Startup is instant.*

---

### 🐍 Option B: Python Setup (Developers/Mac/Linux)

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

**What gets installed:**
- `markdown-it-py` - For generating HTML/PDF outputs
- `google-api-python-client` - YouTube API integration
- `flask` - Web application framework

### 2. Configure YouTube API Key

**Get your API key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable "YouTube Data API v3"
3. Create credentials → API Key
4. Copy your key

**Set environment variable:**

Create a local `.env` file or set the variable in your shell:

```bash
YOUTUBE_API_KEY=YOUR_API_KEY_HERE
```

> **Note**: Do not commit API keys into `config.json` or source files.

---

## 🌐 Method 1: Web Application (Recommended)

### Start the Server

```bash
python web_app.py
```

### Open Your Browser

Navigate to: **http://localhost:5000**

### Use the Interface

The web app has **3 tabs**:

#### 📥 Tab 1: YouTube Indexer
1. Paste a YouTube playlist URL
2. Enter a name for the playlist
3. Choose a color scheme (purple/teal/blue/green)
4. Click **"Start Indexing"**
5. Watch real-time progress with quota tracking

#### 🔍 Tab 2: Master Search
- Search across **all indexed playlists**
- Filter by playlist, category, or keywords
- Click video titles to open in YouTube
- See thumbnails, channels, and tags

#### 📚 Tab 3: Indexed Playlists
- Browse all your indexed playlists
- View playlist metadata (video count, creation date)
- Click playlist cards to explore individual videos
- Scroll through video lists with thumbnails

---

## 💻 Method 2: Command Line (Advanced)

### Quick Index a Playlist

```bash
python playlist_indexer.py \
  --playlist-name "My Awesome Playlist" \
  --playlist-url "https://www.youtube.com/playlist?list=PLxxx..."
```

### With Custom Color Scheme

```bash
python playlist_indexer.py \
  --playlist-name "Power Electronics Tutorials" \
  --playlist-url "https://www.youtube.com/playlist?list=PLxxx..." \
  --color-scheme teal
```

### Using Local JSON Data

```bash
# If you already have video data
python playlist_indexer.py \
  --playlist-name "TEENSY Projects" \
  --input-file my_videos.json
```

**JSON format:**
```json
[
  {
    "title": "Video Title",
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "channel": "Channel Name",
    "description": "Video description..."
  }
]
```

---

## 📂 Output Files

After indexing, find your files in `output/your_playlist_name/`:

| File | Description |
|------|-------------|
| `*.md` | Markdown source with all content |
| `*.html` | Interactive web page with search |
| `*.pdf` | Print-friendly PDF version |
| `*_data.json` | Raw video data for search API |

---

## 🎨 Color Schemes

Choose the right theme for your content:

- **Purple** - General tech content (default)
- **Teal** - Audio/hardware projects
- **Blue** - Programming tutorials
- **Green** - Educational content

---

## 📊 YouTube API Quota

**Daily Quota**: 10,000 units per day (free tier)

**Cost per operation:**
- Playlist metadata: ~3 units
- Per video: ~1 unit

**Example**: A 100-video playlist = ~103 units (~1% of daily quota)

> **Tip**: The web app shows real-time quota tracking!

---

## 🛠️ Troubleshooting

### "No module named 'markdown'"

```bash
pip install markdown-it-py
```

### "API Key Invalid"

1. Check your API key in `config.json`
2. Ensure YouTube Data API v3 is enabled in Google Cloud Console
3. Verify there are no extra spaces in the key

### "Quota Exceeded"

- Wait 24 hours for quota reset (midnight Pacific Time)
- Use your own API key instead of the demo key
- Index smaller playlists or fewer playlists per day

### Web App Won't Start

```bash
# Make sure Flask is installed
pip install flask

# Try a different port if 5000 is busy
python web_app.py --port 8080
```

---

## 📖 Next Steps

**For Web Users:**
1. Index your first playlist
2. Try the Master Search with keywords
3. Explore the Indexed Playlists tab
4. Export HTML files for offline use

**For CLI Users:**
1. Read the full [README.md](README.md) for advanced options
2. Customize categories in `playlist_indexer.py`
3. Create workflows with the output JSON data
4. Integrate with your own tools/scripts

**For Developers:**
- Check [MINDMAP_DEV_LOG.md](MINDMAP_DEV_LOG.md) for upcoming Mind Map feature
- See [PACKAGE_SUMMARY.md](PACKAGE_SUMMARY.md) for architecture overview

---

## 🎯 Common Use Cases

### Use Case 1: Personal Learning Library
Index your saved "Watch Later" or educational playlists, then search them instantly by topic.

### Use Case 2: Content Research
Index competitor channels or industry playlists to analyze trends and gaps.

### Use Case 3: Team Knowledge Base
Index tutorial playlists for your team, generate searchable HTML pages for internal wikis.

### Use Case 4: Offline Archive
Generate PDFs of important playlists before they're deleted or made private.

---

## 💡 Pro Tips

- **Batch indexing**: Use the CLI with a shell script to index multiple playlists
- **Custom tags**: Edit video JSON files to add your own tags before indexing
- **Backup data**: Keep the `output/` folder - it contains all your indexed data
- **Share results**: The HTML files are standalone - just send them to colleagues!

---

**Need more help?** Check the full [README.md](README.md) or open an issue on GitHub.

**Ready to index?** Fire up the web app with `python web_app.py` and get started! 🚀
