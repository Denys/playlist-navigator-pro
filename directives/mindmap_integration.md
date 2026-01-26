# Directive: Mind Map Integration

## Purpose
Add interactive video interconnection visualization to the web app using D3.js force-directed graph.

## Current Status
- ✅ POC complete: `mindmap_poc.html` (standalone demo)
- ❌ Backend not implemented
- ❌ Not integrated into web app

## Implementation Plan

### Backend Tasks
1. Create `graph_generator.py` in `execution/`:
   - `build_graph_data(videos)` - Build nodes and links
   - `calculate_edge_weights(video_a, video_b)` - Connection strength
   - `extract_communities(graph)` - Louvain clustering (optional)

2. Add API endpoint to `web_app.py`:
   ```python
   @app.route('/api/graph/mindmap')
   def get_mindmap_data():
       all_videos = load_all_videos()
       return jsonify(build_graph_data(all_videos))
   ```

3. Dependencies to add:
   ```
   networkx>=3.0
   python-louvain>=0.16  # Optional, for community detection
   ```

### Frontend Tasks
1. Add tab button to `templates/index.html`:
   ```html
   <button class="tab-btn" data-tab="mindmap">🧠 Mind Map</button>
   ```

2. Create `static/js/mindmap.js` from POC code

3. Add styles to `static/css/style.css`

### API Response Format
```json
{
  "nodes": [
    {"id": "video_id", "label": "Title", "group": 0, "tags": [...]}
  ],
  "links": [
    {"source": "id1", "target": "id2", "value": 3, "type": "tag"}
  ]
}
```

## Tools/Scripts
- `mindmap_poc.html` - Reference implementation
- `execution/graph_generator.py` - To be created
- `static/js/mindmap.js` - To be created

## Time Estimate
- Backend: 2-3 hours
- Frontend integration: 3-4 hours
- Testing: 1-2 hours
- **Total: ~6-8 hours**

## Learnings
- D3.js v7 via CDN works well
- Force simulation parameters tuned in POC
- Canvas rendering needed for 500+ nodes
