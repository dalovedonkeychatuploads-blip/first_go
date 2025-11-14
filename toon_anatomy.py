"""
Toon Anatomy System - Character Proportion & Style Definitions
================================================================

This module defines the anatomical data for all 3 default toons:
- Toon 1: Neon Cyan Fighter (sleek, 6.5 heads, cyan glows, fingers)
- Toon 2: Shadow Red Fighter (chunky, 4.2 heads, red eyes, simple hands)
- Toon 3: Googly Eyes Fighter (classic, 7 heads, googly eyes, minimalist)

Design Philosophy:
- Anatomy classes contain DATA ONLY (proportions, colors, flags)
- NO rendering logic (that's RiggedRenderer's job)
- All proportions in "head units" for scale independence
- Multipliers allow slider-based customization
- Preserves exact visual appearance from reference images

Usage:
    anatomy = create_neon_cyan_anatomy()
    torso_height = anatomy.get_torso_height(scale=1.0)
    renderer = RiggedRenderer(anatomy)
"""

from PySide6.QtGui import QColor
from typing import List, Dict, Tuple
from enum import Enum


# ============================================================================
# ENUMS - Style Type Definitions
# ============================================================================

class RenderStyle(Enum):
    """Visual rendering style for toon"""
    VOLUMETRIC = "volumetric"  # 3D-like with gradients and lighting
    FLAT = "flat"             # 2D solid colors, minimalist


class EyeStyle(Enum):
    """Eye rendering style"""
    SLIT = "slit"       # Horizontal glowing slits (Toon 1 & 2)
    GOOGLY = "googly"   # Cartoon googly eyes with pupils (Toon 3)
    DOTS = "dots"       # Simple dot eyes


class HandStyle(Enum):
    """Hand rendering complexity"""
    DETAILED_FINGERS = "detailed_fingers"  # 5 fingers (Toon 1)
    SIMPLE_MITTEN = "simple_mitten"       # Blocky hand (Toon 2 & 3)


# ============================================================================
# BASE TOON ANATOMY CLASS
# ============================================================================

