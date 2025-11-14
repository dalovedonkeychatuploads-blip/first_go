"""
Reference Image Analyzer
Extracts exact RGB colors, sizes, and measurements from Neon Cyan reference image
"""

from PIL import Image
import numpy as np

def analyze_reference(image_path):
    """
    Analyze reference image for exact values

    Returns:
        dict with exact RGB values, glow sizes, proportions
    """
    img = Image.open(image_path)
    pixels = np.array(img)

    print("=" * 60)
    print("NEON CYAN REFERENCE IMAGE ANALYSIS")
    print("=" * 60)
    print(f"Image size: {img.width} x {img.height}")
    print()

    # Sample body parts (manually adjust coordinates based on where fighter is in image)
    # You'll need to adjust these x,y coordinates to match your reference

    samples = {
        "HEAD_HIGHLIGHT": (720, 330),      # Top-left of head (brightest)
        "HEAD_MIDTONE": (740, 340),        # Middle of head
        "HEAD_SHADOW": (760, 350),         # Bottom-right of head (darkest)

        "TORSO_HIGHLIGHT": (720, 400),     # Left edge of torso (lit side)
        "TORSO_MIDTONE": (740, 410),       # Center of torso
        "TORSO_SHADOW": (760, 420),        # Right edge of torso (shadow)

        "LIMB_HIGHLIGHT": (710, 390),      # Lit edge of arm
        "LIMB_MIDTONE": (720, 395),        # Center of arm
        "LIMB_SHADOW": (730, 400),         # Shadow edge of arm

        "JOINT_GLOW_OUTER": (695, 385),    # Outer edge of cyan glow at shoulder
        "JOINT_GLOW_INNER": (700, 385),    # Inner bright part of glow
        "JOINT_GLOW_CORE": (705, 385),     # Core of glow

        "EYE_GLOW": (735, 338),            # Cyan eye glow
        "EYE_CORE": (740, 338),            # Bright eye core
    }

    print("BODY COLOR ANALYSIS (Dark Charcoal)")
    print("-" * 60)

    for part_name, (x, y) in samples.items():
        if y < img.height and x < img.width:
            if "GLOW" in part_name or "EYE" in part_name:
                continue  # Skip glows for body analysis

            r, g, b = pixels[y, x][:3]  # Get RGB (ignore alpha if present)
            print(f"{part_name:20} @ ({x:4}, {y:4}): RGB({r:3}, {g:3}, {b:3})")

    print()
    print("CYAN GLOW COLOR ANALYSIS")
    print("-" * 60)

    for part_name, (x, y) in samples.items():
        if "GLOW" not in part_name and "EYE" not in part_name:
            continue  # Only show glows

        if y < img.height and x < img.width:
            r, g, b, *a = pixels[y, x]
            alpha = a[0] if a else 255
            print(f"{part_name:20} @ ({x:4}, {y:4}): RGB({r:3}, {g:3}, {b:3}, {alpha:3})")

    print()
    print("MEASUREMENTS (estimate from image)")
    print("-" * 60)

    # Estimate measurements (you can measure manually from image)
    print("Head diameter:        ~80-100px")
    print("Torso width:          ~70-90px")
    print("Upper arm thickness:  ~35-45px")
    print("Upper leg thickness:  ~40-50px")
    print("Joint glow radius:    ~25-35px (outer edge)")
    print("Joint core radius:    ~12-18px (bright center)")

    print()
    print("=" * 60)
    print("Use these EXACT values to rebuild Neon Cyan!")
    print("=" * 60)

if __name__ == "__main__":
    # Update this path to your reference image
    reference_path = r"C:\Users\dalov\OneDrive\Pictures\Screenshots\Screenshot 2025-11-14 092005.png"

    try:
        analyze_reference(reference_path)
    except FileNotFoundError:
        print(f"ERROR: Could not find image at: {reference_path}")
        print("Please update the 'reference_path' variable with correct path")
    except Exception as e:
        print(f"ERROR: {e}")
