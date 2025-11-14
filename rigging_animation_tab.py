"""
Rigging & Animation Tab (Tab 2)
Complete UI for creating and customizing stick figure characters with live preview.

Features:
- Body type selection (5 presets: Normal, Muscular, Thin, Child, Giant)
- Color customization (9 presets + custom RGB)
- Proportion sliders (height, limbs, shoulders, head size)
- Facial expression controls (8 expressions)
- Eye and mouth manual controls
- Live OpenGL preview with thick, colored stick figures
- Real-time facial animation
- Limb thickness adjustment
"""

import numpy as np
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSlider, QGroupBox, QComboBox, QGridLayout, QSplitter,
    QColorDialog
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *

# Import VOLUMETRIC 3D stick figures (approved styles)
from volumetric_stick_figure import CartoonVillainStyle, CyberFighterStyle


# ============================================================================
# LIVE PREVIEW CANVAS
# ============================================================================

class RiggingPreviewCanvas(QOpenGLWidget):
    """
    OpenGL canvas for live stick figure preview with facial animation.
    Shows thick, colored stick figure with customizable features.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Volumetric 3D stick figures
        self.current_style = "cartoon"  # "cartoon" or "cyber"
        self.cartoon_style = CartoonVillainStyle()
        self.cyber_style = CyberFighterStyle()

        # Camera & rotation
        self.camera_zoom = 1.3  # Perfect from test previewer
        self.rotation_y = 0.0  # Y-axis rotation
        self.auto_rotate = True  # Auto-spin enabled by default
        self.rotation_speed = 0.5

        # Mouse interaction
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.is_dragging = False

        # Setup 60 FPS timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)  # ~60 FPS

        print("✓ Rigging Preview Canvas initialized (3D Volumetric)")

    def initializeGL(self):
        """Initialize OpenGL context with 3D lighting."""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Enable 3D lighting for volumetric rendering
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Setup lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 3.0, 3.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])

        print("✓ OpenGL initialized for 3D rigging preview")

    def resizeGL(self, w: int, h: int):
        """Handle window resize."""
        glViewport(0, 0, w, h)
        self._update_projection()

    def _update_projection(self):
        """Update camera projection."""
        w = self.width()
        h = self.height()
        aspect = w / h if h > 0 else 1.0
        size = 1.3 / self.camera_zoom  # Perfect framing from test previewer

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if aspect >= 1.0:
            glOrtho(-size * aspect, size * aspect, -size, size, -10, 10)
        else:
            glOrtho(-size, size, -size / aspect, size / aspect, -10, 10)

        glMatrixMode(GL_MODELVIEW)

    def _animate(self):
        """Animation tick - auto-rotate if enabled."""
        if self.auto_rotate:
            self.rotation_y += self.rotation_speed
        self.update()

    def paintGL(self):
        """Render frame."""
        # Clear background - dark for 3D volumetric look
        glClearColor(0.2, 0.22, 0.25, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Setup view with rotation
        glLoadIdentity()
        glRotatef(self.rotation_y, 0, 1, 0)

        # Render current style
        if self.current_style == "cartoon":
            self.cartoon_style.render()
        else:
            self.cyber_style.render()

    def mousePressEvent(self, event):
        """Handle mouse press - start dragging."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.auto_rotate = False  # Stop auto-rotation when user drags
            self.last_mouse_x = event.x()

    def mouseReleaseEvent(self, event):
        """Handle mouse release - stop dragging."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def mouseMoveEvent(self, event):
        """Handle mouse drag - manual rotation."""
        if self.is_dragging:
            dx = event.x() - self.last_mouse_x
            self.rotation_y += dx * 0.5  # Rotate based on horizontal drag
            self.last_mouse_x = event.x()
            self.update()

    def wheelEvent(self, event):
        """Handle mouse wheel for zoom (centered on character)."""
        delta = event.angleDelta().y()

        if delta > 0:
            self.camera_zoom *= 1.1
        else:
            self.camera_zoom *= 0.9

        self.camera_zoom = max(0.5, min(5.0, self.camera_zoom))
        self._update_projection()
        self.update()

    def set_style(self, style_name: str):
        """Change character style."""
        self.current_style = style_name
        self.update()

    def set_color_for_part(self, part: str, r: float, g: float, b: float):
        """Change color for specific part of character."""
        if self.current_style == "cartoon":
            if part == "body":
                self.cartoon_style.body_color = (r, g, b)
            elif part == "eyes":
                self.cartoon_style.eye_white_color = (r, g, b)
            elif part == "pupils":
                self.cartoon_style.pupil_color = (r, g, b)
        else:  # cyber
            if part == "body":
                self.cyber_style.body_color = (r, g, b)
            elif part == "eye_glow":
                self.cyber_style.eye_glow_color = (r, g, b)
            elif part == "joint_glow":
                self.cyber_style.joint_glow_color = (r, g, b)
        self.update()

    def set_limb_thickness(self, multiplier: float):
        """Adjust limb thickness (both styles)."""
        self.cartoon_style.set_thickness(multiplier)
        self.cyber_style.set_thickness(multiplier)
        self.update()


# ============================================================================
# TAB 2: RIGGING & ANIMATION UI
# ============================================================================

class RiggingAnimationTab(QWidget):
    """
    Tab 2: Rigging & Animation
    Complete interface for stick figure customization and animation.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize UI
        self._init_ui()

        print("✓ Rigging & Animation Tab initialized")

    def _init_ui(self):
        """Initialize user interface."""
        layout = QHBoxLayout(self)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: Controls
        controls_panel = self._create_controls_panel()
        splitter.addWidget(controls_panel)

        # Right panel: Preview canvas
        self.preview_canvas = RiggingPreviewCanvas()
        splitter.addWidget(self.preview_canvas)

        # Set initial sizes (30% controls, 70% preview)
        splitter.setSizes([300, 700])

        layout.addWidget(splitter)

    def _create_controls_panel(self) -> QWidget:
        """Create left control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("CHARACTER CUSTOMIZATION")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; color: #ffffff;")
        layout.addWidget(title)

        # Style Section (2 approved styles)
        style_group = self._create_body_type_section()
        layout.addWidget(style_group)

        # Color Section
        color_group = self._create_color_section()
        layout.addWidget(color_group)

        # Facial Expression Section
        expression_group = self._create_expression_section()
        layout.addWidget(expression_group)

        # Limb Thickness Section
        thickness_group = self._create_thickness_section()
        layout.addWidget(thickness_group)

        layout.addStretch()

        # Info label - updated controls
        info = QLabel("💡 Click-drag to rotate | Scroll to zoom")
        info.setStyleSheet("padding: 10px; color: #888;")
        layout.addWidget(info)

        panel.setMaximumWidth(400)
        panel.setStyleSheet("QWidget { background-color: #2a2a2a; }")

        return panel

    def _create_body_type_section(self) -> QGroupBox:
        """Create character style selection section."""
        group = QGroupBox("Character Style")
        layout = QVBoxLayout(group)

        # Style dropdown - 2 approved styles
        self.style_combo = QComboBox()
        self.style_combo.addItem("Cartoon Villain (Default)", "cartoon")
        self.style_combo.addItem("Cyber Fighter", "cyber")
        self.style_combo.currentIndexChanged.connect(self._on_style_changed)
        layout.addWidget(self.style_combo)

        # Info label
        info = QLabel("More styles coming soon!")
        info.setStyleSheet("color: #888; font-size: 11px; padding: 5px;")
        layout.addWidget(info)

        return group

    def _create_color_section(self) -> QGroupBox:
        """Create color customization section with dropdown."""
        group = QGroupBox("Character Colors")
        layout = QVBoxLayout(group)

        # Dropdown: "What to color?"
        layout.addWidget(QLabel("What to color:"))
        self.color_target_combo = QComboBox()
        self._update_color_targets()  # Populate based on current style
        self.color_target_combo.currentIndexChanged.connect(self._on_color_target_changed)
        layout.addWidget(self.color_target_combo)

        # Color preset buttons (3x3 grid)
        grid = QGridLayout()

        color_presets = [
            ("Red", (0.85, 0.15, 0.15), "#D92626"),
            ("Blue", (0.2, 0.4, 0.85), "#3366D9"),
            ("Green", (0.2, 0.75, 0.2), "#33BF33"),
            ("Yellow", (0.95, 0.85, 0.15), "#F2D926"),
            ("Purple", (0.65, 0.2, 0.85), "#A633D9"),
            ("Orange", (1.0, 0.5, 0.1), "#FF8019"),
            ("Cyan", (0.2, 0.85, 0.85), "#33D9D9"),
            ("Black", (0.1, 0.1, 0.1), "#262626"),
            ("White", (0.95, 0.95, 0.95), "#F2F2F2"),
        ]

        for i, (name, rgb, hex_color) in enumerate(color_presets):
            btn = QPushButton(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_color};
                    color: {'white' if i >= 7 else 'black'};
                    padding: 8px;
                    font-weight: bold;
                    border: 2px solid #444;
                }}
                QPushButton:hover {{
                    border: 2px solid white;
                }}
            """)
            btn.clicked.connect(lambda checked, rgb=rgb: self._on_color_preset_clicked(rgb))
            grid.addWidget(btn, i // 3, i % 3)

        layout.addLayout(grid)

        # Custom color button
        custom_btn = QPushButton("🎨 Custom Color...")
        custom_btn.clicked.connect(self._on_custom_color_clicked)
        layout.addWidget(custom_btn)

        return group

    def _create_expression_section(self) -> QGroupBox:
        """Create facial expression controls."""
        group = QGroupBox("Facial Expression")
        layout = QVBoxLayout(group)

        # Expression dropdown (disabled in simple mode)
        self.expression_combo = QComboBox()
        self.expression_combo.addItem("😐 Neutral", "neutral")
        self.expression_combo.setEnabled(False)
        layout.addWidget(self.expression_combo)

        layout.addWidget(QLabel("(Facial controls not available in simple mode)"))

        return group

    def _create_thickness_section(self) -> QGroupBox:
        """Create limb thickness adjustment section."""
        group = QGroupBox("Limb Thickness")
        layout = QVBoxLayout(group)

        # Thickness slider (DISABLED - was breaking proportions)
        slider_layout = QHBoxLayout()

        slider_layout.addWidget(QLabel("Thin"))

        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setMinimum(20)
        self.thickness_slider.setMaximum(150)
        self.thickness_slider.setValue(80)  # Locked at default
        self.thickness_slider.setEnabled(False)  # DISABLED
        slider_layout.addWidget(self.thickness_slider)

        slider_layout.addWidget(QLabel("Thick"))

        layout.addLayout(slider_layout)

        # Disabled label
        self.thickness_label = QLabel("(Coming soon - needs calibration)")
        self.thickness_label.setAlignment(Qt.AlignCenter)
        self.thickness_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.thickness_label)

        return group

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    def _update_color_targets(self):
        """Update color target dropdown based on current style."""
        self.color_target_combo.clear()

        # Get current style from preview canvas (or default to cartoon)
        if hasattr(self, 'preview_canvas'):
            current_style = self.preview_canvas.current_style
        else:
            current_style = 'cartoon'  # Default during initialization

        if current_style == "cartoon":
            self.color_target_combo.addItem("Body", "body")
            self.color_target_combo.addItem("Eye Whites", "eyes")
            self.color_target_combo.addItem("Pupils", "pupils")
        else:  # cyber
            self.color_target_combo.addItem("Body", "body")
            self.color_target_combo.addItem("Eye Glow", "eye_glow")
            self.color_target_combo.addItem("Joint Glow", "joint_glow")

    def _on_style_changed(self, index: int):
        """Handle style selection change."""
        style_name = self.style_combo.itemData(index)
        self.preview_canvas.set_style(style_name)
        self._update_color_targets()  # Update color options when style changes
        print(f"Character style changed to: {style_name}")

    def _on_color_target_changed(self, index: int):
        """Handle color target change."""
        target = self.color_target_combo.itemData(index)
        print(f"Color target changed to: {target}")

    def _on_color_preset_clicked(self, color_rgb: tuple):
        """Handle color preset button click."""
        r, g, b = color_rgb
        target = self.color_target_combo.currentData()
        self.preview_canvas.set_color_for_part(target, r, g, b)
        print(f"{target} color changed to RGB({r:.2f}, {g:.2f}, {b:.2f})")

    def _on_custom_color_clicked(self):
        """Handle custom color button click."""
        color = QColorDialog.getColor()

        if color.isValid():
            r = color.redF()
            g = color.greenF()
            b = color.blueF()
            target = self.color_target_combo.currentData()
            self.preview_canvas.set_color_for_part(target, r, g, b)
            print(f"Custom {target} color set: RGB({r:.2f}, {g:.2f}, {b:.2f})")

    def _on_expression_changed(self, index: int):
        """Handle expression change - not supported in simple mode."""
        pass

    def _on_mouth_changed(self, index: int):
        """Handle manual mouth shape change - not supported in simple mode."""
        pass

    def _on_eye_changed(self, index: int):
        """Handle eye state change - not supported in simple mode."""
        pass

    def _on_thickness_changed(self, value: int):
        """Handle thickness slider change - DISABLED."""
        pass  # Disabled - was breaking model proportions


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def create_rigging_animation_tab() -> RiggingAnimationTab:
    """
    Create and return the Rigging & Animation tab.

    Returns:
        Configured RiggingAnimationTab widget
    """
    return RiggingAnimationTab()
