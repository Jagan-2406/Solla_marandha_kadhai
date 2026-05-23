# generate_icons.py
from PIL import Image, ImageDraw
import os

def create_icon(size, filename):
    # Create image with transparent background
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center = size // 2
    max_radius = size // 2 - int(size * 0.05) # 5% padding
    
    # Render beautiful dark-teal to deep-indigo gradient circles
    for r in range(max_radius, 0, -1):
        ratio = r / max_radius
        # Interpolate color from teal #0d9488 to deep blue #1e293b
        red = int(13 * (1 - ratio) + 30 * ratio)
        green = int(148 * (1 - ratio) + 41 * ratio)
        blue = int(136 * (1 - ratio) + 59 * ratio)
        
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=(red, green, blue, 255)
        )
        
    # Draw a stylized white border
    draw.ellipse(
        [center - max_radius, center - max_radius, center + max_radius, center + max_radius],
        outline=(255, 255, 255, 40),
        width=int(size * 0.03)
    )
    
    # Draw a stylized geometric letter "T" emblem in the center (representing Tamil/Tutor)
    w = int(size * 0.15)
    # Horizontal bar
    draw.rectangle([center - int(w * 1.4), center - int(w * 1.2), center + int(w * 1.4), center - int(w * 0.8)], fill=(255, 255, 255, 220))
    # Vertical stem
    draw.rectangle([center - int(w * 0.3), center - int(w * 1.0), center + int(w * 0.3), center + int(w * 1.1)], fill=(255, 255, 255, 220))
    # Bottom accent dot
    draw.ellipse([center - int(w * 0.3), center + int(w * 1.3), center + int(w * 0.3), center + int(w * 1.9)], fill=(255, 255, 255, 220))
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename)
    print(f"Generated PWA icon: {filename} ({size}x{size})")

if __name__ == '__main__':
    # Make sure Pillow is installed. If not, print error message
    try:
        create_icon(192, "frontend/static/icon-192.png")
        create_icon(512, "frontend/static/icon-512.png")
    except ImportError:
        print("Pillow is not installed. Please install it using: pip install Pillow")
