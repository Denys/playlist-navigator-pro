#!/usr/bin/env python3
"""
Example usage of the YouTube Playlist Indexer
This script demonstrates how to use the PlaylistIndexer class programmatically.
"""

import json
from playlist_indexer import PlaylistIndexer

def example_usage():
    """Example of using the PlaylistIndexer programmatically."""
    
    # Sample playlist data (you would load this from a JSON file or API)
    sample_playlist_data = [
        {
            "title": "Build a Teensy Stand-Alone Filter for Synths",
            "url": "https://www.youtube.com/watch?v=example1",
            "channel": "Notes and Volts"
        },
        {
            "title": "TEENSY-Synth PART 1: BUILD IT",
            "url": "https://www.youtube.com/watch?v=example2",
            "channel": "Notes and Volts"
        },
        {
            "title": "Arduino MIDI Controller: Part 1 - Potentiometers",
            "url": "https://www.youtube.com/watch?v=example3",
            "channel": "Notes and Volts"
        },
        {
            "title": "Polyphonic synthesizer with DaisySeed",
            "url": "https://www.youtube.com/watch?v=example4",
            "channel": "Marcel Licence"
        },
        {
            "title": "Making A $2000 Synth For $99",
            "url": "https://www.youtube.com/watch?v=example5",
            "channel": "Edward Wang"
        }
    ]
    
    # Initialize the indexer with custom configuration
    config = {
        "output_dir": "example_output",
        "generate_html": True,
        "generate_pdf": True,
        "color_scheme": "teal",  # Good for hardware/audio content
        "auto_categorize": True,
        "tag_suggestions": True
    }
    
    # Save custom config
    with open('example_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Create indexer instance
    indexer = PlaylistIndexer('example_config.json')
    
    # Generate the playlist index
    playlist_name = "Hardware Audio Projects"
    output_dir, generated_files = indexer.generate_files(playlist_name, sample_playlist_data)
    
    print(f"Successfully generated playlist index for '{playlist_name}'")
    print(f"Output directory: {output_dir}")
    print("Generated files:")
    for file in generated_files:
        print(f"  - {file}")
    
    # Demonstrate accessing the processed data
    print(f"\nProcessed {len(indexer.video_data)} videos")
    print(f"Found {len(indexer.categories)} categories:")
    for category, videos in indexer.categories.items():
        print(f"  - {category}: {len(videos)} videos")
    
    print(f"\nGenerated {len(indexer.tags)} unique tags:")
    print(f"  {', '.join(sorted(indexer.tags))}")

def batch_processing_example():
    """Example of processing multiple playlists in batch."""
    
    playlists = {
        "TEENSY Projects": [
            {"title": "Teensy Audio Tutorial", "url": "https://youtube.com/watch?v=1", "channel": "PaulStoffregen"},
            {"title": "Build Teensy Synth", "url": "https://youtube.com/watch?v=2", "channel": "Notes and Volts"}
        ],
        "DAISY Projects": [
            {"title": "Daisy Seed Programming", "url": "https://youtube.com/watch?v=3", "channel": "Electrosmith"},
            {"title": "Polyphonic Daisy Synth", "url": "https://youtube.com/watch?v=4", "channel": "Marcel Licence"}
        ]
    }
    
    # Process each playlist with different color schemes
    color_schemes = ["purple", "teal", "blue", "green"]
    
    indexer = PlaylistIndexer()
    
    for i, (playlist_name, videos) in enumerate(playlists.items()):
        # Use different color scheme for each playlist
        indexer.config['color_scheme'] = color_schemes[i % len(color_schemes)]
        
        output_dir, generated_files = indexer.generate_files(playlist_name, videos)
        print(f"Processed '{playlist_name}' -> {output_dir}")

if __name__ == "__main__":
    print("YouTube Playlist Indexer - Example Usage")
    print("=" * 50)
    
    print("\n1. Basic Usage Example:")
    example_usage()
    
    print("\n" + "=" * 50)
    print("\n2. Batch Processing Example:")
    batch_processing_example()
    
    print("\n" + "=" * 50)
    print("\nDone! Check the generated output directories for results.")

