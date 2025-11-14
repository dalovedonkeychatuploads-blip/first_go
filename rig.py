"""
Hierarchical Skeletal Rig System
Professional bone-based character rig with forward kinematics and constraints.
"""

import math
import json
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Optional
from enum import Enum


class BoneType(Enum):
    """Types of bones in the skeleton."""
    ROOT = "root"
    SPINE = "spine"
    LIMB = "limb"
    EXTREMITY = "extremity"
    HEAD = "head"


class VisualStyle(Enum):
    """Visual styles for the stick figure."""
    NEON_CYAN = "neon_cyan"
    SHADOW_RED = "shadow_red"
    CLASSIC_CAPSULE = "classic_capsule"


@dataclass
class BoneConstraint:
    """Angle constraints for a bone."""
    min_x: float = -180.0
    max_x: float = 180.0
    min_y: float = -180.0
    max_y: float = 180.0
    min_z: float = -180.0
    max_z: float = 180.0

    def clamp(self, angle: float, axis: str = 'x') -> float:
        """Clamp angle to valid range for given axis."""
        if axis == 'x':
            return max(self.min_x, min(self.max_x, angle))
        elif axis == 'y':
            return max(self.min_y, min(self.max_y, angle))
        elif axis == 'z':
            return max(self.min_z, min(self.max_z, angle))
        return angle


@dataclass
class BoneVisualStyle:
    """Visual properties for rendering a bone."""
    shape: str = "capsule"  # capsule, cylinder, sphere, box
    color: Tuple[float, float, float] = (0.1, 0.1, 0.1)  # RGB
    glow_color: Optional[Tuple[float, float, float]] = None
    glow_intensity: float = 0.0
    glow_radius: float = 1.0
    thickness_multiplier: float = 1.0


@dataclass
class Bone:
    """A single bone in the skeletal hierarchy."""
    name: str
    parent_name: Optional[str]
    rest_length: float
    rest_rotation: Tuple[float, float, float] = (0, 0, 0)  # Euler angles in degrees
    local_rotation: Tuple[float, float, float] = (0, 0, 0)  # Animated offset
    constraint: BoneConstraint = field(default_factory=BoneConstraint)
    bone_type: BoneType = BoneType.LIMB
    thickness: float = 1.0
    visual_style: BoneVisualStyle = field(default_factory=BoneVisualStyle)
    z_order: int = 0  # For depth sorting

    def get_total_rotation(self) -> Tuple[float, float, float]:
        """Get combined rest + local rotation."""
        return tuple(r + l for r, l in zip(self.rest_rotation, self.local_rotation))

    def set_local_rotation(self, x: float, y: float, z: float):
        """Set local rotation with constraints applied."""
        self.local_rotation = (
            self.constraint.clamp(x, 'x'),
            self.constraint.clamp(y, 'y'),
            self.constraint.clamp(z, 'z')
        )


