"""
Katana Weapon
AAA procedural geometry for a Japanese katana.
Features curved blade, circular tsuba guard, wrapped handle, and authentic proportions.
"""

import numpy as np
from .weapon_base import WeaponBase


class Katana(WeaponBase):
    """
    Procedurally generated katana with premium geometry.
    Authentic Japanese sword styling with characteristic curve.
    """

    def __init__(self, name: str = "Katana"):
        super().__init__(name)

        self.weapon_type = "katana"
        self.description = "Japanese curved sword with single-edged blade"

        # Katana-specific properties (customizable)
        self.blade_length = 3.0  # Longer than short sword
        self.blade_width = 0.12
        self.blade_curve = 0.3  # Sori (curvature) of the blade
        self.tsuba_radius = 0.15  # Circular guard
        self.tsuba_thickness = 0.05
        self.handle_length = 0.9  # Longer two-handed grip
        self.handle_width = 0.08
        self.kashira_size = 0.1  # End cap

        # Color scheme (authentic Japanese katana)
        self.blade_color = np.array([0.95, 0.95, 1.0, 1.0], dtype=np.float32)  # Bright steel
        self.hamon_color = np.array([0.85, 0.85, 0.95, 1.0], dtype=np.float32)  # Temper line
        self.tsuba_color = np.array([0.3, 0.3, 0.35, 1.0], dtype=np.float32)  # Iron/steel guard
        self.handle_color = np.array([0.15, 0.15, 0.2, 1.0], dtype=np.float32)  # Black wrap
        self.kashira_color = np.array([0.5, 0.4, 0.3, 1.0], dtype=np.float32)  # Bronze

        # Generate the geometry
        self.generate_geometry()

    def generate_geometry(self):
        """
        Generate AAA procedural geometry for the katana.
        Creates curved blade, tsuba, wrapped handle, and kashira.
        """
        self.clear_geometry()

        # Build each component
        self._build_blade()
        self._build_tsuba()
        self._build_handle()
        self._build_kashira()

        # Add flame attachment points along the blade
        self._add_flame_points()

        print(f"✓ Generated Katana geometry: {len(self.vertices)} vertices, {len(self.edges)} edges")

    # ========================================================================
    # BLADE CONSTRUCTION
    # ========================================================================

    def _build_blade(self):
        """
        Build the katana blade with authentic curve (sori) and single edge.
        The blade curves backward, typical of Japanese swords.
        """
        # Blade is built from bottom (at tsuba) to tip
        # We'll use segments to create the curve
        num_segments = 12  # More segments = smoother curve

        blade_vertices_sharp = []  # Sharp edge (cutting edge)
        blade_vertices_spine = []  # Spine/back of blade
        blade_vertices_center = []  # Centerline (shinogi)

        for i in range(num_segments + 1):
            # Position along blade (0 = bottom, 1 = tip)
            t = i / num_segments

            # Y position with curve (parabolic curve for sori)
            y = t * self.blade_length
            # Curve offset (maximum at middle of blade)
            curve_offset = 4.0 * self.blade_curve * t * (1.0 - t)

            # Width tapers toward the tip
            if t < 0.8:
                width = self.blade_width
            else:
                # Taper to point in last 20%
                taper = (0.8 - t) / 0.2  # 1 at t=0.8, 0 at t=1.0
                width = self.blade_width * max(0.02, taper)

            # Sharp edge (left side, cutting edge)
            v_sharp = self.add_vertex(
                -width / 2 - curve_offset,
                y,
                0.0,
                self.blade_color
            )
            blade_vertices_sharp.append(v_sharp)

            # Spine/back edge (right side, thicker)
            spine_offset = 0.03  # Slight offset for thickness
            v_spine = self.add_vertex(
                width / 2 - curve_offset + spine_offset,
                y,
                0.0,
                self.blade_color
            )
            blade_vertices_spine.append(v_spine)

            # Center line (shinogi - ridge line)
            if i < num_segments - 2:  # Don't draw center all the way to tip
                v_center = self.add_vertex(
                    -curve_offset,
                    y,
                    0.0,
                    self.blade_color
                )
                blade_vertices_center.append(v_center)

        # EDGES - Connect blade vertices
        # Sharp edge
        for i in range(len(blade_vertices_sharp) - 1):
            self.add_edge(blade_vertices_sharp[i], blade_vertices_sharp[i + 1])

        # Spine edge
        for i in range(len(blade_vertices_spine) - 1):
            self.add_edge(blade_vertices_spine[i], blade_vertices_spine[i + 1])

        # Centerline (shinogi ridge)
        for i in range(len(blade_vertices_center) - 1):
            self.add_edge(blade_vertices_center[i], blade_vertices_center[i + 1])

        # Connect tip
        self.add_edge(blade_vertices_sharp[-1], blade_vertices_spine[-1])

        # Connect base to tsuba
        self.add_edge(blade_vertices_sharp[0], blade_vertices_spine[0])

        # Hamon (temper line) for detail - wavy line along blade
        hamon_vertices = []
        for i in range(num_segments - 3):
            t = (i + 1) / num_segments
            y = t * self.blade_length
            curve_offset = 4.0 * self.blade_curve * t * (1.0 - t)

            # Wavy hamon pattern
            wave_offset = 0.02 * np.sin(t * 10.0)  # Small sine wave

            v_hamon = self.add_vertex(
                -self.blade_width * 0.25 - curve_offset + wave_offset,
                y,
                0.0,
                self.hamon_color
            )
            hamon_vertices.append(v_hamon)

        # Connect hamon vertices
        for i in range(len(hamon_vertices) - 1):
            self.add_edge(hamon_vertices[i], hamon_vertices[i + 1])

        # HD MODE: Add blade faces
        # Build faces from segments
        for i in range(len(blade_vertices_sharp) - 1):
            if i < len(blade_vertices_center):
                # Face from sharp edge to center
                self.add_face([
                    blade_vertices_sharp[i],
                    blade_vertices_sharp[i + 1],
                    blade_vertices_center[i],
                ])

                # Face from center to spine
                self.add_face([
                    blade_vertices_center[i],
                    blade_vertices_sharp[i + 1],
                    blade_vertices_spine[i + 1],
                    blade_vertices_spine[i],
                ])
            else:
                # Tip section (no center line)
                self.add_face([
                    blade_vertices_sharp[i],
                    blade_vertices_sharp[i + 1],
                    blade_vertices_spine[i + 1],
                    blade_vertices_spine[i],
                ])

    # ========================================================================
    # TSUBA (GUARD) CONSTRUCTION
    # ========================================================================

    def _build_tsuba(self):
        """
        Build the tsuba (circular guard) with decorative details.
        Classic round shape with cutout for blade.
        """
        tsuba_y = 0.0  # Tsuba sits at blade base

        # Outer circle
        num_segments = 16
        outer_vertices = []

        for i in range(num_segments):
            angle = 2.0 * np.pi * i / num_segments
            x = self.tsuba_radius * np.cos(angle)
            y = tsuba_y + self.tsuba_radius * 0.6 * np.sin(angle)  # Slightly elliptical

            v = self.add_vertex(x, y, 0.0, self.tsuba_color)
            outer_vertices.append(v)

        # Connect outer circle
        for i in range(num_segments):
            v1 = outer_vertices[i]
            v2 = outer_vertices[(i + 1) % num_segments]
            self.add_edge(v1, v2)

        # Inner circle (handle hole)
        handle_hole_radius = self.handle_width * 0.7
        inner_vertices = []

        for i in range(8):  # Fewer segments for inner hole
            angle = 2.0 * np.pi * i / 8
            x = handle_hole_radius * np.cos(angle)
            y = tsuba_y + handle_hole_radius * np.sin(angle)

            v = self.add_vertex(x, y, 0.0, self.tsuba_color)
            inner_vertices.append(v)

        # Connect inner circle
        for i in range(8):
            v1 = inner_vertices[i]
            v2 = inner_vertices[(i + 1) % 8]
            self.add_edge(v1, v2)

        # Decorative spokes from center to outer edge
        center_v = self.add_vertex(0.0, tsuba_y, 0.0, self.tsuba_color)

        for i in range(0, num_segments, 4):  # Every 4th vertex
            self.add_edge(center_v, outer_vertices[i])

        # HD MODE: Add tsuba face
        self.add_face(outer_vertices)

    # ========================================================================
    # HANDLE (TSUKA) CONSTRUCTION
    # ========================================================================

    def _build_handle(self):
        """
        Build the handle (tsuka) with traditional wrapped pattern.
        """
        handle_top = 0.0 - self.tsuba_thickness
        handle_bottom = handle_top - self.handle_length

        handle_half_width = self.handle_width / 2

        # Handle outline
        v_htl = self.add_vertex(-handle_half_width, handle_top, 0.0, self.handle_color)
        v_htr = self.add_vertex(handle_half_width, handle_top, 0.0, self.handle_color)
        v_hbl = self.add_vertex(-handle_half_width, handle_bottom, 0.0, self.handle_color)
        v_hbr = self.add_vertex(handle_half_width, handle_bottom, 0.0, self.handle_color)

        # EDGES - Handle outline
        self.add_edge(v_htl, v_hbl)  # Left side
        self.add_edge(v_htr, v_hbr)  # Right side
        self.add_edge(v_htl, v_htr)  # Top
        self.add_edge(v_hbl, v_hbr)  # Bottom

        # Traditional wrap pattern (diamond/X pattern)
        wrap_segments = 7
        wrap_vertices_left = []
        wrap_vertices_right = []

        for i in range(wrap_segments + 1):
            t = i / wrap_segments
            y_pos = handle_top - (t * self.handle_length)

            v_l = self.add_vertex(-handle_half_width, y_pos, 0.0, self.handle_color)
            v_r = self.add_vertex(handle_half_width, y_pos, 0.0, self.handle_color)

            wrap_vertices_left.append(v_l)
            wrap_vertices_right.append(v_r)

        # Create X pattern (diamond wrap)
        for i in range(wrap_segments):
            # Diagonal from left-top to right-bottom
            self.add_edge(wrap_vertices_left[i], wrap_vertices_right[i + 1])
            # Diagonal from right-top to left-bottom
            self.add_edge(wrap_vertices_right[i], wrap_vertices_left[i + 1])

        # HD MODE: Add handle face
        self.add_face([v_htl, v_htr, v_hbr, v_hbl])

    # ========================================================================
    # KASHIRA (END CAP) CONSTRUCTION
    # ========================================================================

    def _build_kashira(self):
        """
        Build the kashira (pommel/end cap) of the katana.
        Simple rounded cap design.
        """
        kashira_y = -self.handle_length - self.tsuba_thickness - self.kashira_size / 2

        # Rounded cap (semi-circle approximation)
        num_segments = 6
        kashira_vertices = []

        for i in range(num_segments + 1):
            t = i / num_segments
            angle = np.pi * t  # Half circle

            x = self.kashira_size * np.cos(angle)
            y = kashira_y - self.kashira_size * 0.3 * np.sin(angle)

            v = self.add_vertex(x, y, 0.0, self.kashira_color)
            kashira_vertices.append(v)

        # Connect kashira vertices
        for i in range(num_segments):
            self.add_edge(kashira_vertices[i], kashira_vertices[i + 1])

        # Close the cap
        self.add_edge(kashira_vertices[0], kashira_vertices[-1])

        # HD MODE: Add kashira face
        self.add_face(kashira_vertices)

    # ========================================================================
    # FLAME ATTACHMENT POINTS
    # ========================================================================

    def _add_flame_points(self):
        """
        Add flame attachment points along the curved blade.
        Positioned on the sharp cutting edge for maximum visual impact.
        """
        # Calculate curve offset at different positions
        def get_curve_offset(t):
            return 4.0 * self.blade_curve * t * (1.0 - t)

        # Tip flame point (most dramatic)
        tip_t = 1.0
        tip_curve = get_curve_offset(tip_t)
        self.add_flame_point(
            name="blade_tip",
            position=(-tip_curve, self.blade_length, 0.0),
            direction=(0.0, 1.0, 0.0),
            intensity=1.0
        )

        # Upper blade flame point
        upper_t = 0.75
        upper_y = upper_t * self.blade_length
        upper_curve = get_curve_offset(upper_t)
        upper_width = self.blade_width * 0.5  # Tapered

        self.add_flame_point(
            name="blade_upper",
            position=(-upper_width / 2 - upper_curve, upper_y, 0.0),
            direction=(-0.2, 0.8, 0.0),
            intensity=0.8
        )

        # Mid blade flame points
        mid_t = 0.5
        mid_y = mid_t * self.blade_length
        mid_curve = get_curve_offset(mid_t)

        self.add_flame_point(
            name="blade_mid_sharp",
            position=(-self.blade_width / 2 - mid_curve, mid_y, 0.0),
            direction=(-0.3, 0.7, 0.0),
            intensity=0.7
        )

        # Lower blade flame point
        lower_t = 0.25
        lower_y = lower_t * self.blade_length
        lower_curve = get_curve_offset(lower_t)

        self.add_flame_point(
            name="blade_lower",
            position=(-self.blade_width / 2 - lower_curve, lower_y, 0.0),
            direction=(-0.25, 0.6, 0.0),
            intensity=0.6
        )

    # ========================================================================
    # CUSTOMIZATION METHODS
    # ========================================================================

    def set_blade_length(self, length: float):
        """Customize blade length and regenerate geometry."""
        self.blade_length = max(2.0, min(4.0, length))
        self.generate_geometry()

    def set_blade_curve(self, curve: float):
        """Customize blade curvature (sori) and regenerate geometry."""
        self.blade_curve = max(0.0, min(0.6, curve))
        self.generate_geometry()

    def set_colors(self, blade_color=None, tsuba_color=None, handle_color=None):
        """Customize katana colors and regenerate geometry."""
        if blade_color is not None:
            self.blade_color = np.array(blade_color, dtype=np.float32)
        if tsuba_color is not None:
            self.tsuba_color = np.array(tsuba_color, dtype=np.float32)
        if handle_color is not None:
            self.handle_color = np.array(handle_color, dtype=np.float32)

        self.generate_geometry()


# Convenience function to create a katana
def create_katana(name: str = "Katana") -> Katana:
    """
    Create a new katana with default AAA geometry.

    Args:
        name: Display name for the katana

    Returns:
        Katana instance ready to render
    """
    return Katana(name)
