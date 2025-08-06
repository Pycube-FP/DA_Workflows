#!/usr/bin/env python3
"""
Generate PWA icons for Asset Tracker app
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, text="AT"):
    """Create a simple icon with text"""
    # Create a new image with a blue background
    img = Image.new('RGB', (size, size), color='#10194e')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default if not available
    try:
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Draw white text
    draw.text((x, y), text, fill='white', font=font)
    
    return img

def main():
    """Generate all required PWA icons"""
    # Create static/icons directory if it doesn't exist
    os.makedirs('static/icons', exist_ok=True)
    
    # Icon sizes for PWA
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    print("Generating PWA icons...")
    
    for size in sizes:
        icon = create_icon(size)
        filename = f'static/icons/icon-{size}x{size}.png'
        icon.save(filename)
        print(f"Created: {filename}")
    
    # Create shortcut icons
    shortcuts = {
        'scan': 'Scan',
        'dashboard': 'Dash',
        'register': 'Reg'
    }
    
    for name, text in shortcuts.items():
        icon = create_icon(96, text)
        filename = f'static/icons/{name}-96x96.png'
        icon.save(filename)
        print(f"Created: {filename}")
    
    print("\nAll icons generated successfully!")
    print("Your PWA is now ready to be installed on mobile devices!")

if __name__ == "__main__":
    main() 