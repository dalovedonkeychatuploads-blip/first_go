"""
Weapon Base Module
Base classes for all procedural weapons with flame effect attachment points.
Each weapon inherits from WeaponBase and implements AAA procedural geometry.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from OpenGL.GL import *


@dataclass
class FlameAttachmentPoint:
    """
    Defines a point on the weapon where flame effects can be attached.
    Used for sword blades, mace heads, etc.
    """
    # Position relative to weapon origin
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    # Direction the flame should point (normalized vector)
    direction: Tuple[float, float, float] = (0.0, 1.0, 0.0)

    # Name/identifier for this attachment point
    name: str = "flame_point"

    # Whether this point is currently active
    active: bool = True

    # Flame intensity multiplier at this point (0.0 to 1.0)
    intensity: float = 1.0


@dataclass
class WeaponVertex:
    """Single vertex in weapon geometry."""
    position: Tuple[float, float, float]
    color: Optional[Tuple[float, float, float, float]] = None
    normal: Optional[Tuple[float, float, float]] = None
    uv: Optional[Tuple[float, float]] = None


class WeaponBase:
    """
    Base class for all procedural weapons.
    Provides common functionality for rendering, transforms, and flame attachment.
    """

    def __init__(self, name: str = "Weapon"):
        """
        Initialize weapon base.

        Args:
            name: Display name of the weapon
        """
        self.name = name

        # Transform properties
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.rotation = np.array([0.0, 0.0, 0.0], dtype=np.float32)  # Euler angles (x, y, z)
        self.scale = np.array([1.0, 1.0, 1.0], dtype=np.float32)

        # Visual properties
        self.color = np.array([0.7, 0.7, 0.8, 1.0], dtype=np.float32)  # Default metallic gray
        self.line_width = 3.0

        # Geometry data (to be filled by subclasses)
        self.vertices: List[WeaponVertex] = []
        self.edges: List[Tuple[int, int]] = []  # Pairs of vertex indices
        self.faces: List[List[int]] = []  # Lists of vertex indices (for HD mode)

        # Flame attachment points
        self.flame_points: List[FlameAttachmentPoint] = []

        # Metadata
        self.weapon_type = "base"
        self.description = "Base weapon class"

    # ========================================================================
    # GEOMETRY GENERATION (Override in subclasses)
    # ========================================================================

    def generate_geometry(self):
        """
        Generate procedural geometry for this weapon.
        MUST be overridden by subclasses to create specific weapon shapes.
        """
        raise NotImplementedError("Subclasses must implement generate_geometry()")

    # ========================================================================
    # RENDERING
    # ========================================================================

    def render_vector(self):
        """
        Render weapon in vector mode (clean lines, fast).
        Uses GL_LINES to draw weapon edges.
        """
        if not self.vertices or not self.edges:
            return

        glPushMatrix()

        # Apply transforms
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(self.rotation[2], 0, 0, 1)  # Z rotation (most common for 2D)
        glRotatef(self.rotation[1], 0, 1, 0)  # Y rotation
        glRotatef(self.rotation[0], 1, 0, 0)  # X rotation
        glScalef(self.scale[0], self.scale[1], self.scale[2])

        # Set line width and color
        glLineWidth(self.line_width)
        glColor4fv(self.color)

        # Draw edges as lines
        glBegin(GL_LINES)
        for edge in self.edges:
            if len(edge) != 2:
                continue

            v1_idx, v2_idx = edge

            # Safety check for valid indices
            if v1_idx < 0 or v1_idx >= len(self.vertices):
                continue
            if v2_idx < 0 or v2_idx >= len(self.vertices):
                continue

            v1 = self.vertices[v1_idx]
            v2 = self.vertices[v2_idx]

            # Use vertex color if available, otherwise use weapon color
            if v1.color is not None:
                glColor4fv(v1.color)

            glVertex3fv(v1.position)
            glVertex3fv(v2.position)

        glEnd()

        # Draw flame attachment point indicators (small crosses)
        self._render_flame_attachment_points()

        glPopMatrix()

    def render_hd(self):
        """
        Render weapon in HD mode (textured, shaded, detailed).
        Uses GL_TRIANGLES with lighting and textures.
        """
        if not self.vertices or not self.faces:
            # Fall back to vector rendering if no face data
            self.render_vector()
            return

        glPushMatrix()

        # Apply transforms
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glRotatef(self.rotation[2], 0, 0, 1)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[0], 1, 0, 0)
        glScalef(self.scale[0], self.scale[1], self.scale[2])

        # Enable lighting for HD mode (will be configured in hd_renderer.py)
        # For now, just render faces with flat shading

        glColor4fv(self.color)

        # Draw faces as triangles
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            if len(face) < 3:
                continue

            # Triangulate face (simple fan triangulation)
            for i in range(1, len(face) - 1):
                v1_idx = face[0]
                v2_idx = face[i]
                v3_idx = face[i + 1]

                # Safety checks
                if v1_idx < 0 or v1_idx >= len(self.vertices):
                    continue
                if v2_idx < 0 or v2_idx >= len(self.vertices):
                    continue
                if v3_idx < 0 or v3_idx >= len(self.vertices):
                    continue

                v1 = self.vertices[v1_idx]
                v2 = self.vertices[v2_idx]
                v3 = self.vertices[v3_idx]

                # Calculate face normal if not provided
                if v1.normal is None:
                    # Simple normal calculation
                    p1 = np.array(v1.position)
                    p2 = np.array(v2.position)
                    p3 = np.array(v3.position)

                    edge1 = p2 - p1
                    edge2 = p3 - p1
                    normal = np.cross(edge1, edge2)

                    # Normalize
                    norm_length = np.linalg.norm(normal)
                    if norm_length > 0.0001:
                        normal = normal / norm_length
                    else:
                        normal = np.array([0.0, 0.0, 1.0])

                    glNormal3fv(normal)

                # Draw triangle
                glVertex3fv(v1.position)
                glVertex3fv(v2.position)
                glVertex3fv(v3.position)

        glEnd()

        glPopMatrix()

    def _render_flame_attachment_points(self):
        """
        Render small visual indicators for flame attachment points.
        Useful for debugging and weapon editing.
        """
        glColor4f(1.0, 0.5, 0.0, 0.8)  # Orange color for flame points
        glLineWidth(2.0)

        for point in self.flame_points:
            if not point.active:
                continue

            pos = point.position

            # Draw a small cross at the attachment point
            cross_size = 0.1

            glBegin(GL_LINES)
            # Horizontal line
            glVertex3f(pos[0] - cross_size, pos[1], pos[2])
            glVertex3f(pos[0] + cross_size, pos[1], pos[2])

            # Vertical line
            glVertex3f(pos[0], pos[1] - cross_size, pos[2])
            glVertex3f(pos[0], pos[1] + cross_size, pos[2])
            glEnd()

        glLineWidth(self.line_width)  # Reset line width

    # ========================================================================
    # TRANSFORM METHODS
    # ========================================================================

    def set_position(self, x: float, y: float, z: float = 0.0):
        """Set weapon position."""
        self.position = np.array([x, y, z], dtype=np.float32)

    def set_rotation(self, x: float, y: float, z: float):
        """Set weapon rotation (Euler angles in degrees)."""
        self.rotation = np.array([x, y, z], dtype=np.float32)

    def set_scale(self, x: float, y: float = None, z: float = None):
        """Set weapon scale (uniform if only x provided)."""
        if y is None:
            y = x
        if z is None:
            z = x
        self.scale = np.array([x, y, z], dtype=np.float32)

    def rotate(self, dx: float, dy: float, dz: float):
        """Rotate weapon by delta angles."""
        self.rotation += np.array([dx, dy, dz], dtype=np.float32)

    def translate(self, dx: float, dy: float, dz: float = 0.0):
        """Translate weapon by delta position."""
        self.position += np.array([dx, dy, dz], dtype=np.float32)

    # ========================================================================
    # FLAME ATTACHMENT MANAGEMENT
    # ========================================================================

    def add_flame_point(self, name: str, position: Tuple[float, float, float],
                        direction: Tuple[float, float, float] = (0.0, 1.0, 0.0),
                        intensity: float = 1.0):
        """
        Add a flame attachment point to this weapon.

        Args:
            name: Identifier for this flame point
            position: (x, y, z) position relative to weapon origin
            direction: (x, y, z) normalized direction vector for flame
            intensity: Flame intensity multiplier (0.0 to 1.0)
        """
        point = FlameAttachmentPoint(
            position=position,
            direction=direction,
            name=name,
            active=True,
            intensity=intensity
        )
        self.flame_points.append(point)
        return point

    def get_flame_point(self, name: str) -> Optional[FlameAttachmentPoint]:
        """Get flame attachment point by name."""
        for point in self.flame_points:
            if point.name == name:
                return point
        return None

    def get_world_flame_positions(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Get flame attachment positions in world space (after transforms).
        Returns list of (position, direction) tuples.
        """
        world_positions = []

        for point in self.flame_points:
            if not point.active:
                continue

            # Transform position by weapon transform
            # (Simplified - full matrix transform would be more accurate)
            pos = np.array(point.position, dtype=np.float32)
            dir_vec = np.array(point.direction, dtype=np.float32)

            # Apply scale
            pos = pos * self.scale

            # Apply rotation (simplified 2D rotation around Z axis)
            angle_rad = np.radians(self.rotation[2])
            cos_a = np.cos(angle_rad)
            sin_a = np.sin(angle_rad)

            rotated_pos = np.array([
                pos[0] * cos_a - pos[1] * sin_a,
                pos[0] * sin_a + pos[1] * cos_a,
                pos[2]
            ], dtype=np.float32)

            rotated_dir = np.array([
                dir_vec[0] * cos_a - dir_vec[1] * sin_a,
                dir_vec[0] * sin_a + dir_vec[1] * cos_a,
                dir_vec[2]
            ], dtype=np.float32)

            # Apply translation
            world_pos = rotated_pos + self.position

            world_positions.append((world_pos, rotated_dir))

        return world_positions

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def add_vertex(self, x: float, y: float, z: float = 0.0,
                   color: Optional[Tuple[float, float, float, float]] = None) -> int:
        """
        Add a vertex to the weapon geometry.
        Returns the index of the added vertex.
        """
        vertex = WeaponVertex(
            position=(x, y, z),
            color=color
        )
        self.vertices.append(vertex)
        return len(self.vertices) - 1

    def add_edge(self, v1_idx: int, v2_idx: int):
        """Add an edge between two vertices."""
        self.edges.append((v1_idx, v2_idx))

    def add_face(self, vertex_indices: List[int]):
        """Add a face (polygon) for HD rendering."""
        self.faces.append(vertex_indices)

    def clear_geometry(self):
        """Clear all geometry data."""
        self.vertices.clear()
        self.edges.clear()
        self.faces.clear()

    def get_bounding_box(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate axis-aligned bounding box.
        Returns (min_point, max_point) as numpy arrays.
        """
        if not self.vertices:
            return (np.array([0, 0, 0]), np.array([0, 0, 0]))

        positions = np.array([v.position for v in self.vertices], dtype=np.float32)
        min_point = np.min(positions, axis=0)
        max_point = np.max(positions, axis=0)

        return (min_point, max_point)

    # ========================================================================
    # SERIALIZATION
    # ========================================================================

    def to_dict(self) -> dict:
        """Serialize weapon to dictionary for saving."""
        return {
            'name': self.name,
            'weapon_type': self.weapon_type,
            'position': self.position.tolist(),
            'rotation': self.rotation.tolist(),
            'scale': self.scale.tolist(),
            'color': self.color.tolist(),
            'line_width': self.line_width,
            'flame_points': [
                {
                    'name': fp.name,
                    'position': fp.position,
                    'direction': fp.direction,
                    'active': fp.active,
                    'intensity': fp.intensity
                }
                for fp in self.flame_points
            ]
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize weapon from dictionary."""
        weapon = cls(name=data.get('name', 'Weapon'))

        weapon.position = np.array(data.get('position', [0, 0, 0]), dtype=np.float32)
        weapon.rotation = np.array(data.get('rotation', [0, 0, 0]), dtype=np.float32)
        weapon.scale = np.array(data.get('scale', [1, 1, 1]), dtype=np.float32)
        weapon.color = np.array(data.get('color', [0.7, 0.7, 0.8, 1.0]), dtype=np.float32)
        weapon.line_width = data.get('line_width', 3.0)

        # Restore flame points
        for fp_data in data.get('flame_points', []):
            weapon.add_flame_point(
                name=fp_data['name'],
                position=tuple(fp_data['position']),
                direction=tuple(fp_data['direction']),
                intensity=fp_data.get('intensity', 1.0)
            )

        # Regenerate geometry
        weapon.generate_geometry()

        return weapon

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}' @ {self.position}>"