class ToonAnatomy:
    """
    Base class defining anatomical proportions and visual style for a toon.

    All measurements use "head units" (multiples of head radius) for scale
    independence. This allows toons to be rendered at any size while
    maintaining correct proportions.

    Subclasses override constants to define specific toon types.
    Instances have multipliers for user customization via sliders.
    """

    # ===== PROPORTIONS (Base constants - override in subclasses) =====
    # Total height in head units (1 head = 2× HEAD_RADIUS)
    HEADS_TALL = 6.5

    # Base head size (all proportions derived from this)
    HEAD_RADIUS = 60.0

    # Body part ratios (× head diameter for length, × head radius for thickness)
    NECK_HEIGHT_RATIO = 0.15        # Short neck
    NECK_THICKNESS_RATIO = 0.35     # Thin neck

    TORSO_HEIGHT_RATIO = 1.75       # Torso length
    TORSO_WIDTH_RATIO = 0.80        # Torso width

    # Arms (shoulder to elbow to wrist)
    UPPER_ARM_LENGTH_RATIO = 0.875  # Upper arm length
    LOWER_ARM_LENGTH_RATIO = 0.8125 # Forearm length
    UPPER_ARM_THICKNESS_RATIO = 0.45 # Upper arm thickness
    LOWER_ARM_THICKNESS_RATIO = 0.40 # Forearm thickness

    # Legs (hip to knee to ankle)
    UPPER_LEG_LENGTH_RATIO = 1.0625  # Thigh length
    LOWER_LEG_LENGTH_RATIO = 1.0     # Shin length
    UPPER_LEG_THICKNESS_RATIO = 0.525 # Thigh thickness
    LOWER_LEG_THICKNESS_RATIO = 0.475 # Shin thickness

    # Hands and feet
    HAND_WIDTH_RATIO = 0.40
    HAND_HEIGHT_RATIO = 0.475
    FOOT_WIDTH_RATIO = 0.70
    FOOT_HEIGHT_RATIO = 0.40

    # Joints
    JOINT_RADIUS_RATIO = 0.225      # Joint sphere size

    # ===== COLORS (Override in subclasses) =====
    # Body gradients (for volumetric rendering)
    BODY_HIGHLIGHT = QColor(145, 145, 145)  # Lightest lit area
    BODY_MIDTONE = QColor(69, 69, 69)       # Medium tone
    BODY_SHADOW = QColor(46, 46, 46)        # Darkest shadow

    # Glow colors (for neon effects)
    GLOW_COLOR = QColor(0, 255, 255)        # Cyan default
    GLOW_OPACITY = 0.30                     # Glow transparency

    # Eye colors
    EYE_COLOR = QColor(0, 255, 255)         # Eye glow color
    EYE_PUPIL_COLOR = QColor(0, 0, 0)       # Pupil color (for googly)

    # ===== STYLE FLAGS (Override in subclasses) =====
    RENDER_STYLE = RenderStyle.VOLUMETRIC
    EYE_STYLE = EyeStyle.SLIT
    HAND_STYLE = HandStyle.SIMPLE_MITTEN

    # Feature flags
    HAS_GLOWS = False              # Glowing joints?
    GLOW_JOINTS = []               # Which joints glow (empty = none)
    HAS_GRADIENTS = True           # Use gradients or flat colors?

    # Eye dimensions (ratios of head radius)
    EYE_WIDTH_RATIO = 0.35
    EYE_HEIGHT_RATIO = 0.05
    EYE_SPACING_RATIO = 0.42       # Distance between eyes
    EYE_Y_OFFSET_RATIO = -0.125    # Vertical offset from head center

    # Finger configuration
    FINGER_COUNT = 0               # 0 = simple hand, 5 = detailed

    def __init__(self):
        """Initialize anatomy with default (unadjusted) proportions."""
        # Adjustable multipliers (modified by sliders)
        self.height_multiplier = 1.0       # Overall height scale
        self.arm_length_multiplier = 1.0   # Arm length adjustment
        self.leg_length_multiplier = 1.0   # Leg length adjustment
        self.torso_height_multiplier = 1.0 # Torso height adjustment
        self.shoulder_width_multiplier = 1.0  # Shoulder width
        self.thickness_multiplier = 1.0    # Overall thickness
        self.glow_intensity = 1.0          # Glow brightness (0-2)

        # Toon-specific multipliers (set by subclasses)
        self.chunkiness = 1.0              # For Shadow Red
        self.eye_size_multiplier = 1.0     # For Googly Eyes
        self.pupil_offset_x = 0.0          # For Googly Eyes
        self.pupil_offset_y = 0.0          # For Googly Eyes

    # ===== COMPUTED PROPERTIES (Getters with multipliers applied) =====

    def get_head_radius(self, scale: float = 1.0) -> float:
        """Get actual head radius in pixels"""
        return self.HEAD_RADIUS * scale

    def get_head_diameter(self, scale: float = 1.0) -> float:
        """Get actual head diameter in pixels"""
        return self.HEAD_RADIUS * 2 * scale

    def get_neck_height(self, scale: float = 1.0) -> float:
        """Get neck height with multipliers applied"""
        base = self.HEAD_RADIUS * 2 * self.NECK_HEIGHT_RATIO
        adjusted = base * self.height_multiplier
        return adjusted * scale

    def get_neck_thickness(self, scale: float = 1.0) -> float:
        """Get neck thickness with multipliers applied"""
        base = self.HEAD_RADIUS * self.NECK_THICKNESS_RATIO
        adjusted = base * self.thickness_multiplier
        return adjusted * scale

    def get_torso_height(self, scale: float = 1.0) -> float:
        """Get torso height with multipliers applied"""
        base = self.HEAD_RADIUS * 2 * self.TORSO_HEIGHT_RATIO
        adjusted = base * self.torso_height_multiplier * self.height_multiplier
        return adjusted * scale

    def get_torso_width(self, scale: float = 1.0) -> float:
        """Get torso width with multipliers applied"""
        base = self.HEAD_RADIUS * 2 * self.TORSO_WIDTH_RATIO
        adjusted = base * self.shoulder_width_multiplier
        return adjusted * scale

    def get_upper_arm_length(self, scale: float = 1.0) -> float:
        """Get upper arm length with multipliers applied"""
        base = self.HEAD_RADIUS * 2 * self.UPPER_ARM_LENGTH_RATIO
        adjusted = base * self.arm_length_multiplier * self.height_multiplier
        return adjusted * scale

    def get_lower_arm_length(self, scale: float = 1.0) -> float:
        """Get forearm length with multipliers applied"""
        base = self.HEAD_RADIUS * 2 * self.LOWER_ARM_LENGTH_RATIO
        adjusted = base * self.arm_length_multiplier * self.height_multiplier
        return adjusted * scale

    def get_upper_arm_thickness(self, scale: float = 1.0) -> float:
        """Get upper arm thickness with multipliers applied"""
        base = self.HEAD_RADIUS * self.UPPER_ARM_THICKNESS_RATIO
        adjusted = base * self.thickness_multiplier
        return adjusted * scale

    def get_lower_arm_thickness(self, scale: float = 1.0) -> float:
        """Get forearm thickness with multipliers applied"""
        base = self.HEAD_RADIUS * self.LOWER_ARM_THICKNESS_RATIO
        adjusted = base * self.thickness_multiplier
        return adjusted * scale

    def get_upper_leg_length(self, scale: float = 1.0) -> float:
        """Get thigh length with multipliers applied"""
        base = self.HEAD_RADIUS * 2 * self.UPPER_LEG_LENGTH_RATIO
        adjusted = base * self.leg_length_multiplier * self.height_multiplier
        return adjusted * scale

    def get_lower_leg_length(self, scale: float = 1.0) -> float:
        """Get shin length with multipliers applied"""
        base = self.HEAD_RADIUS * 2 * self.LOWER_LEG_LENGTH_RATIO
        adjusted = base * self.leg_length_multiplier * self.height_multiplier
        return adjusted * scale

    def get_upper_leg_thickness(self, scale: float = 1.0) -> float:
        """Get thigh thickness with multipliers applied"""
        base = self.HEAD_RADIUS * self.UPPER_LEG_THICKNESS_RATIO
        adjusted = base * self.thickness_multiplier
        return adjusted * scale

    def get_lower_leg_thickness(self, scale: float = 1.0) -> float:
        """Get shin thickness with multipliers applied"""
        base = self.HEAD_RADIUS * self.LOWER_LEG_THICKNESS_RATIO
        adjusted = base * self.thickness_multiplier
        return adjusted * scale

    def get_hand_dimensions(self, scale: float = 1.0) -> Tuple[float, float]:
        """Get hand width and height"""
        width = self.HEAD_RADIUS * 2 * self.HAND_WIDTH_RATIO * scale
        height = self.HEAD_RADIUS * 2 * self.HAND_HEIGHT_RATIO * scale
        return (width, height)

    def get_foot_dimensions(self, scale: float = 1.0) -> Tuple[float, float]:
        """Get foot width and height"""
        width = self.HEAD_RADIUS * 2 * self.FOOT_WIDTH_RATIO * scale
        height = self.HEAD_RADIUS * 2 * self.FOOT_HEIGHT_RATIO * scale
        return (width, height)

    def get_joint_radius(self, scale: float = 1.0, size_multiplier: float = 1.0) -> float:
        """Get joint sphere radius (size_multiplier for smaller joints)"""
        base = self.HEAD_RADIUS * self.JOINT_RADIUS_RATIO
        adjusted = base * size_multiplier
        return adjusted * scale

    def get_total_height(self, scale: float = 1.0) -> float:
        """Get total character height in pixels"""
        head = self.get_head_diameter(scale)
        return head * self.HEADS_TALL * self.height_multiplier

    # ===== SERIALIZATION =====

    def to_dict(self) -> Dict:
        """Serialize anatomy to dictionary for saving"""
        return {
            "type": self.__class__.__name__,
            "multipliers": {
                "height": self.height_multiplier,
                "arm_length": self.arm_length_multiplier,
                "leg_length": self.leg_length_multiplier,
                "torso_height": self.torso_height_multiplier,
                "shoulder_width": self.shoulder_width_multiplier,
                "thickness": self.thickness_multiplier,
                "glow_intensity": self.glow_intensity,
                "chunkiness": self.chunkiness,
                "eye_size": self.eye_size_multiplier,
                "pupil_offset_x": self.pupil_offset_x,
                "pupil_offset_y": self.pupil_offset_y,
            }
        }

    def load_from_dict(self, data: Dict):
        """Load multipliers from saved data"""
        multipliers = data.get("multipliers", {})
        self.height_multiplier = multipliers.get("height", 1.0)
        self.arm_length_multiplier = multipliers.get("arm_length", 1.0)
        self.leg_length_multiplier = multipliers.get("leg_length", 1.0)
        self.torso_height_multiplier = multipliers.get("torso_height", 1.0)
        self.shoulder_width_multiplier = multipliers.get("shoulder_width", 1.0)
        self.thickness_multiplier = multipliers.get("thickness", 1.0)
        self.glow_intensity = multipliers.get("glow_intensity", 1.0)
        self.chunkiness = multipliers.get("chunkiness", 1.0)
        self.eye_size_multiplier = multipliers.get("eye_size", 1.0)
        self.pupil_offset_x = multipliers.get("pupil_offset_x", 0.0)
        self.pupil_offset_y = multipliers.get("pupil_offset_y", 0.0)


