"""
Facial Rig System
Animatable facial features (eyes, mouth) for expressive stick figure characters.

Features:
- Eye rendering (open, closed, expressions)
- Mouth shapes for lip-sync (phoneme-based)
- Easy expression presets (happy, angry, surprised, neutral)
- Blink animation
- Smooth mouth shape transitions for voiceovers
"""

import numpy as np
from typing import Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from OpenGL.GL import *


# ============================================================================
# FACIAL EXPRESSIONS
# ============================================================================

class Expression(Enum):
    """Predefined facial expressions."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    ANGRY = "angry"
    SURPRISED = "surprised"
    SAD = "sad"
    DETERMINED = "determined"  # Fighting face
    HURT = "hurt"               # Taking damage
    VICTORY = "victory"         # Won the fight


# ============================================================================
# MOUTH PHONEMES (For Lip-Sync)
# ============================================================================

class MouthShape(Enum):
    """
    Phoneme-based mouth shapes for lip-sync animation.
    These correspond to common speech sounds.
    """
    CLOSED = "closed"           # M, B, P sounds
    SMALL_OPEN = "small_open"   # Rest position
    WIDE_OPEN = "wide_open"     # A, AH sounds
    ROUND_OPEN = "round_open"   # O, OO sounds
    NARROW_OPEN = "narrow_open" # E, EE sounds
    SMILE = "smile"             # Happy, smiling
    FROWN = "frown"             # Sad, angry
    TEETH = "teeth"             # S, Z, T sounds


# ============================================================================
# EYE STATE
# ============================================================================

class EyeState(Enum):
    """Eye open/closed states."""
    OPEN = "open"
    HALF_OPEN = "half_open"
    CLOSED = "closed"
    WINK_LEFT = "wink_left"
    WINK_RIGHT = "wink_right"


# ============================================================================
# FACIAL FEATURE DATA
# ============================================================================

@dataclass
class FacialFeatures:
    """
    Complete facial feature state for a character.
    Stores current expression, eye state, and mouth shape.
    """
    # Eye state
    left_eye_state: EyeState = EyeState.OPEN
    right_eye_state: EyeState = EyeState.OPEN
    eye_size: float = 1.0  # Size multiplier

    # Mouth state
    mouth_shape: MouthShape = MouthShape.CLOSED
    mouth_size: float = 1.0  # Size multiplier

    # Overall expression
    expression: Expression = Expression.NEUTRAL

    # Animation timing
    blink_timer: float = 0.0
    auto_blink: bool = True
    blink_interval: float = 3.0  # Seconds between blinks


# ============================================================================
# FACIAL RIG RENDERER
# ============================================================================

class FacialRig:
    """
    Renders animated facial features on stick figure head.
    Handles eyes, mouth, and expressions.
    """

    def __init__(self):
        """Initialize facial rig renderer."""
        # Feature sizes (relative to head size)
        self.eye_size_ratio = 0.12        # Eyes are 12% of head radius
        self.eye_spacing_ratio = 0.35     # Distance between eyes
        self.mouth_width_ratio = 0.4      # Mouth width relative to head
        self.mouth_y_offset = -0.25       # Mouth position below center

        # Colors
        self.eye_color = (0.0, 0.0, 0.0, 1.0)        # Black eyes
        self.mouth_color = (0.0, 0.0, 0.0, 1.0)      # Black mouth

        print("✓ Facial Rig initialized")

    # ========================================================================
    # MAIN RENDERING
    # ========================================================================

    def render_face(self, head_center: np.ndarray, head_radius: float,
                   features: FacialFeatures):
        """
        Render complete face (eyes + mouth) on head.

        Args:
            head_center: World position of head center
            head_radius: Head radius
            features: Current facial feature state
        """
        # Render eyes
        self._render_eyes(head_center, head_radius, features)

        # Render mouth
        self._render_mouth(head_center, head_radius, features)

    # ========================================================================
    # EYE RENDERING
    # ========================================================================

    def _render_eyes(self, head_center: np.ndarray, head_radius: float,
                    features: FacialFeatures):
        """Render both eyes based on current state."""
        eye_y = head_center[1] + head_radius * 0.1  # Slightly above center
        eye_spacing = head_radius * self.eye_spacing_ratio

        # Left eye
        left_eye_x = head_center[0] - eye_spacing
        self._render_single_eye(
            np.array([left_eye_x, eye_y, head_center[2]], dtype=np.float32),
            head_radius * self.eye_size_ratio * features.eye_size,
            features.left_eye_state
        )

        # Right eye
        right_eye_x = head_center[0] + eye_spacing
        self._render_single_eye(
            np.array([right_eye_x, eye_y, head_center[2]], dtype=np.float32),
            head_radius * self.eye_size_ratio * features.eye_size,
            features.right_eye_state
        )

    def _render_single_eye(self, position: np.ndarray, size: float, state: EyeState):
        """Render a single eye."""
        glColor4fv(self.eye_color)

        if state == EyeState.OPEN:
            # Full circle
            self._draw_filled_circle(position, size, segments=12)

        elif state == EyeState.HALF_OPEN:
            # Half circle (top half visible)
            self._draw_half_circle(position, size, segments=12)

        elif state == EyeState.CLOSED:
            # Horizontal line
            glLineWidth(2.0)
            glBegin(GL_LINES)
            glVertex3f(position[0] - size, position[1], position[2])
            glVertex3f(position[0] + size, position[1], position[2])
            glEnd()

        elif state in [EyeState.WINK_LEFT, EyeState.WINK_RIGHT]:
            # Full circle (winking handled by setting state on one eye to CLOSED)
            self._draw_filled_circle(position, size, segments=12)

    def _draw_filled_circle(self, center: np.ndarray, radius: float, segments: int = 12):
        """Draw a filled circle for eye."""
        glBegin(GL_TRIANGLE_FAN)
        glVertex3fv(center)

        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            glVertex3f(x, y, center[2])

        glEnd()

    def _draw_half_circle(self, center: np.ndarray, radius: float, segments: int = 12):
        """Draw half circle (for half-open eyes)."""
        glBegin(GL_TRIANGLE_FAN)
        glVertex3fv(center)

        # Only draw top half (0 to π)
        for i in range(segments // 2 + 1):
            angle = np.pi * i / (segments // 2)
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            glVertex3f(x, y, center[2])

        glEnd()

    # ========================================================================
    # MOUTH RENDERING
    # ========================================================================

    def _render_mouth(self, head_center: np.ndarray, head_radius: float,
                     features: FacialFeatures):
        """Render mouth based on current phoneme shape."""
        mouth_y = head_center[1] + head_radius * self.mouth_y_offset
        mouth_width = head_radius * self.mouth_width_ratio * features.mouth_size

        mouth_pos = np.array([head_center[0], mouth_y, head_center[2]], dtype=np.float32)

        glColor4fv(self.mouth_color)
        glLineWidth(2.5)

        # Render different mouth shapes
        if features.mouth_shape == MouthShape.CLOSED:
            # Straight horizontal line
            glBegin(GL_LINES)
            glVertex3f(mouth_pos[0] - mouth_width, mouth_pos[1], mouth_pos[2])
            glVertex3f(mouth_pos[0] + mouth_width, mouth_pos[1], mouth_pos[2])
            glEnd()

        elif features.mouth_shape == MouthShape.SMALL_OPEN:
            # Small circle
            self._draw_circle_outline(mouth_pos, mouth_width * 0.3, segments=12)

        elif features.mouth_shape == MouthShape.WIDE_OPEN:
            # Large circle (shouting/surprised)
            self._draw_circle_outline(mouth_pos, mouth_width * 0.6, segments=16)

        elif features.mouth_shape == MouthShape.ROUND_OPEN:
            # Round O shape
            self._draw_circle_outline(mouth_pos, mouth_width * 0.4, segments=16)

        elif features.mouth_shape == MouthShape.NARROW_OPEN:
            # Narrow horizontal oval
            self._draw_oval_outline(mouth_pos, mouth_width * 0.6, mouth_width * 0.2)

        elif features.mouth_shape == MouthShape.SMILE:
            # Curved smile (arc)
            self._draw_smile_arc(mouth_pos, mouth_width, is_smile=True)

        elif features.mouth_shape == MouthShape.FROWN:
            # Curved frown (inverted arc)
            self._draw_smile_arc(mouth_pos, mouth_width, is_smile=False)

        elif features.mouth_shape == MouthShape.TEETH:
            # Small horizontal line (teeth showing)
            glBegin(GL_LINES)
            glVertex3f(mouth_pos[0] - mouth_width * 0.5, mouth_pos[1], mouth_pos[2])
            glVertex3f(mouth_pos[0] + mouth_width * 0.5, mouth_pos[1], mouth_pos[2])
            glEnd()

    def _draw_circle_outline(self, center: np.ndarray, radius: float, segments: int = 12):
        """Draw circle outline for mouth."""
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = 2.0 * np.pi * i / segments
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            glVertex3f(x, y, center[2])
        glEnd()

    def _draw_oval_outline(self, center: np.ndarray, width: float, height: float):
        """Draw oval outline for mouth."""
        segments = 16
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = 2.0 * np.pi * i / segments
            x = center[0] + (width / 2.0) * np.cos(angle)
            y = center[1] + (height / 2.0) * np.sin(angle)
            glVertex3f(x, y, center[2])
        glEnd()

    def _draw_smile_arc(self, center: np.ndarray, width: float, is_smile: bool = True):
        """Draw curved smile or frown arc."""
        segments = 12
        arc_height = width * 0.3

        glBegin(GL_LINE_STRIP)
        for i in range(segments + 1):
            t = i / segments
            x = center[0] + (t - 0.5) * width * 2.0
            # Parabolic curve
            curve_factor = 4.0 * t * (1.0 - t)  # Peaks at 0.5
            y_offset = curve_factor * arc_height

            if is_smile:
                y = center[1] - y_offset  # Curve down for smile
            else:
                y = center[1] + y_offset  # Curve up for frown

            glVertex3f(x, y, center[2])
        glEnd()

    # ========================================================================
    # EXPRESSION PRESETS
    # ========================================================================

    def apply_expression(self, features: FacialFeatures, expression: Expression):
        """
        Apply a preset expression to facial features.

        Args:
            features: Facial features to modify
            expression: Expression to apply
        """
        features.expression = expression

        if expression == Expression.NEUTRAL:
            features.left_eye_state = EyeState.OPEN
            features.right_eye_state = EyeState.OPEN
            features.mouth_shape = MouthShape.CLOSED
            features.eye_size = 1.0
            features.mouth_size = 1.0

        elif expression == Expression.HAPPY:
            features.left_eye_state = EyeState.OPEN
            features.right_eye_state = EyeState.OPEN
            features.mouth_shape = MouthShape.SMILE
            features.eye_size = 0.9  # Slightly squinted from smiling
            features.mouth_size = 1.2

        elif expression == Expression.ANGRY:
            features.left_eye_state = EyeState.HALF_OPEN
            features.right_eye_state = EyeState.HALF_OPEN
            features.mouth_shape = MouthShape.FROWN
            features.eye_size = 0.8
            features.mouth_size = 0.9

        elif expression == Expression.SURPRISED:
            features.left_eye_state = EyeState.OPEN
            features.right_eye_state = EyeState.OPEN
            features.mouth_shape = MouthShape.WIDE_OPEN
            features.eye_size = 1.3  # Wide eyes
            features.mouth_size = 1.4

        elif expression == Expression.SAD:
            features.left_eye_state = EyeState.HALF_OPEN
            features.right_eye_state = EyeState.HALF_OPEN
            features.mouth_shape = MouthShape.FROWN
            features.eye_size = 0.9
            features.mouth_size = 1.0

        elif expression == Expression.DETERMINED:
            features.left_eye_state = EyeState.HALF_OPEN
            features.right_eye_state = EyeState.HALF_OPEN
            features.mouth_shape = MouthShape.CLOSED
            features.eye_size = 0.85  # Focused squint
            features.mouth_size = 0.9

        elif expression == Expression.HURT:
            features.left_eye_state = EyeState.CLOSED
            features.right_eye_state = EyeState.HALF_OPEN
            features.mouth_shape = MouthShape.WIDE_OPEN
            features.eye_size = 1.0
            features.mouth_size = 1.2

        elif expression == Expression.VICTORY:
            features.left_eye_state = EyeState.OPEN
            features.right_eye_state = EyeState.WINK_RIGHT
            features.mouth_shape = MouthShape.SMILE
            features.eye_size = 1.0
            features.mouth_size = 1.3

    # ========================================================================
    # BLINK ANIMATION
    # ========================================================================

    def update_blink(self, features: FacialFeatures, delta_time: float):
        """
        Update automatic blink animation.

        Args:
            features: Facial features to update
            delta_time: Time since last update (seconds)
        """
        if not features.auto_blink:
            return

        features.blink_timer += delta_time

        # Time to blink?
        if features.blink_timer >= features.blink_interval:
            # Start blink
            features.left_eye_state = EyeState.CLOSED
            features.right_eye_state = EyeState.CLOSED

            # Reset timer (add small random variation)
            import random
            features.blink_timer = -0.15  # Blink duration (negative means "in blink")
            features.blink_interval = 2.5 + random.random() * 1.5  # 2.5-4.0 seconds

        # End blink?
        elif features.blink_timer > 0.0 and features.blink_timer < 0.1:
            # Blink just ended, reopen eyes
            features.left_eye_state = EyeState.OPEN
            features.right_eye_state = EyeState.OPEN


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_facial_features(expression: Expression = Expression.NEUTRAL) -> FacialFeatures:
    """
    Create facial features with a preset expression.

    Args:
        expression: Starting expression

    Returns:
        Configured FacialFeatures instance
    """
    features = FacialFeatures()
    rig = FacialRig()
    rig.apply_expression(features, expression)
    return features
