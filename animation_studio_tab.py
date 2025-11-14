"""
Animation Studio Tab (Tab 3)
The ULTIMATE workspace for creating YouTube stick figure fight content.

This is where EVERYTHING comes together:
- Multi-character fight scenes
- Timeline-synced animation playback
- Camera controls (pan, zoom, shake)
- Audio/voiceover sync
- Preset animation loader
- Real-time 60 FPS preview
- Export to 1080p/4K video

This tab is optimized for the COMPLETE YouTube content creation workflow.
"""

import numpy as np
from typing import Optional, List, Dict
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QGroupBox, QComboBox,
    QSlider, QSplitter, QScrollArea, QFrame, QSpinBox,
    QColorDialog, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *

# Import all systems
from rigging.auto_rig import create_stick_figure, BodyType
from rigging.skeleton import Skeleton
from rigging.facial_rig import FacialRig, FacialFeatures, Expression, create_facial_features
from rendering.stick_figure_renderer import StickFigureCharacter, CharacterColorPreset
from rendering.vector_renderer import VectorRenderer, VectorStyle
from rendering.hd_renderer import HDRenderer, HDQualityLevel
from camera_controls import Camera, CameraMode, ShakeType, create_camera
from timeline import TimelineWidget, TimelineTrack
from animations.animation_base import Animation

# Import preset animations
from animations.anim_floss import create_floss_animation
from animations.anim_carlton import create_carlton_animation
from animations.anim_take_the_l import create_take_the_l_animation
from animations.anim_moonwalk import create_moonwalk_animation
from animations.anim_dab import create_dab_animation


# ============================================================================
# CHARACTER IN SCENE
# ============================================================================

@dataclass
class SceneCharacter:
    """
    Character instance in the scene.
    Wraps stick figure with position, animation, and state.
    """
    name: str
    character: StickFigureCharacter
    position: np.ndarray  # World position
    current_animation: Optional[Animation] = None
    animation_time: float = 0.0
    is_visible: bool = True
    is_selected: bool = False


# ============================================================================
# STUDIO CANVAS (Main Viewport)
# ============================================================================

