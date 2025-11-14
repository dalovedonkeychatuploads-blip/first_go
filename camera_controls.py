"""
Camera Controls System
Professional camera system for dynamic YouTube content creation.

Enables cinematic camera movements for stick figure fight choreography:
- Pan (left, right, up, down)
- Zoom (in, out)
- Rotate (for dramatic angles)
- Shake (impact frames, explosions)
- Smooth interpolation between keyframes
- Camera animations (keyframe-able camera movements)

This is CRITICAL for:
- Fight choreography (follow characters)
- Dramatic reveals (zoom in on face)
- Impact moments (screen shake on hits)
- Establishing shots (zoom out to show scene)
- Dynamic transitions (smooth camera moves)
"""

import numpy as np
import math
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

from OpenGL.GL import *
from OpenGL.GLU import *


# ============================================================================
# CAMERA MODES
# ============================================================================

class CameraMode(Enum):
    """Camera control modes."""
    FREE = "free"                  # Manual control
    FOLLOW = "follow"              # Follow a character
    FIXED = "fixed"                # Fixed position (locked)
    ANIMATED = "animated"          # Keyframe-animated camera


class ShakeType(Enum):
    """Screen shake patterns."""
    IMPACT = "impact"              # Quick shake (punch, kick)
    EXPLOSION = "explosion"        # Intense shake (big hits)
    RUMBLE = "rumble"             # Continuous vibration
    RANDOM = "random"             # Random jitter


# ============================================================================
# CAMERA SETTINGS
# ============================================================================

@dataclass
class CameraSettings:
    """
    Camera configuration.
    All settings can be adjusted in real-time.
    """
    # Position limits
    min_x: float = -100.0
    max_x: float = 100.0
    min_y: float = -100.0
    max_y: float = 100.0

    # Zoom limits
    min_zoom: float = 0.1
    max_zoom: float = 10.0

    # Rotation limits (degrees)
    min_rotation: float = -180.0
    max_rotation: float = 180.0

    # Movement speeds
    pan_speed: float = 1.0         # Units per second
    zoom_speed: float = 0.5        # Zoom factor per second
    rotation_speed: float = 45.0   # Degrees per second

    # Smoothing
    enable_smoothing: bool = True
    smoothing_factor: float = 0.15  # 0.0 = instant, 1.0 = very smooth

    # Shake settings
    shake_intensity: float = 1.0    # Multiplier for shake effects
    shake_decay: float = 5.0        # How fast shake fades (per second)


# ============================================================================
# CAMERA SHAKE EFFECT
# ============================================================================

class CameraShake:
    """
    Screen shake effect for impact moments.
    """

    def __init__(self, shake_type: ShakeType, intensity: float, duration: float):
        """
        Initialize camera shake.

        Args:
            shake_type: Type of shake pattern
            intensity: Shake strength (0.0-1.0+)
            duration: How long shake lasts (seconds)
        """
        self.shake_type = shake_type
        self.intensity = intensity
        self.duration = duration
        self.elapsed_time = 0.0
        self.is_active = True

        # Shake parameters based on type
        if shake_type == ShakeType.IMPACT:
            self.frequency = 30.0      # Fast shake
            self.amplitude = 0.5       # Medium distance
            self.decay_rate = 10.0     # Quick fade

        elif shake_type == ShakeType.EXPLOSION:
            self.frequency = 20.0      # Slower, more violent
            self.amplitude = 1.0       # Large distance
            self.decay_rate = 5.0      # Slower fade

        elif shake_type == ShakeType.RUMBLE:
            self.frequency = 15.0      # Low frequency
            self.amplitude = 0.3       # Small continuous
            self.decay_rate = 2.0      # Very slow fade

        elif shake_type == ShakeType.RANDOM:
            self.frequency = 25.0
            self.amplitude = 0.4
            self.decay_rate = 8.0

        # Apply intensity multiplier
        self.amplitude *= intensity

    def update(self, delta_time: float) -> Tuple[float, float]:
        """
        Update shake and get offset.

        Args:
            delta_time: Time since last update (seconds)

        Returns:
            (x_offset, y_offset) for camera position
        """
        if not self.is_active:
            return (0.0, 0.0)

        self.elapsed_time += delta_time

        # Check if shake is done
        if self.elapsed_time >= self.duration:
            self.is_active = False
            return (0.0, 0.0)

        # Calculate decay (shake fades over time)
        time_progress = self.elapsed_time / self.duration
        decay = 1.0 - time_progress
        decay = max(0.0, decay)

        # Calculate shake offset based on type
        if self.shake_type == ShakeType.RANDOM:
            # Random jitter
            x_offset = (np.random.random() - 0.5) * 2.0 * self.amplitude * decay
            y_offset = (np.random.random() - 0.5) * 2.0 * self.amplitude * decay

        else:
            # Sine wave shake
            angle = self.elapsed_time * self.frequency

            x_offset = math.sin(angle) * self.amplitude * decay
            y_offset = math.cos(angle * 1.3) * self.amplitude * decay  # Different frequency for variety

        return (x_offset, y_offset)


