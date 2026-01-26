# Playlist Indexer - Functionality & Architecture

## 1. System Overview
The **Playlist Indexer** is a Python-based web application that serves as a personal video knowledge management system. It extracts metadata from YouTube playlists, stores it locally, and provides tools for analysis, search, and visualization.

### Core Architecture
-   **Backend**: Python (Flask)
-   **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (Vanilla + D3.js)
-   **Data Storage**: JSON (Local filesystem)
-   **External APIs**: YouTube Data API v3

## 2. Key Functional Modules

### A. The Indexer Engine (`playlist_indexer.py`)
This module handles the extraction of data from YouTube.
-   **Input**: YouTube Playlist URL.
-   **Process**:
    1.  Validates API Key (Environment Variable).
    2.  Iterates through playlist pages (paginated API calls).
    3.  Extracts: Video Title, ID, Channel Name, Description, Tags, Publish Date, Duration, Thumbnail URLs.
    4.  **Duration Parsing**: Converts ISO 8601 duration (e.g., `PT1H2M10S`) to readable format (`01:02:10`) and total seconds.
-   **Output**: Saves standardized JSON files in the `output/` directory.

### B. The Web Application (`web_app.py`)
Acts as the central controller and API server.
-   **Routes**:
    -   `/`: Serves the main SPA interface.
    -   `/api/index_playlist`: Trigger for the Indexer Engine.
    -   `/api/playlists`: Returns list of all indexed JSON files.
    -   `/api/playlists/<name>`: Returns content of a specific playlist.
    -   `/api/mindmap_data`: **Critical** - Generates the node-edge structure for the Mind Map.
-   **Search Logic**: Implements server-side filtering across all loaded JSON files.

### C. Mind Map Generator (`execution/graph_generator.py`)
Responsible for creating the "Knowledge Graph".
-   **Node Generation**:
    -   **Video Nodes**: Represent individual videos.
    -   **Tag Nodes**: Represent keywords (e.g., "Python", "Music").
    -   **Channel Nodes**: Represent content creators.
-   **Edge Generation**:
    -   Connects `Video -> Tag` (weighted by tag relevance).
    -   Connects `Video -> Channel`.
    -   Connects `Video -> Video` (if they share significant tags).
-   **Clustering**: Uses algorithms (like Louvain) to group related content visually.

### D. Data Management
-   **Storage**: Flat JSON files. No SQL database required, ensuring portability.
-   **Backup**: User can simply copy the `output/` folder.
-   **Export**: Features to export playlist data to Excel (`.xlsx`) via frontend JS generation.

## 3. Data Flow

1.  **User Action**: Enters Playlist URL -> `POST /api/index_playlist`.
2.  **Backend**: Calls YouTube API -> Indexes 50-500+ videos.
3.  **Storage**: Writes `[Playlist Name].json` to `output/`.
4.  **Frontend**: Auto-refreshes "Playlists" and "Gallery" tabs.
5.  **Visualization**: User clicks "Mind Map" -> `GET /api/mindmap_data` reads all JSONs -> Builds Graph -> D3.js renders it.

## 4. Future Functional Goals (Brainstorming)

### A. Transcript Indexing
-   **Goal**: Search *within* videos.
-   **Method**: Use YouTube Transcript API to download captions.
-   **Storage**: SQLite (upgrade from JSON required for indexed text search).

### B. "Smart Auto-Tagging"
-   **Goal**: Improve categorization for videos with poor metadata.
-   **Method**: Use a local LLM (e.g., Ollama key) to analyze video Titles/Descriptions and generate standardized tags (e.g., "Educational", "Entertainment", "Tutorial").

### C. Multi-Platform Support
-   **Goal**: Index content from other sources.
-   **Scope**: Vimeo, DailyMotion, or local video files.

### D. Automated Sync
-   **Goal**: Keep indexed playlists up-to-date.
-   **Logic**: Background cron job that checks indexed playlists for new videos every 24 hours.
