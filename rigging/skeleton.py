"""
Skeleton System
Hierarchical bone-based rigging for stick figure characters.

Features:
- Parent-child bone hierarchy
- Forward kinematics (FK) with transform propagation
- Local and world space transformations
- Weapon attachment points
- Angle constraints for realistic movement
- Pose saving/loading for keyframe animation
- Debug visualization rendering
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from enum import Enum
from OpenGL.GL import *


# ============================================================================
# BONE TYPES ENUM
# ============================================================================

class BoneType(Enum):
    """Predefined bone types for stick figure skeleton."""
    ROOT = "root"               # Hip/pelvis (skeleton root)
    SPINE = "spine"            # Torso/spine
    NECK = "neck"              # Neck
    HEAD = "head"              # Head
    UPPER_ARM_L = "upper_arm_l"
    UPPER_ARM_R = "upper_arm_r"
    FOREARM_L = "forearm_l"
    FOREARM_R = "forearm_r"
    HAND_L = "hand_l"
    HAND_R = "hand_r"
    THIGH_L = "thigh_l"
    THIGH_R = "thigh_r"
    SHIN_L = "shin_l"
    SHIN_R = "shin_r"
    FOOT_L = "foot_l"
    FOOT_R = "foot_r"


# ============================================================================
# BONE CLASS
# ============================================================================

@dataclass
class Bone:
    """
    Single bone in a skeletal hierarchy.
    Supports parent-child relationships and forward kinematics.
    """
    # Identification
    name: str
    bone_type: Optional[BoneType] = None

    # Hierarchy
    parent: Optional['Bone'] = None
    children: List['Bone'] = field(default_factory=list)

    # Local transform (relative to parent)
    local_position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0], dtype=np.float32))
    local_rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0], dtype=np.float32))  # Euler angles (degrees)
    local_scale: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0], dtype=np.float32))

    # Bone properties
    length: float = 1.0
    thickness: float = 0.05

    # World transform cache (computed via forward kinematics)
    _world_position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0], dtype=np.float32))
    _world_rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0], dtype=np.float32))
    _world_dirty: bool = True

    # Constraints (for realistic movement)
    rotation_limits_min: np.ndarray = field(default_factory=lambda: np.array([-180.0, -180.0, -180.0], dtype=np.float32))
    rotation_limits_max: np.ndarray = field(default_factory=lambda: np.array([180.0, 180.0, 180.0], dtype=np.float32))

    # Visual properties
    color: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32))
    visible: bool = True

    def __post_init__(self):
        """Initialize bone and validate parameters."""
        # Ensure all numpy arrays are float32 for OpenGL compatibility
        if not isinstance(self.local_position, np.ndarray):
            self.local_position = np.array(self.local_position, dtype=np.float32)
        if not isinstance(self.local_rotation, np.ndarray):
            self.local_rotation = np.array(self.local_rotation, dtype=np.float32)
        if not isinstance(self.local_scale, np.ndarray):
            self.local_scale = np.array(self.local_scale, dtype=np.float32)

        # Validate length and thickness
        if self.length <= 0:
            raise ValueError(f"Bone length must be positive, got {self.length}")
        if self.thickness <= 0:
            raise ValueError(f"Bone thickness must be positive, got {self.thickness}")

    # ========================================================================
    # HIERARCHY MANAGEMENT
    # ========================================================================

    def add_child(self, child: 'Bone'):
        """
        Add a child bone to this bone.

        Args:
            child: Child bone to add

        Raises:
            ValueError: If child already has a parent or creates a cycle
        """
        if child.parent is not None and child.parent != self:
            raise ValueError(f"Bone '{child.name}' already has parent '{child.parent.name}'")

        if self._would_create_cycle(child):
            raise ValueError(f"Adding bone '{child.name}' would create a cycle")

        if child not in self.children:
            self.children.append(child)
            child.parent = self
            child.mark_dirty()

    def remove_child(self, child: 'Bone'):
        """Remove a child bone from this bone."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            child.mark_dirty()

    def _would_create_cycle(self, potential_child: 'Bone') -> bool:
        """Check if adding a child would create a cycle in the hierarchy."""
        current = self
        while current is not None:
            if current == potential_child:
                return True
            current = current.parent
        return False

    def get_root(self) -> 'Bone':
        """Get the root bone of this hierarchy."""
        root = self
        while root.parent is not None:
            root = root.parent
        return root

    def get_all_descendants(self) -> List['Bone']:
        """Get all descendant bones (children, grandchildren, etc.)."""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    # ========================================================================
    # LOCAL TRANSFORM MANIPULATION
    # ========================================================================

    def set_local_position(self, x: float, y: float, z: float = 0.0):
        """Set bone position relative to parent."""
        self.local_position = np.array([x, y, z], dtype=np.float32)
        self.mark_dirty()

    def set_local_rotation(self, x: float, y: float, z: float):
        """
        Set bone rotation relative to parent (Euler angles in degrees).

        Args:
            x, y, z: Rotation in degrees around X, Y, Z axes
        """
        # Clamp to rotation limits
        x = max(self.rotation_limits_min[0], min(self.rotation_limits_max[0], x))
        y = max(self.rotation_limits_min[1], min(self.rotation_limits_max[1], y))
        z = max(self.rotation_limits_min[2], min(self.rotation_limits_max[2], z))

        self.local_rotation = np.array([x, y, z], dtype=np.float32)
        self.mark_dirty()

    def rotate(self, dx: float, dy: float, dz: float):
        """Rotate bone by delta angles (relative rotation)."""
        new_rotation = self.local_rotation + np.array([dx, dy, dz], dtype=np.float32)
        self.set_local_rotation(new_rotation[0], new_rotation[1], new_rotation[2])

    def set_local_scale(self, x: float, y: float = None, z: float = None):
        """Set bone scale relative to parent."""
        if y is None:
            y = x
        if z is None:
            z = x
        self.local_scale = np.array([x, y, z], dtype=np.float32)
        self.mark_dirty()

    # ========================================================================
    # FORWARD KINEMATICS (World Transform Computation)
    # ========================================================================

    def mark_dirty(self):
        """Mark this bone and all descendants as needing transform update."""
        self._world_dirty = True
        for child in self.children:
            child.mark_dirty()

    def update_world_transform(self):
        """
        Update world transform from local transform and parent.
        This implements forward kinematics.
        """
        if not self._world_dirty:
            return  # Already up to date

        if self.parent is None:
            # Root bone: world transform = local transform
            self._world_position = self.local_position.copy()
            self._world_rotation = self.local_rotation.copy()
        else:
            # Non-root: combine with parent's world transform
            # Ensure parent is up to date first
            self.parent.update_world_transform()

            # Compute world position
            # Rotate local position by parent's world rotation, then add parent's world position
            parent_rot_rad = np.radians(self.parent._world_rotation[2])  # Z rotation (2D)
            cos_r = np.cos(parent_rot_rad)
            sin_r = np.sin(parent_rot_rad)

            rotated_local_x = self.local_position[0] * cos_r - self.local_position[1] * sin_r
            rotated_local_y = self.local_position[0] * sin_r + self.local_position[1] * cos_r

            self._world_position = self.parent._world_position + np.array([
                rotated_local_x,
                rotated_local_y,
                self.local_position[2]
            ], dtype=np.float32)

            # Compute world rotation (simple addition for Euler angles)
            self._world_rotation = self.parent._world_rotation + self.local_rotation

        self._world_dirty = False

    def get_world_position(self) -> np.ndarray:
        """Get bone position in world space."""
        self.update_world_transform()
        return self._world_position.copy()

    def get_world_rotation(self) -> np.ndarray:
        """Get bone rotation in world space (Euler angles in degrees)."""
        self.update_world_transform()
        return self._world_rotation.copy()

    def get_end_position(self) -> np.ndarray:
        """
        Get the world position of the bone's end point (tip).
        Useful for connecting child bones.
        """
        self.update_world_transform()

        # Calculate end position based on bone length and world rotation
        angle_rad = np.radians(self._world_rotation[2])  # Z rotation (2D)

        end_x = self._world_position[0] + self.length * np.sin(angle_rad)
        end_y = self._world_position[1] + self.length * np.cos(angle_rad)
        end_z = self._world_position[2]

        return np.array([end_x, end_y, end_z], dtype=np.float32)

    # ========================================================================
    # CONSTRAINTS
    # ========================================================================

    def set_rotation_limits(self, min_angles: Tuple[float, float, float],
                           max_angles: Tuple[float, float, float]):
        """
        Set rotation constraints for this bone.

        Args:
            min_angles: Minimum rotation (x, y, z) in degrees
            max_angles: Maximum rotation (x, y, z) in degrees
        """
        self.rotation_limits_min = np.array(min_angles, dtype=np.float32)
        self.rotation_limits_max = np.array(max_angles, dtype=np.float32)

        # Re-clamp current rotation
        self.set_local_rotation(
            self.local_rotation[0],
            self.local_rotation[1],
            self.local_rotation[2]
        )

    # ========================================================================
    # RENDERING
    # ========================================================================

    def render(self, draw_endpoints: bool = True, draw_constraints: bool = False):
        """
        Render this bone for debugging/visualization.

        Args:
            draw_endpoints: Whether to draw circles at bone endpoints
            draw_constraints: Whether to visualize rotation limits
        """
        if not self.visible:
            return

        self.update_world_transform()

        start_pos = self._world_position
        end_pos = self.get_end_position()

        # Draw bone as line
        glLineWidth(self.thickness * 100.0)  # Scale thickness for visibility
        glColor4fv(self.color)

        glBegin(GL_LINES)
        glVertex3fv(start_pos)
        glVertex3fv(end_pos)
        glEnd()

        # Draw endpoints as circles
        if draw_endpoints:
            self._draw_joint(start_pos, self.thickness * 1.5)
            self._draw_joint(end_pos, self.thickness * 1.2)

        # Draw constraints visualization
        if draw_constraints and self.parent is not None:
            self._draw_constraints(start_pos)

    def _draw_joint(self, position: np.ndarray, radius: float):
        """Draw a joint (circle) at the specified position."""
        glColor4fv(self.color)
        segments = 12

        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = 2.0 * np.pi * i / segments
            x = position[0] + radius * np.cos(angle)
            y = position[1] + radius * np.sin(angle)
            glVertex3f(x, y, position[2])
        glEnd()

    def _draw_constraints(self, position: np.ndarray):
        """Draw rotation constraint arcs."""
        # Draw arc showing rotation limits
        glColor4f(1.0, 1.0, 0.0, 0.3)  # Yellow, semi-transparent

        min_angle_rad = np.radians(self.rotation_limits_min[2])
        max_angle_rad = np.radians(self.rotation_limits_max[2])

        arc_radius = self.length * 0.3
        segments = 20

        glBegin(GL_LINE_STRIP)
        for i in range(segments + 1):
            t = i / segments
            angle = min_angle_rad + t * (max_angle_rad - min_angle_rad)
            x = position[0] + arc_radius * np.sin(angle)
            y = position[1] + arc_radius * np.cos(angle)
            glVertex3f(x, y, position[2])
        glEnd()

    # ========================================================================
    # SERIALIZATION
    # ========================================================================

    def to_dict(self) -> dict:
        """Serialize bone to dictionary."""
        return {
            'name': self.name,
            'bone_type': self.bone_type.value if self.bone_type else None,
            'local_position': self.local_position.tolist(),
            'local_rotation': self.local_rotation.tolist(),
            'local_scale': self.local_scale.tolist(),
            'length': self.length,
            'thickness': self.thickness,
            'rotation_limits_min': self.rotation_limits_min.tolist(),
            'rotation_limits_max': self.rotation_limits_max.tolist(),
            'color': self.color.tolist(),
            'visible': self.visible,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Bone':
        """Deserialize bone from dictionary."""
        bone_type = BoneType(data['bone_type']) if data.get('bone_type') else None

        bone = cls(
            name=data['name'],
            bone_type=bone_type,
            local_position=np.array(data['local_position'], dtype=np.float32),
            local_rotation=np.array(data['local_rotation'], dtype=np.float32),
            local_scale=np.array(data['local_scale'], dtype=np.float32),
            length=data.get('length', 1.0),
            thickness=data.get('thickness', 0.05),
            color=np.array(data.get('color', [1.0, 1.0, 1.0, 1.0]), dtype=np.float32),
            visible=data.get('visible', True),
        )

        bone.rotation_limits_min = np.array(data['rotation_limits_min'], dtype=np.float32)
        bone.rotation_limits_max = np.array(data['rotation_limits_max'], dtype=np.float32)

        return bone

    def __repr__(self):
        parent_name = self.parent.name if self.parent else "None"
        return f"<Bone '{self.name}' parent={parent_name} pos={self.local_position} rot={self.local_rotation}>"


# ============================================================================
# SKELETON CLASS
# ============================================================================

class Skeleton:
    """
    Complete skeletal rig for a stick figure character.
    Manages bone hierarchy and provides high-level rigging operations.
    """

    def __init__(self, name: str = "Skeleton"):
        """
        Initialize skeleton.

        Args:
            name: Skeleton identifier
        """
        self.name = name

        # Bone storage
        self.bones: Dict[str, Bone] = {}  # name -> Bone
        self.root_bone: Optional[Bone] = None

        # Skeleton properties
        self.scale = 1.0
        self.visible = True

        print(f"✓ Skeleton '{name}' created")

    # ========================================================================
    # BONE MANAGEMENT
    # ========================================================================

    def add_bone(self, bone: Bone, parent_name: Optional[str] = None):
        """
        Add a bone to the skeleton.

        Args:
            bone: Bone to add
            parent_name: Name of parent bone (None for root)

        Raises:
            ValueError: If bone name already exists or parent not found
        """
        if bone.name in self.bones:
            raise ValueError(f"Bone '{bone.name}' already exists in skeleton")

        # Add to storage
        self.bones[bone.name] = bone

        # Set up hierarchy
        if parent_name is None:
            if self.root_bone is None:
                self.root_bone = bone
            else:
                raise ValueError("Skeleton already has a root bone")
        else:
            if parent_name not in self.bones:
                raise ValueError(f"Parent bone '{parent_name}' not found")

            parent_bone = self.bones[parent_name]
            parent_bone.add_child(bone)

        bone.mark_dirty()

    def get_bone(self, name: str) -> Optional[Bone]:
        """Get bone by name."""
        return self.bones.get(name)

    def get_all_bones(self) -> List[Bone]:
        """Get all bones in the skeleton."""
        return list(self.bones.values())

    def remove_bone(self, name: str):
        """
        Remove a bone and all its descendants from the skeleton.

        Args:
            name: Name of bone to remove
        """
        if name not in self.bones:
            return

        bone = self.bones[name]

        # Remove all descendants first
        for child in bone.children[:]:
            self.remove_bone(child.name)

        # Remove from parent
        if bone.parent:
            bone.parent.remove_child(bone)

        # Remove from storage
        del self.bones[name]

        # Update root if needed
        if bone == self.root_bone:
            self.root_bone = None

    # ========================================================================
    # POSE MANIPULATION
    # ========================================================================

    def set_bone_rotation(self, bone_name: str, x: float, y: float, z: float):
        """Set rotation for a specific bone."""
        bone = self.get_bone(bone_name)
        if bone:
            bone.set_local_rotation(x, y, z)

    def reset_pose(self):
        """Reset all bones to default pose (zero rotation)."""
        for bone in self.bones.values():
            bone.set_local_rotation(0.0, 0.0, 0.0)

    def get_pose(self) -> Dict[str, np.ndarray]:
        """
        Get current pose as dictionary of bone rotations.

        Returns:
            Dict mapping bone names to rotation arrays
        """
        pose = {}
        for name, bone in self.bones.items():
            pose[name] = bone.local_rotation.copy()
        return pose

    def set_pose(self, pose: Dict[str, np.ndarray]):
        """
        Set skeleton pose from dictionary.

        Args:
            pose: Dict mapping bone names to rotation arrays
        """
        for name, rotation in pose.items():
            if name in self.bones:
                bone = self.bones[name]
                bone.set_local_rotation(rotation[0], rotation[1], rotation[2])

    # ========================================================================
    # FORWARD KINEMATICS
    # ========================================================================

    def update(self):
        """Update all bone world transforms (forward kinematics)."""
        if self.root_bone:
            self.root_bone.update_world_transform()

    # ========================================================================
    # RENDERING
    # ========================================================================

    def render(self, draw_joints: bool = True, draw_constraints: bool = False):
        """
        Render the entire skeleton.

        Args:
            draw_joints: Whether to draw joint circles
            draw_constraints: Whether to visualize rotation limits
        """
        if not self.visible:
            return

        # Update transforms first
        self.update()

        # Render all bones
        for bone in self.bones.values():
            bone.render(draw_endpoints=draw_joints, draw_constraints=draw_constraints)

    # ========================================================================
    # SERIALIZATION
    # ========================================================================

    def to_dict(self) -> dict:
        """Serialize skeleton to dictionary."""
        # Build hierarchy representation
        bones_data = []

        for bone in self.bones.values():
            bone_data = bone.to_dict()
            bone_data['parent'] = bone.parent.name if bone.parent else None
            bones_data.append(bone_data)

        return {
            'name': self.name,
            'scale': self.scale,
            'visible': self.visible,
            'root_bone': self.root_bone.name if self.root_bone else None,
            'bones': bones_data,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Skeleton':
        """Deserialize skeleton from dictionary."""
        skeleton = cls(name=data['name'])
        skeleton.scale = data.get('scale', 1.0)
        skeleton.visible = data.get('visible', True)

        # First pass: create all bones
        bones_by_name = {}
        for bone_data in data['bones']:
            bone = Bone.from_dict(bone_data)
            bones_by_name[bone.name] = bone

        # Second pass: build hierarchy
        for bone_data in data['bones']:
            bone = bones_by_name[bone_data['name']]
            parent_name = bone_data.get('parent')

            skeleton.add_bone(bone, parent_name)

        return skeleton

    def __repr__(self):
        return f"<Skeleton '{self.name}' bones={len(self.bones)}>"