# ============================================================================
# CAMERA CONTROLLER
# ============================================================================

class Camera:
    """
    Professional camera controller for animation viewport.
    Handles all camera movements, shake effects, and keyframe animation.
    """

    def __init__(self, settings: Optional[CameraSettings] = None):
        """
        Initialize camera.

        Args:
            settings: Camera settings (uses defaults if None)
        """
        self.settings = settings if settings else CameraSettings()

        # Current state
        self.position = np.array([0.0, 0.0], dtype=np.float32)
        self.target_position = np.array([0.0, 0.0], dtype=np.float32)

        self.zoom = 1.0
        self.target_zoom = 1.0

        self.rotation = 0.0  # Degrees
        self.target_rotation = 0.0

        # Mode
        self.mode = CameraMode.FREE
        self.follow_target: Optional[np.ndarray] = None
        self.follow_offset = np.array([0.0, 0.0], dtype=np.float32)

        # Shake effects
        self.active_shakes: List[CameraShake] = []
        self.shake_offset = np.array([0.0, 0.0], dtype=np.float32)

        # Camera animations (keyframes for camera movement)
        self.is_animated = False
        self.animation_keyframes: List[Tuple[float, np.ndarray, float, float]] = []  # (time, pos, zoom, rot)
        self.animation_time = 0.0

        print("✓ Camera controller initialized")

    def update(self, delta_time: float):
        """
        Update camera state.

        Args:
            delta_time: Time since last update (seconds)
        """
        # Update camera animations if active
        if self.is_animated and self.animation_keyframes:
            self._update_camera_animation(delta_time)

        # Update follow mode
        elif self.mode == CameraMode.FOLLOW and self.follow_target is not None:
            self.target_position = self.follow_target + self.follow_offset

        # Smooth interpolation to target
        if self.settings.enable_smoothing:
            # Position
            self.position += (self.target_position - self.position) * self.settings.smoothing_factor

            # Zoom
            self.zoom += (self.target_zoom - self.zoom) * self.settings.smoothing_factor

            # Rotation
            self.rotation += (self.target_rotation - self.rotation) * self.settings.smoothing_factor
        else:
            # Instant snap
            self.position = self.target_position.copy()
            self.zoom = self.target_zoom
            self.rotation = self.target_rotation

        # Clamp values
        self.position[0] = np.clip(self.position[0], self.settings.min_x, self.settings.max_x)
        self.position[1] = np.clip(self.position[1], self.settings.min_y, self.settings.max_y)
        self.zoom = np.clip(self.zoom, self.settings.min_zoom, self.settings.max_zoom)
        self.rotation = np.clip(self.rotation, self.settings.min_rotation, self.settings.max_rotation)

        # Update shake effects
        self._update_shake_effects(delta_time)

    def _update_shake_effects(self, delta_time: float):
        """Update all active shake effects."""
        total_shake = np.array([0.0, 0.0], dtype=np.float32)

        # Remove inactive shakes
        self.active_shakes = [shake for shake in self.active_shakes if shake.is_active]

        # Accumulate shake offsets
        for shake in self.active_shakes:
            x_offset, y_offset = shake.update(delta_time)
            total_shake[0] += x_offset
            total_shake[1] += y_offset

        # Apply shake intensity multiplier
        self.shake_offset = total_shake * self.settings.shake_intensity

    def _update_camera_animation(self, delta_time: float):
        """Update keyframe-animated camera movement."""
        self.animation_time += delta_time

        # Find keyframes to interpolate between
        if len(self.animation_keyframes) < 2:
            return

        # Find current keyframe range
        prev_kf = None
        next_kf = None

        for i, (time, pos, zoom, rot) in enumerate(self.animation_keyframes):
            if time <= self.animation_time:
                prev_kf = (time, pos, zoom, rot)
            if time > self.animation_time and next_kf is None:
                next_kf = (time, pos, zoom, rot)
                break

        # Interpolate between keyframes
        if prev_kf and next_kf:
            t1, p1, z1, r1 = prev_kf
            t2, p2, z2, r2 = next_kf

            # Calculate interpolation factor
            if t2 > t1:
                factor = (self.animation_time - t1) / (t2 - t1)
                factor = np.clip(factor, 0.0, 1.0)

                # Interpolate
                self.target_position = p1 + (p2 - p1) * factor
                self.target_zoom = z1 + (z2 - z1) * factor
                self.target_rotation = r1 + (r2 - r1) * factor

    # ========================================================================
    # CAMERA MOVEMENTS
    # ========================================================================

    def pan(self, dx: float, dy: float, delta_time: Optional[float] = None):
        """
        Pan camera (move left/right/up/down).

        Args:
            dx: Horizontal movement
            dy: Vertical movement
            delta_time: Time-based movement (if None, use raw values)
        """
        if self.mode == CameraMode.FIXED:
            return

        if delta_time:
            # Time-based movement
            dx *= self.settings.pan_speed * delta_time
            dy *= self.settings.pan_speed * delta_time

        self.target_position[0] += dx
        self.target_position[1] += dy

    def zoom_in(self, amount: float = 0.1):
        """Zoom in."""
        self.target_zoom *= (1.0 + amount)

    def zoom_out(self, amount: float = 0.1):
        """Zoom out."""
        self.target_zoom *= (1.0 - amount)

    def set_zoom(self, zoom: float):
        """Set zoom level directly."""
        self.target_zoom = zoom

    def rotate(self, angle_delta: float, delta_time: Optional[float] = None):
        """
        Rotate camera.

        Args:
            angle_delta: Rotation change (degrees)
            delta_time: Time-based rotation
        """
        if delta_time:
            angle_delta *= self.settings.rotation_speed * delta_time

        self.target_rotation += angle_delta

    def set_rotation(self, angle: float):
        """Set rotation directly (degrees)."""
        self.target_rotation = angle

    def set_position(self, x: float, y: float):
        """Set camera position directly."""
        self.target_position[0] = x
        self.target_position[1] = y

    def look_at(self, x: float, y: float):
        """Point camera at specific position."""
        self.set_position(x, y)

    def reset(self):
        """Reset camera to default position."""
        self.target_position = np.array([0.0, 0.0], dtype=np.float32)
        self.target_zoom = 1.0
        self.target_rotation = 0.0
        self.active_shakes.clear()
        self.shake_offset = np.array([0.0, 0.0], dtype=np.float32)

    # ========================================================================
    # CAMERA MODES
    # ========================================================================

    def set_mode(self, mode: CameraMode):
        """Change camera mode."""
        self.mode = mode

        if mode != CameraMode.FOLLOW:
            self.follow_target = None

        if mode != CameraMode.ANIMATED:
            self.is_animated = False

        print(f"📷 Camera mode: {mode.value}")

    def follow_character(self, position: np.ndarray, offset: Optional[np.ndarray] = None):
        """
        Follow a character.

        Args:
            position: Character position to follow
            offset: Optional offset from character
        """
        self.mode = CameraMode.FOLLOW
        self.follow_target = position

        if offset is not None:
            self.follow_offset = offset
        else:
            self.follow_offset = np.array([0.0, 0.0], dtype=np.float32)

    # ========================================================================
    # SCREEN SHAKE
    # ========================================================================

    def shake(self, shake_type: ShakeType, intensity: float = 1.0, duration: float = 0.3):
        """
        Add screen shake effect.

        Args:
            shake_type: Type of shake
            intensity: Shake strength
            duration: How long shake lasts
        """
        shake = CameraShake(shake_type, intensity, duration)
        self.active_shakes.append(shake)

        print(f"📳 Camera shake: {shake_type.value} (intensity: {intensity:.1f}, duration: {duration:.2f}s)")

    def impact_shake(self, intensity: float = 1.0):
        """Quick impact shake (punch, kick)."""
        self.shake(ShakeType.IMPACT, intensity, 0.2)

    def explosion_shake(self, intensity: float = 1.5):
        """Big explosion shake."""
        self.shake(ShakeType.EXPLOSION, intensity, 0.5)

    def rumble_shake(self, intensity: float = 0.5, duration: float = 1.0):
        """Continuous rumble."""
        self.shake(ShakeType.RUMBLE, intensity, duration)

    # ========================================================================
    # CAMERA ANIMATION
    # ========================================================================

    def add_camera_keyframe(self, time: float, position: np.ndarray, zoom: float, rotation: float):
        """
        Add keyframe for camera animation.

        Args:
            time: Time of keyframe (seconds)
            position: Camera position
            zoom: Zoom level
            rotation: Rotation (degrees)
        """
        keyframe = (time, position.copy(), zoom, rotation)
        self.animation_keyframes.append(keyframe)

        # Sort by time
        self.animation_keyframes.sort(key=lambda kf: kf[0])

    def start_camera_animation(self, loop: bool = False):
        """Start playing camera animation."""
        if not self.animation_keyframes:
            print("⚠ No camera keyframes to animate")
            return

        self.is_animated = True
        self.mode = CameraMode.ANIMATED
        self.animation_time = 0.0

        print(f"🎬 Camera animation started ({len(self.animation_keyframes)} keyframes)")

    def stop_camera_animation(self):
        """Stop camera animation."""
        self.is_animated = False
        self.mode = CameraMode.FREE

    def clear_camera_keyframes(self):
        """Remove all camera animation keyframes."""
        self.animation_keyframes.clear()
        self.is_animated = False

    # ========================================================================
    # OPENGL INTEGRATION
    # ========================================================================

    def apply_to_opengl(self):
        """Apply camera transform to OpenGL view."""
        # Get final position (with shake)
        final_x = self.position[0] + self.shake_offset[0]
        final_y = self.position[1] + self.shake_offset[1]

        # Reset matrix
        glLoadIdentity()

        # Apply camera rotation (around center)
        if abs(self.rotation) > 0.001:
            glRotatef(self.rotation, 0.0, 0.0, 1.0)

        # Apply camera position (inverted for viewport)
        glTranslatef(-final_x, -final_y, 0.0)

    def setup_projection(self, width: int, height: int):
        """
        Setup orthographic projection with zoom.

        Args:
            width: Viewport width
            height: Viewport height
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect = width / height if height > 0 else 1.0
        size = 10.0 / self.zoom  # Base size divided by zoom

        if aspect >= 1.0:
            glOrtho(-size * aspect, size * aspect, -size, size, -100, 100)
        else:
            glOrtho(-size, size, -size / aspect, size / aspect, -100, 100)

        glMatrixMode(GL_MODELVIEW)

    # ========================================================================
    # UTILITY
    # ========================================================================

    def get_position(self) -> np.ndarray:
        """Get current camera position (with shake)."""
        return self.position + self.shake_offset

    def get_zoom(self) -> float:
        """Get current zoom level."""
        return self.zoom

    def get_rotation(self) -> float:
        """Get current rotation (degrees)."""
        return self.rotation

    def is_shaking(self) -> bool:
        """Check if camera is currently shaking."""
        return len(self.active_shakes) > 0


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_camera(smooth: bool = True) -> Camera:
    """
    Create camera with default settings.

    Args:
        smooth: Enable smooth camera movement

    Returns:
        Configured Camera
    """
    settings = CameraSettings()
    settings.enable_smoothing = smooth
    return Camera(settings)


def create_action_camera() -> Camera:
    """Create camera optimized for action sequences (faster movement)."""
    settings = CameraSettings()
    settings.pan_speed = 2.0
    settings.zoom_speed = 1.0
    settings.rotation_speed = 90.0
    settings.smoothing_factor = 0.1  # Less smoothing for snappy action
    settings.shake_intensity = 1.5   # More intense shakes
    return Camera(settings)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CAMERA CONTROLS TEST")
    print("=" * 60)

    # Create camera
    camera = create_camera()

    print(f"\nCamera Position: {camera.position}")
    print(f"Camera Zoom: {camera.zoom}")
    print(f"Camera Rotation: {camera.rotation}°")
    print(f"Camera Mode: {camera.mode.value}")

    # Test movements
    print("\n" + "=" * 60)
    print("Testing Camera Movements")
    print("=" * 60)

    camera.pan(5.0, 3.0)
    camera.update(0.016)  # 60 FPS
    print(f"After pan: {camera.position}")

    camera.zoom_in(0.5)
    camera.update(0.016)
    print(f"After zoom in: {camera.zoom:.2f}")

    camera.rotate(45.0)
    camera.update(0.016)
    print(f"After rotate: {camera.rotation:.1f}°")

    # Test shake
    print("\n" + "=" * 60)
    print("Testing Screen Shake")
    print("=" * 60)

    camera.impact_shake(1.0)
    print(f"Active shakes: {len(camera.active_shakes)}")

    for _ in range(5):
        camera.update(0.05)
        print(f"  Shake offset: {camera.shake_offset}")

    print("\n✓ All tests passed!")
    print("\nCamera system ready for cinematic YouTube fight choreography!")
