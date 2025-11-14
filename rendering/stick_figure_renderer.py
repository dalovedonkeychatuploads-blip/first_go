"""
Stick Figure Renderer
Professional thick-limbed stick figure rendering for YouTube content.

Features:
- Thick, filled limb rendering (not thin 2px lines)
- Customizable body colors (red, blue, custom RGB)
- Round head rendering with facial features
- Smooth anti-aliased edges
- Optimized for 60 FPS rendering
- Color presets for quick character creation
"""

import numpy as np
from typing import Optional, Tuple
from enum import Enum
from OpenGL.GL import *

from rigging.skeleton import Skeleton, Bone


# ============================================================================
# COLOR PRESETS
# ============================================================================

class CharacterColorPreset(Enum):
    """Predefined character color schemes for quick setup."""
    RED_FIGHTER = "red_fighter"          # Classic red (like YouTube video)
    BLUE_FIGHTER = "blue_fighter"        # Classic blue (like YouTube video)
    GREEN_FIGHTER = "green_fighter"      # Green
    YELLOW_FIGHTER = "yellow_fighter"    # Yellow/gold
    PURPLE_FIGHTER = "purple_fighter"    # Purple
    ORANGE_FIGHTER = "orange_fighter"    # Orange
    CYAN_FIGHTER = "cyan_fighter"        # Cyan
    BLACK_FIGHTER = "black_fighter"      # Black (villain style)
    WHITE_FIGHTER = "white_fighter"      # White (hero style)
    CUSTOM = "custom"                     # User-defined RGB


# Preset color definitions (RGB)
PRESET_COLORS = {
    CharacterColorPreset.RED_FIGHTER: (0.85, 0.15, 0.15),      # Bright red
    CharacterColorPreset.BLUE_FIGHTER: (0.2, 0.4, 0.85),       # Bright blue
    CharacterColorPreset.GREEN_FIGHTER: (0.2, 0.75, 0.2),      # Bright green
    CharacterColorPreset.YELLOW_FIGHTER: (0.95, 0.85, 0.15),   # Bright yellow
    CharacterColorPreset.PURPLE_FIGHTER: (0.65, 0.2, 0.85),    # Purple
    CharacterColorPreset.ORANGE_FIGHTER: (1.0, 0.5, 0.1),      # Orange
    CharacterColorPreset.CYAN_FIGHTER: (0.2, 0.85, 0.85),      # Cyan
    CharacterColorPreset.BLACK_FIGHTER: (0.1, 0.1, 0.1),       # Dark gray (black) - maximum visibility
    CharacterColorPreset.WHITE_FIGHTER: (0.95, 0.95, 0.95),    # Light gray (white)
}


# ============================================================================
# STICK FIGURE RENDERER
# ============================================================================

