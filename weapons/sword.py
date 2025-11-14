"""
Short Sword Weapon
AAA procedural geometry for a medieval-style short sword.
Features detailed blade, cross guard, grip, and pommel with flame attachment points.
"""

import numpy as np
from .weapon_base import WeaponBase


class ShortSword(WeaponBase):
    """
    Procedurally generated short sword with premium geometry.
    Perfect for stick figure combat animations.
    """

    def __init__(self, name: str = "Short Sword"):
        super().__init__(name)

        self.weapon_type = "sword"
        self.description = "Medieval short sword with straight blade and cross guard"

        # Sword-specific properties (customizable)
        self.blade_length = 2.5
        self.blade_width = 0.15
        self.guard_width = 0.6
        self.guard_thickness = 0.08
        self.grip_length = 0.6
        self.grip_width = 0.08
        self.pommel_size = 0.12

        # Color scheme (can be customized)
        self.blade_color = np.array([0.9, 0.9, 0.95, 1.0], dtype=np.float32)  # Bright steel
        self.guard_color = np.array([0.6, 0.5, 0.3, 1.0], dtype=np.float32)  # Bronze/brass
        self.grip_color = np.array([0.4, 0.25, 0.15, 1.0], dtype=np.float32)  # Leather brown
        self.pommel_color = np.array([0.7, 0.6, 0.4, 1.0], dtype=np.float32)  # Gold

        # Generate the geometry
        self.generate_geometry()

    def generate_geometry(self):
        """
        Generate AAA procedural geometry for the short sword.
        Creates blade, cross guard, grip, and pommel with detailed edges.
        """
        self.clear_geometry()

        # Build each component
        self._build_blade()
        self._build_cross_guard()
        self._build_grip()
        self._build_pommel()

        # Add flame attachment points along the blade
        self._add_flame_points()

        print(f"✓ Generated Short Sword geometry: {len(self.vertices)} vertices, {len(self.edges)} edges")

    # ========================================================================
    # BLADE CONSTRUCTION
    # ========================================================================

    def _build_blade(self):
        """
        Build the sword blade with centerline detail and sharp tip.
        The blade is the most important visual element.
        """
        # Blade starts at y = 0 (guard level) and extends upward
        blade_bottom = 0.0
        blade_top = self.blade_length

        # Blade outline vertices
        # Bottom left
        v_bl = self.add_vertex(-self.blade_width / 2, blade_bottom, 0.0, self.blade_color)
        # Bottom right
        v_br = self.add_vertex(self.blade_width / 2, blade_bottom, 0.0, self.blade_color)

        # Mid-left (where blade starts to taper)
        taper_start = blade_top * 0.7
        v_ml = self.add_vertex(-self.blade_width / 2, taper_start, 0.0, self.blade_color)
        v_mr = self.add_vertex(self.blade_width / 2, taper_start, 0.0, self.blade_color)

        # Tip (sharp point)
        tip_width = 0.02
        v_tl = self.add_vertex(-tip_width, blade_top - 0.2, 0.0, self.blade_color)
        v_tr = self.add_vertex(tip_width, blade_top - 0.2, 0.0, self.blade_color)
        v_tip = self.add_vertex(0.0, blade_top, 0.0, self.blade_color)

        # Centerline vertices for detail
        v_center_bottom = self.add_vertex(0.0, blade_bottom, 0.0, self.blade_color)
        v_center_mid = self.add_vertex(0.0, taper_start, 0.0, self.blade_color)
        v_center_tip_start = self.add_vertex(0.0, blade_top - 0.2, 0.0, self.blade_color)

        # EDGES - Blade outline
        # Left edge
        self.add_edge(v_bl, v_ml)
        self.add_edge(v_ml, v_tl)
        self.add_edge(v_tl, v_tip)

        # Right edge
        self.add_edge(v_br, v_mr)
        self.add_edge(v_mr, v_tr)
        self.add_edge(v_tr, v_tip)

        # Bottom edge (at guard)
        self.add_edge(v_bl, v_br)

        # Centerline (detail)
        self.add_edge(v_center_bottom, v_center_mid)
        self.add_edge(v_center_mid, v_center_tip_start)
        self.add_edge(v_center_tip_start, v_tip)

        # Fuller grooves (blood grooves) for detail
        fuller_width = self.blade_width * 0.3
        fuller_top = taper_start - 0.1

        # Left fuller
        v_fl_bl = self.add_vertex(-fuller_width, blade_bottom + 0.1, 0.0, self.blade_color)
        v_fl_tl = self.add_vertex(-fuller_width, fuller_top, 0.0, self.blade_color)
        self.add_edge(v_fl_bl, v_fl_tl)

        # Right fuller
        v_fr_br = self.add_vertex(fuller_width, blade_bottom + 0.1, 0.0, self.blade_color)
        v_fr_tr = self.add_vertex(fuller_width, fuller_top, 0.0, self.blade_color)
        self.add_edge(v_fr_br, v_fr_tr)

        # HD MODE: Add faces for the blade
        # Left blade face
        self.add_face([v_bl, v_ml, v_tl, v_tip, v_center_tip_start, v_center_mid, v_center_bottom])

        # Right blade face
        self.add_face([v_br, v_center_bottom, v_center_mid, v_center_tip_start, v_tip, v_tr, v_mr])

    # ========================================================================
    # CROSS GUARD CONSTRUCTION
    # ========================================================================

    def _build_cross_guard(self):
        """
        Build the cross guard (quillons) that protects the hand.
        Classic medieval style with slight upward curve.
        """
        guard_y = 0.0  # Guard sits at the base of the blade

        # Main horizontal bar of the guard
        guard_left = -self.guard_width / 2
        guard_right = self.guard_width / 2
        guard_top = guard_y + self.guard_thickness / 2
        guard_bottom = guard_y - self.guard_thickness / 2

        # Guard vertices
        # Left end
        v_gtl = self.add_vertex(guard_left, guard_top, 0.0, self.guard_color)
        v_gbl = self.add_vertex(guard_left, guard_bottom, 0.0, self.guard_color)

        # Center (where grip connects)
        center_width = self.grip_width
        v_gtc_l = self.add_vertex(-center_width / 2, guard_top, 0.0, self.guard_color)
        v_gbc_l = self.add_vertex(-center_width / 2, guard_bottom, 0.0, self.guard_color)
        v_gtc_r = self.add_vertex(center_width / 2, guard_top, 0.0, self.guard_color)
        v_gbc_r = self.add_vertex(center_width / 2, guard_bottom, 0.0, self.guard_color)

        # Right end
        v_gtr = self.add_vertex(guard_right, guard_top, 0.0, self.guard_color)
        v_gbr = self.add_vertex(guard_right, guard_bottom, 0.0, self.guard_color)

        # EDGES - Guard outline
        # Left side
        self.add_edge(v_gtl, v_gbl)  # Left end vertical
        self.add_edge(v_gtl, v_gtc_l)  # Top left horizontal
        self.add_edge(v_gbl, v_gbc_l)  # Bottom left horizontal

        # Center (grip connection)
        self.add_edge(v_gtc_l, v_gtc_r)  # Top center
        self.add_edge(v_gbc_l, v_gbc_r)  # Bottom center
        self.add_edge(v_gtc_l, v_gbc_l)  # Left center vertical
        self.add_edge(v_gtc_r, v_gbc_r)  # Right center vertical

        # Right side
        self.add_edge(v_gtc_r, v_gtr)  # Top right horizontal
        self.add_edge(v_gbc_r, v_gbr)  # Bottom right horizontal
        self.add_edge(v_gtr, v_gbr)  # Right end vertical

        # HD MODE: Add guard faces
        self.add_face([v_gtl, v_gtc_l, v_gbc_l, v_gbl])  # Left section
        self.add_face([v_gtc_l, v_gtc_r, v_gbc_r, v_gbc_l])  # Center section
        self.add_face([v_gtc_r, v_gtr, v_gbr, v_gbc_r])  # Right section

    # ========================================================================
    # GRIP CONSTRUCTION
    # ========================================================================

    def _build_grip(self):
        """
        Build the grip (handle) with wrapped leather texture detail.
        """
        grip_top = 0.0 - self.guard_thickness / 2  # Just below guard
        grip_bottom = grip_top - self.grip_length

        grip_half_width = self.grip_width / 2

        # Grip outline
        v_gtl = self.add_vertex(-grip_half_width, grip_top, 0.0, self.grip_color)
        v_gtr = self.add_vertex(grip_half_width, grip_top, 0.0, self.grip_color)
        v_gbl = self.add_vertex(-grip_half_width, grip_bottom, 0.0, self.grip_color)
        v_gbr = self.add_vertex(grip_half_width, grip_bottom, 0.0, self.grip_color)

        # EDGES - Grip outline
        self.add_edge(v_gtl, v_gbl)  # Left side
        self.add_edge(v_gtr, v_gbr)  # Right side
        self.add_edge(v_gtl, v_gtr)  # Top
        self.add_edge(v_gbl, v_gbr)  # Bottom

        # Leather wrap detail (diagonal lines)
        wrap_segments = 5
        for i in range(wrap_segments):
            y_pos = grip_top - (i * self.grip_length / wrap_segments)
            v_wrap_l = self.add_vertex(-grip_half_width, y_pos, 0.0, self.grip_color)
            v_wrap_r = self.add_vertex(grip_half_width, y_pos, 0.0, self.grip_color)

            # Diagonal wrap lines
            if i > 0:
                self.add_edge(v_wrap_l, v_wrap_r)

        # HD MODE: Add grip face
        self.add_face([v_gtl, v_gtr, v_gbr, v_gbl])

    # ========================================================================
    # POMMEL CONSTRUCTION
    # ========================================================================

    def _build_pommel(self):
        """
        Build the pommel (counterweight at the end of the grip).
        Round decorative design.
        """
        pommel_y = -self.grip_length - self.guard_thickness / 2 - self.pommel_size / 2

        # Pommel is roughly circular
        pommel_segments = 8
        pommel_indices = []

        for i in range(pommel_segments):
            angle = 2.0 * np.pi * i / pommel_segments
            x = self.pommel_size * np.cos(angle)
            y = pommel_y + self.pommel_size * 0.5 * np.sin(angle)
            v = self.add_vertex(x, y, 0.0, self.pommel_color)
            pommel_indices.append(v)

        # EDGES - Connect pommel vertices in a loop
        for i in range(pommel_segments):
            v1 = pommel_indices[i]
            v2 = pommel_indices[(i + 1) % pommel_segments]
            self.add_edge(v1, v2)

        # Add cross detail on pommel
        v_center = self.add_vertex(0.0, pommel_y, 0.0, self.pommel_color)
        self.add_edge(pommel_indices[0], v_center)  # Top
        self.add_edge(pommel_indices[pommel_segments // 2], v_center)  # Bottom
        self.add_edge(pommel_indices[pommel_segments // 4], v_center)  # Left
        self.add_edge(pommel_indices[3 * pommel_segments // 4], v_center)  # Right

        # HD MODE: Add pommel face
        self.add_face(pommel_indices)

    # ========================================================================
    # FLAME ATTACHMENT POINTS
    # ========================================================================

    def _add_flame_points(self):
        """
        Add flame attachment points along the blade.
        These are where the fire effects will be rendered.
        """
        # Main flame point at the tip (most dramatic)
        self.add_flame_point(
            name="blade_tip",
            position=(0.0, self.blade_length, 0.0),
            direction=(0.0, 1.0, 0.0),
            intensity=1.0
        )

        # Mid-blade flame points (left and right edges)
        mid_blade_y = self.blade_length * 0.5

        self.add_flame_point(
            name="blade_mid_left",
            position=(-self.blade_width / 2, mid_blade_y, 0.0),
            direction=(-0.3, 0.7, 0.0),  # Angled outward and up
            intensity=0.7
        )

        self.add_flame_point(
            name="blade_mid_right",
            position=(self.blade_width / 2, mid_blade_y, 0.0),
            direction=(0.3, 0.7, 0.0),  # Angled outward and up
            intensity=0.7
        )

        # Lower blade flame points
        lower_blade_y = self.blade_length * 0.25

        self.add_flame_point(
            name="blade_lower_left",
            position=(-self.blade_width / 2, lower_blade_y, 0.0),
            direction=(-0.2, 0.5, 0.0),
            intensity=0.5
        )

        self.add_flame_point(
            name="blade_lower_right",
            position=(self.blade_width / 2, lower_blade_y, 0.0),
            direction=(0.2, 0.5, 0.0),
            intensity=0.5
        )

    # ========================================================================
    # CUSTOMIZATION METHODS
    # ========================================================================

    def set_blade_length(self, length: float):
        """Customize blade length and regenerate geometry."""
        self.blade_length = max(1.0, min(5.0, length))  # Clamp between 1 and 5
        self.generate_geometry()

    def set_blade_width(self, width: float):
        """Customize blade width and regenerate geometry."""
        self.blade_width = max(0.05, min(0.5, width))  # Clamp
        self.generate_geometry()

    def set_colors(self, blade_color=None, guard_color=None, grip_color=None, pommel_color=None):
        """Customize sword colors and regenerate geometry."""
        if blade_color is not None:
            self.blade_color = np.array(blade_color, dtype=np.float32)
        if guard_color is not None:
            self.guard_color = np.array(guard_color, dtype=np.float32)
        if grip_color is not None:
            self.grip_color = np.array(grip_color, dtype=np.float32)
        if pommel_color is not None:
            self.pommel_color = np.array(pommel_color, dtype=np.float32)

        self.generate_geometry()


# Convenience function to create a short sword
def create_short_sword(name: str = "Short Sword") -> ShortSword:
    """
    Create a new short sword with default AAA geometry.

    Args:
        name: Display name for the sword

    Returns:
        ShortSword instance ready to render
    """
    return ShortSword(name)
