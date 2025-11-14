"""
Mace Weapon
AAA procedural geometry for a medieval spiked mace.
Features spiked ball head, sturdy handle, and hand guard.
"""

import numpy as np
from .weapon_base import WeaponBase


class Mace(WeaponBase):
    """
    Procedurally generated mace with AAA geometry.
    Perfect for crushing blows in stick figure combat.
    """

    def __init__(self, name: str = "Mace"):
        super().__init__(name)

        self.weapon_type = "mace"
        self.description = "Medieval mace with spiked ball head"

        # Mace-specific properties
        self.head_radius = 0.4
        self.spike_count = 8
        self.spike_length = 0.25
        self.handle_length = 1.8
        self.handle_width = 0.08
        self.guard_width = 0.2

        # Colors
        self.head_color = np.array([0.5, 0.5, 0.55, 1.0], dtype=np.float32)  # Steel
        self.spike_color = np.array([0.7, 0.7, 0.75, 1.0], dtype=np.float32)  # Bright steel spikes
        self.handle_color = np.array([0.3, 0.2, 0.15, 1.0], dtype=np.float32)  # Wood
        self.guard_color = np.array([0.4, 0.35, 0.25, 1.0], dtype=np.float32)  # Bronze

        self.generate_geometry()

    def generate_geometry(self):
        """Generate mace geometry with spiked head and handle."""
        self.clear_geometry()

        self._build_head()
        self._build_spikes()
        self._build_handle()
        self._build_guard()
        self._add_flame_points()

        print(f"✓ Generated Mace geometry: {len(self.vertices)} vertices, {len(self.edges)} edges")

    def _build_head(self):
        """Build the spherical mace head."""
        head_y = self.handle_length + self.head_radius
        segments = 12

        head_vertices = []
        for i in range(segments):
            angle = 2.0 * np.pi * i / segments
            x = self.head_radius * np.cos(angle)
            y_offset = self.head_radius * 0.7 * np.sin(angle)
            y = head_y + y_offset

            v = self.add_vertex(x, y, 0.0, self.head_color)
            head_vertices.append(v)

        # Connect head circle
        for i in range(segments):
            v1 = head_vertices[i]
            v2 = head_vertices[(i + 1) % segments]
            self.add_edge(v1, v2)

        # Add center and spokes
        v_center = self.add_vertex(0.0, head_y, 0.0, self.head_color)
        for i in range(0, segments, 2):
            self.add_edge(v_center, head_vertices[i])

        # HD faces
        self.add_face(head_vertices)

    def _build_spikes(self):
        """Build sharp spikes around the mace head."""
        head_y = self.handle_length + self.head_radius

        for i in range(self.spike_count):
            angle = 2.0 * np.pi * i / self.spike_count

            # Base of spike (on head surface)
            base_x = self.head_radius * np.cos(angle)
            base_y = head_y + self.head_radius * 0.7 * np.sin(angle)

            # Tip of spike (pointing outward)
            spike_dir_x = np.cos(angle)
            spike_dir_y = 0.7 * np.sin(angle)

            tip_x = base_x + self.spike_length * spike_dir_x
            tip_y = base_y + self.spike_length * spike_dir_y

            v_base = self.add_vertex(base_x, base_y, 0.0, self.spike_color)
            v_tip = self.add_vertex(tip_x, tip_y, 0.0, self.spike_color)

            self.add_edge(v_base, v_tip)

            # Add spike width (triangle base)
            angle_offset = np.pi / self.spike_count
            left_x = base_x + 0.05 * np.cos(angle - angle_offset)
            left_y = base_y + 0.05 * 0.7 * np.sin(angle - angle_offset)

            right_x = base_x + 0.05 * np.cos(angle + angle_offset)
            right_y = base_y + 0.05 * 0.7 * np.sin(angle + angle_offset)

            v_left = self.add_vertex(left_x, left_y, 0.0, self.spike_color)
            v_right = self.add_vertex(right_x, right_y, 0.0, self.spike_color)

            self.add_edge(v_left, v_tip)
            self.add_edge(v_right, v_tip)
            self.add_edge(v_left, v_right)

            # HD face
            self.add_face([v_left, v_right, v_tip])

    def _build_handle(self):
        """Build the wooden handle."""
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

        # Wood grain detail
        segments = 5
        for i in range(1, segments):
            y = handle_bottom + (i / segments) * self.handle_length
            v_l = self.add_vertex(-half_width, y, 0.0, self.handle_color)
            v_r = self.add_vertex(half_width, y, 0.0, self.handle_color)
            self.add_edge(v_l, v_r)

        self.add_face([v_tl, v_tr, v_br, v_bl])

    def _build_guard(self):
        """Build hand guard at base of handle."""
        guard_y = 0.0
        half_width = self.guard_width / 2
        thickness = 0.06

        v_tl = self.add_vertex(-half_width, guard_y + thickness, 0.0, self.guard_color)
        v_tr = self.add_vertex(half_width, guard_y + thickness, 0.0, self.guard_color)
        v_bl = self.add_vertex(-half_width, guard_y - thickness, 0.0, self.guard_color)
        v_br = self.add_vertex(half_width, guard_y - thickness, 0.0, self.guard_color)

        self.add_edge(v_tl, v_tr)
        self.add_edge(v_bl, v_br)
        self.add_edge(v_tl, v_bl)
        self.add_edge(v_tr, v_br)

        self.add_face([v_tl, v_tr, v_br, v_bl])

    def _add_flame_points(self):
        """Add flame points on spike tips."""
        head_y = self.handle_length + self.head_radius

        # Center top flame
        self.add_flame_point(
            name="head_top",
            position=(0.0, head_y + self.head_radius + 0.1, 0.0),
            direction=(0.0, 1.0, 0.0),
            intensity=1.0
        )

        # Spike tip flames
        for i in range(0, self.spike_count, 2):
            angle = 2.0 * np.pi * i / self.spike_count
            base_x = self.head_radius * np.cos(angle)
            base_y = head_y + self.head_radius * 0.7 * np.sin(angle)

            spike_dir_x = np.cos(angle)
            spike_dir_y = 0.7 * np.sin(angle)

            tip_x = base_x + self.spike_length * spike_dir_x
            tip_y = base_y + self.spike_length * spike_dir_y

            self.add_flame_point(
                name=f"spike_{i}",
                position=(tip_x, tip_y, 0.0),
                direction=(spike_dir_x, spike_dir_y, 0.0),
                intensity=0.7
            )


def create_mace(name: str = "Mace") -> Mace:
    """Create a new mace instance."""
    return Mace(name)