# ============================================================================
# TOON 1: NEON CYAN FIGHTER
# ============================================================================

class NeonCyanAnatomy(ToonAnatomy):
    """
    Toon 1: Neon Cyan Fighter

    Sleek athletic fighter with cyan glowing joints.
    Reference-matched to toon1.jpeg (medium-gray body, subtle cyan accents)

    Characteristics:
    - 6.5 heads tall (realistic fighter proportions)
    - Medium-gray gradient body (RGB 46-145)
    - Subtle cyan glows at ALL joints
    - Detailed 5-finger hands (index, middle, ring, pinky, thumb)
    - Horizontal cyan slit eyes
    - Volumetric rendering with gradients
    """

    # Proportions (6.5 heads tall - realistic)
    HEADS_TALL = 6.5
    HEAD_RADIUS = 40.0  # Base unit (80px diameter)

    NECK_HEIGHT_RATIO = 0.225
    NECK_THICKNESS_RATIO = 0.35

    TORSO_HEIGHT_RATIO = 1.75
    TORSO_WIDTH_RATIO = 1.0

    UPPER_ARM_LENGTH_RATIO = 0.875
    LOWER_ARM_LENGTH_RATIO = 0.8125
    UPPER_ARM_THICKNESS_RATIO = 0.45
    LOWER_ARM_THICKNESS_RATIO = 0.40

    UPPER_LEG_LENGTH_RATIO = 1.0625
    LOWER_LEG_LENGTH_RATIO = 1.0
    UPPER_LEG_THICKNESS_RATIO = 0.525
    LOWER_LEG_THICKNESS_RATIO = 0.475

    HAND_WIDTH_RATIO = 0.40
    HAND_HEIGHT_RATIO = 0.475
    FOOT_WIDTH_RATIO = 0.70
    FOOT_HEIGHT_RATIO = 0.40

    JOINT_RADIUS_RATIO = 0.225

    # Colors (EXACT from neon_cyan_fighter.py reference)
    BODY_HIGHLIGHT = QColor(145, 145, 145)  # RGB(145,145,145)
    BODY_MIDTONE = QColor(69, 69, 69)       # RGB(69,69,69)
    BODY_SHADOW = QColor(46, 46, 46)        # RGB(46,46,46)

    GLOW_COLOR = QColor(0, 255, 255)        # Cyan RGB(0,255,255)
    GLOW_OPACITY = 0.30                     # Subtle glow

    EYE_COLOR = QColor(0, 255, 255)         # Cyan eyes

    # Style flags
    RENDER_STYLE = RenderStyle.VOLUMETRIC
    EYE_STYLE = EyeStyle.SLIT
    HAND_STYLE = HandStyle.DETAILED_FINGERS

    HAS_GLOWS = True
    GLOW_JOINTS = [  # All joints glow
        "neck", "shoulder_left", "shoulder_right",
        "elbow_left", "elbow_right", "wrist_left", "wrist_right",
        "hip_left", "hip_right", "knee_left", "knee_right",
        "ankle_left", "ankle_right"
    ]
    HAS_GRADIENTS = True

    # Eye dimensions
    EYE_WIDTH_RATIO = 0.35
    EYE_HEIGHT_RATIO = 0.05
    EYE_SPACING_RATIO = 0.40
    EYE_Y_OFFSET_RATIO = -0.125

    # Fingers
    FINGER_COUNT = 5  # Detailed hand with 5 fingers


