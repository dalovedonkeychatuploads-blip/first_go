"""
Maul Weapon
AAA procedural geometry for a two-handed war hammer/maul.
Features massive hammer head, long handle, and brutal impact design.
"""

import numpy as np
from .weapon_base import WeaponBase


class Maul(WeaponBase):
    """
    Procedurally generated two-handed maul with AAA geometry.
    Perfect for devastating crushing attacks in stick figure combat.
    """

    def __init__(self, name: str = "War Maul"):
        super().__init__(name)

        self.weapon_type = "maul"
        self.description = "Massive two-handed war hammer"

        # Maul-specific properties
        self.head_width = 0.7
        self.head_height = 0.4
        self.head_depth = 0.15
        self.spike_on_back = True
        self.handle_length = 2.2  # Long two-handed grip
        self.handle_width = 0.09

        # Colors
        self.head_color = np.array([0.45, 0.45, 0.5, 1.0], dtype=np.float32)  # Dark steel
        self.spike_color = np.array([0.6, 0.6, 0.65, 1.0], dtype=np.float32)  # Steel spike
        self.handle_color = np.array([0.35, 0.25, 0.15, 1.0], dtype=np.float32)  # Dark wood
        self.grip_color = np.array([0.25, 0.15, 0.1, 1.0], dtype=np.float32)  # Leather wraps

        self.generate_geometry()

    def generate_geometry(self):
        """Generate maul geometry with massive head and long handle."""
        self.clear_geometry()

        self._build_hammer_head()
        if self.spike_on_back:
            self._build_back_spike()
        self._build_handle()
        self._build_grip_wraps()
        self._add_flame_points()

        print(f"✓ Generated Maul geometry: {len(self.vertices)} vertices, {len(self.edges)} edges")

    def _build_hammer_head(self):
        """Build the massive rectangular hammer head."""
        head_y = self.handle_length + self.head_height / 2
        half_width = self.head_width / 2
        half_height = self.head_height / 2

        # Front face (hitting surface)
        v_ftl = self.add_vertex(-half_width, head_y + half_height, 0.0, self.head_color)
        v_ftr = self.add_vertex(half_width, head_y + half_height, 0.0, self.head_color)
        v_fbl = self.add_vertex(-half_width, head_y - half_height, 0.0, self.head_color)
        v_fbr = self.add_vertex(half_width, head_y - half_height, 0.0, self.head_color)

        # Front face edges
        self.add_edge(v_ftl, v_ftr)
        self.add_edge(v_ftr, v_fbr)
        self.add_edge(v_fbr, v_fbl)
        self.add_edge(v_fbl, v_ftl)

        # Diagonal reinforcement lines
        self.add_edge(v_ftl, v_fbr)
        self.add_edge(v_ftr, v_fbl)

        # Center handle connection
        handle_half = self.handle_width / 2
        v_htl = self.add_vertex(-handle_half, head_y + half_height, 0.0, self.head_color)
        v_htr = self.add_vertex(handle_half, head_y + half_height, 0.0, self.head_color)
        v_hbl = self.add_vertex(-handle_half, head_y - half_height, 0.0, self.head_color)
        v_hbr = self.add_vertex(handle_half, head_y - half_height, 0.0, self.head_color)

        # Connection edges
        self.add_edge(v_htl, v_hbl)
        self.add_edge(v_htr, v_hbr)
        self.add_edge(v_htl, v_htr)
        self.add_edge(v_hbl, v_hbr)

        # HD faces
        self.add_face([v_ftl, v_ftr, v_fbr, v_fbl])
        self.add_face([v_htl, v_htr, v_hbr, v_hbl])

    def _build_back_spike(self):
        """Build the spike on the back of the hammer for armor piercing."""
        head_y = self.handle_length + self.head_height / 2
        spike_base_x = -self.head_width / 2 - 0.05
        spike_length = 0.5

        # Top spike edge
        v_top_base = self.add_vertex(spike_base_x, head_y + 0.1, 0.0, self.spike_color)
        v_top_tip = self.add_vertex(spike_base_x - spike_length, head_y + 0.05, 0.0, self.spike_color)

        # Bottom spike edge
        v_bot_base = self.add_vertex(spike_base_x, head_y - 0.1, 0.0, self.spike_color)
        v_bot_tip = self.add_vertex(spike_base_x - spike_length, head_y - 0.05, 0.0, self.spike_color)

        # Tip point
        v_tip = self.add_vertex(spike_base_x - spike_length - 0.1, head_y, 0.0, self.spike_color)

        # Spike edges
        self.add_edge(v_top_base, v_top_tip)
        self.add_edge(v_bot_base, v_bot_tip)
        self.add_edge(v_top_tip, v_tip)
        self.add_edge(v_bot_tip, v_tip)
        self.add_edge(v_top_base, v_bot_base)

        # HD face
        self.add_face([v_top_base, v_top_tip, v_tip, v_bot_tip, v_bot_base])

    def _build_handle(self):
        """Build long two-handed handle."""
        handle_top = self.handle_length
        handle_bottom = 0.0
        half_width = self.handle_width / 2

        v_tl = self.add_vertex(-half_width, handle_top, 0.0, self.handle_color)
        v_tr = self.add_vertex(half_width, handle_top, 0.0, self.handle_color)
        v_bl = self.add_vertex(-half_width, handle_bottom, 0.0, self.handle_color)
        v_br = self.add_vertex(half_width, handle_bottom, 0.0, self.handle_color)

        self.add_edge(v_tl, v_bl)
        self.add_edge(v_tr, v_br)
        self.add_edge(v_tl, v_tr)
        self.add_edge(v_bl, v_br)

        self.add_face([v_tl, v_tr, v_br, v_bl])

    def _build_grip_wraps(self):
        """Build leather grip wraps for two-handed grip."""
        # Upper grip zone
        upper_y_top = self.handle_length * 0.6
        upper_y_bot = self.handle_length * 0.4
        half_width = self.handle_width / 2

        v_utl = self.add_vertex(-half_width, upper_y_top, 0.0, self.grip_color)
        v_utr = self.add_vertex(half_width, upper_y_top, 0.0, self.grip_color)
        v_ubl = self.add_vertex(-half_width, upper_y_bot, 0.0, self.grip_color)
        v_ubr = self.add_vertex(half_width, upper_y_bot, 0.0, self.grip_color)

        self.add_edge(v_utl, v_utr)
        self.add_edge(v_ubl, v_ubr)
        self.add_edge(v_utl, v_ubl)
        self.add_edge(v_utr, v_ubr)

        # Lower grip zone
        lower_y_top = self.handle_length * 0.3
        lower_y_bot = self.handle_length * 0.1

        v_ltl = self.add_vertex(-half_width, lower_y_top, 0.0, self.grip_color)
        v_ltr = self.add_vertex(half_width, lower_y_top, 0.0, self.grip_color)
        v_lbl = self.add_vertex(-half_width, lower_y_bot, 0.0, self.grip_color)
        v_lbr = self.add_vertex(half_width, lower_y_bot, 0.0, self.grip_color)

        self.add_edge(v_ltl, v_ltr)
        self.add_edge(v_lbl, v_lbr)
        self.add_edge(v_ltl, v_lbl)
        self.add_edge(v_ltr, v_lbr)

    def _add_flame_points(self):
        """Add flame points on hammer head and spike."""
        head_y = self.handle_length + self.head_height / 2

        # Main impact face flames
        self.add_flame_point(
            name="head_top",
            position=(self.head_width / 2, head_y + self.head_height / 2, 0.0),
            direction=(1.0, 0.5, 0.0),
            intensity=1.0
        )

        self.add_flame_point(
            name="head_center",
            position=(self.head_width / 2, head_y, 0.0),
            direction=(1.0, 0.0, 0.0),
            intensity=0.9
        )

        self.add_flame_point(
            name="head_bottom",
            position=(self.head_width / 2, head_y - self.head_height / 2, 0.0),
            direction=(1.0, -0.5, 0.0),
            intensity=1.0
        )

        # Spike tip flame
        if self.spike_on_back:
            spike_tip_x = -self.head_width / 2 - 0.6
            self.add_flame_point(
                name="spike_tip",
                position=(spike_tip_x, head_y, 0.0),
                direction=(-1.0, 0.0, 0.0),
                intensity=0.8
            )


def create_maul(name: str = "War Maul") -> Maul:
    """Create a new maul instance."""
    return Maul(name)
