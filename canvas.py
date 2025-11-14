"""
OpenGL Canvas Module
GPU-accelerated rendering canvas optimized for 60 FPS on RTX 3060M.
Supports both Vector and HD rendering modes.
"""

import time
import numpy as np
from PySide6.QtOpenGLWidgets import QOpenGLWidget  # Correct import for PySide6
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QSurfaceFormat
from OpenGL.GL import *
from OpenGL.GLU import *


class RenderCanvas(QOpenGLWidget):
    """
    OpenGL rendering canvas for stick figure animations.
    Optimized for high-performance GPU rendering at 60 FPS.
    """

    # Signals for FPS reporting
    fps_updated = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Performance settings
        self.target_fps = 60
        self.frame_time = 1000.0 / self.target_fps  # ~16.67ms per frame

        # FPS tracking
        self.fps_counter = 0
        self.fps_last_time = time.time()
        self.current_fps = 0

        # Rendering state
        self.render_mode = "vector"  # "vector" or "hd"
        self.is_playing = False
        self.current_frame = 0

        # Content rendering mode
        self.content_mode = "animation"  # "animation" (show stick figure) or "weapon" (show weapon only)
        self.current_weapon = None  # Weapon instance to render
        self.current_flame_effect = None  # Flame effect to render

        # Camera state
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_zoom = 1.0
        self.camera_rotation = 0.0

        # Mouse interaction state
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.is_panning = False
        self.is_rotating_weapon = False
        self.is_panning_weapon = False  # Middle-click to pan weapon position

        # Weapon rotation mode
        self.weapon_rotation_mode = "3D"  # "3D" or "2D"

        # Configure OpenGL format for best performance
        self._configure_opengl_format()

        # Setup render timer (60 FPS)
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self._on_render_tick)
        self.render_timer.start(int(self.frame_time))

        # Setup FPS counter timer (update every second)
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self._update_fps_counter)
        self.fps_timer.start(1000)

        print("✓ OpenGL canvas initialized (Target: 60 FPS)")

    # ========================================================================
    # OPENGL CONFIGURATION
    # ========================================================================

    def _configure_opengl_format(self):
        """
        Configure OpenGL surface format for optimal performance.
        Uses Compatibility Profile to support legacy OpenGL calls (glBegin/glEnd, matrix stack).
        """
        fmt = QSurfaceFormat()
        fmt.setVersion(2, 1)  # OpenGL 2.1 for maximum compatibility
        fmt.setProfile(QSurfaceFormat.CompatibilityProfile)  # Support legacy OpenGL calls
        fmt.setSamples(4)  # 4x MSAA for smooth anti-aliased lines
        fmt.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
        fmt.setSwapInterval(1)  # V-Sync enabled for smooth 60 FPS

        self.setFormat(fmt)

    # ========================================================================
    # OPENGL LIFECYCLE METHODS
    # ========================================================================

    def initializeGL(self):
        """
        Initialize OpenGL context and set up rendering state.
        Called once when the widget is first shown.
        """
        # Set clear color (dark gray background)
        glClearColor(0.15, 0.15, 0.15, 1.0)

        # Enable depth testing for 3D rendering (even though stick figures are 2D)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # Enable blending for transparency (flame effects, etc.)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Enable line smoothing for anti-aliased stick figures
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        # Set line width for stick figure limbs
        glLineWidth(3.0)

        # Enable multisampling (if supported)
        glEnable(GL_MULTISAMPLE)

        print("✓ OpenGL context initialized")
        print(f"  OpenGL Version: {glGetString(GL_VERSION).decode()}")
        print(f"  GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
        print(f"  Renderer: {glGetString(GL_RENDERER).decode()}")

    def resizeGL(self, width, height):
        """
        Handle window resize events.
        Updates the viewport and projection matrix.
        """
        if height == 0:
            height = 1

        # Set viewport to cover entire widget
        glViewport(0, 0, width, height)

        # Set up orthographic projection for 2D rendering
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # Calculate aspect ratio
        aspect_ratio = width / height

        # Set orthographic view (adjust based on zoom)
        ortho_size = 10.0 / self.camera_zoom
        if aspect_ratio >= 1.0:
            # Wider than tall
            glOrtho(-ortho_size * aspect_ratio, ortho_size * aspect_ratio,
                    -ortho_size, ortho_size, -100.0, 100.0)
        else:
            # Taller than wide
            glOrtho(-ortho_size, ortho_size,
                    -ortho_size / aspect_ratio, ortho_size / aspect_ratio,
                    -100.0, 100.0)

        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """
        Main rendering function.
        Called every frame by the render timer (60 times per second).
        """
        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Reset modelview matrix
        glLoadIdentity()

        # Apply camera transformations
        glTranslatef(self.camera_x, self.camera_y, 0.0)
        glRotatef(self.camera_rotation, 0.0, 0.0, 1.0)

        # Render based on current mode
        if self.render_mode == "vector":
            self._render_vector_mode()
        elif self.render_mode == "hd":
            self._render_hd_mode()

        # Update FPS counter
        self.fps_counter += 1

    # ========================================================================
    # RENDERING MODES
    # ========================================================================

    def _render_vector_mode(self):
        """
        Vector rendering mode (default, fast).
        Clean anti-aliased lines, solid colors, optimized for 60 FPS.
        """
        # Draw grid for reference (back layer)
        self._draw_grid()

        # Clear depth buffer after grid so weapons/flames always render on top
        # This ensures weapons never go "behind" the grid during rotation
        glClear(GL_DEPTH_BUFFER_BIT)

        # Render based on content mode
        if self.content_mode == "weapon":
            # Weapon preview mode - only show weapon
            if self.current_weapon is not None:
                self._draw_weapon(self.current_weapon)
            if self.current_flame_effect is not None:
                self._draw_flame_effect(self.current_flame_effect)
        else:
            # Animation mode - show stick figure
            self._draw_test_stick_figure()

    def _render_hd_mode(self):
        """
        HD rendering mode (optional, quality).
        Textured surfaces, shaders, lighting effects.
        More GPU-intensive but stunning visual quality.
        """
        # For now, same as vector mode but with note that shaders will be added
        self._render_vector_mode()

        # TODO: Add shader-based rendering with textures and lighting

    def _draw_grid(self):
        """Draw a reference grid on the canvas."""
        glColor4f(0.3, 0.3, 0.3, 0.5)
        glBegin(GL_LINES)

        # Vertical lines
        for x in range(-10, 11):
            glVertex3f(x, -10, -0.1)
            glVertex3f(x, 10, -0.1)

        # Horizontal lines
        for y in range(-10, 11):
            glVertex3f(-10, y, -0.1)
            glVertex3f(10, y, -0.1)

        glEnd()

        # Draw origin axes (red X, green Y)
        glLineWidth(2.0)

        # X axis (red)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(-10, 0, 0)
        glVertex3f(10, 0, 0)
        glEnd()

        # Y axis (green)
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, -10, 0)
        glVertex3f(0, 10, 0)
        glEnd()

        glLineWidth(3.0)  # Reset line width

    def _draw_test_stick_figure(self):
        """
        Draw a simple test stick figure to verify rendering.
        This will be replaced with actual skeleton rendering later.
        """
        glColor3f(1.0, 1.0, 1.0)  # White
        glLineWidth(4.0)

        # Head (circle approximation)
        glBegin(GL_LINE_LOOP)
        head_radius = 0.5
        head_y = 2.0
        segments = 20
        for i in range(segments):
            angle = 2.0 * np.pi * i / segments
            x = head_radius * np.cos(angle)
            y = head_y + head_radius * np.sin(angle)
            glVertex3f(x, y, 0.0)
        glEnd()

        # Body and limbs
        glBegin(GL_LINES)

        # Spine
        glVertex3f(0.0, 1.5, 0.0)  # Neck
        glVertex3f(0.0, 0.0, 0.0)  # Hips

        # Left arm
        glVertex3f(0.0, 1.2, 0.0)  # Shoulder
        glVertex3f(-0.6, 0.8, 0.0)  # Elbow
        glVertex3f(-0.6, 0.8, 0.0)
        glVertex3f(-1.0, 0.2, 0.0)  # Hand

        # Right arm
        glVertex3f(0.0, 1.2, 0.0)  # Shoulder
        glVertex3f(0.6, 0.8, 0.0)  # Elbow
        glVertex3f(0.6, 0.8, 0.0)
        glVertex3f(1.0, 0.2, 0.0)  # Hand

        # Left leg
        glVertex3f(0.0, 0.0, 0.0)  # Hip
        glVertex3f(-0.4, -1.0, 0.0)  # Knee
        glVertex3f(-0.4, -1.0, 0.0)
        glVertex3f(-0.5, -2.0, 0.0)  # Foot

        # Right leg
        glVertex3f(0.0, 0.0, 0.0)  # Hip
        glVertex3f(0.4, -1.0, 0.0)  # Knee
        glVertex3f(0.4, -1.0, 0.0)
        glVertex3f(0.5, -2.0, 0.0)  # Foot

        glEnd()

        glLineWidth(3.0)  # Reset line width

    def _draw_weapon(self, weapon):
        """
        Draw a weapon using its built-in render method.
        Weapons inherit from WeaponBase which provides render_vector() and render_hd().
        """
        if weapon is None:
            return

        # Weapons have built-in rendering methods - just call the appropriate one
        try:
            if self.render_mode == "hd":
                weapon.render_hd()
            else:
                weapon.render_vector()
        except Exception as e:
            print(f"Error rendering weapon: {e}")

    def _draw_flame_effect(self, flame_effect):
        """
        Draw flame effect using procedural rendering.
        Uses flame parameters (colors, size) for visual variety between presets.
        IMPORTANT: Draws in weapon's local coordinate space to follow all transforms.
        """
        if flame_effect is None or self.current_weapon is None:
            return

        params = flame_effect.parameters
        weapon = self.current_weapon

        # Apply weapon's transform matrix so flames follow ALL rotations/translations
        glPushMatrix()

        # Apply same transforms as weapon (from weapon_base.py render_vector)
        glTranslatef(weapon.position[0], weapon.position[1], weapon.position[2])
        glRotatef(weapon.rotation[2], 0, 0, 1)  # Z rotation
        glRotatef(weapon.rotation[1], 0, 1, 0)  # Y rotation
        glRotatef(weapon.rotation[0], 1, 0, 0)  # X rotation
        glScalef(weapon.scale[0], weapon.scale[1], weapon.scale[2])

        # Now get flame points in LOCAL weapon space (before transforms)
        if weapon.flame_points:
            flame_points = [(np.array(fp.position), np.array(fp.direction))
                           for fp in weapon.flame_points if fp.active]
        else:
            # Default: flame at weapon tip in local space
            flame_points = [(np.array([0.0, 0.7, 0.0]), np.array([0.0, 1.0, 0.0]))]

        # Enable additive blending for glow effect
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        for position, direction in flame_points:
            # Draw multi-layered flame for depth
            self._draw_flame_layer(position, params, layer=0, scale=1.0)
            self._draw_flame_layer(position, params, layer=1, scale=0.7)
            self._draw_flame_layer(position, params, layer=2, scale=0.4)

        # Restore normal blending
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glPopMatrix()

    def _draw_flame_layer(self, position, params, layer, scale):
        """Draw a single flame layer with gradient colors."""
        import math
        import time

        # Animated flicker offset
        time_offset = time.time() * params.speed + layer * 0.5
        flicker = 1.0 + math.sin(time_offset * 5.0) * params.flicker_intensity * 0.3

        # Scale by height/width parameters
        height = params.height * scale * flicker
        width = params.width * scale

        # Get colors from parameters
        color_bottom = params.color_bottom
        color_top = params.color_top

        # Apply intensity and opacity
        alpha_bottom = color_bottom[3] * params.opacity * params.intensity
        alpha_top = color_top[3] * params.opacity * params.intensity * 0.5

        # Draw flame shape with gradient
        glBegin(GL_TRIANGLE_FAN)

        # Top point (tip of flame) - bright color
        glColor4f(color_top[0] * params.intensity,
                  color_top[1] * params.intensity,
                  color_top[2] * params.intensity,
                  alpha_top)
        glVertex3f(position[0], position[1] + height, position[2])

        # Base points - dark/orange color
        segments = 8
        for i in range(segments + 1):
            angle = (i / segments) * math.pi  # Half circle
            x_offset = math.sin(angle) * width * (1.0 - params.taper * 0.5)

            glColor4f(color_bottom[0], color_bottom[1], color_bottom[2], alpha_bottom)
            glVertex3f(position[0] + x_offset, position[1], position[2])

        glEnd()

    # ========================================================================
    # RENDER TIMER CALLBACK
    # ========================================================================

    def _on_render_tick(self):
        """
        Called every frame by the render timer.
        Triggers a repaint if animation is playing.
        """
        if self.is_playing:
            self.current_frame += 1

        # Always update the canvas (even when paused, for camera movements)
        self.update()

    # ========================================================================
    # FPS COUNTER
    # ========================================================================

    def _update_fps_counter(self):
        """Update FPS calculation (called every second)."""
        current_time = time.time()
        elapsed = current_time - self.fps_last_time

        if elapsed > 0:
            self.current_fps = int(self.fps_counter / elapsed)
            self.fps_updated.emit(self.current_fps)

        # Reset counter
        self.fps_counter = 0
        self.fps_last_time = current_time

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def set_render_mode(self, mode):
        """
        Set rendering mode.
        Args:
            mode (str): "vector" or "hd"
        """
        if mode in ["vector", "hd"]:
            self.render_mode = mode
            print(f"Render mode set to: {mode}")
            self.update()
        else:
            print(f"Warning: Invalid render mode '{mode}'. Use 'vector' or 'hd'.")

    def play(self):
        """Start playing the animation."""
        self.is_playing = True
        print("Animation playing...")

    def stop(self):
        """Stop the animation."""
        self.is_playing = False
        self.current_frame = 0
        print("Animation stopped.")

    def reset_camera(self):
        """Reset camera to default position."""
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_zoom = 1.0
        self.camera_rotation = 0.0
        self.resizeGL(self.width(), self.height())
        self.update()
        print("Camera reset to default position")

    def set_weapon(self, weapon):
        """
        Set the weapon to render in the canvas.
        Automatically switches to weapon content mode.

        Args:
            weapon: Weapon instance with vertices and edges, or None to clear
        """
        self.current_weapon = weapon
        self.content_mode = "weapon"
        self.update()

    def set_flame_effect(self, flame_effect):
        """
        Set the flame effect to render with the weapon.

        Args:
            flame_effect: FlameEffect instance, or None to clear
        """
        self.current_flame_effect = flame_effect
        self.update()

    def set_content_mode(self, mode):
        """
        Set what content to render.

        Args:
            mode: "animation" (show stick figures) or "weapon" (show weapons only)
        """
        if mode in ["animation", "weapon"]:
            self.content_mode = mode
            self.update()

    def set_weapon_rotation_mode(self, mode):
        """
        Set weapon rotation mode.

        Args:
            mode: "3D" (full 3D rotation) or "2D" (Z-axis spin only)
        """
        if mode in ["3D", "2D"]:
            self.weapon_rotation_mode = mode

    # ========================================================================
    # MOUSE/KEYBOARD INPUT
    # ========================================================================

    def mousePressEvent(self, event):
        """Handle mouse press - different behavior for weapon vs animation mode."""
        if self.content_mode == "weapon":
            # Weapon mode: left-click to rotate, middle-click to pan weapon
            if event.button() == Qt.LeftButton:
                self.is_rotating_weapon = True
                self.last_mouse_x = event.position().x()
                self.last_mouse_y = event.position().y()
            elif event.button() == Qt.MiddleButton:
                self.is_panning_weapon = True
                self.last_mouse_x = event.position().x()
                self.last_mouse_y = event.position().y()
        else:
            # Animation mode: middle/right-click to pan camera
            if event.button() == Qt.MiddleButton or event.button() == Qt.RightButton:
                self.is_panning = True
                self.last_mouse_x = event.position().x()
                self.last_mouse_y = event.position().y()

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self.is_rotating_weapon = False
        if event.button() == Qt.MiddleButton:
            self.is_panning_weapon = False
            self.is_panning = False
        if event.button() == Qt.RightButton:
            self.is_panning = False

    def mouseMoveEvent(self, event):
        """Handle mouse move - pan camera, rotate weapon, or pan weapon position."""
        delta_x = event.position().x() - self.last_mouse_x
        delta_y = event.position().y() - self.last_mouse_y

        if self.is_rotating_weapon and self.current_weapon is not None:
            # Rotate weapon based on mouse drag
            rotation_speed = 0.675  # Degrees per pixel (35% faster for snappier feel)

            if self.weapon_rotation_mode == "2D":
                # 2D mode: only rotate around Z axis (horizontal drag)
                delta_rotation = delta_x * rotation_speed
                self.current_weapon.rotate(0, 0, delta_rotation)
            else:
                # 3D mode: rotate around Y (horizontal) and X (vertical) axes
                # Horizontal drag = rotate around Y axis (yaw)
                # Vertical drag = rotate around X axis (pitch)
                delta_y_rotation = delta_x * rotation_speed  # Yaw
                delta_x_rotation = -delta_y * rotation_speed  # Pitch (inverted for natural feel)
                self.current_weapon.rotate(delta_x_rotation, delta_y_rotation, 0)

            self.update()

        elif self.is_panning_weapon and self.current_weapon is not None:
            # Pan weapon position (physically move weapon around canvas)
            # Convert screen pixels to world units
            pan_speed = 0.02  # World units per pixel

            # Move weapon position (inverted Y for natural feel)
            self.current_weapon.translate(delta_x * pan_speed, -delta_y * pan_speed, 0)
            self.update()

        elif self.is_panning:
            # Pan camera (animation mode)
            pan_speed = 0.02 / self.camera_zoom
            self.camera_x += delta_x * pan_speed
            self.camera_y -= delta_y * pan_speed
            self.update()

        self.last_mouse_x = event.position().x()
        self.last_mouse_y = event.position().y()

    def wheelEvent(self, event):
        """Handle mouse wheel - zoom camera or scale weapon depending on mode."""
        delta = event.angleDelta().y()

        if self.content_mode == "weapon" and self.current_weapon is not None:
            # Weapon mode: scale weapon directly
            if delta > 0:
                scale_factor = 1.1  # Scale up
            else:
                scale_factor = 0.9  # Scale down

            current_scale = self.current_weapon.scale[0]  # Assuming uniform scale
            new_scale = current_scale * scale_factor
            new_scale = max(0.1, min(5.0, new_scale))  # Clamp scale
            self.current_weapon.set_scale(new_scale)
        else:
            # Animation mode: zoom camera
            if delta > 0:
                self.camera_zoom *= 1.1  # Zoom in
            elif delta < 0:
                self.camera_zoom *= 0.9  # Zoom out

            # Clamp zoom
            self.camera_zoom = max(0.1, min(10.0, self.camera_zoom))

            # Update projection
            self.resizeGL(self.width(), self.height())

        self.update()

    def keyPressEvent(self, event):
        """Handle keyboard input."""
        if event.key() == Qt.Key_Space:
            # Toggle play/pause
            if self.is_playing:
                self.stop()
            else:
                self.play()

        elif event.key() == Qt.Key_Home:
            # Reset camera
            self.reset_camera()

        elif event.key() == Qt.Key_R:
            # Reset to frame 0
            self.current_frame = 0
            self.update()
