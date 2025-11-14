"""
Animation Base System
Keyframe-based animation with interpolation for skeletal rigs.

Features:
- Keyframe storage (bone transforms at specific times)
- Multiple interpolation types (linear, ease-in/out, bezier)
- Animation playback and evaluation
- Animation curves and easing functions
- Animation blending
- Serialization (save/load animations)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json


# ============================================================================
# INTERPOLATION TYPES
# ============================================================================

class InterpolationType(Enum):
    """Keyframe interpolation methods."""
    LINEAR = "linear"                    # Simple linear interpolation
    EASE_IN = "ease_in"                  # Slow start, fast end
    EASE_OUT = "ease_out"                # Fast start, slow end
    EASE_IN_OUT = "ease_in_out"          # Slow start, slow end, fast middle
    BEZIER = "bezier"                    # Custom bezier curve
    STEP = "step"                        # No interpolation (snap to value)


# ============================================================================
# KEYFRAME CLASS
# ============================================================================

@dataclass
class Keyframe:
    """
    Single keyframe storing bone transforms at a specific time.
    """
    # Timing
    time: float  # Time in seconds

    # Bone transforms (bone_name -> rotation array)
    bone_rotations: Dict[str, np.ndarray] = field(default_factory=dict)

    # Optional bone positions (if animating position)
    bone_positions: Dict[str, np.ndarray] = field(default_factory=dict)

    # Interpolation type to next keyframe
    interpolation: InterpolationType = InterpolationType.LINEAR

    # Bezier control points (if using bezier interpolation)
    bezier_handle_in: Tuple[float, float] = (0.33, 0.33)
    bezier_handle_out: Tuple[float, float] = (0.66, 0.66)

    def add_bone_rotation(self, bone_name: str, rotation: np.ndarray):
        """Add or update bone rotation in this keyframe."""
        self.bone_rotations[bone_name] = rotation.copy()

    def add_bone_position(self, bone_name: str, position: np.ndarray):
        """Add or update bone position in this keyframe."""
        self.bone_positions[bone_name] = position.copy()

    def get_bone_rotation(self, bone_name: str) -> Optional[np.ndarray]:
        """Get bone rotation at this keyframe."""
        return self.bone_rotations.get(bone_name)

    def get_bone_position(self, bone_name: str) -> Optional[np.ndarray]:
        """Get bone position at this keyframe."""
        return self.bone_positions.get(bone_name)

    def to_dict(self) -> dict:
        """Serialize keyframe to dictionary."""
        return {
            'time': self.time,
            'bone_rotations': {name: rot.tolist() for name, rot in self.bone_rotations.items()},
            'bone_positions': {name: pos.tolist() for name, pos in self.bone_positions.items()},
            'interpolation': self.interpolation.value,
            'bezier_handle_in': self.bezier_handle_in,
            'bezier_handle_out': self.bezier_handle_out,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Keyframe':
        """Deserialize keyframe from dictionary."""
        keyframe = cls(
            time=data['time'],
            interpolation=InterpolationType(data.get('interpolation', 'linear')),
            bezier_handle_in=tuple(data.get('bezier_handle_in', (0.33, 0.33))),
            bezier_handle_out=tuple(data.get('bezier_handle_out', (0.66, 0.66))),
        )

        for bone_name, rot_list in data.get('bone_rotations', {}).items():
            keyframe.bone_rotations[bone_name] = np.array(rot_list, dtype=np.float32)

        for bone_name, pos_list in data.get('bone_positions', {}).items():
            keyframe.bone_positions[bone_name] = np.array(pos_list, dtype=np.float32)

        return keyframe


# ============================================================================
# EASING FUNCTIONS
# ============================================================================

class EasingFunctions:
    """
    Collection of easing functions for smooth interpolation.
    All functions take t in [0, 1] and return eased value in [0, 1].
    """

    @staticmethod
    def linear(t: float) -> float:
        """Linear interpolation (no easing)."""
        return t

    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic ease-in (accelerating)."""
        return t * t

    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease-out (decelerating)."""
        return t * (2.0 - t)

    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease-in-out (accelerate then decelerate)."""
        if t < 0.5:
            return 2.0 * t * t
        else:
            return -1.0 + (4.0 - 2.0 * t) * t

    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic ease-in (strong acceleration)."""
        return t * t * t

    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out (strong deceleration)."""
        t_minus_1 = t - 1.0
        return t_minus_1 * t_minus_1 * t_minus_1 + 1.0

    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease-in-out."""
        if t < 0.5:
            return 4.0 * t * t * t
        else:
            t_minus_1 = t - 1.0
            return 1.0 + 4.0 * t_minus_1 * t_minus_1 * t_minus_1

    @staticmethod
    def bezier_cubic(t: float, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """
        Cubic bezier curve interpolation.

        Args:
            t: Time parameter [0, 1]
            p1: First control point (x, y)
            p2: Second control point (x, y)

        Returns:
            Interpolated value
        """
        # Cubic bezier: B(t) = (1-t)³P₀ + 3(1-t)²t P₁ + 3(1-t)t² P₂ + t³P₃
        # Where P₀ = (0, 0) and P₃ = (1, 1) for our normalized curve

        one_minus_t = 1.0 - t

        # Calculate Y value (we use Y for the interpolation)
        y = (3.0 * one_minus_t * one_minus_t * t * p1[1] +
             3.0 * one_minus_t * t * t * p2[1] +
             t * t * t)

        return y


# ============================================================================
# ANIMATION CLASS
# ============================================================================

class Animation:
    """
    Complete animation with keyframes and playback control.
    Stores bone transforms over time with interpolation.
    """

    def __init__(self, name: str, duration: float = 1.0, fps: int = 60):
        """
        Initialize animation.

        Args:
            name: Animation identifier
            duration: Animation duration in seconds
            fps: Frames per second (for frame-based operations)
        """
        self.name = name
        self.duration = duration
        self.fps = fps

        # Keyframes (sorted by time)
        self.keyframes: List[Keyframe] = []

        # Playback state
        self.current_time = 0.0
        self.is_playing = False
        self.loop = True

        print(f"✓ Animation '{name}' created (duration: {duration}s @ {fps}fps)")

    # ========================================================================
    # KEYFRAME MANAGEMENT
    # ========================================================================

    def add_keyframe(self, keyframe: Keyframe):
        """
        Add a keyframe to the animation.
        Keyframes are automatically sorted by time.
        """
        self.keyframes.append(keyframe)
        self.keyframes.sort(key=lambda k: k.time)

    def add_keyframe_at_time(self, time: float, bone_poses: Dict[str, np.ndarray],
                            interpolation: InterpolationType = InterpolationType.LINEAR) -> Keyframe:
        """
        Convenience method to add a keyframe with bone poses.

        Args:
            time: Time in seconds
            bone_poses: Dict mapping bone names to rotation arrays
            interpolation: Interpolation type to next keyframe

        Returns:
            Created Keyframe
        """
        keyframe = Keyframe(time=time, interpolation=interpolation)

        for bone_name, rotation in bone_poses.items():
            keyframe.add_bone_rotation(bone_name, rotation)

        self.add_keyframe(keyframe)

        return keyframe

    def remove_keyframe_at_time(self, time: float, tolerance: float = 0.01):
        """Remove keyframe at specified time (within tolerance)."""
        self.keyframes = [k for k in self.keyframes if abs(k.time - time) > tolerance]

    def get_keyframe_at_time(self, time: float, tolerance: float = 0.01) -> Optional[Keyframe]:
        """Get keyframe at specified time (within tolerance)."""
        for keyframe in self.keyframes:
            if abs(keyframe.time - time) < tolerance:
                return keyframe
        return None

    def get_keyframes_around_time(self, time: float) -> Tuple[Optional[Keyframe], Optional[Keyframe]]:
        """
        Get keyframes immediately before and after specified time.

        Returns:
            (keyframe_before, keyframe_after) tuple
        """
        before = None
        after = None

        for keyframe in self.keyframes:
            if keyframe.time <= time:
                before = keyframe
            elif keyframe.time > time and after is None:
                after = keyframe
                break  # Found both, can stop

        return (before, after)

    # ========================================================================
    # INTERPOLATION
    # ========================================================================

    def evaluate_at_time(self, time: float) -> Dict[str, np.ndarray]:
        """
        Evaluate animation at a specific time.
        Returns interpolated bone rotations.

        Args:
            time: Time in seconds

        Returns:
            Dict mapping bone names to interpolated rotation arrays
        """
        if not self.keyframes:
            return {}

        # Clamp time to animation duration if not looping
        if not self.loop:
            time = max(0.0, min(self.duration, time))
        else:
            # Wrap time for looping
            time = time % self.duration

        # Get surrounding keyframes
        kf_before, kf_after = self.get_keyframes_around_time(time)

        # If exactly on a keyframe, return its values
        if kf_before and abs(kf_before.time - time) < 0.001:
            return kf_before.bone_rotations.copy()

        # If before first keyframe, return first keyframe values
        if kf_before is None:
            return self.keyframes[0].bone_rotations.copy()

        # If after last keyframe, return last keyframe values
        if kf_after is None:
            return self.keyframes[-1].bone_rotations.copy()

        # Interpolate between keyframes
        return self._interpolate_keyframes(kf_before, kf_after, time)

    def _interpolate_keyframes(self, kf1: Keyframe, kf2: Keyframe, time: float) -> Dict[str, np.ndarray]:
        """
        Interpolate between two keyframes.

        Args:
            kf1: First keyframe (earlier in time)
            kf2: Second keyframe (later in time)
            time: Current time

        Returns:
            Interpolated bone rotations
        """
        # Calculate interpolation parameter (0 to 1)
        time_delta = kf2.time - kf1.time
        if time_delta < 0.0001:
            return kf1.bone_rotations.copy()

        t = (time - kf1.time) / time_delta
        t = max(0.0, min(1.0, t))  # Clamp to [0, 1]

        # Apply easing function based on interpolation type
        eased_t = self._apply_easing(t, kf1.interpolation, kf1.bezier_handle_in, kf1.bezier_handle_out)

        # Interpolate bone rotations
        result = {}

        # Get all bones from both keyframes
        all_bones = set(kf1.bone_rotations.keys()) | set(kf2.bone_rotations.keys())

        for bone_name in all_bones:
            rot1 = kf1.bone_rotations.get(bone_name)
            rot2 = kf2.bone_rotations.get(bone_name)

            if rot1 is not None and rot2 is not None:
                # Interpolate rotation
                result[bone_name] = rot1 + (rot2 - rot1) * eased_t
            elif rot1 is not None:
                result[bone_name] = rot1.copy()
            elif rot2 is not None:
                result[bone_name] = rot2.copy()

        return result

    def _apply_easing(self, t: float, interpolation: InterpolationType,
                     bezier_in: Tuple[float, float], bezier_out: Tuple[float, float]) -> float:
        """Apply easing function to interpolation parameter."""
        if interpolation == InterpolationType.LINEAR:
            return EasingFunctions.linear(t)

        elif interpolation == InterpolationType.EASE_IN:
            return EasingFunctions.ease_in_cubic(t)

        elif interpolation == InterpolationType.EASE_OUT:
            return EasingFunctions.ease_out_cubic(t)

        elif interpolation == InterpolationType.EASE_IN_OUT:
            return EasingFunctions.ease_in_out_cubic(t)

        elif interpolation == InterpolationType.BEZIER:
            return EasingFunctions.bezier_cubic(t, bezier_in, bezier_out)

        elif interpolation == InterpolationType.STEP:
            return 0.0  # No interpolation (stays at kf1 until kf2)

        else:
            return t  # Fallback to linear

    # ========================================================================
    # PLAYBACK CONTROL
    # ========================================================================

    def play(self):
        """Start playing the animation."""
        self.is_playing = True

    def pause(self):
        """Pause the animation."""
        self.is_playing = False

    def stop(self):
        """Stop and reset the animation."""
        self.is_playing = False
        self.current_time = 0.0

    def update(self, delta_time: float):
        """
        Update animation playback.

        Args:
            delta_time: Time elapsed since last update (seconds)
        """
        if not self.is_playing:
            return

        self.current_time += delta_time

        if self.loop:
            self.current_time = self.current_time % self.duration
        else:
            if self.current_time >= self.duration:
                self.current_time = self.duration
                self.is_playing = False  # Stop at end

    def seek(self, time: float):
        """Jump to specific time in animation."""
        self.current_time = max(0.0, min(self.duration, time))

    def get_current_pose(self) -> Dict[str, np.ndarray]:
        """Get bone rotations at current playback time."""
        return self.evaluate_at_time(self.current_time)

    # ========================================================================
    # ANIMATION BLENDING
    # ========================================================================

    @staticmethod
    def blend_poses(pose1: Dict[str, np.ndarray], pose2: Dict[str, np.ndarray],
                   blend_factor: float) -> Dict[str, np.ndarray]:
        """
        Blend between two poses.

        Args:
            pose1: First pose (bone rotations)
            pose2: Second pose (bone rotations)
            blend_factor: Blend weight (0.0 = pose1, 1.0 = pose2)

        Returns:
            Blended pose
        """
        blend_factor = max(0.0, min(1.0, blend_factor))

        result = {}

        all_bones = set(pose1.keys()) | set(pose2.keys())

        for bone_name in all_bones:
            rot1 = pose1.get(bone_name)
            rot2 = pose2.get(bone_name)

            if rot1 is not None and rot2 is not None:
                result[bone_name] = rot1 + (rot2 - rot1) * blend_factor
            elif rot1 is not None:
                result[bone_name] = rot1.copy()
            elif rot2 is not None:
                result[bone_name] = rot2.copy()

        return result

    # ========================================================================
    # SERIALIZATION
    # ========================================================================

    def to_dict(self) -> dict:
        """Serialize animation to dictionary."""
        return {
            'name': self.name,
            'duration': self.duration,
            'fps': self.fps,
            'loop': self.loop,
            'keyframes': [kf.to_dict() for kf in self.keyframes],
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Animation':
        """Deserialize animation from dictionary."""
        animation = cls(
            name=data['name'],
            duration=data['duration'],
            fps=data.get('fps', 60),
        )

        animation.loop = data.get('loop', True)

        for kf_data in data.get('keyframes', []):
            keyframe = Keyframe.from_dict(kf_data)
            animation.add_keyframe(keyframe)

        return animation

    def save_to_file(self, filepath: str):
        """Save animation to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"✓ Animation saved to {filepath}")

    @classmethod
    def load_from_file(cls, filepath: str) -> 'Animation':
        """Load animation from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        animation = cls.from_dict(data)
        print(f"✓ Animation loaded from {filepath}")
        return animation

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_frame_count(self) -> int:
        """Get total number of frames."""
        return int(self.duration * self.fps)

    def frame_to_time(self, frame: int) -> float:
        """Convert frame number to time."""
        return frame / self.fps

    def time_to_frame(self, time: float) -> int:
        """Convert time to frame number."""
        return int(time * self.fps)

    def __repr__(self):
        return f"<Animation '{self.name}' duration={self.duration}s keyframes={len(self.keyframes)}>"


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_animation(name: str, duration: float = 1.0) -> Animation:
    """Quick function to create an animation."""
    return Animation(name, duration)
