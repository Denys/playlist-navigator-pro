#!/usr/bin/env python3
"""
Generate PlaylistIndexer application icon in multiple sizes and ICO format.

Design Concept:
- Modern minimalist flat design with subtle glassmorphism
- Visual metaphors: playlist lines + magnifying glass (indexing)
- Deep blue/teal/purple gradient palette
- Scales from 16x16 to 512x512 pixels with size-optimized designs
"""

from PIL import Image, ImageDraw, ImageFilter
import math
import os


def create_gradient_background(size, color1, color2):
    """Create a vertical gradient background."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    for y in range(size):
        ratio = y / size
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    return img


def draw_playlist_lines_compact(draw, size, line_color):
    """Draw compact playlist lines for small icons."""
    margin = size // 8
    line_width = max(1, size // 16)
    line_spacing = size // 5
    start_y = size // 4
    
    # Three lines with bullet points
    for i in range(3):
        y = start_y + i * line_spacing
        # Small bullet
        bullet_x = margin
        bullet_radius = max(1, size // 24)
        draw.ellipse([bullet_x - bullet_radius, y - bullet_radius,
                     bullet_x + bullet_radius, y + bullet_radius],
                    fill=line_color)
        
        # Short line
        line_start = margin + size // 8
        line_end = size - margin
        draw.line([(line_start, y), (line_end, y)], 
                 fill=line_color, width=line_width)


def draw_magnifying_glass_compact(draw, size, cx, cy, glass_color, handle_color):
    """Draw compact magnifying glass for small icons."""
    radius = size // 4
    width = max(1, size // 24)
    
    # Simple circle
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                outline=glass_color, width=width)
    
    # Short handle
    handle_len = size // 6
    angle = math.pi / 4
    end_x = cx + int(radius * 0.7 * math.cos(angle)) + int(handle_len * math.cos(angle))
    end_y = cy + int(radius * 0.7 * math.sin(angle)) + int(handle_len * math.sin(angle))
    start_x = cx + int(radius * 0.7 * math.cos(angle))
    start_y = cy + int(radius * 0.7 * math.sin(angle))
    
    draw.line([(start_x, start_y), (end_x, end_y)],
             fill=handle_color, width=max(1, size // 16))


def draw_playlist_lines_full(draw, size, center_y, line_color):
    """Draw stylized playlist lines for larger icons."""
    margin = size // 4
    line_width = max(2, size // 32)
    line_spacing = size // 12
    
    # Three lines representing playlist items
    for i in range(3):
        y = center_y + (i - 1) * line_spacing
        # Bullet point (small circle)
        bullet_x = margin + size // 16
        bullet_radius = max(3, size // 48)
        draw.ellipse([bullet_x - bullet_radius, y - bullet_radius,
                     bullet_x + bullet_radius, y + bullet_radius],
                    fill=line_color)
        
        # Horizontal line
        line_start = margin + size // 8
        line_end = size - margin
        draw.line([(line_start, y), (line_end, y)], 
                 fill=line_color, width=line_width)


def draw_magnifying_glass_full(draw, size, cx, cy, glass_color, handle_color):
    """Draw full magnifying glass for larger icons."""
    base_unit = size // 16
    
    # Glass circle
    radius = base_unit * 3
    circle_width = max(2, size // 48)
    
    # Outer ring
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                outline=glass_color, width=circle_width)
    
    # Inner highlight ring
    highlight_radius = radius - circle_width
    draw.ellipse([cx - highlight_radius, cy - highlight_radius,
                 cx + highlight_radius, cy + highlight_radius],
                outline=(255, 255, 255, 100), width=1)
    
    # Handle (angled down-right)
    handle_length = base_unit * 2.5
    angle = math.pi / 4  # 45 degrees
    handle_end_x = cx + radius * 0.7 + handle_length * math.cos(angle)
    handle_end_y = cy + radius * 0.7 + handle_length * math.sin(angle)
    handle_start_x = cx + radius * 0.7
    handle_start_y = cy + radius * 0.7
    
    draw.line([(handle_start_x, handle_start_y), 
              (handle_end_x, handle_end_y)],
             fill=handle_color, width=max(3, size // 32))


def create_icon_small(size):
    """Create compact icon for small sizes (16x16, 24x24, 32x32)."""
    # Color palette
    primary_dark = (26, 42, 108)
    accent_purple = (95, 75, 160)
    white = (255, 255, 255)
    accent_teal = (64, 156, 180)
    
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # Simple gradient background
    bg = create_gradient_background(size, primary_dark, accent_purple)
    
    # Rounded mask
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = size // 4
    margin = size // 32
    mask_draw.rounded_rectangle([margin, margin, size-margin, size-margin], 
                               radius=radius, fill=255)
    
    bg.putalpha(mask)
    img = Image.alpha_composite(img, bg)
    
    # Draw elements
    draw = ImageDraw.Draw(img)
    
    # Compact layout
    draw_playlist_lines_compact(draw, size, white)
    
    # Magnifying glass in lower right
    glass_cx = size * 3 // 4
    glass_cy = size * 3 // 4
    draw_magnifying_glass_compact(draw, size, glass_cx, glass_cy, white, accent_teal)
    
    return img


def create_icon_medium(size):
    """Create icon for medium sizes (48x48, 64x64, 96x96)."""
    # Color palette
    primary_dark = (26, 42, 108)
    primary_mid = (45, 85, 155)
    accent_purple = (95, 75, 160)
    white = (255, 255, 255)
    light_teal = (150, 220, 230)
    accent_teal = (64, 156, 180)
    
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # Gradient background
    bg = create_gradient_background(size, primary_dark, accent_purple)
    
    # Rounded mask
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = size // 6
    margin = size // 32
    mask_draw.rounded_rectangle([margin, margin, size-margin, size-margin], 
                               radius=radius, fill=255)
    
    bg.putalpha(mask)
    img = Image.alpha_composite(img, bg)
    
    # Add subtle glass effect
    overlay = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    highlight_margin = size // 16
    overlay_draw.rounded_rectangle([highlight_margin, highlight_margin, 
                                    size - highlight_margin, size // 3],
                                   radius=size//12, fill=(255, 255, 255, 25))
    img = Image.alpha_composite(img, overlay)
    
    # Draw elements
    draw = ImageDraw.Draw(img)
    
    center_y = size * 5 // 16
    glass_cx = size * 11 // 16
    glass_cy = size * 11 // 16
    
    # Simplified lines for medium size
    margin = size // 5
    line_width = max(2, size // 40)
    line_spacing = size // 10
    
    for i in range(3):
        y = center_y + (i - 1) * line_spacing
        bullet_x = margin + size // 20
        bullet_radius = max(2, size // 60)
        draw.ellipse([bullet_x - bullet_radius, y - bullet_radius,
                     bullet_x + bullet_radius, y + bullet_radius],
                    fill=white)
        
        line_start = margin + size // 10
        line_end = size - margin
        draw.line([(line_start, y), (line_end, y)], fill=white, width=line_width)
    
    # Simplified magnifying glass
    radius = size // 5
    width = max(2, size // 48)
    draw.ellipse([glass_cx - radius, glass_cy - radius, 
                  glass_cx + radius, glass_cy + radius],
                outline=white, width=width)
    
    # Handle
    handle_len = size // 6
    angle = math.pi / 4
    end_x = glass_cx + int(radius * 0.7 * math.cos(angle)) + int(handle_len * math.cos(angle))
    end_y = glass_cy + int(radius * 0.7 * math.sin(angle)) + int(handle_len * math.sin(angle))
    start_x = glass_cx + int(radius * 0.7 * math.cos(angle))
    start_y = glass_cy + int(radius * 0.7 * math.sin(angle))
    
    draw.line([(start_x, start_y), (end_x, end_y)],
             fill=accent_teal, width=max(2, size // 32))
    
    return img


def create_icon_large(size):
    """Create detailed icon for large sizes (128x128+)."""
    # Color palette
    primary_dark = (26, 42, 108)
    primary_mid = (45, 85, 155)
    accent_teal = (64, 156, 180)
    accent_purple = (95, 75, 160)
    white = (255, 255, 255)
    light_teal = (150, 220, 230)
    
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # Create gradient background
    bg = create_gradient_background(size, primary_dark, accent_purple)
    
    # Create rounded mask
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = size // 8
    margin = size // 32
    mask_draw.rounded_rectangle([margin, margin, size-margin, size-margin], 
                               radius=radius, fill=255)
    
    bg.putalpha(mask)
    img = Image.alpha_composite(img, bg)
    
    # Add glassmorphism effect
    overlay = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Top highlight
    hl_margin = size // 16
    overlay_draw.rounded_rectangle([hl_margin, hl_margin, 
                                    size - hl_margin, size // 3],
                                   radius=size//8, fill=(255, 255, 255, 30))
    img = Image.alpha_composite(img, overlay)
    
    # Draw elements
    draw = ImageDraw.Draw(img)
    
    center_x = size // 2
    playlist_y = size * 5 // 16
    glass_cx = size * 11 // 16
    glass_cy = size * 11 // 16
    
    # Draw playlist lines
    draw_playlist_lines_full(draw, size, playlist_y, light_teal)
    
    # Draw magnifying glass
    draw_magnifying_glass_full(draw, size, glass_cx, glass_cy, white, accent_teal)
    
    # Subtle border
    border_width = max(1, size // 128)
    border_color = (255, 255, 255, 40)
    draw.rounded_rectangle([margin, margin, size-margin, size-margin],
                          radius=radius, outline=border_color, width=border_width)
    
    return img


def create_icon(size):
    """Create the PlaylistIndexer icon at specified size."""
    if size <= 32:
        return create_icon_small(size)
    elif size <= 96:
        return create_icon_medium(size)
    else:
        return create_icon_large(size)


def main():
    """Generate icons in multiple sizes and create ICO file."""
    
    # Create assets directory
    os.makedirs('assets', exist_ok=True)
    
    # Standard Windows icon sizes
    sizes = [16, 24, 32, 48, 64, 96, 128, 256, 512]
    
    images = []
    
    print("Generating PlaylistIndexer icons...")
    
    for size in sizes:
        print(f"  Creating {size}x{size}...")
        icon = create_icon(size)
        images.append(icon)
        
        # Save individual PNG for inspection
        icon.save(f'assets/icon_{size}x{size}.png', 'PNG')
    
    # Create multi-resolution ICO file
    # ICO format needs sizes from largest to smallest for best compatibility
    ico_images = list(reversed(images))
    
    print("Creating PlaylistIndexer.ico...")
    ico_images[0].save('assets/PlaylistIndexer.ico', 
                      format='ICO', 
                      sizes=[(img.width, img.height) for img in ico_images])
    
    print("\nDone! Files created:")
    print("  - assets/PlaylistIndexer.ico (multi-resolution)")
    for size in sizes:
        print(f"  - assets/icon_{size}x{size}.png")


if __name__ == '__main__':
    main()