# ============================================================================
# TOON 2: SHADOW RED FIGHTER
# ============================================================================

class ShadowRedAnatomy(ToonAnatomy):
    """
    Toon 2: Shadow Red Fighter

    Chunky demon-boss with menacing red slit eyes.
    Reference-matched to toon2.jpeg (very dark body, red glowing eyes)

    Characteristics:
    - 4.2 heads tall (compact toy/boss proportions)
    - Very dark gradient body (RGB 5-40)
    - RED glowing eyes ONLY (no joint glows)
    - Simple blocky mitten hands (no fingers)
    - Wide horizontal red slit eyes (3-layer glow)
    - SHORT and WIDE torso (power stance)
    - THICK stubby limbs
    """

    # Proportions (4.2 heads tall - chunky)
    HEADS_TALL = 4.2
    HEAD_RADIUS = 60.0  # Larger head (120px diameter)

    NECK_HEIGHT_RATIO = 0.05   # Almost no neck
    NECK_THICKNESS_RATIO = 0.6  # Thick neck

    TORSO_HEIGHT_RATIO = 0.7    # SHORT torso
    TORSO_WIDTH_RATIO = 0.9     # WIDE torso (1.8× head in original)

    UPPER_ARM_LENGTH_RATIO = 0.375   # STUBBY arms (0.75× head in original)
    LOWER_ARM_LENGTH_RATIO = 0.35
    UPPER_ARM_THICKNESS_RATIO = 0.175  # THICK arms
    LOWER_ARM_THICKNESS_RATIO = 0.15

    UPPER_LEG_LENGTH_RATIO = 0.45    # SHORT legs (0.9× head in original)
    LOWER_LEG_LENGTH_RATIO = 0.40
    UPPER_LEG_THICKNESS_RATIO = 0.1917  # THICK legs
    LOWER_LEG_THICKNESS_RATIO = 0.175

    HAND_WIDTH_RATIO = 0.233
    HAND_HEIGHT_RATIO = 0.292
    FOOT_WIDTH_RATIO = 0.267
    FOOT_HEIGHT_RATIO = 0.208

    JOINT_RADIUS_RATIO = 0.15

    # Colors (EXACT from shadow_red_fighter.py reference)
    BODY_HIGHLIGHT = QColor(40, 40, 40)     # RGB(40,40,40)
    BODY_MIDTONE = QColor(20, 20, 20)       # RGB(20,20,20)
    BODY_SHADOW = QColor(10, 10, 10)        # RGB(10,10,10)

    GLOW_COLOR = QColor(255, 20, 20)        # Red glow (eyes only)
    GLOW_OPACITY = 0.40                     # Bright red glow

    EYE_COLOR = QColor(255, 20, 20)         # Red eyes

    # Style flags
    RENDER_STYLE = RenderStyle.VOLUMETRIC
    EYE_STYLE = EyeStyle.SLIT
    HAND_STYLE = HandStyle.SIMPLE_MITTEN

    HAS_GLOWS = False       # NO joint glows!
    GLOW_JOINTS = []        # Empty - only eyes glow
    HAS_GRADIENTS = True

    # Eye dimensions (WIDE menacing slits)
    EYE_WIDTH_RATIO = 0.5    # Wide eyes
    EYE_HEIGHT_RATIO = 0.10  # Taller slits
    EYE_SPACING_RATIO = 0.42
    EYE_Y_OFFSET_RATIO = -0.15

    # No fingers
    FINGER_COUNT = 0


