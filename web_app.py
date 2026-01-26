#!/usr/bin/env python3
"""
Unified Playlist Manager Web Application
Combines YouTube Playlist Indexer and Master Search in one tabbed interface.
"""

from flask import Flask, render_template, request, jsonify, Response
from threading import Thread
import datetime # Added to fix datetime.datetime.utcnow()
import uuid
import time
import os
import json
from io import BytesIO # Added as per instruction
from typing import List, Dict, Union
from playlist_indexer import PlaylistIndexer
from execution.metadata_enricher import MetadataEnricher
from execution.delta_sync import DeltaSync
from execution.tag_manager import TagManager
from execution.video_store_api import VideoStoreAPI
from execution.utils import check_duplicate_playlist
from execution.models import VideoData


app = Flask(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON Encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder # For Flask < 2.2 compatibility (optional but good)

# Job tracking for indexing
jobs = {}
enricher = MetadataEnricher()
delta_sync = DeltaSync(enricher)
tag_manager = TagManager()
store_api = VideoStoreAPI()




class IndexingJob:
    """Track indexing job progress."""
    def __init__(self, job_id, playlist_url, name, color_scheme):
        self.job_id = job_id
        self.playlist_url = playlist_url
        self.name = name
        self.color_scheme = color_scheme
        self.status = "queued"
        self.progress = 0
        self.message = "Waiting to start..."
        self.result = None
        self.error = None
        self.quota_used = 0


@app.route('/')
def index():
    """Serve the unified interface."""
    return render_template('index.html')


@app.route('/api/index', methods=['POST'])
def start_indexing():
    """Start a new indexing job."""
    data = request.json
    
    if not data.get('playlist_url') or not data.get('name'):
        return jsonify({'error': 'Missing playlist_url or name'}), 400
        
    # Check for duplicates if mode is not explicit overwrite
    mode = data.get('mode', 'new')
    if mode == 'new':
        dup_check = check_duplicate_playlist(data['playlist_url'])
        if dup_check['is_duplicate']:
            return jsonify({
                'error': 'Duplicate playlist detected',
                'is_duplicate': True,
                'existing_playlist': dup_check['existing_playlist']
            }), 409
    
    job_id = str(uuid.uuid4())[:8]
    job = IndexingJob(
        job_id,
        data['playlist_url'],
        data['name'],
        data.get('color_scheme', 'purple')
    )
    job.mode = mode # Store mode
    
    jobs[job_id] = job
    
    # Start processing in background
    thread = Thread(target=process_indexing_job, args=(job,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'job_id': job_id, 'status': 'processing'})

@app.route('/api/sync/delta/<playlist_id>', methods=['POST'])
def delta_sync_playlist(playlist_id):
    """
    Trigger a delta sync for modification mode.
    Compares existing local data with current YouTube state and applies delta.
    """
    data = request.json
    playlist_url = data.get('playlist_url')
    
    if not playlist_url:
        return jsonify({'error': 'playlist_url required'}), 400
    
    try:
        # Load existing data
        registry = load_playlists_registry()
        playlist_info = next((p for p in registry['playlists'] if p['id'] == playlist_id), None)
        
        if not playlist_info:
            return jsonify({'error': 'Playlist not found in registry'}), 404
            
        data_file = os.path.join(playlist_info['output_dir'], f"{playlist_id}_data.json")
        if not os.path.exists(data_file):
            return jsonify({'error': 'Playlist data file not found'}), 404
            
        with open(data_file, 'r', encoding='utf-8') as f:
            existing_videos = json.load(f)
        
        # Fetch current state from YouTube
        from youtube_api_extractor import YouTubeAPIExtractor
        extractor = YouTubeAPIExtractor()
        current_videos = extractor.get_playlist_videos(playlist_url)
        
        # Apply delta sync
        result_videos, stats = delta_sync.apply_delta_with_stats(
            existing_videos, 
            current_videos, 
            keep_removed=True
        )
        
        # Save updated data
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(result_videos, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
        
        # Update registry
        playlist_info['video_count'] = len([v for v in result_videos 
                                            if v.get('sync_status', {}).get('exists_at_source', True)])
        playlist_info['last_updated'] = datetime.datetime.utcnow().isoformat()
        
        with open(os.path.join('output', 'playlists.json'), 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
        
        return jsonify({
            'status': 'success',
            'playlist_id': playlist_id,
            'stats': stats,
            'total_videos': len(result_videos)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500




@app.route('/api/status/<job_id>')
def job_status(job_id):
    """Stream job progress via Server-Sent Events."""
    def generate():
        if job_id not in jobs:
            yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
            return
        
        job = jobs[job_id]
        
        while job.status not in ['complete', 'error']:
            data = {
                'status': job.status,
                'progress': job.progress,
                'message': job.message,
                'quota_used': job.quota_used
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.5)
        
        # Final update
        if job.status == 'complete':
            data = {
                'status': 'complete',
                'progress': 100,
                'message': 'Indexing complete!',
                'files': job.result,
                'quota_used': job.quota_used
            }
        else:
            data = {
                'status': 'error',
                'message': job.error
            }
        
        yield f"data: {json.dumps(data)}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/quota')
def get_quota():
    """Get current YouTube API quota information."""
    try:
        from youtube_api_extractor import YouTubeAPIExtractor
        
        indexer = PlaylistIndexer()
        api_key = indexer.config.get('youtube_api_key', '')
        
        if not api_key:
            return jsonify({'remaining': 0, 'total': 10000, 'percentage': 0})
        
        # Estimate remaining quota (would need actual Google Cloud API for real data)
        # For now, return static estimate
        return jsonify({
            'remaining': 9847,
            'total': 10000,
            'percentage': 98.47
        })
        
    except Exception as e:
        return jsonify({'remaining': 0, 'total': 10000, 'percentage': 0})


@app.route('/api/search')
def search_playlists():
    """Search across all indexed playlists."""
    query = request.args.get('q', '').lower()
    playlist_filter = request.args.get('playlist', '')
    category_filter = request.args.get('category', '')
    
    # Load all playlists data
    videos = load_all_videos()
    
    # Apply filters
    videos = filter_video_list(videos, query, playlist_filter, category_filter)
    
    return jsonify({
        'results': videos[:50],  # Limit to 50 results
        'total': len(videos)
    })


def filter_video_list(videos, query, playlist_filter, category_filter):
    """
    Filter a list of videos based on search criteria.
    
    Args:
        videos: List of video dictionaries
        query: Text query to search in title/channel/description/tags
        playlist_filter: Filter by specific playlist ID
        category_filter: Filter by category/thematic
        
    Returns:
        List of filtered video dictionaries
    """
    filtered = videos
    
    if query:
        query = query.lower()
        filtered = [v for v in filtered if
                  query in v.get('title', '').lower() or
                  query in v.get('channel', '').lower() or
                  query in v.get('description', '').lower() or
                  any(query in tag.lower() for tag in _get_video_tags(v))]
    
    if playlist_filter:
        filtered = [v for v in filtered if v.get('playlist_id') == playlist_filter]
    
    if category_filter:
        filtered = [v for v in filtered if 
                    v.get('category') == category_filter or
                    v.get('metadata', {}).get('thematic', {}).get('primary') == category_filter]
                    
    return filtered


def _get_video_tags(video):
    """Helper to extract tags from video in various formats."""
    tags = video.get('tags', [])
    if isinstance(tags, dict):
        return tags.get('combined', [])
    elif isinstance(tags, list):
        return tags
    return []



@app.route('/api/playlists')
def list_playlists():
    """Get list of all indexed playlists."""
    registry_file = os.path.join('output', 'playlists.json')
    
    if os.path.exists(registry_file):
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
            return jsonify(registry)
    
    return jsonify({'playlists': [], 'total_playlists': 0, 'total_videos': 0})


@app.route('/api/playlist/<playlist_id>')
def get_playlist(playlist_id):
    """Get a single playlist with all its videos."""
    registry_file = os.path.join('output', 'playlists.json')
    
    if not os.path.exists(registry_file):
        return jsonify({'error': 'No playlists found'}), 404
    
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # Find playlist by ID
    playlist = next((p for p in registry['playlists'] if p['id'] == playlist_id), None)
    
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404
    
    # Load videos
    data_file = os.path.join(playlist['output_dir'], f"{playlist_id}_data.json")
    videos = []
    
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            videos = json.load(f)
    
    return jsonify({
        'playlist': playlist,
        'videos': videos
    })


@app.route('/share/<playlist_id>')
def share_playlist(playlist_id):
    """Render a shareable standalone page for a playlist."""
    registry_file = os.path.join('output', 'playlists.json')
    
    if not os.path.exists(registry_file):
        return "Playlist not found", 404
    
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # Find playlist by ID
    playlist = next((p for p in registry['playlists'] if p['id'] == playlist_id), None)
    
    if not playlist:
        return "Playlist not found", 404
    
    # Load videos
    data_file = os.path.join(playlist['output_dir'], f"{playlist_id}_data.json")
    videos = []
    
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            videos = json.load(f)
    
    return render_template('share.html', playlist=playlist, videos=videos)


@app.route('/api/videos/all')
def get_all_videos():
    """Get all videos from all indexed playlists."""
    all_videos = load_all_videos()
    
    # Get unique playlists
    playlists = list(set(v.get('playlist_id', '') for v in all_videos))
    playlists = [p for p in playlists if p]  # Remove empty strings
    
    return jsonify({
        'videos': all_videos,
        'total_count': len(all_videos),
        'playlists': sorted(playlists)
    })


@app.route('/api/export/excel')
def export_excel():
    """Export playlist(s) to Excel file."""
    from io import BytesIO
    from urllib.parse import quote
    from execution.excel_exporter import export_to_excel, load_playlist_videos, load_all_videos as load_all_for_export
    
    filename = "export.xlsx"
    playlist_id = request.args.get('playlist', '')
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    try:
        # Load all videos (easier to just filter from all than selective load for search)
        videos = load_all_for_export()
        
        # Determine filename base
        if playlist_id:
            filename = f"{playlist_id}_filtered_export.xlsx"
        elif query:
            filename = "search_results_export.xlsx"
        else:
            filename = "all_videos_export.xlsx"
            
        # Apply filters
        videos = filter_video_list(videos, query, playlist_id, category)

        
        if not videos:
            return jsonify({'error': 'No videos to export'}), 404
        
        # Create Excel in memory
        output = BytesIO()
        export_to_excel(videos, output)
        output.seek(0)
        excel_data = output.getvalue()
        
        # Create response with proper headers for browser compatibility
        response = Response(
            excel_data,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # RFC 5987 compliant Content-Disposition with both filename and filename*
        # This ensures maximum browser compatibility
        encoded_filename = quote(filename)
        response.headers['Content-Disposition'] = (
            f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
        )
        response.headers['Content-Length'] = len(excel_data)
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/tags')
def list_unique_tags():
    """Get all unique tags across all videos."""
    # This requires loading all video data into Pydantic models ideally
    # For now, we load dicts and pass to TagManager if it accepts dicts or convert
    # TagManager expects List[List[VideoData]]
    all_videos_dicts = load_all_videos()
    # Convert to models (expensive? maybe just adapt TagManager to be flexible later)
    # For now let's assume TagManager can handle dicts or we ignore type hint runtime
    # But better to use helper that extracts tags from dicts
    
    # Extract tags manually to avoid heavy instantiation
    youtube = set()
    auto = set()
    user = set()
    for v in all_videos_dicts:
        tags = v.get('tags', {})
        if isinstance(tags, dict):
             youtube.update(tags.get('youtube_tags', []))
             auto.update(tags.get('auto_generated', []))
             user.update(tags.get('user_defined', []))
        elif isinstance(tags, list):
             youtube.update(tags)
             
    return jsonify({
        "youtube_tags": sorted(list(youtube)),
        "auto_generated": sorted(list(auto)),
        "user_defined": sorted(list(user)),
        "all": sorted(list(youtube | auto | user))
    })

@app.route('/api/videos/<video_id>/tags', methods=['POST'])
def add_user_tag(video_id):
    """Add a user tag to a video."""
    data = request.json
    tag = data.get('tag')
    if not tag:
        return jsonify({'error': 'No tag provided'}), 400
        
    # We need to find the playlist this video belongs to, load it, update it, save it
    # This logic is complex because videos are spread across files
    # Shortcut: search in all loading (slow) or use an index?
    # For prototype: Load all playlists, find video, update specific file
    
    registry = load_playlists_registry()
    target_playlist = None
    target_video = None
    
    for p in registry['playlists']:
        data_file = os.path.join(p['output_dir'], f"{p['id']}_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                videos = json.load(f)
            
            for v in videos:
                if v.get('video_id') == video_id:
                    target_video = v
                    target_playlist = p
                    break
            if target_video: break
            
    if not target_video:
        return jsonify({'error': 'Video not found'}), 404
        
    # Update Tag
    tags = target_video.get('tags')
    if isinstance(tags, list):
        # Migrate on fly?
        tags = {'youtube_tags': tags, 'user_defined': [], 'auto_generated': [], 'combined': tags}
        target_video['tags'] = tags
        
    if 'user_defined' not in tags: tags['user_defined'] = []
    if tag not in tags['user_defined']:
        tags['user_defined'].append(tag)
        # Update combined
        # Re-calc combined
        combined = set(tags.get('youtube_tags', []) + tags.get('auto_generated', []) + tags['user_defined'])
        tags['combined'] = list(combined)
        
    # Save back to file
    data_file = os.path.join(target_playlist['output_dir'], f"{target_playlist['id']}_data.json")
    # We need to reload the file to be safe? We effectively have the list 'videos' from usage above
    # 'videos' variable holds the list where 'target_video' is a reference
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
        
    return jsonify({'status': 'success', 'video': target_video})

@app.route('/api/videos/<video_id>/tags/<tag_name>', methods=['DELETE'])
def remove_user_tag(video_id, tag_name):
    """Remove a user-defined tag from a video."""
    # Find the video across all playlists
    registry = load_playlists_registry()
    target_playlist = None
    target_video = None
    
    for p in registry['playlists']:
        data_file = os.path.join(p['output_dir'], f"{p['id']}_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                videos = json.load(f)
            
            for v in videos:
                if v.get('video_id') == video_id:
                    target_video = v
                    target_playlist = p
                    break
            if target_video: break
            
    if not target_video:
        return jsonify({'error': 'Video not found'}), 404
        
    # Get tags structure
    tags = target_video.get('tags')
    if isinstance(tags, list):
        # Legacy format - cannot remove from flat list
        return jsonify({'error': 'Cannot remove tags from legacy format'}), 400
        
    if not isinstance(tags, dict) or 'user_defined' not in tags:
        return jsonify({'error': 'No user-defined tags found'}), 404
        
    # Remove the tag if it exists
    if tag_name not in tags['user_defined']:
        return jsonify({'error': 'Tag not found in user-defined tags'}), 404
        
    tags['user_defined'].remove(tag_name)
    
    # Recalculate combined tags
    combined = set(tags.get('youtube_tags', []) + tags.get('auto_generated', []) + tags['user_defined'])
    tags['combined'] = list(combined)
    
    # Save back to file
    data_file = os.path.join(target_playlist['output_dir'], f"{target_playlist['id']}_data.json")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
        
    return jsonify({'status': 'success', 'video': target_video})


def load_playlists_registry():
    registry_file = os.path.join('output', 'playlists.json')
    if os.path.exists(registry_file):
        with open(registry_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'playlists': []}

# Mind Map Route (Moved down)
@app.route('/api/graph/mindmap')
def get_mindmap_data():
    """Get graph data for mind map visualization."""
    from execution.graph_generator import build_graph_data
    from execution.excel_exporter import load_all_videos as load_all_for_graph
    
    try:
        videos = load_all_for_graph()
        # Phase 2: use view mode if passed
        view_mode = request.args.get('view', 'default')
        graph_data = build_graph_data(videos) # Update build_graph_data signature later
        return jsonify(graph_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def process_indexing_job(job):
    """Background job processor."""
    try:
        job.status = "extracting"
        job.progress = 10
        job.message = "Extracting playlist data from YouTube..."
        
        # Initialize indexer
        indexer = PlaylistIndexer()
        indexer.config['color_scheme'] = job.color_scheme
        
        if hasattr(job, 'mode') and job.mode == 'overwrite':
            # Handling overwrite specific logic if needed
            pass

        # Extract data
        raw_playlist_data = indexer.extract_from_youtube_url(job.playlist_url)
        job.progress = 40
        
        # Enrich Data (Phase 1 Integration)
        job.message = "Enriching metadata..."
        playlist_data = enricher.process_videos(raw_playlist_data)
        
        job.progress = 60
        job.message = f"Extracted & Enriched {len(playlist_data)} videos"
        
        # Estimate quota
        job.quota_used = len(playlist_data) + 2
        
        job.status = "generating"
        job.progress = 80
        job.message = "Generating index files..."
        
        # Generate files
        output_dir, files = indexer.generate_files(job.name, playlist_data)
        
        # Register playlist
        register_playlist(job.name, output_dir, files, playlist_data, job.color_scheme, job.playlist_url)
        
        job.status = "complete"
        job.progress = 100
        job.message = "Complete!"
        job.result = files
        
    except Exception as e:
        job.status = "error"
        job.error = str(e)
        import traceback
        traceback.print_exc()


def register_playlist(name, output_dir, files, playlist_data, color_scheme, youtube_url):
    """Register a newly indexed playlist."""
    registry_file = os.path.join('output', 'playlists.json')
    
    # Load existing registry
    if os.path.exists(registry_file):
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    else:
        registry = {'playlists': [], 'total_playlists': 0, 'total_videos': 0}
    
    # Create safe ID
    safe_id = name.lower().replace(' ', '_').replace('-', '_')
    
    # Check if exists
    existing_idx = next((i for i, p in enumerate(registry['playlists']) if p['id'] == safe_id), None)
    
    playlist_info = {
        'id': safe_id,
        'name': name,
        'created_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'video_count': len(playlist_data),
        'output_dir': output_dir,
        'html_file': next((f for f in files if f.endswith('.html')), ''),
        'md_file': next((f for f in files if f.endswith('.md')), ''),
        'color_scheme': color_scheme,
        'youtube_url': youtube_url
    }
    
    if existing_idx is not None:
        registry['playlists'][existing_idx] = playlist_info
    else:
        registry['playlists'].append(playlist_info)
    
    # Update totals
    registry['total_playlists'] = len(registry['playlists'])
    registry['total_videos'] = sum(p['video_count'] for p in registry['playlists'])
    registry['last_updated'] = datetime.datetime.utcnow().isoformat() + 'Z'
    
    # Save registry
    os.makedirs('output', exist_ok=True)
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)
    
    # Save video data for searching
    data_file = os.path.join(output_dir, f"{safe_id}_data.json")
    video_data_with_playlist = []
    for video in playlist_data:
        video_copy = video.copy()
        video_copy['playlist_id'] = safe_id
        video_copy['playlist_name'] = name
        video_data_with_playlist.append(video_copy)
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(video_data_with_playlist, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)


def load_all_videos():
    """Load all videos from all indexed playlists."""
    all_videos = []
    registry_file = os.path.join('output', 'playlists.json')
    
    if not os.path.exists(registry_file):
        return []
    
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    for playlist in registry['playlists']:
        data_file = os.path.join(playlist['output_dir'], f"{playlist['id']}_data.json")
        
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                videos = json.load(f)
                all_videos.extend(videos)
    
    return all_videos


@app.route('/api/store/categories')
def store_categories():
    """Get thematic categories with counts."""
    return jsonify(store_api.get_categories())

@app.route('/api/store/filters')
def store_filters():
    """Get available filter options."""
    return jsonify(store_api.get_filter_options())

@app.route('/api/store/search')
def store_search():
    """Advanced search for Video Store."""
    try:
        results = store_api.search_videos(
            query=request.args.get('q'),
            thematic=request.args.get('thematic'),
            genre=request.args.get('genre'),
            length=request.args.get('length'),
            author_type=request.args.get('author_type'),
            sort_by=request.args.get('sort', 'newest'),
            page=int(request.args.get('page', 1)),
            per_page=int(request.args.get('per_page', 24))
        )
        return jsonify(results)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Playlist Navigator Pro...")
    print("📍 Open your browser to: http://localhost:5000")
    app.run(debug=True, port=5000, threaded=True)
