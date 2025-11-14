"""
Manual Rig System
Advanced manual bone placement and editing for custom stick figure rigs.

Features:
- T-pose template as starting point
- Interactive bone creation and editing
- Parent-child bone linking
- Symmetry tools (mirror left/right)
- Bone transformation (move, rotate, resize)
- Hierarchy validation
- Constraint editing
"""

import numpy as np
from typing import Optional, List, Tuple, Dict
from copy import deepcopy

from .skeleton import Skeleton, Bone, BoneType
from .auto_rig import AutoRig, BodyType


# ============================================================================
# MANUAL RIG BUILDER
# ============================================================================

class ManualRig:
    """
    Manual rigging tools for advanced skeleton customization.
    Allows precise control over bone placement and hierarchy.
    """

    def __init__(self):
        """Initialize manual rig builder."""
        self.current_skeleton: Optional[Skeleton] = None
        self.selected_bone: Optional[Bone] = None
        self.bone_creation_mode = False

        print("✓ Manual Rig system initialized")

    # ========================================================================
    # T-POSE TEMPLATE
    # ========================================================================

    def create_t_pose_template(self, name: str = "T-Pose") -> Skeleton:
        """
        Create a T-pose skeleton template as starting point for manual editing.
        T-pose has arms extended horizontally.

        Args:
            name: Skeleton name

        Returns:
            Skeleton in T-pose
        """
        print(f"Creating T-pose template '{name}'...")

        # Start with auto-rigged skeleton
        auto_rig = AutoRig()
        skeleton = auto_rig.create_skeleton(name, BodyType.NORMAL)

        # Adjust to T-pose (arms horizontal)
        # Left arm
        upper_arm_l = skeleton.get_bone("upper_arm_l")
        if upper_arm_l:
            upper_arm_l.set_local_rotation(0.0, 0.0, -90.0)  # Point left

        forearm_l = skeleton.get_bone("forearm_l")
        if forearm_l:
            forearm_l.set_local_rotation(0.0, 0.0, 0.0)  # Straight

        hand_l = skeleton.get_bone("hand_l")
        if hand_l:
            hand_l.set_local_rotation(0.0, 0.0, 0.0)

        # Right arm
        upper_arm_r = skeleton.get_bone("upper_arm_r")
        if upper_arm_r:
            upper_arm_r.set_local_rotation(0.0, 0.0, 90.0)  # Point right

        forearm_r = skeleton.get_bone("forearm_r")
        if forearm_r:
            forearm_r.set_local_rotation(0.0, 0.0, 0.0)  # Straight

        hand_r = skeleton.get_bone("hand_r")
        if hand_r:
            hand_r.set_local_rotation(0.0, 0.0, 0.0)

        # Legs straight down (rotate 180 degrees to point downward)
        for side in ["l", "r"]:
            thigh = skeleton.get_bone(f"thigh_{side}")
            if thigh:
                thigh.set_local_rotation(0.0, 0.0, 180.0)  # Point downward

            shin = skeleton.get_bone(f"shin_{side}")
            if shin:
                shin.set_local_rotation(0.0, 0.0, 0.0)  # Straight continuation

            foot = skeleton.get_bone(f"foot_{side}")
            if foot:
                foot.set_local_rotation(0.0, 0.0, -90.0)  # Point forward (perpendicular to shin)

        skeleton.update()

        print("✓ T-pose template created")

        self.current_skeleton = skeleton
        return skeleton

    # ========================================================================
    # BONE CREATION
    # ========================================================================

    def add_bone(self, name: str, position: Tuple[float, float, float],
                 length: float = 1.0, parent_name: Optional[str] = None) -> Bone:
        """
        Manually add a new bone to the skeleton.

        Args:
            name: Bone name (must be unique)
            position: Local position (x, y, z) relative to parent
            length: Bone length
            parent_name: Parent bone name (None for root)

        Returns:
            Created Bone instance

        Raises:
            ValueError: If skeleton not initialized or bone name exists
        """
        if self.current_skeleton is None:
            raise ValueError("No skeleton loaded. Create a template first.")

        if name in self.current_skeleton.bones:
            raise ValueError(f"Bone '{name}' already exists")

        # Create bone
        bone = Bone(
            name=name,
            local_position=np.array(position, dtype=np.float32),
            length=length,
            thickness=0.05,
            color=np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32),
        )

        # Add to skeleton
        self.current_skeleton.add_bone(bone, parent_name)

        print(f"✓ Added bone '{name}' (parent: {parent_name})")

        return bone

    def duplicate_bone(self, source_name: str, new_name: str,
                      mirror: bool = False) -> Optional[Bone]:
        """
        Duplicate an existing bone with optional mirroring.

        Args:
            source_name: Name of bone to duplicate
            new_name: Name for the new bone
            mirror: If True, mirror position across Y axis

        Returns:
            Duplicated Bone or None if source not found
        """
        if self.current_skeleton is None:
            return None

        source_bone = self.current_skeleton.get_bone(source_name)
        if source_bone is None:
            print(f"Warning: Bone '{source_name}' not found")
            return None

        # Create new bone with same properties
        new_bone = Bone(
            name=new_name,
            local_position=source_bone.local_position.copy(),
            local_rotation=source_bone.local_rotation.copy(),
            local_scale=source_bone.local_scale.copy(),
            length=source_bone.length,
            thickness=source_bone.thickness,
            color=source_bone.color.copy(),
        )

        # Mirror if requested
        if mirror:
            new_bone.local_position[0] *= -1  # Flip X position
            new_bone.local_rotation[2] *= -1  # Flip Z rotation

        # Add to skeleton (same parent as source)
        parent_name = source_bone.parent.name if source_bone.parent else None
        self.current_skeleton.add_bone(new_bone, parent_name)

        print(f"✓ Duplicated bone '{source_name}' -> '{new_name}' (mirrored: {mirror})")

        return new_bone

    def remove_bone(self, name: str):
        """
        Remove a bone and all its descendants.

        Args:
            name: Bone name to remove
        """
        if self.current_skeleton is None:
            return

        self.current_skeleton.remove_bone(name)
        print(f"✓ Removed bone '{name}' and descendants")

    # ========================================================================
    # BONE EDITING
    # ========================================================================

    def move_bone(self, name: str, x: float, y: float, z: float = 0.0):
        """
        Move a bone to a new local position.

        Args:
            name: Bone name
            x, y, z: New local position
        """
        if self.current_skeleton is None:
            return

        bone = self.current_skeleton.get_bone(name)
        if bone:
            bone.set_local_position(x, y, z)
            print(f"✓ Moved bone '{name}' to ({x}, {y}, {z})")

    def rotate_bone(self, name: str, x: float, y: float, z: float):
        """
        Set bone rotation.

        Args:
            name: Bone name
            x, y, z: Euler angles in degrees
        """
        if self.current_skeleton is None:
            return

        bone = self.current_skeleton.get_bone(name)
        if bone:
            bone.set_local_rotation(x, y, z)
            print(f"✓ Rotated bone '{name}' to ({x}, {y}, {z})")

    def resize_bone(self, name: str, length: float):
        """
        Change bone length.

        Args:
            name: Bone name
            length: New length
        """
        if self.current_skeleton is None:
            return

        bone = self.current_skeleton.get_bone(name)
        if bone:
            bone.length = max(0.01, length)
            bone.mark_dirty()
            print(f"✓ Resized bone '{name}' to length {length}")

    def set_bone_thickness(self, name: str, thickness: float):
        """
        Change bone visual thickness.

        Args:
            name: Bone name
            thickness: New thickness
        """
        if self.current_skeleton is None:
            return

        bone = self.current_skeleton.get_bone(name)
        if bone:
            bone.thickness = max(0.01, thickness)
            print(f"✓ Set bone '{name}' thickness to {thickness}")

    def set_bone_color(self, name: str, r: float, g: float, b: float, a: float = 1.0):
        """
        Change bone color.

        Args:
            name: Bone name
            r, g, b, a: Color components (0.0 - 1.0)
        """
        if self.current_skeleton is None:
            return

        bone = self.current_skeleton.get_bone(name)
        if bone:
            bone.color = np.array([r, g, b, a], dtype=np.float32)
            print(f"✓ Set bone '{name}' color to ({r}, {g}, {b}, {a})")

    # ========================================================================
    # HIERARCHY EDITING
    # ========================================================================

    def reparent_bone(self, bone_name: str, new_parent_name: Optional[str]):
        """
        Change a bone's parent (re-parent in hierarchy).

        Args:
            bone_name: Bone to reparent
            new_parent_name: New parent bone name (None for root)

        Raises:
            ValueError: If would create cycle or bone not found
        """
        if self.current_skeleton is None:
            return

        bone = self.current_skeleton.get_bone(bone_name)
        if bone is None:
            print(f"Warning: Bone '{bone_name}' not found")
            return

        # Remove from current parent
        if bone.parent:
            bone.parent.remove_child(bone)

        # Add to new parent
        if new_parent_name is None:
            # Make new root
            if self.current_skeleton.root_bone is not None:
                print("Warning: Skeleton already has a root. Creating disconnected bone.")
        else:
            new_parent = self.current_skeleton.get_bone(new_parent_name)
            if new_parent is None:
                print(f"Warning: Parent bone '{new_parent_name}' not found")
                return

            new_parent.add_child(bone)

        print(f"✓ Reparented bone '{bone_name}' to '{new_parent_name}'")

    # ========================================================================
    # CONSTRAINT EDITING
    # ========================================================================

    def set_rotation_limits(self, bone_name: str,
                           min_x: float, min_y: float, min_z: float,
                           max_x: float, max_y: float, max_z: float):
        """
        Set rotation constraints for a bone.

        Args:
            bone_name: Bone name
            min_x, min_y, min_z: Minimum rotation angles
            max_x, max_y, max_z: Maximum rotation angles
        """
        if self.current_skeleton is None:
            return

        bone = self.current_skeleton.get_bone(bone_name)
        if bone:
            bone.set_rotation_limits(
                (min_x, min_y, min_z),
                (max_x, max_y, max_z)
            )
            print(f"✓ Set rotation limits for bone '{bone_name}'")

    def remove_rotation_limits(self, bone_name: str):
        """
        Remove rotation constraints (allow free rotation).

        Args:
            bone_name: Bone name
        """
        self.set_rotation_limits(
            bone_name,
            -180.0, -180.0, -180.0,
            180.0, 180.0, 180.0
        )
        print(f"✓ Removed rotation limits for bone '{bone_name}'")

    # ========================================================================
    # SYMMETRY TOOLS
    # ========================================================================

    def mirror_bone_hierarchy(self, source_bone_name: str,
                             prefix_map: Dict[str, str]):
        """
        Mirror an entire bone hierarchy (useful for left/right symmetry).

        Args:
            source_bone_name: Root bone of hierarchy to mirror
            prefix_map: Mapping of name prefixes (e.g., {"_l": "_r"})

        Example:
            mirror_bone_hierarchy("upper_arm_l", {"_l": "_r"})
            Creates upper_arm_r, forearm_r, hand_r
        """
        if self.current_skeleton is None:
            return

        source_bone = self.current_skeleton.get_bone(source_bone_name)
        if source_bone is None:
            print(f"Warning: Source bone '{source_bone_name}' not found")
            return

        # Find replacement in name
        new_name = source_bone_name
        for old_prefix, new_prefix in prefix_map.items():
            if old_prefix in new_name:
                new_name = new_name.replace(old_prefix, new_prefix)
                break

        # Duplicate bone (mirrored)
        self.duplicate_bone(source_bone_name, new_name, mirror=True)

        # Recursively mirror children
        for child in source_bone.children:
            self.mirror_bone_hierarchy(child.name, prefix_map)

        print(f"✓ Mirrored bone hierarchy '{source_bone_name}' -> '{new_name}'")

    def mirror_left_to_right(self):
        """
        Convenience function to mirror all left bones to right side.
        Assumes bones use "_l" and "_r" suffixes.
        """
        # Find all left bones
        left_bones = [name for name in self.current_skeleton.bones.keys() if "_l" in name]

        for left_name in left_bones:
            right_name = left_name.replace("_l", "_r")

            # Skip if right already exists
            if right_name in self.current_skeleton.bones:
                continue

            # Mirror the bone
            self.duplicate_bone(left_name, right_name, mirror=True)

        print("✓ Mirrored all left bones to right side")

    # ========================================================================
    # VALIDATION
    # ========================================================================

    def validate_hierarchy(self) -> Tuple[bool, List[str]]:
        """
        Validate the skeleton hierarchy for common issues.

        Returns:
            (is_valid, error_messages)
        """
        if self.current_skeleton is None:
            return (False, ["No skeleton loaded"])

        errors = []

        # Check for root bone
        if self.current_skeleton.root_bone is None:
            errors.append("No root bone found")

        # Check for cycles (should be prevented by Bone class, but double-check)
        for bone in self.current_skeleton.bones.values():
            visited = set()
            current = bone
            while current is not None:
                if current in visited:
                    errors.append(f"Cycle detected in hierarchy at bone '{bone.name}'")
                    break
                visited.add(current)
                current = current.parent

        # Check for orphaned bones
        for bone in self.current_skeleton.bones.values():
            if bone.parent is None and bone != self.current_skeleton.root_bone:
                errors.append(f"Orphaned bone '{bone.name}' (no parent, not root)")

        # Check for invalid bone properties
        for bone in self.current_skeleton.bones.values():
            if bone.length <= 0:
                errors.append(f"Bone '{bone.name}' has invalid length: {bone.length}")

            if bone.thickness <= 0:
                errors.append(f"Bone '{bone.name}' has invalid thickness: {bone.thickness}")

        is_valid = len(errors) == 0

        if is_valid:
            print("✓ Skeleton hierarchy is valid")
        else:
            print(f"❌ Skeleton has {len(errors)} validation errors:")
            for error in errors:
                print(f"  - {error}")

        return (is_valid, errors)

    # ========================================================================
    # SELECTION
    # ========================================================================

    def select_bone(self, name: str):
        """Select a bone for editing."""
        if self.current_skeleton is None:
            return

        bone = self.current_skeleton.get_bone(name)
        if bone:
            self.selected_bone = bone
            print(f"✓ Selected bone '{name}'")

    def deselect_bone(self):
        """Deselect current bone."""
        self.selected_bone = None
        print("✓ Deselected bone")

    # ========================================================================
    # SKELETON OPERATIONS
    # ========================================================================

    def get_skeleton(self) -> Optional[Skeleton]:
        """Get the current skeleton."""
        return self.current_skeleton

    def load_skeleton(self, skeleton: Skeleton):
        """Load an existing skeleton for editing."""
        self.current_skeleton = skeleton
        print(f"✓ Loaded skeleton '{skeleton.name}' for editing")

    def clear_skeleton(self):
        """Clear the current skeleton."""
        self.current_skeleton = None
        self.selected_bone = None
        print("✓ Cleared skeleton")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_manual_rig() -> ManualRig:
    """Create a manual rig instance with T-pose template."""
    manual_rig = ManualRig()
    manual_rig.create_t_pose_template()
    return manual_rig