# ============================================================================
# TOON 3: GOOGLY EYES FIGHTER
# ============================================================================

class GooglyEyesAnatomy(ToonAnatomy):
    """
    Toon 3: Googly Eyes Fighter

    Classic minimalist stick figure with cartoon googly eyes.
    Reference-matched to toon3.jpeg (pure black, simple, googly eyes)

    Characteristics:
    - 7 heads tall (classic tall stick figure)
    - Pure black body (RGB 0,0,0) - NO gradients!
    - White googly eyes with black pupils
    - Simple rounded oval hands (no fingers)
    - Clean cylindrical limbs (uniform thickness)
    - Flat rendering (no volumetric effects)
    - Retro internet stick figure aesthetic
    """

    # Proportions (7 heads tall - classic stick)
    HEADS_TALL = 7.0
    HEAD_RADIUS = 35.0  # Smaller head (70px diameter)

    NECK_HEIGHT_RATIO = 0.286
    NECK_THICKNESS_RATIO = 0.286

    TORSO_HEIGHT_RATIO = 2.286
    TORSO_WIDTH_RATIO = 0.857

    UPPER_ARM_LENGTH_RATIO = 1.143
    LOWER_ARM_LENGTH_RATIO = 1.071
    UPPER_ARM_THICKNESS_RATIO = 0.429
    LOWER_ARM_THICKNESS_RATIO = 0.371

    UPPER_LEG_LENGTH_RATIO = 1.429
    LOWER_LEG_LENGTH_RATIO = 1.357
    UPPER_LEG_THICKNESS_RATIO = 0.486
    LOWER_LEG_THICKNESS_RATIO = 0.429

    HAND_WIDTH_RATIO = 0.457
    HAND_HEIGHT_RATIO = 0.543
    FOOT_WIDTH_RATIO = 0.8
    FOOT_HEIGHT_RATIO = 0.457

    JOINT_RADIUS_RATIO = 0.257

    # Colors (FLAT - no gradients!)
    BODY_HIGHLIGHT = QColor(0, 0, 0)        # Pure black
    BODY_MIDTONE = QColor(0, 0, 0)          # Pure black
    BODY_SHADOW = QColor(0, 0, 0)           # Pure black

    GLOW_COLOR = QColor(0, 0, 0)            # No glow
    GLOW_OPACITY = 0.0

    EYE_COLOR = QColor(255, 255, 255)       # White eyes
    EYE_PUPIL_COLOR = QColor(0, 0, 0)       # Black pupils

    # Style flags
    RENDER_STYLE = RenderStyle.FLAT         # NO gradients!
    EYE_STYLE = EyeStyle.GOOGLY             # Googly eyes!
    HAND_STYLE = HandStyle.SIMPLE_MITTEN

    HAS_GLOWS = False
    GLOW_JOINTS = []
    HAS_GRADIENTS = False  # CRITICAL: Flat solid colors only

    # Googly eye dimensions
    EYE_WIDTH_RATIO = 0.6   # Large cartoon eyes
    EYE_HEIGHT_RATIO = 0.6  # Round eyes
    EYE_SPACING_RATIO = 0.5
    EYE_Y_OFFSET_RATIO = -0.1

    # No fingers
    FINGER_COUNT = 0