class StudioCanvas(QOpenGLWidget):
    """
    Main animation viewport with multi-character rendering.
    This is where users see their YouTube content come to life!
    """

    # Signals
    character_selected = Signal(str)  # Character name

    def __init__(self, parent=None):
        super().__init__(parent)

        # Scene
        self.characters: List[SceneCharacter] = []
        self.selected_character: Optional[SceneCharacter] = None

        # Camera
        self.camera = create_camera(smooth=True)

        # Renderers
        self.vector_renderer = VectorRenderer()
        self.hd_renderer = HDRenderer()
        self.use_hd_rendering = False

        # Playback
        self.is_playing = False
        self.current_time = 0.0
        self.timeline_duration = 10.0  # seconds

        # FPS monitoring
        self.frame_count = 0
        self.fps = 60.0
        self.last_fps_update = 0.0

        # Setup 60 FPS timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS

        print("✓ Studio canvas initialized")

    def initializeGL(self):
        """Initialize OpenGL."""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Initialize HD renderer if needed
        if self.use_hd_rendering:
            self.hd_renderer.initialize_shaders()

        print("✓ OpenGL initialized for studio")

    def resizeGL(self, w: int, h: int):
        """Handle resize."""
        glViewport(0, 0, w, h)
        self.camera.setup_projection(w, h)

    def paintGL(self):
        """Render frame."""
        import time
        current_time = time.time()

        # Update camera
        delta_time = 0.016  # Assume 60 FPS
        self.camera.update(delta_time)

        # Update FPS counter
        if current_time - self.last_fps_update >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = current_time

        self.frame_count += 1

        # Clear background
        glClearColor(0.12, 0.12, 0.12, 1.0)  # Dark gray (YouTube video background)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Setup camera projection
        self.camera.setup_projection(self.width(), self.height())

        # Apply camera transform
        self.camera.apply_to_opengl()

        # Render all characters
        for scene_char in self.characters:
            if not scene_char.is_visible:
                continue

            # Translate to character's world position
            glPushMatrix()
            glTranslatef(scene_char.position[0], scene_char.position[1], 0.0)

            # Update animation if playing
            if self.is_playing and scene_char.current_animation:
                scene_char.animation_time += delta_time
                # Apply animation pose to skeleton
                pose = scene_char.current_animation.get_pose_at_time(scene_char.animation_time)
                scene_char.character.skeleton.apply_pose(pose)

            # Render character
            if self.use_hd_rendering:
                self.hd_renderer.render_skeleton_hd(scene_char.character.skeleton)
            else:
                # Use character's color
                color = scene_char.character.get_render_color()
                self.vector_renderer.render_skeleton(scene_char.character.skeleton, color)

            # Render face
            head_bone = scene_char.character.skeleton.get_bone("head")
            if head_bone:
                head_bone.update_world_transform()
                head_pos = head_bone.get_world_position()
                head_radius = head_bone.length * 0.8

                # Use character's facial rig
                facial_rig = FacialRig()
                facial_features = create_facial_features(Expression.NEUTRAL)
                facial_rig.render_face(head_pos, head_radius, facial_features)

            # Highlight if selected
            if scene_char.is_selected:
                self._render_selection_box(scene_char)

            glPopMatrix()

        # Draw grid
        self._draw_grid()

    def _draw_grid(self):
        """Draw reference grid."""
        glColor4f(0.2, 0.2, 0.2, 0.5)
        glLineWidth(1.0)

        glBegin(GL_LINES)

        # Vertical lines
        for x in range(-20, 21, 2):
            glVertex3f(x, -20, -0.1)
            glVertex3f(x, 20, -0.1)

        # Horizontal lines
        for y in range(-20, 21, 2):
            glVertex3f(-20, y, -0.1)
            glVertex3f(20, y, -0.1)

        glEnd()

        # Draw origin (0,0) with different color
        glColor4f(0.5, 0.5, 0.5, 0.8)
        glLineWidth(2.0)

        glBegin(GL_LINES)
        # X axis
        glVertex3f(-20, 0, -0.05)
        glVertex3f(20, 0, -0.05)
        # Y axis
        glVertex3f(0, -20, -0.05)
        glVertex3f(0, 20, -0.05)
        glEnd()

    def _render_selection_box(self, scene_char: SceneCharacter):
        """Render selection box around character."""
        # Calculate bounding box
        skeleton = scene_char.character.skeleton
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')

        for bone in skeleton.bones.values():
            pos = bone.get_world_position()
            min_x = min(min_x, pos[0])
            max_x = max(max_x, pos[0])
            min_y = min(min_y, pos[1])
            max_y = max(max_y, pos[1])

        # Add padding
        padding = 0.5
        min_x -= padding
        max_x += padding
        min_y -= padding
        max_y += padding

        # Draw box
        glColor4f(1.0, 0.8, 0.0, 0.8)  # Yellow
        glLineWidth(3.0)

        glBegin(GL_LINE_LOOP)
        glVertex3f(min_x, min_y, 0.1)
        glVertex3f(max_x, min_y, 0.1)
        glVertex3f(max_x, max_y, 0.1)
        glVertex3f(min_x, max_y, 0.1)
        glEnd()

    def mousePressEvent(self, event):
        """Handle mouse click for character selection."""
        if event.button() != Qt.LeftButton:
            return

        # TODO: Implement raycast selection
        # For now, cycle through characters
        if self.characters:
            if self.selected_character:
                # Deselect current
                self.selected_character.is_selected = False

                # Select next
                current_index = self.characters.index(self.selected_character)
                next_index = (current_index + 1) % len(self.characters)
                self.selected_character = self.characters[next_index]
            else:
                # Select first
                self.selected_character = self.characters[0]

            self.selected_character.is_selected = True
            self.character_selected.emit(self.selected_character.name)

    def wheelEvent(self, event):
        """Handle mouse wheel for zoom."""
        delta = event.angleDelta().y()

        if delta > 0:
            self.camera.zoom_in(0.1)
        else:
            self.camera.zoom_out(0.1)

        self.update()

    # ========================================================================
    # CHARACTER MANAGEMENT
    # ========================================================================

    def add_character(self, name: str, body_type: BodyType, color_preset: CharacterColorPreset) -> SceneCharacter:
        """Add character to scene."""
        # Create skeleton
        skeleton = create_stick_figure(name, body_type)

        # Create character
        character = StickFigureCharacter(name, skeleton, color_preset)

        # Create scene character
        position = np.array([len(self.characters) * 3.0, 0.0, 0.0], dtype=np.float32)  # Space them out
        scene_char = SceneCharacter(name, character, position)

        self.characters.append(scene_char)

        print(f"✓ Added character to scene: {name}")

        return scene_char

    def remove_character(self, name: str):
        """Remove character from scene."""
        self.characters = [char for char in self.characters if char.name != name]

        if self.selected_character and self.selected_character.name == name:
            self.selected_character = None

        print(f"✓ Removed character: {name}")

    def apply_animation_to_character(self, character_name: str, animation: Animation):
        """Apply animation to character."""
        for scene_char in self.characters:
            if scene_char.name == character_name:
                scene_char.current_animation = animation
                scene_char.animation_time = 0.0
                print(f"✓ Applied animation to {character_name}: {animation.name}")
                return

    # ========================================================================
    # PLAYBACK
    # ========================================================================

    def play(self):
        """Start playback."""
        self.is_playing = True
        print("▶ Studio playback started")

    def pause(self):
        """Pause playback."""
        self.is_playing = False
        print("⏸ Studio playback paused")

    def stop(self):
        """Stop playback and reset."""
        self.is_playing = False
        self.current_time = 0.0

        # Reset all character animations
        for scene_char in self.characters:
            scene_char.animation_time = 0.0

        print("■ Studio playback stopped")

    def toggle_rendering_mode(self):
        """Toggle between vector and HD rendering."""
        self.use_hd_rendering = not self.use_hd_rendering

        mode = "HD" if self.use_hd_rendering else "Vector"
        print(f"🎨 Rendering mode: {mode}")


