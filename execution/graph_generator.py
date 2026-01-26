import networkx as nx
import community.community_louvain as community_louvain
import itertools
from typing import List, Dict, Any

def build_graph_data(videos: List[Dict[str, Any]], view_mode: str = 'default') -> Dict[str, Any]:
    """
    Build nodes and edges for D3.js force graph from video data.
    
    Args:
        videos: List of video dictionaries from the indexer
        view_mode: Visualization mode - 'default', 'thematic', 'genre', 'channel', 'timeline'
        
    Returns:
        Dict with 'nodes' and 'links' keys suitable for D3.js
    """
    if not videos:
        return {"nodes": [], "links": []}
        
    if view_mode == 'thematic':
        return build_thematic_graph(videos)
    elif view_mode == 'genre':
        return build_genre_graph(videos)
    elif view_mode == 'channel':
        return build_channel_graph(videos)
    else:
        return _build_default_graph(videos)


def _build_default_graph(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build default tag-based clustering graph."""
    if not videos:
        return {"nodes": [], "links": []}

    G = nx.Graph()
    
    # 1. Add Nodes
    # Map video ID (or title+channel as fallback) to node attributes
    for vid in videos:
        # Use video_id if available, else generate a hash from URL
        video_id = vid.get('video_id') or vid.get('id') or vid.get('url')
        
        G.add_node(video_id, 
                   label=vid.get('title', 'Unknown'),
                   channel=vid.get('channel', 'Unknown'),
                   tags=vid.get('tags', []),
                   url=vid.get('url', ''),
                   thumbnail=vid.get('thumbnail', '')
                   )

    # 2. Add Edges (Connections)
    # Strategy: Inverted index for tags to find connections efficiently
    tag_to_videos = {}
    channel_to_videos = {}

    for vid in videos:
        video_id = vid.get('video_id') or vid.get('id') or vid.get('url')
        
        # Index by Tags
        for tag in vid.get('tags', []):
            if tag not in tag_to_videos:
                tag_to_videos[tag] = []
            tag_to_videos[tag].append(video_id)
            
        # Index by Channel
        channel = vid.get('channel')
        if channel:
            if channel not in channel_to_videos:
                channel_to_videos[channel] = []
            channel_to_videos[channel].append(video_id)

    # Create Tag Links (Primary connection)
    # If two videos share a tag, add an edge. Weight = number of shared tags.
    tag_edges = {}  # (u, v) -> weight
    
    for tag, video_ids in tag_to_videos.items():
        if len(video_ids) < 2:
            continue
            
        # Create edges between all pairs in this tag group
        # Limit to reasonable number to prevent explosive cliques on common tags
        # (For now, full clique is fine for small datasets < 500 nodes)
        for u, v in itertools.combinations(video_ids, 2):
            if u > v:
                u, v = v, u
            
            if (u, v) not in tag_edges:
                tag_edges[(u, v)] = 0
            tag_edges[(u, v)] += 1

    for (u, v), weight in tag_edges.items():
        # Only add strong connections if weight >= 1
        G.add_edge(u, v, weight=weight, type='tag')

    # Create Channel Links (Secondary connection)
    # Usually weaker or distinct type
    for channel, video_ids in channel_to_videos.items():
        if len(video_ids) < 2:
            continue
        for u, v in itertools.combinations(video_ids, 2):
            # If edge exists, boost weight? Or separate type?
            # Let's boost weight if exists, or add new if not
            if G.has_edge(u, v):
                G[u][v]['weight'] += 0.5  # Boost existing
            else:
                G.add_edge(u, v, weight=0.5, type='channel')

    # 3. Community Detection (Louvain)
    # Fallback to single group if library fails or graph is empty
    try:
        if len(G.nodes) > 0:
            partition = community_louvain.best_partition(G)
        else:
            partition = {}
    except Exception as e:
        print(f"Community detection failed: {e}")
        partition = {n: 0 for n in G.nodes}

    # 4. Format for D3.js
    d3_nodes = []
    d3_links = []

    for node_id in G.nodes:
        node_attrs = G.nodes[node_id]
        d3_nodes.append({
            "id": node_id,
            "label": node_attrs['label'],
            "group": partition.get(node_id, 0),
            "tags": node_attrs['tags'],
            "channel": node_attrs['channel'],
            "url": node_attrs['url'],
            "thumbnail": node_attrs['thumbnail']
        })

    for u, v, attrs in G.edges(data=True):
        d3_links.append({
            "source": u,
            "target": v,
            "value": attrs['weight'],
            "type": attrs.get('type', 'tag')
        })

    return {
        "nodes": d3_nodes,
        "links": d3_links,
        "meta": {
            "nodeCount": len(d3_nodes),
            "edgeCount": len(d3_links),
            "communityCount": len(set(partition.values())) if partition else 0
        }
    }


def build_thematic_graph(videos: List[Dict[str, Any]]) -> Dict:
    """
    Build graph with thematic super-nodes in radial layout.
    Creates central hub nodes for each thematic category.
    """
    if not videos:
        return {"nodes": [], "links": []}
        
    G = nx.Graph()
    
    # Collect thematics
    thematics = set()
    for v in videos:
        metadata = v.get('metadata', {})
        if metadata:
            thematic_data = metadata.get('thematic', {})
            if isinstance(thematic_data, dict):
                primary = thematic_data.get('primary')
                if primary:
                    thematics.add(primary)
    
    # Create thematic super-nodes
    for them in thematics:
        G.add_node(f"thematic:{them}",
                   node_type='thematic',
                   label=them.replace('_', ' ').title(),
                   size=30)
    
    # Add video nodes and connect to thematics
    for vid in videos:
        video_id = vid.get('video_id') or vid.get('url')
        metadata = vid.get('metadata', {})
        
        thematic_primary = None
        if metadata:
            thematic_data = metadata.get('thematic', {})
            if isinstance(thematic_data, dict):
                thematic_primary = thematic_data.get('primary')
        
        G.add_node(video_id,
                   node_type='video',
                   label=vid.get('title', 'Unknown')[:50],
                   channel=vid.get('channel', ''),
                   url=vid.get('url', ''))
        
        if thematic_primary:
            G.add_edge(video_id, f"thematic:{thematic_primary}",
                      edge_type='thematic_membership',
                      weight=2)
    
    # Convert to D3
    d3_nodes = []
    d3_links = []
    
    for node_id in G.nodes:
        node_data = G.nodes[node_id]
        d3_nodes.append({
            "id": node_id,
            "label": node_data.get('label', node_id),
            "node_type": node_data.get('node_type', 'video'),
            "size": node_data.get('size', 10),
            "url": node_data.get('url', ''),
            "channel": node_data.get('channel', '')
        })
    
    for u, v, attrs in G.edges(data=True):
        d3_links.append({
            "source": u,
            "target": v,
            "value": attrs.get('weight', 1),
            "type": attrs.get('edge_type', 'default')
        })
    
    return {
        "nodes": d3_nodes,
        "links": d3_links,
        "meta": {
            "nodeCount": len(d3_nodes),
            "edgeCount": len(d3_links),
            "view_mode": "thematic"
        }
    }


def build_genre_graph(videos: List[Dict[str, Any]]) -> Dict:
    """Build graph grouped by genre."""
    return _build_default_graph(videos)


def build_channel_graph(videos: List[Dict[str, Any]]) -> Dict:
    """Build graph grouped by channel."""
    return _build_default_graph(videos)
