"""
Stick Figure Rig System
"""

import math
from enum import Enum
from typing import Dict, Tuple, Optional


class VisualStyle(Enum):
    """Visual styles for the stick figure."""
    NEON_CYAN = "neon_cyan"
    SHADOW_RED = "shadow_red"
    CLASSIC_CAPSULE = "classic_capsule"


class Bone:
    """A single bone in the rig."""

    def __init__(self, name: str, parent: Optional[str] = None,
                 length: float = 1.0, rest_angle: float = 0):
        self.name = name
        self.parent = parent
        self.length = length
        self.rest_angle = rest_angle  # Rest pose angle
        self.local_angle = 0  # Current rotation from rest
        self.thickness = 1.0
        self.constraints = (-180, 180)  # Min/max rotation


class StickmanRig:
    """Complete stick figure rig with hierarchical bones."""

    def __init__(self):
        self.bones = {}
        self.visual_style = VisualStyle.NEON_CYAN
        self.scale = 1.0
        self.create_default_rig()

    def create_default_rig(self):
        """Create the default T-pose rig."""
        # Pelvis/Root
        self.add_bone(Bone("pelvis", None, 0))

        # Spine
        self.add_bone(Bone("spine_lower", "pelvis", 20, 90))
        self.add_bone(Bone("spine_upper", "spine_lower", 20, 0))

        # Neck and head
        self.add_bone(Bone("neck", "spine_upper", 10, 0))
        self.add_bone(Bone("head", "neck", 15, 0))

        # Left arm
        self.add_bone(Bone("upper_arm_L", "spine_upper", 30, 180))
        self.add_bone(Bone("lower_arm_L", "upper_arm_L", 25, 0))
        self.add_bone(Bone("hand_L", "lower_arm_L", 10, 0))

        # Right arm
        self.add_bone(Bone("upper_arm_R", "spine_upper", 30, 0))
        self.add_bone(Bone("lower_arm_R", "upper_arm_R", 25, 0))
        self.add_bone(Bone("hand_R", "lower_arm_R", 10, 0))

        # Left leg
        self.add_bone(Bone("thigh_L", "pelvis", 35, -95))
        self.add_bone(Bone("shin_L", "thigh_L", 35, 0))
        self.add_bone(Bone("foot_L", "shin_L", 10, 90))

        # Right leg
        self.add_bone(Bone("thigh_R", "pelvis", 35, -85))
        self.add_bone(Bone("shin_R", "thigh_R", 35, 0))
        self.add_bone(Bone("foot_R", "shin_R", 10, 90))

        # Set constraints
        self.set_constraints()

    def add_bone(self, bone: Bone):
        """Add a bone to the rig."""
        self.bones[bone.name] = bone

    def set_constraints(self):
        """Set rotation constraints for realistic movement."""
        # Spine constraints
        self.bones["spine_lower"].constraints = (-20, 40)
        self.bones["spine_upper"].constraints = (-20, 40)

        # Neck constraints
        self.bones["neck"].constraints = (-45, 45)
        self.bones["head"].constraints = (-30, 30)

        # Arm constraints
        self.bones["upper_arm_L"].constraints = (-90, 120)
        self.bones["lower_arm_L"].constraints = (0, 135)
        self.bones["upper_arm_R"].constraints = (-90, 120)
        self.bones["lower_arm_R"].constraints = (0, 135)

        # Leg constraints
        self.bones["thigh_L"].constraints = (-30, 90)
        self.bones["shin_L"].constraints = (0, 135)
        self.bones["thigh_R"].constraints = (-30, 90)
        self.bones["shin_R"].constraints = (0, 135)

    def get_bone(self, name: str) -> Optional[Bone]:
        """Get a bone by name."""
        return self.bones.get(name)

    def get_joint_transforms(self) -> Dict[str, Tuple[float, float]]:
        """Calculate global positions for all joints."""
        transforms = {}

        def calculate_transform(bone_name: str, parent_pos: Tuple[float, float] = (0, 0),
                              parent_angle: float = 0) -> Tuple[float, float]:
            if bone_name not in self.bones:
                return parent_pos

            bone = self.bones[bone_name]

            # Calculate total angle
            total_angle = parent_angle + bone.rest_angle + bone.local_angle

            # Calculate end position
            angle_rad = math.radians(total_angle)
            dx = bone.length * self.scale * math.cos(angle_rad)
            dy = bone.length * self.scale * math.sin(angle_rad)

            end_pos = (parent_pos[0] + dx, parent_pos[1] + dy)

            # Store position
            transforms[bone_name] = end_pos

            # Process children
            for child_name, child_bone in self.bones.items():
                if child_bone.parent == bone_name:
                    calculate_transform(child_name, end_pos, total_angle)

            return end_pos

        # Start from root
        transforms["pelvis"] = (0, 0)
        for bone_name, bone in self.bones.items():
            if bone.parent == "pelvis" or (bone.parent is None and bone_name != "pelvis"):
                calculate_transform(bone_name)

        return transforms

    def set_bone_rotation(self, bone_name: str, angle: float):
        """Set a bone's local rotation."""
        bone = self.get_bone(bone_name)
        if bone:
            # Apply constraints
            min_angle, max_angle = bone.constraints
            angle = max(min_angle, min(max_angle, angle))
            bone.local_angle = angle

    def reset_to_rest_pose(self):
        """Reset all bones to T-pose."""
        for bone in self.bones.values():
            bone.local_angle = 0

    def apply_visual_style(self, style: VisualStyle):
        """Apply a visual style to the rig."""
        self.visual_style = style

    def set_proportions(self, proportions: Dict[str, float]):
        """Set body proportions."""
        if "height" in proportions:
            self.scale = proportions["height"]

        if "arm_length" in proportions:
            multiplier = proportions["arm_length"]
            self.bones["upper_arm_L"].length = 30 * multiplier
            self.bones["upper_arm_R"].length = 30 * multiplier
            self.bones["lower_arm_L"].length = 25 * multiplier
            self.bones["lower_arm_R"].length = 25 * multiplier

        if "leg_length" in proportions:
            multiplier = proportions["leg_length"]
            self.bones["thigh_L"].length = 35 * multiplier
            self.bones["thigh_R"].length = 35 * multiplier
            self.bones["shin_L"].length = 35 * multiplier
            self.bones["shin_R"].length = 35 * multiplier

        if "torso_height" in proportions:
            multiplier = proportions["torso_height"]
            self.bones["spine_lower"].length = 20 * multiplier
            self.bones["spine_upper"].length = 20 * multiplier

        if "head_size" in proportions:
            self.bones["head"].length = 15 * proportions["head_size"]

    def mirror_pose(self, from_side: str = "L", to_side: str = "R"):
        """Mirror pose from one side to another."""
        for bone_name, bone in self.bones.items():
            if from_side in bone_name:
                mirror_name = bone_name.replace(from_side, to_side)
                mirror_bone = self.get_bone(mirror_name)
                if mirror_bone:
                    mirror_bone.local_angle = -bone.local_angle

    def save_to_dict(self) -> dict:
        """Save rig to dictionary."""
        return {
            "visual_style": self.visual_style.value,
            "scale": self.scale,
            "bones": {
                name: {
                    "parent": bone.parent,
                    "length": bone.length,
                    "rest_angle": bone.rest_angle,
                    "local_angle": bone.local_angle,
                    "thickness": bone.thickness
                }
                for name, bone in self.bones.items()
            }
        }

    def load_from_dict(self, data: dict):
        """Load rig from dictionary."""
        self.visual_style = VisualStyle(data.get("visual_style", "neon_cyan"))
        self.scale = data.get("scale", 1.0)

        self.bones.clear()
        for name, bone_data in data.get("bones", {}).items():
            bone = Bone(
                name=name,
                parent=bone_data["parent"],
                length=bone_data["length"],
                rest_angle=bone_data["rest_angle"]
            )
            bone.local_angle = bone_data.get("local_angle", 0)
            bone.thickness = bone_data.get("thickness", 1.0)
            self.add_bone(bone)

        self.set_constraints()