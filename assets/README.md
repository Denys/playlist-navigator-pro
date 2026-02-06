# PlaylistIndexer Icon Assets

This folder contains the application icon for PlaylistIndexer in multiple formats and sizes.

## Design Specification

### Visual Concept
The icon combines two core metaphors:
- **Playlist elements**: Three horizontal lines with bullet points representing an organized media list
- **Indexing symbol**: A magnifying glass representing search and indexing functionality

### Design Characteristics
- **Style**: Modern minimalist flat design with subtle glassmorphism
- **Shape**: Square with rounded corners (15% radius)
- **Background**: Deep blue to purple vertical gradient
- **Accents**: Clean white lines with teal highlights
- **Transparency**: Full alpha channel support

### Color Palette
- **Primary Dark**: `#1A2A6C` (Deep blue)
- **Primary Mid**: `#2D559B` (Medium blue)
- **Accent Purple**: `#5F4BA0` (Purple gradient end)
- **Accent Teal**: `#409CB4` (Teal handle/highlight)
- **Light Teal**: `#96DCE6` (Playlist lines)
- **White**: `#FFFFFF` (Magnifying glass, highlights)

## File Structure

```
assets/
├── generate_icon.py          # Icon generation script
├── PlaylistIndexer.ico       # Multi-resolution Windows icon
├── README.md                 # This file
├── icon_16x16.png           # Taskbar / small list view
├── icon_24x24.png           # Toolbar
├── icon_32x32.png           # Standard icon size
├── icon_48x48.png           # Explorer large icons
├── icon_64x64.png           # Start menu
├── icon_96x96.png           # Tile view
├── icon_128x128.png         # Desktop large icons
├── icon_256x256.png         # High DPI displays
└── icon_512x512.png         # Highest resolution
```

## Windows ICO Contents

The `PlaylistIndexer.ico` file contains all standard Windows icon sizes:
- 16×16 (taskbar, small icons)
- 24×24 (toolbars)
- 32×32 (standard icons)
- 48×48 (Explorer large icons)
- 64×64 (Start menu)
- 96×96 (tile view)
- 128×128 (desktop large icons)
- 256×256 (high DPI)
- 512×512 (highest resolution)

## Scalability Strategy

The icon uses three optimized designs based on size:

### Small (16-32px)
- Simplified elements with thicker lines
- Reduced detail for clarity at tiny sizes
- Compact layout maximizing visible area

### Medium (48-96px)
- Balanced detail level
- Clear separation between elements
- Subtle glassmorphism highlights

### Large (128-512px)
- Full detail with inner highlight ring on magnifying glass
- Enhanced glassmorphism effect
- Premium polished appearance

## Usage

### In Python/PyInstaller
```python
# In your .spec file or build script
icon='PlaylistIndexer.ico'
```

### In Windows Shortcuts
Simply reference `PlaylistIndexer.ico` as the icon file.

### Regenerating Icons
To regenerate all icon files:
```bash
cd assets
python generate_icon.py
```

## Requirements

- Python 3.7+
- Pillow (PIL) library: `pip install Pillow`

## License

Icon design is part of the PlaylistIndexer project and follows the same license terms.
