"""
Auto-Rig System
Automatic skeleton generation for stick figure characters.

Features:
- One-click creation of complete stick figure skeleton
- Anatomically correct bone hierarchy and proportions
- Customizable proportions (height, limb lengths, body width)
- Realistic rotation constraints per bone
- Weapon attachment points on hands
- Multiple body type presets (normal, muscular, thin, child, giant)
"""

import numpy as np
from typing import Optional, Tuple
from enum import Enum

from .skeleton import Skeleton, Bone, BoneType


# ============================================================================
# BODY TYPE PRESETS
# ============================================================================

class BodyType(Enum):
    """Predefined body type presets with different proportions."""
    NORMAL = "normal"          # Average human proportions
    MUSCULAR = "muscular"      # Broader shoulders, thicker limbs
    THIN = "thin"              # Narrower frame, longer limbs
    CHILD = "child"            # Shorter limbs, larger head ratio
    GIANT = "giant"            # Massive frame, thick limbs


# ============================================================================
# PROPORTION PARAMETERS
# ============================================================================

class ProportionParameters:
    """
    Customizable proportion parameters for stick figure.
    All values are relative to a base height of 2.0 units.
    """

    def __init__(self):
        # Overall scale
        self.height_scale = 1.0         # Overall character height multiplier

        # Torso proportions
        self.spine_length = 0.6         # Torso length
        self.neck_length = 0.15         # Neck length
        self.head_size = 0.25           # Head radius
        self.shoulder_width = 0.4       # Distance from spine to shoulder

        # Arm proportions
        self.upper_arm_length = 0.35    # Upper arm bone length
        self.forearm_length = 0.35      # Forearm bone length
        self.hand_size = 0.12           # Hand size

        # Leg proportions
        self.thigh_length = 0.45        # Thigh bone length
        self.shin_length = 0.45         # Shin bone length
        self.foot_size = 0.15           # Foot length

        # Thickness
        self.bone_thickness = 0.05      # Visual bone thickness

    def apply_body_type(self, body_type: BodyType):
        """Apply a preset body type."""
        if body_type == BodyType.NORMAL:
            # Default proportions (already set)
            pass

        elif body_type == BodyType.MUSCULAR:
            self.shoulder_width = 0.5
            self.upper_arm_length = 0.38
            self.forearm_length = 0.38
            self.bone_thickness = 0.08

        elif body_type == BodyType.THIN:
            self.shoulder_width = 0.3
            self.upper_arm_length = 0.4
            self.forearm_length = 0.4
            self.thigh_length = 0.5
            self.shin_length = 0.5
            self.bone_thickness = 0.03

        elif body_type == BodyType.CHILD:
            self.height_scale = 0.7
            self.head_size = 0.3  # Proportionally larger head
            self.spine_length = 0.5
            self.upper_arm_length = 0.28
            self.forearm_length = 0.28
            self.thigh_length = 0.35
            self.shin_length = 0.35

        elif body_type == BodyType.GIANT:
            self.height_scale = 1.5
            self.shoulder_width = 0.6
            self.spine_length = 0.7
            self.bone_thickness = 0.1


# ============================================================================
# AUTO-RIG BUILDER
# ============================================================================

