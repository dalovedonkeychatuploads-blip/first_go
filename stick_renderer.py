#!/usr/bin/env python3
"""
DONK Stickman Engine - Stick Figure Renderer
MODULAR ARCHITECTURE - Delegates to specialized fighter classes

Each toon has its own deep-coded fighter class:
- Neon Cyan (Toon 1): neon_cyan_fighter.py
- Shadow Red (Toon 2): shadow_red_fighter.py
- Classic Capsule (Toon 3): classic_capsule_fighter.py
"""

from neon_cyan_fighter import NeonCyanFighter
from shadow_red_fighter import ShadowRedFighter
from classic_capsule_fighter import ClassicCapsuleFighter


class StickRenderer:
    """
    Thin router that delegates rendering to specialized fighter classes.
    Each fighter is deeply coded with all details for that specific character.
    """

    def __init__(self, scale=0.5):
        """
        Initialize renderer with scale factor.

        Args:
            scale: Scale multiplier for all rendering
        """
        self.scale = scale

        # Initialize all fighter classes
        self.neon_cyan = NeonCyanFighter()
        self.shadow_red = ShadowRedFighter()
        self.classic_capsule = ClassicCapsuleFighter()

    def update_measurements(self):
        """
        Update scale (legacy method for compatibility).
        Fighter classes use scale directly in render() calls.
        """
        pass  # No-op - fighters handle scaling internally

    def render_neon_cyan(self, painter, cx, cy):
        """
        Render Neon Cyan Fighter (Toon 1).
        Delegates to NeonCyanFighter class.

        Args:
            painter: QPainter instance
            cx, cy: Center position
        """
        self.neon_cyan.render(painter, cx, cy, self.scale)

    def render_shadow_red(self, painter, cx, cy):
        """
        Render Shadow Red Fighter (Toon 2).
        Delegates to ShadowRedFighter class.

        Args:
            painter: QPainter instance
            cx, cy: Center position
        """
        self.shadow_red.render(painter, cx, cy, self.scale)

    def render_classic_capsule(self, painter, cx, cy):
        """
        Render Classic Capsule Fighter (Toon 3).
        Delegates to ClassicCapsuleFighter class.

        Args:
            painter: QPainter instance
            cx, cy: Center position
        """
        self.classic_capsule.render(painter, cx, cy, self.scale)