class StickFigureRenderer:
    """
    Professional stick figure renderer with thick, colored limbs.
    Designed for YouTube content creation with clear, readable characters.
    """

    def __init__(self):
        """Initialize stick figure renderer."""
        # Default rendering parameters
        self.limb_thickness_multiplier = 8.0   # Makes limbs THICC (not thin 2px)
        self.head_detail_segments = 24         # Smooth circular head
        self.joint_size_multiplier = 1.3       # Joint circles slightly bigger than limb width

        # Anti-aliasing
        self.enable_antialiasing = True

        # Outline for extra definition
        self.draw_outline = True
        self.outline_thickness = 1.5
        self.outline_color = (0.0, 0.0, 0.0, 0.3)  # Subtle dark outline

        print("✓ Stick Figure Renderer initialized (YouTube style - THICC limbs)")

    # ========================================================================
    # MAIN RENDERING
    # ========================================================================

    def render_skeleton(self, skeleton: Skeleton,
                       color_preset: CharacterColorPreset = CharacterColorPreset.RED_FIGHTER,
                       custom_color: Optional[Tuple[float, float, float]] = None,
                       draw_face: bool = True):
        """
        Render a complete stick figure skeleton with thick, colored limbs.

        Args:
            skeleton: Skeleton to render
            color_preset: Predefined color scheme
            custom_color: Custom RGB color (overrides preset if provided)
            draw_face: Whether to draw facial features on head
        """
        if not skeleton.visible:
            return

        # Update skeleton transforms
        skeleton.update()

        # Determine body color
        if custom_color is not None:
            body_color = custom_color
        else:
            body_color = PRESET_COLORS.get(color_preset, PRESET_COLORS[CharacterColorPreset.RED_FIGHTER])

        # Enable anti-aliasing
        if self.enable_antialiasing:
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_POLYGON_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
            glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

        # Render all bones as thick limbs
        for bone in skeleton.bones.values():
            if bone.visible and bone.bone_type and bone.bone_type.value != "root":
                self._render_thick_limb(bone, body_color)

        # Render joints (circles at connection points)
        for bone in skeleton.bones.values():
            if bone.visible:
                self._render_joint(bone, body_color)

        # Render head with face
        head_bone = skeleton.get_bone("head")
        if head_bone and draw_face:
            self._render_head_with_face(head_bone, body_color)

        # Disable anti-aliasing
        if self.enable_antialiasing:
            glDisable(GL_LINE_SMOOTH)
            glDisable(GL_POLYGON_SMOOTH)

    # ========================================================================
    # LIMB RENDERING (THICK, FILLED)
    # ========================================================================

    def _render_thick_limb(self, bone: Bone, color: Tuple[float, float, float]):
        """
        Render a bone as a thick, filled rectangle (not a thin line).
        This gives the "meaty" stick figure look from YouTube videos.
        """
        bone.update_world_transform()

        start_pos = bone.get_world_position()
        end_pos = bone.get_end_position()

        # Calculate thickness
        thickness = bone.thickness * self.limb_thickness_multiplier

        # Calculate perpendicular offset for rectangle corners
        # Vector from start to end
        direction = end_pos - start_pos
        length = np.linalg.norm(direction)

        if length < 0.001:
            return  # Bone too small to render

        direction = direction / length  # Normalize

        # Perpendicular vector (rotate 90 degrees in 2D)
        perpendicular = np.array([-direction[1], direction[0], 0.0], dtype=np.float32)
        offset = perpendicular * thickness / 2.0

        # Four corners of the limb rectangle
        corner1 = start_pos - offset
        corner2 = start_pos + offset
        corner3 = end_pos + offset
        corner4 = end_pos - offset

        # Draw outline first (if enabled)
        if self.draw_outline:
            outline_offset = offset * (1.0 + self.outline_thickness / 10.0)
            outline_c1 = start_pos - outline_offset
            outline_c2 = start_pos + outline_offset
            outline_c3 = end_pos + outline_offset
            outline_c4 = end_pos - outline_offset

            glColor4fv(self.outline_color)
            glBegin(GL_TRIANGLE_FAN)
            glVertex3fv(outline_c1)
            glVertex3fv(outline_c2)
            glVertex3fv(outline_c3)
            glVertex3fv(outline_c4)
            glEnd()

        # Draw filled limb
        glColor3fv(color)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3fv(corner1)
        glVertex3fv(corner2)
        glVertex3fv(corner3)
        glVertex3fv(corner4)
        glEnd()

    # ========================================================================
    # JOINT RENDERING (CIRCLES AT CONNECTIONS)
    # ========================================================================

    def _render_joint(self, bone: Bone, color: Tuple[float, float, float]):
        """
        Render a circular joint at the bone's start position.
        This creates smooth connections between limbs.
        """
        bone.update_world_transform()
        position = bone.get_world_position()

        radius = bone.thickness * self.limb_thickness_multiplier * self.joint_size_multiplier / 2.0

        # Draw outline circle
        if self.draw_outline:
            outline_radius = radius * (1.0 + self.outline_thickness / 10.0)
            glColor4fv(self.outline_color)
            self._draw_filled_circle(position, outline_radius, segments=20)

        # Draw joint circle
        glColor3fv(color)
        self._draw_filled_circle(position, radius, segments=20)

    def _draw_filled_circle(self, center: np.ndarray, radius: float, segments: int = 24):
        """Draw a filled circle."""
        glBegin(GL_TRIANGLE_FAN)
        glVertex3fv(center)  # Center point

        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            glVertex3f(x, y, center[2])

        glEnd()

    # ========================================================================
    # HEAD RENDERING (WITH FACE)
    # ========================================================================

    def _render_head_with_face(self, head_bone: Bone, body_color: Tuple[float, float, float]):
        """
        Render the head as a large circle with facial features.

        Args:
            head_bone: Head bone
            body_color: Body color for the head fill
        """
        head_bone.update_world_transform()
        head_pos = head_bone.get_world_position()

        # Head is larger than regular joints
        head_radius = head_bone.length * 0.8  # Large round head

        # Draw outline
        if self.draw_outline:
            outline_radius = head_radius * (1.0 + self.outline_thickness / 10.0)
            glColor4fv(self.outline_color)
            self._draw_filled_circle(head_pos, outline_radius, segments=self.head_detail_segments)

        # Draw head
        glColor3fv(body_color)
        self._draw_filled_circle(head_pos, head_radius, segments=self.head_detail_segments)

        # Draw facial features (eyes and mouth)
        # Note: Facial features are rendered separately in facial_rig.py for animation
        # This is just the head shape

    # ========================================================================
    # CUSTOMIZATION
    # ========================================================================

    def set_limb_thickness(self, multiplier: float):
        """
        Set limb thickness multiplier.

        Args:
            multiplier: Thickness multiplier (default 8.0 for YouTube style)
                       Higher = thicker limbs
        """
        self.limb_thickness_multiplier = max(1.0, min(20.0, multiplier))

    def set_outline_enabled(self, enabled: bool):
        """Enable or disable limb outlines."""
        self.draw_outline = enabled

    def set_antialiasing(self, enabled: bool):
        """Enable or disable anti-aliasing."""
        self.enable_antialiasing = enabled


