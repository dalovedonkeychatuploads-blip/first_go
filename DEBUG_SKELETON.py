"""Quick debug to see skeleton joint positions"""
from toon_anatomy import create_neon_cyan_anatomy
from rig_system import create_t_pose_skeleton_from_anatomy

anatomy = create_neon_cyan_anatomy()
skeleton = create_t_pose_skeleton_from_anatomy(anatomy)
transforms = skeleton.get_joint_transforms()

print("\n" + "="*60)
print("SKELETON JOINT POSITIONS (T-POSE)")
print("="*60)

for name, (x, y) in sorted(transforms.items(), key=lambda item: -item[1][1]):
    print(f"{name:20s}  X={x:8.1f}  Y={y:8.1f}")

print("\n" + "="*60)
print(f"Bounding box:")
all_x = [pos[0] for pos in transforms.values()]
all_y = [pos[1] for pos in transforms.values()]
print(f"  X range: {min(all_x):.1f} to {max(all_x):.1f} (width: {max(all_x)-min(all_x):.1f})")
print(f"  Y range: {min(all_y):.1f} to {max(all_y):.1f} (height: {max(all_y)-min(all_y):.1f})")
print("="*60 + "\n")

print("Expected for T-pose:")
print("  - Head should have HIGHEST Y value (top)")
print("  - Feet should have LOWEST Y value (bottom)")
print("  - Left hand should have LOWEST X (left)")
print("  - Right hand should have HIGHEST X (right)")
print("\nDoes the output above match these expectations?")
