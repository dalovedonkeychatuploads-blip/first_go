"""
Smart Reference Image Analyzer
Automatically detects cyan glows and body colors by searching for patterns
"""

from PIL import Image
import numpy as np

def analyze_reference_smart(image_path):
    """
    Analyze reference image by detecting color patterns

    Returns:
        dict with exact RGB values, glow sizes, proportions
    """
    img = Image.open(image_path)
    pixels = np.array(img)

    print("=" * 60)
    print("SMART NEON CYAN REFERENCE IMAGE ANALYSIS")
    print("=" * 60)
    print(f"Image size: {img.width} x {img.height}")
    print()

    # Find all pixels with cyan glow (high cyan value, low red)
    # Cyan = high green + high blue, low red
    r = pixels[:, :, 0]
    g = pixels[:, :, 1]
    b = pixels[:, :, 2]

    # Find cyan pixels (where green and blue are significantly higher than red)
    cyan_mask = (g > r + 20) & (b > r + 20) & (g > 50) & (b > 50)

    # Find body pixels (gray, not background, not cyan)
    # Body should be brighter than background RGB(38,38,42)
    gray_mask = (r > 45) & (r < 150) & (np.abs(r - g) < 20) & (np.abs(r - b) < 20)

    print("CYAN GLOW DETECTION")
    print("-" * 60)

    if np.any(cyan_mask):
        cyan_coords = np.argwhere(cyan_mask)
        print(f"Found {len(cyan_coords)} cyan pixels")

        # Sample a few cyan pixels
        num_samples = min(5, len(cyan_coords))
        sample_indices = np.linspace(0, len(cyan_coords) - 1, num_samples, dtype=int)

        for i, idx in enumerate(sample_indices):
            y, x = cyan_coords[idx]
            rgb = pixels[y, x][:3]
            print(f"  Cyan sample {i+1} @ ({x:4}, {y:4}): RGB({rgb[0]:3}, {rgb[1]:3}, {rgb[2]:3})")

        # Find brightest cyan pixel (core of glow)
        cyan_brightness = g[cyan_mask] + b[cyan_mask]
        brightest_idx = np.argmax(cyan_brightness)
        brightest_coord = cyan_coords[brightest_idx]
        y, x = brightest_coord
        rgb = pixels[y, x][:3]
        print(f"  BRIGHTEST cyan @ ({x:4}, {y:4}): RGB({rgb[0]:3}, {rgb[1]:3}, {rgb[2]:3})")
    else:
        print("  No cyan pixels detected!")

    print()
    print("BODY COLOR DETECTION (Gray)")
    print("-" * 60)

    if np.any(gray_mask):
        gray_coords = np.argwhere(gray_mask)
        print(f"Found {len(gray_coords)} gray body pixels")

        # Get brightness distribution of gray pixels
        gray_brightness = r[gray_mask].astype(int)

        # Find darkest (shadow), mid (midtone), brightest (highlight)
        darkest_val = np.min(gray_brightness)
        brightest_val = np.max(gray_brightness)
        mid_val = np.median(gray_brightness)

        # Find sample pixels for each brightness level
        darkest_idx = np.argmin(r[gray_mask])
        brightest_idx = np.argmax(r[gray_mask])
        mid_diff = np.abs(gray_brightness - mid_val)
        mid_idx = np.argmin(mid_diff)

        # Get coordinates
        shadow_coord = gray_coords[darkest_idx]
        highlight_coord = gray_coords[brightest_idx]
        mid_coord = gray_coords[mid_idx]

        # Print samples
        for name, coord in [("SHADOW (darkest)", shadow_coord),
                            ("MIDTONE (median)", mid_coord),
                            ("HIGHLIGHT (brightest)", highlight_coord)]:
            y, x = coord
            rgb = pixels[y, x][:3]
            print(f"  {name:25} @ ({x:4}, {y:4}): RGB({rgb[0]:3}, {rgb[1]:3}, {rgb[2]:3})")

        print()
        print(f"  Brightness range: {darkest_val} -> {int(mid_val)} -> {brightest_val}")
    else:
        print("  No gray body pixels detected!")

    print()
    print("ESTIMATED MEASUREMENTS")
    print("-" * 60)

    if np.any(gray_mask) or np.any(cyan_mask):
        # Find bounding box of fighter (gray + cyan)
        fighter_mask = gray_mask | cyan_mask
        fighter_coords = np.argwhere(fighter_mask)

        min_y, min_x = fighter_coords.min(axis=0)
        max_y, max_x = fighter_coords.max(axis=0)

        height = max_y - min_y
        width = max_x - min_x

        print(f"Fighter bounding box: ({min_x}, {min_y}) to ({max_x}, {max_y})")
        print(f"Fighter size: {width}px wide × {height}px tall")

        # Estimate proportions (assuming ~6-7 heads tall)
        estimated_head_diameter = height / 6.5
        print(f"Estimated head diameter: ~{estimated_head_diameter:.1f}px")
        print(f"Estimated torso width: ~{estimated_head_diameter * 0.9:.1f}px")
        print(f"Estimated arm thickness: ~{estimated_head_diameter * 0.45:.1f}px")
        print(f"Estimated leg thickness: ~{estimated_head_diameter * 0.52:.1f}px")

    print()
    print("=" * 60)
    print("Use these EXACT values to rebuild Neon Cyan!")
    print("=" * 60)

if __name__ == "__main__":
    reference_path = r"C:\Users\dalov\OneDrive\Pictures\Screenshots\Screenshot 2025-11-14 092005.png"

    try:
        analyze_reference_smart(reference_path)
    except FileNotFoundError:
        print(f"ERROR: Could not find image at: {reference_path}")
        print("Please update the 'reference_path' variable with correct path")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