# ============================================================================
# CHARACTER CLASS (Skeleton + Color)
# ============================================================================

class StickFigureCharacter:
    """
    Complete stick figure character with skeleton and visual properties.
    Combines rigging with rendering for easy character management.
    """

    def __init__(self, name: str, skeleton: Skeleton,
                 color_preset: CharacterColorPreset = CharacterColorPreset.RED_FIGHTER):
        """
        Initialize character.

        Args:
            name: Character name
            skeleton: Rigged skeleton
            color_preset: Color scheme
        """
        self.name = name
        self.skeleton = skeleton
        self.color_preset = color_preset
        self.custom_color: Optional[Tuple[float, float, float]] = None

        # Facial animation state (for future integration)
        self.current_expression = "neutral"
        self.mouth_phoneme = "closed"

        # Renderer instance
        self.renderer = StickFigureRenderer()

    def set_color(self, preset: CharacterColorPreset):
        """Set character color from preset."""
        self.color_preset = preset
        self.custom_color = None

    def set_custom_color(self, r: float, g: float, b: float):
        """Set custom RGB color."""
        self.custom_color = (r, g, b)
        self.color_preset = CharacterColorPreset.CUSTOM

    def render(self, draw_face: bool = True):
        """Render the character."""
        self.renderer.render_skeleton(
            self.skeleton,
            self.color_preset,
            self.custom_color,
            draw_face
        )

    def get_color_rgb(self) -> Tuple[float, float, float]:
        """Get current character color as RGB tuple."""
        if self.custom_color:
            return self.custom_color
        else:
            return PRESET_COLORS.get(self.color_preset, (0.85, 0.15, 0.15))


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_red_vs_blue_fighters(red_name: str = "Red Fighter",
                                blue_name: str = "Blue Fighter"):
    """
    Create classic red vs blue fighter setup (like YouTube video).

    Returns:
        (red_character, blue_character) tuple
    """
    from rigging.auto_rig import create_stick_figure, BodyType

    # Create skeletons
    red_skeleton = create_stick_figure(red_name, BodyType.NORMAL)
    blue_skeleton = create_stick_figure(blue_name, BodyType.NORMAL)

    # Position them facing each other
    red_skeleton.root_bone.set_local_position(-2.0, 0.0, 0.0)
    blue_skeleton.root_bone.set_local_position(2.0, 0.0, 0.0)

    # Create characters
    red_char = StickFigureCharacter(red_name, red_skeleton, CharacterColorPreset.RED_FIGHTER)
    blue_char = StickFigureCharacter(blue_name, blue_skeleton, CharacterColorPreset.BLUE_FIGHTER)

    return (red_char, blue_char)


def get_available_colors():
    """Get list of available color presets."""
    return [preset for preset in CharacterColorPreset if preset != CharacterColorPreset.CUSTOM]