class AutoRig:
    """
    Automatic skeleton builder for stick figures.
    Creates a complete rigged character with one function call.
    """

    def __init__(self):
        """Initialize auto-rig builder."""
        self.proportions = ProportionParameters()

    # ========================================================================
    # MAIN RIG CREATION
    # ========================================================================

    def create_skeleton(self, name: str = "StickFigure",
                       body_type: BodyType = BodyType.NORMAL) -> Skeleton:
        """
        Create a complete stick figure skeleton with automatic rigging.

        Args:
            name: Skeleton identifier
            body_type: Preset body type

        Returns:
            Fully rigged Skeleton instance
        """
        print(f"Auto-rigging stick figure '{name}' (type: {body_type.value})...")

        # Apply body type preset
        self.proportions.apply_body_type(body_type)

        # Create skeleton
        skeleton = Skeleton(name)

        # Build bone hierarchy from bottom to top
        # This ensures proper forward kinematics propagation

        # 1. Root bone (hips/pelvis)
        root = self._create_root_bone()
        skeleton.add_bone(root)

        # 2. Spine (torso)
        spine = self._create_spine_bone()
        skeleton.add_bone(spine, root.name)

        # 3. Neck
        neck = self._create_neck_bone()
        skeleton.add_bone(neck, spine.name)

        # 4. Head
        head = self._create_head_bone()
        skeleton.add_bone(head, neck.name)

        # 5. Arms (left and right)
        # Left arm
        upper_arm_l = self._create_upper_arm_bone(is_left=True)
        skeleton.add_bone(upper_arm_l, spine.name)

        forearm_l = self._create_forearm_bone(is_left=True)
        skeleton.add_bone(forearm_l, upper_arm_l.name)

        hand_l = self._create_hand_bone(is_left=True)
        skeleton.add_bone(hand_l, forearm_l.name)

        # Right arm
        upper_arm_r = self._create_upper_arm_bone(is_left=False)
        skeleton.add_bone(upper_arm_r, spine.name)

        forearm_r = self._create_forearm_bone(is_left=False)
        skeleton.add_bone(forearm_r, upper_arm_r.name)

        hand_r = self._create_hand_bone(is_left=False)
        skeleton.add_bone(hand_r, forearm_r.name)

        # 6. Legs (left and right)
        # Left leg
        thigh_l = self._create_thigh_bone(is_left=True)
        skeleton.add_bone(thigh_l, root.name)

        shin_l = self._create_shin_bone(is_left=True)
        skeleton.add_bone(shin_l, thigh_l.name)

        foot_l = self._create_foot_bone(is_left=True)
        skeleton.add_bone(foot_l, shin_l.name)

        # Right leg
        thigh_r = self._create_thigh_bone(is_left=False)
        skeleton.add_bone(thigh_r, root.name)

        shin_r = self._create_shin_bone(is_left=False)
        skeleton.add_bone(shin_r, thigh_r.name)

        foot_r = self._create_foot_bone(is_left=False)
        skeleton.add_bone(foot_r, shin_r.name)

        # Update all transforms
        skeleton.update()

        print(f"✓ Auto-rig complete: {len(skeleton.bones)} bones created")

        return skeleton

    # ========================================================================
    # BONE CREATION METHODS
    # ========================================================================

    def _create_root_bone(self) -> Bone:
        """Create root bone (hips/pelvis)."""
        bone = Bone(
            name="root",
            bone_type=BoneType.ROOT,
            local_position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            length=0.1,  # Root is very short
            thickness=self.proportions.bone_thickness * 1.5,
            color=np.array([0.8, 0.6, 0.4, 1.0], dtype=np.float32),  # Brownish
        )

        # Root can rotate freely (it's the base of the character)
        bone.set_rotation_limits((-30.0, -30.0, -180.0), (30.0, 30.0, 180.0))

        return bone

    def _create_spine_bone(self) -> Bone:
        """Create spine bone (torso)."""
        bone = Bone(
            name="spine",
            bone_type=BoneType.SPINE,
            local_position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            length=self.proportions.spine_length * self.proportions.height_scale,
            thickness=self.proportions.bone_thickness * 1.2,
            color=np.array([0.7, 0.5, 0.3, 1.0], dtype=np.float32),
        )

        # Spine can bend forward/backward and twist slightly
        bone.set_rotation_limits((-20.0, -10.0, -45.0), (20.0, 10.0, 45.0))

        return bone

    def _create_neck_bone(self) -> Bone:
        """Create neck bone."""
        bone = Bone(
            name="neck",
            bone_type=BoneType.NECK,
            local_position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            length=self.proportions.neck_length * self.proportions.height_scale,
            thickness=self.proportions.bone_thickness * 0.7,
            color=np.array([0.9, 0.8, 0.7, 1.0], dtype=np.float32),  # Lighter
        )

        # Neck can tilt and turn
        bone.set_rotation_limits((-30.0, -40.0, -60.0), (30.0, 40.0, 60.0))

        return bone

    def _create_head_bone(self) -> Bone:
        """Create head bone."""
        bone = Bone(
            name="head",
            bone_type=BoneType.HEAD,
            local_position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            length=self.proportions.head_size * 2.0 * self.proportions.height_scale,
            thickness=self.proportions.bone_thickness * 2.0,
            color=np.array([1.0, 0.9, 0.8, 1.0], dtype=np.float32),  # Skin tone
        )

        # Head can tilt slightly
        bone.set_rotation_limits((-20.0, -20.0, -30.0), (20.0, 20.0, 30.0))

        return bone

    def _create_upper_arm_bone(self, is_left: bool) -> Bone:
        """Create upper arm bone."""
        side_name = "l" if is_left else "r"
        side_multiplier = -1.0 if is_left else 1.0

        bone = Bone(
            name=f"upper_arm_{side_name}",
            bone_type=BoneType.UPPER_ARM_L if is_left else BoneType.UPPER_ARM_R,
            # Position at shoulder (offset from spine)
            local_position=np.array([
                side_multiplier * self.proportions.shoulder_width * self.proportions.height_scale,
                0.0,
                0.0
            ], dtype=np.float32),
            length=self.proportions.upper_arm_length * self.proportions.height_scale,
            thickness=self.proportions.bone_thickness,
            color=np.array([0.7, 0.5, 0.3, 1.0], dtype=np.float32),
        )

        # Shoulder can move in wide range
        bone.set_rotation_limits((-90.0, -45.0, -180.0), (90.0, 45.0, 180.0))

        return bone

    def _create_forearm_bone(self, is_left: bool) -> Bone:
        """Create forearm bone."""
        side_name = "l" if is_left else "r"

        bone = Bone(
            name=f"forearm_{side_name}",
            bone_type=BoneType.FOREARM_L if is_left else BoneType.FOREARM_R,
            local_position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            length=self.proportions.forearm_length * self.proportions.height_scale,
            thickness=self.proportions.bone_thickness * 0.9,
            color=np.array([0.8, 0.6, 0.4, 1.0], dtype=np.float32),
        )

        # Elbow can only bend forward (can't bend backward)
        bone.set_rotation_limits((0.0, 0.0, -150.0), (0.0, 0.0, 5.0))

        return bone

    def _create_hand_bone(self, is_left: bool) -> Bone:
        """Create hand bone (weapon attachment point)."""
        side_name = "l" if is_left else "r"

        bone = Bone(
            name=f"hand_{side_name}",
            bone_type=BoneType.HAND_L if is_left else BoneType.HAND_R,
            local_position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            length=self.proportions.hand_size * self.proportions.height_scale,
            thickness=self.proportions.bone_thickness * 0.8,
            color=np.array([0.9, 0.7, 0.5, 1.0], dtype=np.float32),
        )

        # Wrist can rotate freely
        bone.set_rotation_limits((-45.0, -45.0, -90.0), (45.0, 45.0, 90.0))

        return bone

    def _create_thigh_bone(self, is_left: bool) -> Bone:
        """Create thigh bone."""
        side_name = "l" if is_left else "r"
        side_multiplier = -1.0 if is_left else 1.0

        bone = Bone(
            name=f"thigh_{side_name}",
            bone_type=BoneType.THIGH_L if is_left else BoneType.THIGH_R,
            # Position at hip (offset from root)
            local_position=np.array([
                side_multiplier * 0.1 * self.proportions.height_scale,
                0.0,
                0.0
            ], dtype=np.float32),
            length=self.proportions.thigh_length * self.proportions.height_scale,
            thickness=self.proportions.bone_thickness * 1.1,
            color=np.array([0.6, 0.4, 0.2, 1.0], dtype=np.float32),
        )

        # Hip can move in wide range (walking, kicking, etc.)
        bone.set_rotation_limits((-45.0, -30.0, -120.0), (45.0, 30.0, 120.0))

        return bone

    def _create_shin_bone(self, is_left: bool) -> Bone:
        """Create shin bone."""
        side_name = "l" if is_left else "r"

        bone = Bone(
            name=f"shin_{side_name}",
            bone_type=BoneType.SHIN_L if is_left else BoneType.SHIN_R,
            local_position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            length=self.proportions.shin_length * self.proportions.height_scale,
            thickness=self.proportions.bone_thickness,
            color=np.array([0.7, 0.5, 0.3, 1.0], dtype=np.float32),
        )

        # Knee can only bend backward (opposite of elbow)
        bone.set_rotation_limits((0.0, 0.0, -5.0), (0.0, 0.0, 150.0))

        return bone

    def _create_foot_bone(self, is_left: bool) -> Bone:
        """Create foot bone."""
        side_name = "l" if is_left else "r"

        bone = Bone(
            name=f"foot_{side_name}",
            bone_type=BoneType.FOOT_L if is_left else BoneType.FOOT_R,
            local_position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            length=self.proportions.foot_size * self.proportions.height_scale,
            thickness=self.proportions.bone_thickness * 0.9,
            color=np.array([0.8, 0.6, 0.4, 1.0], dtype=np.float32),
        )

        # Ankle can flex up/down
        bone.set_rotation_limits((-30.0, -20.0, -45.0), (30.0, 20.0, 45.0))

        return bone

    # ========================================================================
    # PROPORTION ADJUSTMENT
    # ========================================================================

    def set_height(self, height_scale: float):
        """Set overall character height."""
        self.proportions.height_scale = max(0.5, min(2.0, height_scale))

    def set_limb_length_ratio(self, ratio: float):
        """
        Adjust limb length relative to torso.

        Args:
            ratio: Multiplier for arm/leg lengths (0.5 - 1.5)
        """
        ratio = max(0.5, min(1.5, ratio))

        # Scale arms
        self.proportions.upper_arm_length = 0.35 * ratio
        self.proportions.forearm_length = 0.35 * ratio

        # Scale legs
        self.proportions.thigh_length = 0.45 * ratio
        self.proportions.shin_length = 0.45 * ratio

    def set_shoulder_width(self, width: float):
        """Set shoulder width (0.2 - 0.8)."""
        self.proportions.shoulder_width = max(0.2, min(0.8, width))

    def set_head_size(self, size: float):
        """Set head size (0.15 - 0.4)."""
        self.proportions.head_size = max(0.15, min(0.4, size))


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_stick_figure(name: str = "StickFigure",
                       body_type: BodyType = BodyType.NORMAL) -> Skeleton:
    """
    Quick function to create a stick figure skeleton.

    Args:
        name: Skeleton name
        body_type: Preset body type

    Returns:
        Fully rigged Skeleton
    """
    auto_rig = AutoRig()
    return auto_rig.create_skeleton(name, body_type)


def create_custom_stick_figure(name: str,
                               height: float = 1.0,
                               limb_ratio: float = 1.0,
                               shoulder_width: float = 0.4,
                               head_size: float = 0.25) -> Skeleton:
    """
    Create a stick figure with custom proportions.

    Args:
        name: Skeleton name
        height: Overall height multiplier (0.5 - 2.0)
        limb_ratio: Limb length ratio (0.5 - 1.5)
        shoulder_width: Shoulder width (0.2 - 0.8)
        head_size: Head size (0.15 - 0.4)

    Returns:
        Fully rigged Skeleton
    """
    auto_rig = AutoRig()

    # Set custom proportions
    auto_rig.set_height(height)
    auto_rig.set_limb_length_ratio(limb_ratio)
    auto_rig.set_shoulder_width(shoulder_width)
    auto_rig.set_head_size(head_size)

    return auto_rig.create_skeleton(name, BodyType.NORMAL)