# ============================================================================
# FACTORY FUNCTIONS - Convenience Constructors
# ============================================================================

def create_neon_cyan_anatomy() -> NeonCyanAnatomy:
    """Create Toon 1: Neon Cyan Fighter anatomy"""
    return NeonCyanAnatomy()


def create_shadow_red_anatomy() -> ShadowRedAnatomy:
    """Create Toon 2: Shadow Red Fighter anatomy"""
    return ShadowRedAnatomy()


def create_googly_eyes_anatomy() -> GooglyEyesAnatomy:
    """Create Toon 3: Googly Eyes Fighter anatomy"""
    return GooglyEyesAnatomy()


def get_anatomy_by_name(name: str) -> ToonAnatomy:
    """Get anatomy instance by toon name"""
    name_map = {
        "neon_cyan": create_neon_cyan_anatomy,
        "shadow_red": create_shadow_red_anatomy,
        "googly_eyes": create_googly_eyes_anatomy,
        "cyan": create_neon_cyan_anatomy,
        "red": create_shadow_red_anatomy,
        "googly": create_googly_eyes_anatomy,
        "1": create_neon_cyan_anatomy,
        "2": create_shadow_red_anatomy,
        "3": create_googly_eyes_anatomy,
    }

    factory = name_map.get(name.lower())
    if factory:
        return factory()
    else:
        raise ValueError(f"Unknown toon name: {name}")