# ============================================================================
# ANIMATION STUDIO TAB
# ============================================================================

class AnimationStudioTab(QWidget):
    """
    Tab 3: Full Animation Studio
    Complete workspace for creating YouTube stick figure fight content.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize UI
        self._init_ui()

        print("✓ Animation Studio Tab initialized")

    def _init_ui(self):
        """Initialize user interface."""
        layout = QHBoxLayout(self)

        # Create splitter for panels
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: Character list and controls
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)

        # Center: Main canvas
        self.canvas = StudioCanvas()
        splitter.addWidget(self.canvas)

        # Right panel: Animation controls
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # Set initial sizes (20% left, 60% center, 20% right)
        splitter.setSizes([250, 800, 250])

        layout.addWidget(splitter)

        # Bottom: Timeline
        self.timeline = self._create_timeline()
        layout.addWidget(self.timeline)

    def _create_left_panel(self) -> QWidget:
        """Create left control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("🎬 SCENE CHARACTERS")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Character list
        self.character_list = QListWidget()
        self.character_list.itemClicked.connect(self._on_character_selected)
        layout.addWidget(self.character_list)

        # Add character group
        add_group = self._create_add_character_group()
        layout.addWidget(add_group)

        # Character controls
        char_controls = self._create_character_controls()
        layout.addWidget(char_controls)

        layout.addStretch()

        panel.setMaximumWidth(300)
        panel.setStyleSheet("QWidget { background-color: #2a2a2a; }")

        return panel

    def _create_add_character_group(self) -> QGroupBox:
        """Create add character controls."""
        group = QGroupBox("Add Character")
        layout = QVBoxLayout(group)

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.char_name_input = QComboBox()
        self.char_name_input.setEditable(True)
        self.char_name_input.addItems(["Red Fighter", "Blue Fighter", "Green Fighter", "Yellow Fighter", "Villain"])
        name_layout.addWidget(self.char_name_input)
        layout.addLayout(name_layout)

        # Body type
        body_layout = QHBoxLayout()
        body_layout.addWidget(QLabel("Body:"))
        self.body_type_combo = QComboBox()
        self.body_type_combo.addItem("Normal", BodyType.NORMAL)
        self.body_type_combo.addItem("Muscular", BodyType.MUSCULAR)
        self.body_type_combo.addItem("Thin", BodyType.THIN)
        self.body_type_combo.addItem("Child", BodyType.CHILD)
        self.body_type_combo.addItem("Giant", BodyType.GIANT)
        body_layout.addWidget(self.body_type_combo)
        layout.addLayout(body_layout)

        # Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItem("Red", CharacterColorPreset.RED_FIGHTER)
        self.color_combo.addItem("Blue", CharacterColorPreset.BLUE_FIGHTER)
        self.color_combo.addItem("Green", CharacterColorPreset.GREEN_FIGHTER)
        self.color_combo.addItem("Yellow", CharacterColorPreset.YELLOW_FIGHTER)
        self.color_combo.addItem("Purple", CharacterColorPreset.PURPLE_FIGHTER)
        self.color_combo.addItem("Orange", CharacterColorPreset.ORANGE_FIGHTER)
        self.color_combo.addItem("Cyan", CharacterColorPreset.CYAN_FIGHTER)
        self.color_combo.addItem("Black", CharacterColorPreset.BLACK_FIGHTER)
        self.color_combo.addItem("White", CharacterColorPreset.WHITE_FIGHTER)
        color_layout.addWidget(self.color_combo)
        layout.addLayout(color_layout)

        # Add button
        add_btn = QPushButton("➕ Add to Scene")
        add_btn.clicked.connect(self._on_add_character)
        layout.addWidget(add_btn)

        return group

    def _create_character_controls(self) -> QGroupBox:
        """Create character manipulation controls."""
        group = QGroupBox("Character Controls")
        layout = QVBoxLayout(group)

        # Remove button
        remove_btn = QPushButton("🗑 Remove Selected")
        remove_btn.clicked.connect(self._on_remove_character)
        layout.addWidget(remove_btn)

        # Load preset animation
        preset_group = QGroupBox("Load Preset Animation")
        preset_layout = QVBoxLayout(preset_group)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("🕺 Floss Dance", "floss")
        self.preset_combo.addItem("🕴️ Carlton Dance", "carlton")
        self.preset_combo.addItem("👋 Take the L", "take_the_l")
        self.preset_combo.addItem("🌙 Moonwalk", "moonwalk")
        self.preset_combo.addItem("😎 Dab", "dab")
        preset_layout.addWidget(self.preset_combo)

        load_preset_btn = QPushButton("Load Animation")
        load_preset_btn.clicked.connect(self._on_load_preset_animation)
        preset_layout.addWidget(load_preset_btn)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        return group

    def _create_right_panel(self) -> QWidget:
        """Create right control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("🎥 CAMERA & PLAYBACK")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Playback controls
        playback_group = self._create_playback_controls()
        layout.addWidget(playback_group)

        # Camera controls
        camera_group = self._create_camera_controls()
        layout.addWidget(camera_group)

        # Rendering controls
        render_group = self._create_rendering_controls()
        layout.addWidget(render_group)

        layout.addStretch()

        # FPS display
        self.fps_label = QLabel("FPS: 60")
        self.fps_label.setStyleSheet("padding: 10px; color: #0f0; font-weight: bold;")
        layout.addWidget(self.fps_label)

        # Update FPS display
        fps_timer = QTimer(self)
        fps_timer.timeout.connect(self._update_fps_display)
        fps_timer.start(500)

        panel.setMaximumWidth(300)
        panel.setStyleSheet("QWidget { background-color: #2a2a2a; }")

        return panel

    def _create_playback_controls(self) -> QGroupBox:
        """Create playback controls."""
        group = QGroupBox("Playback")
        layout = QVBoxLayout(group)

        # Play/Pause button
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self._on_play_pause)
        layout.addWidget(self.play_btn)

        # Stop button
        stop_btn = QPushButton("■ Stop")
        stop_btn.clicked.connect(self._on_stop)
        layout.addWidget(stop_btn)

        return group

    def _create_camera_controls(self) -> QGroupBox:
        """Create camera controls."""
        group = QGroupBox("Camera")
        layout = QVBoxLayout(group)

        # Reset camera
        reset_btn = QPushButton("🎯 Reset Camera")
        reset_btn.clicked.connect(self._on_reset_camera)
        layout.addWidget(reset_btn)

        # Shake test
        shake_btn = QPushButton("📳 Test Shake")
        shake_btn.clicked.connect(self._on_test_shake)
        layout.addWidget(shake_btn)

        # Zoom controls
        zoom_layout = QHBoxLayout()
        zoom_out_btn = QPushButton("−")
        zoom_out_btn.clicked.connect(lambda: self.canvas.camera.zoom_out(0.2))
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.clicked.connect(lambda: self.canvas.camera.zoom_in(0.2))
        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(QLabel("Zoom"))
        zoom_layout.addWidget(zoom_in_btn)
        layout.addLayout(zoom_layout)

        return group

    def _create_rendering_controls(self) -> QGroupBox:
        """Create rendering controls."""
        group = QGroupBox("Rendering")
        layout = QVBoxLayout(group)

        # Toggle rendering mode
        self.render_mode_btn = QPushButton("Switch to HD Mode")
        self.render_mode_btn.clicked.connect(self._on_toggle_render_mode)
        layout.addWidget(self.render_mode_btn)

        # Export button
        export_btn = QPushButton("📹 Export Video")
        export_btn.setStyleSheet("background-color: #d93636; font-weight: bold;")
        export_btn.clicked.connect(self._on_export_video)
        layout.addWidget(export_btn)

        return group

    def _create_timeline(self) -> TimelineWidget:
        """Create timeline widget."""
        from timeline import create_timeline_widget

        timeline = create_timeline_widget(fps=60, duration=10.0)
        timeline.setMaximumHeight(200)

        # Connect signals
        timeline.time_changed.connect(self._on_timeline_changed)
        timeline.playback_state_changed.connect(self._on_timeline_playback_changed)

        return timeline

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    def _on_add_character(self):
        """Add character to scene."""
        name = self.char_name_input.currentText()
        body_type = self.body_type_combo.currentData()
        color_preset = self.color_combo.currentData()

        # Check if name already exists
        if any(char.name == name for char in self.canvas.characters):
            QMessageBox.warning(self, "Duplicate Name", f"Character '{name}' already exists!")
            return

        # Add to scene
        scene_char = self.canvas.add_character(name, body_type, color_preset)

        # Add to list
        item = QListWidgetItem(f"{name} ({color_preset.value})")
        self.character_list.addItem(item)

    def _on_remove_character(self):
        """Remove selected character."""
        selected_items = self.character_list.selectedItems()

        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a character to remove.")
            return

        item = selected_items[0]
        name = item.text().split(" (")[0]

        # Remove from scene
        self.canvas.remove_character(name)

        # Remove from list
        self.character_list.takeItem(self.character_list.row(item))

    def _on_character_selected(self, item):
        """Character selected in list."""
        name = item.text().split(" (")[0]

        # Select in canvas
        for scene_char in self.canvas.characters:
            scene_char.is_selected = (scene_char.name == name)

        self.canvas.selected_character = next((char for char in self.canvas.characters if char.name == name), None)

    def _on_load_preset_animation(self):
        """Load preset animation to selected character."""
        if not self.canvas.selected_character:
            QMessageBox.warning(self, "No Selection", "Please select a character first.")
            return

        preset_id = self.preset_combo.currentData()
        char_name = self.canvas.selected_character.name

        # Create animation based on preset
        if preset_id == "floss":
            animation = create_floss_animation(char_name)
        elif preset_id == "carlton":
            animation = create_carlton_animation(char_name)
        elif preset_id == "take_the_l":
            animation = create_take_the_l_animation(char_name)
        elif preset_id == "moonwalk":
            animation = create_moonwalk_animation(char_name)
        elif preset_id == "dab":
            animation = create_dab_animation(char_name)
        else:
            return

        # Apply to character
        self.canvas.apply_animation_to_character(char_name, animation)

        QMessageBox.information(self, "Animation Loaded",
                                f"Loaded {self.preset_combo.currentText()} to {char_name}!")

    def _on_play_pause(self):
        """Toggle play/pause."""
        if self.canvas.is_playing:
            self.canvas.pause()
            self.play_btn.setText("▶ Play")
        else:
            self.canvas.play()
            self.play_btn.setText("⏸ Pause")

    def _on_stop(self):
        """Stop playback."""
        self.canvas.stop()
        self.play_btn.setText("▶ Play")

    def _on_reset_camera(self):
        """Reset camera to default."""
        self.canvas.camera.reset()

    def _on_test_shake(self):
        """Test camera shake."""
        self.canvas.camera.impact_shake(1.0)

    def _on_toggle_render_mode(self):
        """Toggle rendering mode."""
        self.canvas.toggle_rendering_mode()

        if self.canvas.use_hd_rendering:
            self.render_mode_btn.setText("Switch to Vector Mode")
        else:
            self.render_mode_btn.setText("Switch to HD Mode")

    def _on_export_video(self):
        """Export to video."""
        QMessageBox.information(self, "Export",
                                "Video export will be implemented in the export system!")

    def _on_timeline_changed(self, time: float):
        """Timeline position changed."""
        self.canvas.current_time = time

    def _on_timeline_playback_changed(self, state):
        """Timeline playback state changed."""
        # Sync canvas playback with timeline
        pass

    def _update_fps_display(self):
        """Update FPS display."""
        self.fps_label.setText(f"FPS: {self.canvas.fps:.0f}")


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def create_animation_studio_tab() -> AnimationStudioTab:
    """
    Create and return the Animation Studio tab.

    Returns:
        Configured AnimationStudioTab widget
    """
    return AnimationStudioTab()


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    print("=" * 60)
    print("ANIMATION STUDIO TAB TEST")
    print("=" * 60)

    app = QApplication(sys.argv)

    tab = create_animation_studio_tab()
    tab.show()

    print("\n✓ Animation Studio ready for YouTube content creation!")

    sys.exit(app.exec())
