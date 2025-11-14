"""
Crossbow Weapon
AAA procedural geometry for a medieval crossbow.
Features bow arms, stock, trigger mechanism, and bolt (arrow).
"""

import numpy as np
from .weapon_base import WeaponBase


class Crossbow(WeaponBase):
    """
    Procedurally generated crossbow with AAA geometry.
    Perfect for ranged combat in stick figure animations.
    """

    def __init__(self, name: str = "Crossbow"):
        super().__init__(name)

        self.weapon_type = "crossbow"
        self.description = "Medieval crossbow with mechanical trigger"

        # Crossbow-specific properties
        self.bow_width = 1.2  # Width of bow arms (horizontal)
        self.bow_thickness = 0.08
        self.stock_length = 1.5
        self.stock_width = 0.12
        self.bolt_length = 0.8
        self.string_tension = 0.15  # How much the string curves back
        self.bolt_loaded = True

        # Colors
        self.bow_color = np.array([0.3, 0.25, 0.2, 1.0], dtype=np.float32)  # Dark wood
        self.stock_color = np.array([0.4, 0.3, 0.2, 1.0], dtype=np.float32)  # Light wood
        self.string_color = np.array([0.8, 0.8, 0.7, 1.0], dtype=np.float32)  # Hemp/sinew
        self.metal_color = np.array([0.5, 0.5, 0.55, 1.0], dtype=np.float32)  # Steel
        self.bolt_color = np.array([0.6, 0.55, 0.5, 1.0], dtype=np.float32)  # Wood shaft
        self.bolt_tip_color = np.array([0.7, 0.7, 0.75, 1.0], dtype=np.float32)  # Steel tip

        self.generate_geometry()

    def generate_geometry(self):
        """Generate crossbow geometry with bow, stock, and bolt."""
        self.clear_geometry()

        self._build_stock()
        self._build_bow_arms()
        self._build_string()
        self._build_trigger_mechanism()
        if self.bolt_loaded:
            self._build_bolt()
        self._add_flame_points()

        print(f"✓ Generated Crossbow geometry: {len(self.vertices)} vertices, {len(self.edges)} edges")

    def _build_stock(self):
        """Build the wooden stock (main body)."""
        stock_top = self.stock_length
        stock_bottom = 0.0
        half_width = self.stock_width / 2

        # Main stock outline
        v_tl = self.add_vertex(-half_width, stock_top, 0.0, self.stock_color)
        v_tr = self.add_vertex(half_width, stock_top, 0.0, self.stock_color)
        v_bl = self.add_vertex(-half_width, stock_bottom, 0.0, self.stock_color)
        v_br = self.add_vertex(half_width, stock_bottom, 0.0, self.stock_color)

        self.add_edge(v_tl, v_bl)
        self.add_edge(v_tr, v_br)
        self.add_edge(v_tl, v_tr)
        self.add_edge(v_bl, v_br)

        # Bolt channel (groove along top)
        channel_width = 0.04
        channel_top = stock_top
        channel_bottom = stock_top - 0.7

        v_ctl = self.add_vertex(-channel_width, channel_top, 0.0, self.stock_color)
        v_ctr = self.add_vertex(channel_width, channel_top, 0.0, self.stock_color)
        v_cbl = self.add_vertex(-channel_width, channel_bottom, 0.0, self.stock_color)
        v_cbr = self.add_vertex(channel_width, channel_bottom, 0.0, self.stock_color)

        self.add_edge(v_ctl, v_cbl)
        self.add_edge(v_ctr, v_cbr)

        # Grip area detail
        grip_y = stock_bottom + 0.3
        for i in range(3):
            y = grip_y + i * 0.08
            v_l = self.add_vertex(-half_width, y, 0.0, self.stock_color)
            v_r = self.add_vertex(half_width, y, 0.0, self.stock_color)
            self.add_edge(v_l, v_r)

        # HD face
        self.add_face([v_tl, v_tr, v_br, v_bl])

    def _build_bow_arms(self):
        """Build the curved bow arms (prod)."""
        bow_y = self.stock_length  # Bow sits at top of stock
        bow_half_width = self.bow_width / 2
        thickness = self.bow_thickness

        # Left bow arm (curved)
        left_segments = 5
        left_vertices = []

        for i in range(left_segments + 1):
            t = i / left_segments
            x = -t * bow_half_width
            # Slight forward curve
            y_offset = 0.1 * np.sin(t * np.pi)
            y = bow_y + y_offset

            v = self.add_vertex(x, y, 0.0, self.bow_color)
            left_vertices.append(v)

        # Connect left arm
        for i in range(left_segments):
            self.add_edge(left_vertices[i], left_vertices[i + 1])

        # Right bow arm (curved)
        right_vertices = []

        for i in range(left_segments + 1):
            t = i / left_segments
            x = t * bow_half_width
            y_offset = 0.1 * np.sin(t * np.pi)
            y = bow_y + y_offset

            v = self.add_vertex(x, y, 0.0, self.bow_color)
            right_vertices.append(v)

        # Connect right arm
        for i in range(left_segments):
            self.add_edge(right_vertices[i], right_vertices[i + 1])

        # Connect center of arms
        self.add_edge(left_vertices[0], right_vertices[0])

        # Reinforcement bands on bow arms
        v_rbl = self.add_vertex(-0.15, bow_y, 0.0, self.metal_color)
        v_rbr = self.add_vertex(0.15, bow_y, 0.0, self.metal_color)
        self.add_edge(v_rbl, v_rbr)

    def _build_string(self):
        """Build the bowstring."""
        bow_y = self.stock_length
        bow_half_width = self.bow_width / 2

        # String endpoints (at bow arm tips)
        left_tip_y = bow_y + 0.1 * np.sin(np.pi)
        right_tip_y = bow_y + 0.1 * np.sin(np.pi)

        v_left_tip = self.add_vertex(-bow_half_width, left_tip_y, 0.0, self.string_color)
        v_right_tip = self.add_vertex(bow_half_width, right_tip_y, 0.0, self.string_color)

        # String center (pulled back for tension)
        string_center_y = bow_y - self.string_tension

        v_string_center = self.add_vertex(0.0, string_center_y, 0.0, self.string_color)

        # String edges (two segments for curve)
        self.add_edge(v_left_tip, v_string_center)
        self.add_edge(v_right_tip, v_string_center)

    def _build_trigger_mechanism(self):
        """Build the trigger and release mechanism."""
        trigger_y = self.stock_length * 0.4
        trigger_half_width = 0.06

        # Trigger guard (metal loop)
        guard_vertices = []
        segments = 6

        for i in range(segments + 1):
            t = i / segments
            angle = -np.pi * t  # Half circle downward
            x = trigger_half_width * np.cos(angle)
            y = trigger_y + trigger_half_width * np.sin(angle)

            v = self.add_vertex(x, y, 0.0, self.metal_color)
            guard_vertices.append(v)

        # Connect guard
        for i in range(segments):
            self.add_edge(guard_vertices[i], guard_vertices[i + 1])

        # Trigger itself
        trigger_bottom = trigger_y - 0.08
        v_trigger = self.add_vertex(0.0, trigger_bottom, 0.0, self.metal_color)
        v_trigger_top = self.add_vertex(0.0, trigger_y - 0.02, 0.0, self.metal_color)

        self.add_edge(v_trigger_top, v_trigger)

    def _build_bolt(self):
        """Build the crossbow bolt (arrow)."""
        # Bolt sits in the channel on top of stock
        bolt_back = self.stock_length - 0.2
        bolt_front = bolt_back + self.bolt_length

        # Shaft
        shaft_half_width = 0.02

        v_bl = self.add_vertex(-shaft_half_width, bolt_back, 0.0, self.bolt_color)
        v_br = self.add_vertex(shaft_half_width, bolt_back, 0.0, self.bolt_color)
        v_fl = self.add_vertex(-shaft_half_width, bolt_front - 0.15, 0.0, self.bolt_color)
        v_fr = self.add_vertex(shaft_half_width, bolt_front - 0.15, 0.0, self.bolt_color)

        self.add_edge(v_bl, v_fl)
        self.add_edge(v_br, v_fr)

        # Tip (pointed)
        v_tip = self.add_vertex(0.0, bolt_front, 0.0, self.bolt_tip_color)

        self.add_edge(v_fl, v_tip)
        self.add_edge(v_fr, v_tip)

        # Fletching (feathers at back)
        fletch_width = 0.06
        v_fletch_l = self.add_vertex(-fletch_width, bolt_back, 0.0, self.bolt_color)
        v_fletch_r = self.add_vertex(fletch_width, bolt_back, 0.0, self.bolt_color)
        v_fletch_c = self.add_vertex(0.0, bolt_back - 0.05, 0.0, self.bolt_color)

        self.add_edge(v_fletch_l, v_fletch_c)
        self.add_edge(v_fletch_r, v_fletch_c)

        # HD faces
        self.add_face([v_bl, v_br, v_fr, v_fl])
        self.add_face([v_fl, v_fr, v_tip])

    def _add_flame_points(self):
        """Add flame points on bolt tip and bow arms."""
        if self.bolt_loaded:
            # Bolt tip flame (main projectile effect)
            bolt_front = self.stock_length - 0.2 + self.bolt_length

            self.add_flame_point(
                name="bolt_tip",
                position=(0.0, bolt_front, 0.0),
                direction=(0.0, 1.0, 0.0),
                intensity=1.0
            )

        # Bow arm tip flames
        bow_y = self.stock_length
        bow_half_width = self.bow_width / 2

        self.add_flame_point(
            name="bow_left",
            position=(-bow_half_width, bow_y + 0.1, 0.0),
            direction=(-0.5, 0.5, 0.0),
            intensity=0.6
        )

        self.add_flame_point(
            name="bow_right",
            position=(bow_half_width, bow_y + 0.1, 0.0),
            direction=(0.5, 0.5, 0.0),
            intensity=0.6
        )

    def set_bolt_loaded(self, loaded: bool):
        """Toggle whether bolt is loaded."""
        self.bolt_loaded = loaded
        self.generate_geometry()


def create_crossbow(name: str = "Crossbow") -> Crossbow:
    """Create a new crossbow instance."""
    return Crossbow(name)