class StickRig:
    """Complete hierarchical skeleton for a stick figure."""

    def __init__(self):
        self.bones: Dict[str, Bone] = {}
        self.visual_style = VisualStyle.NEON_CYAN
        self.overall_scale = 1.0
        self.create_default_skeleton()

    def create_default_skeleton(self):
        """Create the default T-pose skeleton."""
        # Define realistic joint constraints
        spine_constraint = BoneConstraint(-20, 40, -20, 20, -35, 35)
        neck_constraint = BoneConstraint(-20, 20, -45, 45, -15, 15)
        shoulder_constraint = BoneConstraint(-40, 120, -90, 90, -90, 90)
        elbow_constraint = BoneConstraint(0, 135, -30, 30, -90, 90)
        hip_constraint = BoneConstraint(-30, 90, -45, 45, -45, 45)
        knee_constraint = BoneConstraint(0, 135, -10, 10, -10, 10)
        foot_constraint = BoneConstraint(-20, 20, -30, 30, -15, 15)

        # Root and spine
        self.add_bone(Bone("pelvis", None, 0, bone_type=BoneType.ROOT, thickness=1.2))
        self.add_bone(Bone("spine_lower", "pelvis", 3, rest_rotation=(0, 0, 0),
                          constraint=spine_constraint, bone_type=BoneType.SPINE, thickness=1.1))
        self.add_bone(Bone("spine_upper", "spine_lower", 3,
                          constraint=spine_constraint, bone_type=BoneType.SPINE, thickness=1.1))
        self.add_bone(Bone("neck", "spine_upper", 1,
                          constraint=neck_constraint, bone_type=BoneType.SPINE, thickness=0.7))
        self.add_bone(Bone("head", "neck", 2.5, bone_type=BoneType.HEAD, thickness=1.5))

        # Left arm
        self.add_bone(Bone("clavicle_L", "spine_upper", 1, rest_rotation=(0, 0, 15),
                          bone_type=BoneType.LIMB, thickness=0.6))
        self.add_bone(Bone("upper_arm_L", "clavicle_L", 3.5, rest_rotation=(0, 0, 75),
                          constraint=shoulder_constraint, thickness=0.8))
        self.add_bone(Bone("lower_arm_L", "upper_arm_L", 3,
                          constraint=elbow_constraint, thickness=0.7))
        self.add_bone(Bone("hand_L", "lower_arm_L", 1,
                          bone_type=BoneType.EXTREMITY, thickness=0.6))

        # Right arm
        self.add_bone(Bone("clavicle_R", "spine_upper", 1, rest_rotation=(0, 0, -15),
                          bone_type=BoneType.LIMB, thickness=0.6))
        self.add_bone(Bone("upper_arm_R", "clavicle_R", 3.5, rest_rotation=(0, 0, -75),
                          constraint=shoulder_constraint, thickness=0.8))
        self.add_bone(Bone("lower_arm_R", "upper_arm_R", 3,
                          constraint=elbow_constraint, thickness=0.7))
        self.add_bone(Bone("hand_R", "lower_arm_R", 1,
                          bone_type=BoneType.EXTREMITY, thickness=0.6))

        # Left leg
        self.add_bone(Bone("thigh_L", "pelvis", 4, rest_rotation=(0, 0, 5),
                          constraint=hip_constraint, thickness=1.0, z_order=-1))
        self.add_bone(Bone("shin_L", "thigh_L", 3.5,
                          constraint=knee_constraint, thickness=0.9, z_order=-1))
        self.add_bone(Bone("foot_L", "shin_L", 1.5, rest_rotation=(-90, 0, 0),
                          constraint=foot_constraint, bone_type=BoneType.EXTREMITY,
                          thickness=0.7, z_order=-1))

        # Right leg
        self.add_bone(Bone("thigh_R", "pelvis", 4, rest_rotation=(0, 0, -5),
                          constraint=hip_constraint, thickness=1.0))
        self.add_bone(Bone("shin_R", "thigh_R", 3.5,
                          constraint=knee_constraint, thickness=0.9))
        self.add_bone(Bone("foot_R", "shin_R", 1.5, rest_rotation=(-90, 0, 0),
                          constraint=foot_constraint, bone_type=BoneType.EXTREMITY, thickness=0.7))

        self.apply_visual_style(VisualStyle.NEON_CYAN)

    def add_bone(self, bone: Bone):
        """Add a bone to the skeleton."""
        self.bones[bone.name] = bone

    def get_bone(self, name: str) -> Optional[Bone]:
        """Get a bone by name."""
        return self.bones.get(name)

    def apply_visual_style(self, style: VisualStyle):
        """Apply a visual style to all bones."""
        self.visual_style = style

        for bone in self.bones.values():
            if style == VisualStyle.NEON_CYAN:
                bone.visual_style = BoneVisualStyle(
                    shape="capsule",
                    color=(0.05, 0.05, 0.08),
                    glow_color=(0, 1, 1) if bone.bone_type == BoneType.LIMB else None,
                    glow_intensity=0.8 if bone.bone_type == BoneType.LIMB else 0,
                    glow_radius=1.5
                )
                # Special eyes for head
                if bone.name == "head":
                    bone.visual_style.glow_color = (0, 1, 1)
                    bone.visual_style.glow_intensity = 1.0

            elif style == VisualStyle.SHADOW_RED:
                bone.visual_style = BoneVisualStyle(
                    shape="capsule",
                    color=(0.08, 0.02, 0.02),
                    glow_color=None,
                    glow_intensity=0,
                )
                # Red glowing eyes for head
                if bone.name == "head":
                    bone.visual_style.glow_color = (1, 0, 0)
                    bone.visual_style.glow_intensity = 1.0

            elif style == VisualStyle.CLASSIC_CAPSULE:
                bone.visual_style = BoneVisualStyle(
                    shape="capsule",
                    color=(0.1, 0.1, 0.1),
                    glow_color=None,
                    glow_intensity=0,
                    thickness_multiplier=1.2  # Slightly thicker for cartoon look
                )

    def set_bone_angle(self, bone_name: str, x: float, y: float, z: float):
        """Set a bone's local rotation angles (in degrees)."""
        bone = self.get_bone(bone_name)
        if bone:
            bone.set_local_rotation(x, y, z)

    def get_joint_transform(self, bone_name: str) -> Dict[str, any]:
        """Calculate global position and rotation for a bone using forward kinematics."""
        transforms = {}

        def calculate_transform(name: str, parent_pos: np.ndarray = None,
                               parent_rot: np.ndarray = None) -> Dict:
            if name not in self.bones:
                return None

            bone = self.bones[name]

            # Start with parent transform or origin
            if parent_pos is None:
                parent_pos = np.array([0, 0, 0], dtype=float)
            if parent_rot is None:
                parent_rot = np.array([0, 0, 0], dtype=float)

            # Add bone's rotation to parent's
            total_rot = parent_rot + np.array(bone.get_total_rotation())

            # Calculate bone endpoint using rotation and length
            # Simplified for 2D/2.5D visualization
            angle_rad = math.radians(total_rot[2])  # Use Z rotation for 2D
            dx = bone.rest_length * math.cos(angle_rad) * self.overall_scale
            dy = bone.rest_length * math.sin(angle_rad) * self.overall_scale

            end_pos = parent_pos + np.array([dx, dy, 0])

            return {
                'start': parent_pos.tolist(),
                'end': end_pos.tolist(),
                'rotation': total_rot.tolist(),
                'bone': bone
            }

        # Build transform hierarchy
        def process_bone(name: str, parent_transform: Optional[Dict] = None):
            if parent_transform:
                parent_end = np.array(parent_transform['end'])
                parent_rot = np.array(parent_transform['rotation'])
            else:
                parent_end = None
                parent_rot = None

            transform = calculate_transform(name, parent_end, parent_rot)
            if transform:
                transforms[name] = transform

                # Process children
                for child_name, child_bone in self.bones.items():
                    if child_bone.parent_name == name:
                        process_bone(child_name, transform)

        # Start from root
        process_bone("pelvis")
        return transforms

    def reset_to_rest_pose(self):
        """Reset all bones to their rest pose (T-pose)."""
        for bone in self.bones.values():
            bone.local_rotation = (0, 0, 0)

    def apply_proportion_profile(self, profile: Dict[str, float]):
        """Apply proportion multipliers to bone lengths and thickness."""
        for bone_name, multiplier in profile.items():
            bone = self.get_bone(bone_name)
            if bone:
                if "length" in bone_name:
                    bone.rest_length *= multiplier
                elif "thickness" in bone_name:
                    bone.thickness *= multiplier

    def to_json(self) -> str:
        """Serialize the rig to JSON."""
        data = {
            'visual_style': self.visual_style.value,
            'overall_scale': self.overall_scale,
            'bones': {}
        }

        for name, bone in self.bones.items():
            data['bones'][name] = {
                'parent': bone.parent_name,
                'rest_length': bone.rest_length,
                'rest_rotation': bone.rest_rotation,
                'local_rotation': bone.local_rotation,
                'thickness': bone.thickness,
                'bone_type': bone.bone_type.value,
                'z_order': bone.z_order
            }

        return json.dumps(data, indent=2)

    def from_json(self, json_str: str):
        """Load rig from JSON."""
        data = json.loads(json_str)
        self.visual_style = VisualStyle(data.get('visual_style', 'neon_cyan'))
        self.overall_scale = data.get('overall_scale', 1.0)

        # Recreate bones
        self.bones.clear()
        for name, bone_data in data.get('bones', {}).items():
            bone = Bone(
                name=name,
                parent_name=bone_data['parent'],
                rest_length=bone_data['rest_length'],
                rest_rotation=tuple(bone_data['rest_rotation']),
                local_rotation=tuple(bone_data['local_rotation']),
                thickness=bone_data['thickness'],
                bone_type=BoneType(bone_data['bone_type']),
                z_order=bone_data.get('z_order', 0)
            )
            self.add_bone(bone)

        self.apply_visual_style(self.visual_style)