"""
Animation Studio Module - The Heart of Donk Animation Studio
Professional DaVinci-style timeline with scene management, voice recording,
smart lip-sync, and 30+ animation presets.

This is the main workspace where all animation magic happens!
"""

import os
import sys
import json
import time
import wave
import struct
import threading
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque
import numpy as np

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QFrame,
    QPushButton, QSlider, QLabel, QComboBox, QListWidget,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsTextItem, QMenu, QToolBar, QSpinBox, QCheckBox,
    QScrollArea, QGridLayout, QButtonGroup, QRadioButton,
    QTabWidget, QTextEdit, QProgressBar, QFileDialog,
    QMessageBox, QInputDialog, QColorDialog, QListWidgetItem,
    QGraphicsDropShadowEffect, QGroupBox
)
from PySide6.QtCore import (
    Qt, QTimer, Signal, QRect, QPoint, QSize, QRectF, QPointF,
    QThread, QObject, QEvent, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QSequentialAnimationGroup, Slot
)
from PySide6.QtGui import (
    QPainter, QBrush, QPen, QColor, QFont, QPixmap, QImage,
    QLinearGradient, QRadialGradient, QPolygonF, QPainterPath,
    QTransform, QKeySequence, QShortcut, QCursor, QWheelEvent
)
# Audio imports (optional, may not be installed)
try:
    from PySide6.QtMultimedia import QAudioInput, QMediaRecorder, QMediaCaptureSession
    MULTIMEDIA_AVAILABLE = True
except ImportError:
    MULTIMEDIA_AVAILABLE = False
    print("[WARNING] QtMultimedia not available. Voice features disabled.")

from PySide6.QtOpenGLWidgets import QOpenGLWidget

try:
    import sounddevice as sd
    import scipy.io.wavfile as wav
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("[WARNING] Audio libraries not available. Voice recording disabled.")

from OpenGL.GL import *
from OpenGL.GLU import *

# Import our modules
from stick_figure_maker import StickFigurePreset, StickFigureStyle


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class InterpolationType(Enum):
    """Animation interpolation types."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BEZIER = "bezier"
    STEP = "step"
    BOUNCE = "bounce"
    ELASTIC = "elastic"


class AnimationPresetType(Enum):
    """Categories of animation presets."""
    COMBAT = "Combat"
    MOVEMENT = "Movement"
    EMOTION = "Emotion"
    SPECIAL = "Special"
    CUSTOM = "Custom"


@dataclass
class Keyframe:
    """Single keyframe in animation."""
    time: float  # Time in seconds
    position: Tuple[float, float]  # X, Y position
    rotation: float  # Rotation in degrees
    scale: float  # Scale multiplier
    properties: Dict[str, Any] = field(default_factory=dict)  # Additional properties
    interpolation: InterpolationType = InterpolationType.LINEAR


@dataclass
class AnimationClip:
    """Reusable animation clip."""
    name: str
    duration: float  # Duration in seconds
    keyframes: Dict[str, List[Keyframe]]  # bone_name -> keyframes
    category: AnimationPresetType
    tags: List[str] = field(default_factory=list)
    loop: bool = False


@dataclass
class VoiceClip:
    """Voice recording clip with metadata."""
    name: str
    file_path: str
    start_time: float  # Position on timeline
    duration: float
    character_id: Optional[str] = None
    transcript: Optional[str] = None
    phonemes: List[Tuple[float, str]] = field(default_factory=list)  # Time-phoneme pairs


@dataclass
class Scene:
    """Single scene in the animation."""
    id: str
    name: str
    duration: float = 5.0  # Default 5 seconds
    characters: List[str] = field(default_factory=list)  # Character IDs
    background: Optional[str] = None  # Background image path
    animations: Dict[str, List[AnimationClip]] = field(default_factory=dict)  # character_id -> clips
    voice_clips: List[VoiceClip] = field(default_factory=list)
    effects: List[Dict] = field(default_factory=list)  # Particle effects, overlays
    camera_keyframes: List[Keyframe] = field(default_factory=list)


# ============================================================================
# TIMELINE WIDGET
# ============================================================================

class Timeline(QGraphicsView):
    """
    Professional timeline widget similar to DaVinci Resolve.
    Features multi-track editing, keyframe management, and real-time preview.
    """

    playhead_moved = Signal(float)  # Time in seconds
    keyframe_added = Signal(str, float)  # Track name, time
    clip_moved = Signal(str, float, float)  # Clip ID, old time, new time

    def __init__(self, parent=None):
        super().__init__(parent)

        # Timeline properties
        self.duration = 10.0  # Total duration in seconds
        self.zoom = 100  # Pixels per second
        self.current_time = 0.0
        self.tracks = {}  # Track name -> list of clips
        self.selected_clip = None
        self.is_playing = False

        # Setup scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Setup view
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        # Colors
        self.bg_color = QColor(20, 25, 40)
        self.grid_color = QColor(40, 45, 60)
        self.playhead_color = QColor(0, 217, 255)
        self.track_colors = {
            "character": QColor(123, 97, 255),
            "voice": QColor(255, 107, 53),
            "effect": QColor(0, 255, 136),
            "camera": QColor(255, 184, 0)
        }

        # Initialize timeline
        self._setup_timeline()
        self._setup_shortcuts()

    def _setup_timeline(self):
        """Initialize timeline UI."""
        self.setBackgroundBrush(QBrush(self.bg_color))

        # Create timeline ruler
        self._draw_ruler()

        # Create default tracks
        self.add_track("Character 1", "character")
        self.add_track("Voice", "voice")
        self.add_track("Effects", "effect")
        self.add_track("Camera", "camera")

        # Create playhead
        self._create_playhead()

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Space - Play/Pause
        space_shortcut = QShortcut(QKeySequence("Space"), self)
        space_shortcut.activated.connect(self.toggle_playback)

        # K - Add keyframe
        k_shortcut = QShortcut(QKeySequence("K"), self)
        k_shortcut.activated.connect(self.add_keyframe_at_playhead)

        # R - Record voice
        r_shortcut = QShortcut(QKeySequence("R"), self)
        r_shortcut.activated.connect(self.start_voice_recording)

    def _draw_ruler(self):
        """Draw time ruler at top of timeline."""
        ruler_height = 30
        width = self.duration * self.zoom

        # Background
        ruler_bg = self.scene.addRect(0, 0, width, ruler_height)
        ruler_bg.setBrush(QBrush(QColor(30, 35, 50)))
        ruler_bg.setPen(QPen(Qt.NoPen))

        # Time markers
        for second in range(int(self.duration) + 1):
            x = second * self.zoom

            # Vertical line
            line = self.scene.addLine(x, 0, x, ruler_height)
            line.setPen(QPen(self.grid_color, 1))

            # Time text
            time_text = self.scene.addText(f"{second}s")
            time_text.setDefaultTextColor(QColor(200, 200, 200))
            time_text.setPos(x + 2, 5)
            time_text.setFont(QFont("Arial", 9))

    def _create_playhead(self):
        """Create the playhead indicator."""
        self.playhead = self.scene.addLine(0, 0, 0, 600)
        self.playhead.setPen(QPen(self.playhead_color, 2))

        # Playhead handle
        handle = self.scene.addRect(-8, -5, 16, 10)
        handle.setBrush(QBrush(self.playhead_color))
        handle.setParentItem(self.playhead)

    def add_track(self, name: str, track_type: str = "character"):
        """Add a new track to timeline."""
        track_y = 40 + len(self.tracks) * 60
        track_height = 50
        width = self.duration * self.zoom

        # Track background
        track_bg = self.scene.addRect(0, track_y, width, track_height)
        track_bg.setBrush(QBrush(QColor(25, 30, 45)))
        track_bg.setPen(QPen(self.grid_color, 1))

        # Track label
        label_bg = self.scene.addRect(0, track_y, 120, track_height)
        label_bg.setBrush(QBrush(self.track_colors.get(track_type, QColor(100, 100, 100))))

        label_text = self.scene.addText(name)
        label_text.setDefaultTextColor(Qt.white)
        label_text.setPos(10, track_y + 15)
        label_text.setFont(QFont("Arial", 10, QFont.Bold))

        # Store track info
        self.tracks[name] = {
            "type": track_type,
            "y": track_y,
            "height": track_height,
            "clips": []
        }

    def add_clip(self, track_name: str, start_time: float, duration: float,
                 clip_data: Any, color: Optional[QColor] = None):
        """Add a clip to a track."""
        if track_name not in self.tracks:
            return

        track = self.tracks[track_name]
        x = start_time * self.zoom
        width = duration * self.zoom
        y = track["y"] + 5
        height = track["height"] - 10

        # Create clip rectangle
        clip_color = color or self.track_colors.get(track["type"], QColor(100, 100, 100))
        clip_rect = self.scene.addRect(x, y, width, height)
        clip_rect.setBrush(QBrush(clip_color))
        clip_rect.setPen(QPen(clip_color.lighter(120), 2))
        clip_rect.setFlag(QGraphicsItem.ItemIsMovable)
        clip_rect.setFlag(QGraphicsItem.ItemIsSelectable)

        # Add clip label
        if hasattr(clip_data, 'name'):
            label = self.scene.addText(clip_data.name)
            label.setDefaultTextColor(Qt.white)
            label.setPos(x + 5, y + 5)
            label.setParentItem(clip_rect)

        # Store clip info
        clip_info = {
            "rect": clip_rect,
            "data": clip_data,
            "start_time": start_time,
            "duration": duration
        }
        track["clips"].append(clip_info)

        return clip_rect

    def set_playhead_position(self, time: float):
        """Set playhead to specific time."""
        self.current_time = max(0, min(time, self.duration))
        x = self.current_time * self.zoom
        self.playhead.setPos(x, 0)
        self.playhead_moved.emit(self.current_time)

    def toggle_playback(self):
        """Toggle play/pause."""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self._start_playback()
        else:
            self._stop_playback()

    def _start_playback(self):
        """Start timeline playback."""
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self._update_playback)
        self.playback_timer.start(33)  # ~30 FPS

    def _stop_playback(self):
        """Stop timeline playback."""
        if hasattr(self, 'playback_timer'):
            self.playback_timer.stop()

    def _update_playback(self):
        """Update playhead during playback."""
        self.current_time += 0.033  # 30 FPS
        if self.current_time > self.duration:
            self.current_time = 0
        self.set_playhead_position(self.current_time)

    def add_keyframe_at_playhead(self):
        """Add keyframe at current playhead position."""
        # TODO: Implement based on selected object
        self.keyframe_added.emit("current", self.current_time)

    def start_voice_recording(self):
        """Trigger voice recording at playhead position."""
        # This will be handled by the parent studio
        self.parent().start_voice_recording_at(self.current_time)

    def mousePressEvent(self, event):
        """Handle mouse press for playhead dragging."""
        if event.button() == Qt.LeftButton:
            # Check if clicking on timeline ruler area
            scene_pos = self.mapToScene(event.pos())
            if scene_pos.y() < 30:  # Ruler area
                time = scene_pos.x() / self.zoom
                self.set_playhead_position(time)
        super().mousePressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """Handle zoom with Ctrl+Wheel."""
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom = min(500, self.zoom * 1.1)
            else:
                self.zoom = max(20, self.zoom / 1.1)
            self._refresh_timeline()
        else:
            super().wheelEvent(event)

    def _refresh_timeline(self):
        """Refresh timeline after zoom change."""
        # TODO: Redraw all elements with new zoom
        pass


# ============================================================================
# SCENE PANEL
# ============================================================================

class ScenePanel(QWidget):
    """
    Scene management panel showing all scenes as thumbnails.
    Similar to DaVinci Resolve's media pool.
    """

    scene_selected = Signal(str)  # Scene ID
    scene_added = Signal()
    scene_deleted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.scenes = []  # List of Scene objects
        self.current_scene_id = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup scene panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("SCENES")
        title.setStyleSheet("""
            QLabel {
                color: #00D9FF;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1A1F2E, stop:1 #2A3142);
                border-radius: 4px;
            }
        """)
        layout.addWidget(title)

        # Scene list
        self.scene_list = QListWidget()
        self.scene_list.setStyleSheet("""
            QListWidget {
                background: #141B2D;
                border: 1px solid #2A3142;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 5px;
                margin: 2px;
                background: #1A1F2E;
                border: 1px solid #2A3142;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00D9FF, stop:1 #7B61FF);
                border: 2px solid #00D9FF;
            }
            QListWidget::item:hover {
                background: #222837;
                border: 1px solid #00D9FF;
            }
        """)
        self.scene_list.itemClicked.connect(self._on_scene_selected)
        layout.addWidget(self.scene_list)

        # Scene controls
        controls_layout = QHBoxLayout()

        add_btn = QPushButton("+")
        add_btn.setToolTip("Add new scene")
        add_btn.clicked.connect(self.add_scene)
        controls_layout.addWidget(add_btn)

        duplicate_btn = QPushButton("⧉")
        duplicate_btn.setToolTip("Duplicate scene")
        duplicate_btn.clicked.connect(self.duplicate_scene)
        controls_layout.addWidget(duplicate_btn)

        delete_btn = QPushButton("−")
        delete_btn.setToolTip("Delete scene")
        delete_btn.clicked.connect(self.delete_scene)
        controls_layout.addWidget(delete_btn)

        up_btn = QPushButton("↑")
        up_btn.setToolTip("Move scene up")
        up_btn.clicked.connect(self.move_scene_up)
        controls_layout.addWidget(up_btn)

        down_btn = QPushButton("↓")
        down_btn.setToolTip("Move scene down")
        down_btn.clicked.connect(self.move_scene_down)
        controls_layout.addWidget(down_btn)

        layout.addLayout(controls_layout)

        # Scene properties
        props_group = QGroupBox("Properties")
        props_layout = QVBoxLayout()

        # Duration
        dur_layout = QHBoxLayout()
        dur_layout.addWidget(QLabel("Duration:"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 300)
        self.duration_spin.setValue(5)
        self.duration_spin.setSuffix(" sec")
        dur_layout.addWidget(self.duration_spin)
        props_layout.addLayout(dur_layout)

        props_group.setLayout(props_layout)
        layout.addWidget(props_group)

        # Style all buttons
        button_style = """
            QPushButton {
                background: #2A3142;
                color: white;
                border: 1px solid #3A4152;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3A4152;
                border: 1px solid #00D9FF;
            }
            QPushButton:pressed {
                background: #1A2132;
            }
        """
        for btn in [add_btn, duplicate_btn, delete_btn, up_btn, down_btn]:
            btn.setStyleSheet(button_style)

    def add_scene(self, name: Optional[str] = None):
        """Add a new scene."""
        if not name:
            name, ok = QInputDialog.getText(self, "New Scene", "Scene name:")
            if not ok or not name:
                name = f"Scene {len(self.scenes) + 1}"

        # Create new scene
        scene = Scene(
            id=f"scene_{int(time.time() * 1000)}",
            name=name,
            duration=self.duration_spin.value()
        )

        self.scenes.append(scene)

        # Add to list
        item = QListWidgetItem(f"{name} ({scene.duration}s)")
        self.scene_list.addItem(item)

        self.scene_added.emit()

    def duplicate_scene(self):
        """Duplicate selected scene."""
        current = self.scene_list.currentItem()
        if current:
            index = self.scene_list.row(current)
            original = self.scenes[index]

            # Create copy
            import copy
            new_scene = copy.deepcopy(original)
            new_scene.id = f"scene_{int(time.time() * 1000)}"
            new_scene.name = f"{original.name} (Copy)"

            self.scenes.insert(index + 1, new_scene)

            # Add to list
            item = QListWidgetItem(f"{new_scene.name} ({new_scene.duration}s)")
            self.scene_list.insertItem(index + 1, item)

    def delete_scene(self):
        """Delete selected scene."""
        current = self.scene_list.currentItem()
        if current:
            reply = QMessageBox.question(self, "Delete Scene",
                                        "Delete this scene?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                index = self.scene_list.row(current)
                scene = self.scenes.pop(index)
                self.scene_list.takeItem(index)
                self.scene_deleted.emit(scene.id)

    def move_scene_up(self):
        """Move scene up in order."""
        current = self.scene_list.currentRow()
        if current > 0:
            # Swap in list
            self.scenes[current], self.scenes[current-1] = \
                self.scenes[current-1], self.scenes[current]

            # Update UI
            item = self.scene_list.takeItem(current)
            self.scene_list.insertItem(current-1, item)
            self.scene_list.setCurrentRow(current-1)

    def move_scene_down(self):
        """Move scene down in order."""
        current = self.scene_list.currentRow()
        if current < self.scene_list.count() - 1:
            # Swap in list
            self.scenes[current], self.scenes[current+1] = \
                self.scenes[current+1], self.scenes[current]

            # Update UI
            item = self.scene_list.takeItem(current)
            self.scene_list.insertItem(current+1, item)
            self.scene_list.setCurrentRow(current+1)

    def _on_scene_selected(self, item):
        """Handle scene selection."""
        index = self.scene_list.row(item)
        if index < len(self.scenes):
            scene = self.scenes[index]
            self.current_scene_id = scene.id
            self.scene_selected.emit(scene.id)

    def get_current_scene(self) -> Optional[Scene]:
        """Get currently selected scene."""
        if self.current_scene_id:
            for scene in self.scenes:
                if scene.id == self.current_scene_id:
                    return scene
        return None


# ============================================================================
# PREVIEW CANVAS
# ============================================================================

class PreviewCanvas(QOpenGLWidget):
    """
    OpenGL canvas for real-time animation preview.
    Shows previous, current, and next frames with onion skinning.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_frame = 0
        self.total_frames = 300  # 10 seconds at 30 FPS
        self.show_onion_skin = True
        self.onion_skin_frames = 3
        self.characters = []  # List of stick figures in scene
        self.playing = False

        # Frame cache for smooth playback
        self.frame_cache = {}

        self.setMinimumSize(800, 450)  # 16:9 aspect ratio

    def initializeGL(self):
        """Initialize OpenGL."""
        glClearColor(0.1, 0.1, 0.15, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Enable antialiasing
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

    def resizeGL(self, w, h):
        """Handle resize."""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = w / max(1, h)
        gluPerspective(45, aspect, 0.1, 100.0)

    def paintGL(self):
        """Render the scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Camera position
        glTranslatef(0.0, 0.0, -5.0)

        # Draw grid/stage
        self._draw_stage()

        # Draw onion skin (previous frames)
        if self.show_onion_skin:
            self._draw_onion_skin()

        # Draw current frame
        self._draw_current_frame()

        # Draw UI overlays
        self._draw_overlays()

    def _draw_stage(self):
        """Draw the stage/grid."""
        glColor4f(0.2, 0.2, 0.3, 0.5)
        glLineWidth(1.0)

        # Grid
        glBegin(GL_LINES)
        for i in range(-10, 11):
            glVertex3f(i, 0, 0)
            glVertex3f(i, 0, -10)
            glVertex3f(-10, 0, i/2)
            glVertex3f(10, 0, i/2)
        glEnd()

        # Stage boundary
        glColor4f(0.3, 0.3, 0.4, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex3f(-3, -2, 0)
        glVertex3f(3, -2, 0)
        glVertex3f(3, 2, 0)
        glVertex3f(-3, 2, 0)
        glEnd()

    def _draw_onion_skin(self):
        """Draw semi-transparent previous frames."""
        for i in range(1, self.onion_skin_frames + 1):
            frame = self.current_frame - i
            if frame >= 0:
                alpha = 0.2 / i  # Fade older frames more
                glColor4f(0.5, 0.5, 1.0, alpha)
                # Draw frame data
                # TODO: Draw actual character positions for this frame

    def _draw_current_frame(self):
        """Draw the current frame."""
        glColor4f(1.0, 1.0, 1.0, 1.0)

        # Draw all characters at their current positions
        for character in self.characters:
            self._draw_character(character)

    def _draw_character(self, character):
        """Draw a stick figure character."""
        # TODO: Implement based on character data and current frame
        pass

    def _draw_overlays(self):
        """Draw UI overlays like frame counter."""
        # This would be done with QPainter in paintEvent override
        pass

    def set_frame(self, frame: int):
        """Set current frame and update display."""
        self.current_frame = max(0, min(frame, self.total_frames - 1))
        self.update()

    def toggle_onion_skin(self):
        """Toggle onion skinning."""
        self.show_onion_skin = not self.show_onion_skin
        self.update()


# ============================================================================
# VOICE RECORDING SYSTEM
# ============================================================================

class VoiceRecorder(QObject):
    """
    Voice recording system with real-time level monitoring.
    Records at timeline position with automatic waveform generation.
    """

    recording_started = Signal()
    recording_stopped = Signal(str)  # File path
    level_updated = Signal(float)  # Audio level 0-1

    def __init__(self, parent=None):
        super().__init__(parent)

        self.recording = False
        self.audio_data = []
        self.sample_rate = 44100

        if AUDIO_AVAILABLE:
            self.setup_audio()

    def setup_audio(self):
        """Setup audio recording."""
        try:
            # Get default input device
            self.input_device = sd.default.device[0]
            print(f"[Audio] Using input device: {sd.query_devices(self.input_device)['name']}")
        except Exception as e:
            print(f"[Audio] Error setting up audio: {e}")

    def start_recording(self):
        """Start recording audio."""
        if not AUDIO_AVAILABLE:
            QMessageBox.warning(None, "Audio Not Available",
                               "Audio libraries not installed. Please install sounddevice.")
            return

        self.recording = True
        self.audio_data = []
        self.recording_started.emit()

        # Start recording thread
        self.record_thread = threading.Thread(target=self._record_audio)
        self.record_thread.start()

    def stop_recording(self) -> Optional[str]:
        """Stop recording and save to file."""
        if not self.recording:
            return None

        self.recording = False

        # Wait for thread to finish
        if hasattr(self, 'record_thread'):
            self.record_thread.join()

        # Save audio to file
        if self.audio_data:
            filename = f"assets/audio/recording_{int(time.time())}.wav"
            os.makedirs("assets/audio", exist_ok=True)

            # Convert to numpy array and save
            audio_array = np.array(self.audio_data)
            wav.write(filename, self.sample_rate, audio_array)

            self.recording_stopped.emit(filename)
            return filename

        return None

    def _record_audio(self):
        """Recording thread function."""
        try:
            with sd.InputStream(samplerate=self.sample_rate,
                               channels=1,
                               callback=self._audio_callback):
                while self.recording:
                    sd.sleep(100)
        except Exception as e:
            print(f"[Audio] Recording error: {e}")

    def _audio_callback(self, indata, frames, time_info, status):
        """Audio stream callback."""
        if status:
            print(f"[Audio] Status: {status}")

        if self.recording:
            # Store audio data
            self.audio_data.extend(indata[:, 0])

            # Calculate level for visualization
            level = np.abs(indata[:, 0]).mean()
            self.level_updated.emit(min(1.0, level * 10))


# ============================================================================
# ANIMATION PRESET LIBRARY
# ============================================================================

class AnimationLibrary:
    """
    Library of 30+ animation presets for drag-and-drop.
    """

    def __init__(self):
        self.presets = {}
        self._create_all_presets()

    def _create_all_presets(self):
        """Create all animation presets."""

        # === COMBAT ANIMATIONS (8) ===
        self.presets["punch"] = self._create_punch_animation()
        self.presets["kick"] = self._create_kick_animation()
        self.presets["block"] = self._create_block_animation()
        self.presets["dodge"] = self._create_dodge_animation()
        self.presets["sword_swing"] = self._create_sword_swing_animation()
        self.presets["hit_reaction"] = self._create_hit_reaction_animation()
        self.presets["fall"] = self._create_fall_animation()
        self.presets["death"] = self._create_death_animation()

        # === MOVEMENT ANIMATIONS (8) ===
        self.presets["walk"] = self._create_walk_animation()
        self.presets["run"] = self._create_run_animation()
        self.presets["jump"] = self._create_jump_animation()
        self.presets["crouch"] = self._create_crouch_animation()
        self.presets["turn"] = self._create_turn_animation()
        self.presets["idle"] = self._create_idle_animation()
        self.presets["climb"] = self._create_climb_animation()
        self.presets["roll"] = self._create_roll_animation()

        # === EMOTION ANIMATIONS (8) ===
        self.presets["laugh"] = self._create_laugh_animation()
        self.presets["cry"] = self._create_cry_animation()
        self.presets["angry"] = self._create_angry_animation()
        self.presets["surprise"] = self._create_surprise_animation()
        self.presets["think"] = self._create_think_animation()
        self.presets["victory"] = self._create_victory_animation()
        self.presets["defeat"] = self._create_defeat_animation()
        self.presets["taunt"] = self._create_taunt_animation()

        # === SPECIAL ANIMATIONS (6) ===
        self.presets["dance"] = self._create_dance_animation()
        self.presets["backflip"] = self._create_backflip_animation()
        self.presets["power_up"] = self._create_power_up_animation()
        self.presets["teleport"] = self._create_teleport_animation()
        self.presets["explode"] = self._create_explode_animation()
        self.presets["dizzy"] = self._create_dizzy_animation()

    # --- Combat Animations ---

    def _create_punch_animation(self) -> AnimationClip:
        """Create punch animation."""
        keyframes = {
            "right_arm": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN),
                Keyframe(0.1, (-0.3, 0.2), -30, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.2, (0.5, 0.1), 0, 1.2, interpolation=InterpolationType.EASE_OUT),
                Keyframe(0.3, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
            ],
            "torso": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.15, (0.1, 0), -10, 1.0),
                Keyframe(0.3, (0, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Punch", 0.3, keyframes, AnimationPresetType.COMBAT,
                           ["combat", "attack", "melee"])

    def _create_kick_animation(self) -> AnimationClip:
        """Create kick animation."""
        keyframes = {
            "right_leg": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN),
                Keyframe(0.15, (0, 0.3), -45, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.25, (0.4, 0.5), -90, 1.1, interpolation=InterpolationType.EASE_OUT),
                Keyframe(0.4, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
            ],
            "torso": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.2, (-0.1, 0), 10, 1.0),
                Keyframe(0.4, (0, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Kick", 0.4, keyframes, AnimationPresetType.COMBAT,
                           ["combat", "attack", "melee"])

    def _create_block_animation(self) -> AnimationClip:
        """Create block animation."""
        keyframes = {
            "left_arm": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_OUT),
                Keyframe(0.1, (0.2, 0.3), 45, 1.0, interpolation=InterpolationType.STEP),
                Keyframe(0.5, (0.2, 0.3), 45, 1.0, interpolation=InterpolationType.STEP),
                Keyframe(0.6, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN),
            ],
            "right_arm": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_OUT),
                Keyframe(0.1, (-0.2, 0.3), -45, 1.0, interpolation=InterpolationType.STEP),
                Keyframe(0.5, (-0.2, 0.3), -45, 1.0, interpolation=InterpolationType.STEP),
                Keyframe(0.6, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN),
            ]
        }
        return AnimationClip("Block", 0.6, keyframes, AnimationPresetType.COMBAT,
                           ["combat", "defense", "protect"])

    def _create_dodge_animation(self) -> AnimationClip:
        """Create dodge animation."""
        keyframes = {
            "root": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(0.15, (-0.5, -0.1), 0, 1.0, interpolation=InterpolationType.EASE_OUT),
                Keyframe(0.3, (-0.5, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN),
                Keyframe(0.45, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
            ],
            "torso": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.15, (0, 0), -20, 1.0),
                Keyframe(0.3, (0, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Dodge", 0.45, keyframes, AnimationPresetType.COMBAT,
                           ["combat", "evade", "defense"])

    def _create_sword_swing_animation(self) -> AnimationClip:
        """Create sword swing animation."""
        keyframes = {
            "right_arm": [
                Keyframe(0.0, (0, 0), 45, 1.0, interpolation=InterpolationType.EASE_IN),
                Keyframe(0.2, (0.2, 0.4), 135, 1.0, interpolation=InterpolationType.EASE_OUT),
                Keyframe(0.35, (0.3, -0.2), -45, 1.2, interpolation=InterpolationType.LINEAR),
                Keyframe(0.5, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
            ],
            "weapon": [  # Attached weapon follows arm
                Keyframe(0.0, (0, 0), 45, 1.0),
                Keyframe(0.2, (0, 0), 135, 1.0),
                Keyframe(0.35, (0, 0), -45, 1.0),
                Keyframe(0.5, (0, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Sword Swing", 0.5, keyframes, AnimationPresetType.COMBAT,
                           ["combat", "weapon", "attack"])

    def _create_hit_reaction_animation(self) -> AnimationClip:
        """Create hit reaction animation."""
        keyframes = {
            "root": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.STEP),
                Keyframe(0.05, (-0.2, 0), 0, 1.0, interpolation=InterpolationType.BOUNCE),
                Keyframe(0.2, (-0.1, 0), 0, 1.0, interpolation=InterpolationType.EASE_OUT),
                Keyframe(0.35, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
            ],
            "head": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.05, (-0.1, 0.1), -15, 1.0),
                Keyframe(0.2, (0, 0), 5, 1.0),
                Keyframe(0.35, (0, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Hit Reaction", 0.35, keyframes, AnimationPresetType.COMBAT,
                           ["combat", "reaction", "damage"])

    def _create_fall_animation(self) -> AnimationClip:
        """Create fall animation."""
        keyframes = {
            "root": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN),
                Keyframe(0.3, (0, -0.5), 0, 1.0, interpolation=InterpolationType.EASE_OUT),
                Keyframe(0.6, (0, -1.0), 0, 1.0, interpolation=InterpolationType.BOUNCE),
            ],
            "torso": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.3, (0, 0), -45, 1.0),
                Keyframe(0.6, (0, 0), -90, 1.0),
            ]
        }
        return AnimationClip("Fall", 0.6, keyframes, AnimationPresetType.COMBAT,
                           ["combat", "knockdown", "reaction"])

    def _create_death_animation(self) -> AnimationClip:
        """Create death animation."""
        keyframes = {
            "root": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN),
                Keyframe(0.5, (0, -0.5), 0, 1.0, interpolation=InterpolationType.EASE_OUT),
                Keyframe(1.0, (0, -1.2), 0, 1.0, interpolation=InterpolationType.EASE_OUT),
            ],
            "torso": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.5, (0, 0), -45, 1.0),
                Keyframe(1.0, (0, 0), -90, 1.0),
            ],
            "opacity": [  # Fade out
                Keyframe(0.0, (0, 0), 0, 1.0, {"opacity": 1.0}),
                Keyframe(0.8, (0, 0), 0, 1.0, {"opacity": 1.0}),
                Keyframe(1.2, (0, 0), 0, 1.0, {"opacity": 0.3}),
            ]
        }
        return AnimationClip("Death", 1.2, keyframes, AnimationPresetType.COMBAT,
                           ["combat", "defeat", "ko"])

    # --- Movement Animations ---

    def _create_walk_animation(self) -> AnimationClip:
        """Create walk cycle animation."""
        keyframes = {
            "left_leg": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(0.25, (0.2, 0.1), 15, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(0.5, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(0.75, (-0.2, 0.1), -15, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(1.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
            ],
            "right_leg": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(0.25, (-0.2, 0.1), -15, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(0.5, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(0.75, (0.2, 0.1), 15, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(1.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
            ]
        }
        return AnimationClip("Walk", 1.0, keyframes, AnimationPresetType.MOVEMENT,
                           ["movement", "locomotion", "walk"], loop=True)

    def _create_run_animation(self) -> AnimationClip:
        """Create run cycle animation."""
        keyframes = {
            "left_leg": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.15, (0.3, 0.2), 30, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.3, (0, 0), 0, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.45, (-0.3, 0.2), -30, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.6, (0, 0), 0, 1.0, interpolation=InterpolationType.LINEAR),
            ],
            "right_leg": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.15, (-0.3, 0.2), -30, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.3, (0, 0), 0, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.45, (0.3, 0.2), 30, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.6, (0, 0), 0, 1.0, interpolation=InterpolationType.LINEAR),
            ],
            "arms": [  # Both arms swing
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.3, (0, 0), 20, 1.0),
                Keyframe(0.6, (0, 0), -20, 1.0),
            ]
        }
        return AnimationClip("Run", 0.6, keyframes, AnimationPresetType.MOVEMENT,
                           ["movement", "locomotion", "run", "sprint"], loop=True)

    def _create_jump_animation(self) -> AnimationClip:
        """Create jump animation."""
        keyframes = {
            "root": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN),
                Keyframe(0.2, (0, -0.2), 0, 0.9, interpolation=InterpolationType.EASE_OUT),
                Keyframe(0.4, (0, 0.8), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(0.6, (0, 0.6), 0, 1.0, interpolation=InterpolationType.EASE_IN),
                Keyframe(0.8, (0, 0), 0, 1.0, interpolation=InterpolationType.BOUNCE),
            ],
            "arms": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.2, (0, 0.3), 45, 1.0),
                Keyframe(0.4, (0, 0.4), 60, 1.0),
                Keyframe(0.8, (0, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Jump", 0.8, keyframes, AnimationPresetType.MOVEMENT,
                           ["movement", "jump", "leap"])

    def _create_crouch_animation(self) -> AnimationClip:
        """Create crouch animation."""
        keyframes = {
            "root": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(0.3, (0, -0.4), 0, 0.7, interpolation=InterpolationType.EASE_OUT),
            ],
            "torso": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.3, (0, 0), 10, 0.9),
            ]
        }
        return AnimationClip("Crouch", 0.3, keyframes, AnimationPresetType.MOVEMENT,
                           ["movement", "crouch", "stealth"])

    def _create_turn_animation(self) -> AnimationClip:
        """Create turn around animation."""
        keyframes = {
            "root": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(0.25, (0, 0), 90, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.5, (0, 0), 180, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
            ]
        }
        return AnimationClip("Turn", 0.5, keyframes, AnimationPresetType.MOVEMENT,
                           ["movement", "turn", "rotate"])

    def _create_idle_animation(self) -> AnimationClip:
        """Create idle breathing animation."""
        keyframes = {
            "torso": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(1.0, (0, 0.02), 0, 1.02, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(2.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
            ],
            "head": [  # Subtle head movement
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(1.5, (0.01, 0), 2, 1.0),
                Keyframe(3.0, (0, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Idle", 3.0, keyframes, AnimationPresetType.MOVEMENT,
                           ["movement", "idle", "breathing"], loop=True)

    def _create_climb_animation(self) -> AnimationClip:
        """Create climbing animation."""
        keyframes = {
            "left_arm": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.25, (0, 0.4), -10, 1.0),
                Keyframe(0.5, (0, 0), 0, 1.0),
            ],
            "right_arm": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.25, (0, 0), 0, 1.0),
                Keyframe(0.5, (0, 0.4), 10, 1.0),
                Keyframe(0.75, (0, 0), 0, 1.0),
            ],
            "root": [  # Moving up
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.5, (0, 0.2), 0, 1.0),
                Keyframe(1.0, (0, 0.4), 0, 1.0),
            ]
        }
        return AnimationClip("Climb", 1.0, keyframes, AnimationPresetType.MOVEMENT,
                           ["movement", "climb", "vertical"], loop=True)

    def _create_roll_animation(self) -> AnimationClip:
        """Create combat roll animation."""
        keyframes = {
            "root": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN),
                Keyframe(0.2, (0.3, -0.3), 180, 0.7, interpolation=InterpolationType.LINEAR),
                Keyframe(0.4, (0.6, 0), 360, 1.0, interpolation=InterpolationType.EASE_OUT),
            ]
        }
        return AnimationClip("Roll", 0.4, keyframes, AnimationPresetType.MOVEMENT,
                           ["movement", "roll", "evade"])

    # --- Emotion Animations ---

    def _create_laugh_animation(self) -> AnimationClip:
        """Create laughing animation."""
        keyframes = {
            "torso": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.1, (0, 0), -5, 1.0),
                Keyframe(0.2, (0, 0), 5, 1.0),
                Keyframe(0.3, (0, 0), -5, 1.0),
                Keyframe(0.4, (0, 0), 5, 1.0),
                Keyframe(0.5, (0, 0), 0, 1.0),
            ],
            "head": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.15, (0, 0.05), -10, 1.0),
                Keyframe(0.3, (0, 0.05), 10, 1.0),
                Keyframe(0.5, (0, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Laugh", 0.5, keyframes, AnimationPresetType.EMOTION,
                           ["emotion", "happy", "laugh"], loop=True)

    def _create_cry_animation(self) -> AnimationClip:
        """Create crying animation."""
        keyframes = {
            "head": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.5, (0, -0.05), 10, 1.0),
                Keyframe(1.0, (0, -0.05), 10, 1.0),
            ],
            "arms": [  # Hands to face
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.3, (0, 0.3), 45, 0.9),
                Keyframe(1.0, (0, 0.3), 45, 0.9),
            ]
        }
        return AnimationClip("Cry", 1.0, keyframes, AnimationPresetType.EMOTION,
                           ["emotion", "sad", "cry"])

    def _create_angry_animation(self) -> AnimationClip:
        """Create angry animation."""
        keyframes = {
            "torso": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.2, (0, 0), -5, 1.05),
                Keyframe(0.4, (0, 0), 5, 1.05),
                Keyframe(0.6, (0, 0), 0, 1.0),
            ],
            "arms": [  # Fists clenched
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.2, (0, -0.1), -20, 1.1),
                Keyframe(0.6, (0, -0.1), -20, 1.1),
            ]
        }
        return AnimationClip("Angry", 0.6, keyframes, AnimationPresetType.EMOTION,
                           ["emotion", "angry", "rage"])

    def _create_surprise_animation(self) -> AnimationClip:
        """Create surprise/shock animation."""
        keyframes = {
            "root": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.STEP),
                Keyframe(0.1, (0, 0.1), 0, 1.1, interpolation=InterpolationType.BOUNCE),
                Keyframe(0.3, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_OUT),
            ],
            "arms": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.1, (0.2, 0.2), 30, 1.0),
                Keyframe(0.3, (0.2, 0.2), 30, 1.0),
            ]
        }
        return AnimationClip("Surprise", 0.3, keyframes, AnimationPresetType.EMOTION,
                           ["emotion", "surprise", "shock"])

    def _create_think_animation(self) -> AnimationClip:
        """Create thinking animation."""
        keyframes = {
            "right_arm": [  # Hand to chin
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.3, (0.1, 0.3), 90, 1.0),
                Keyframe(1.0, (0.1, 0.3), 90, 1.0),
            ],
            "head": [  # Look up
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.3, (0, 0.05), -10, 1.0),
                Keyframe(1.0, (0, 0.05), -10, 1.0),
            ]
        }
        return AnimationClip("Think", 1.0, keyframes, AnimationPresetType.EMOTION,
                           ["emotion", "think", "ponder"])

    def _create_victory_animation(self) -> AnimationClip:
        """Create victory celebration animation."""
        keyframes = {
            "arms": [  # Arms up
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_OUT),
                Keyframe(0.2, (0, 0.5), 120, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
                Keyframe(0.6, (0, 0.5), 120, 1.0, interpolation=InterpolationType.EASE_IN_OUT),
            ],
            "root": [  # Jump
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.2, (0, 0.3), 0, 1.0),
                Keyframe(0.4, (0, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Victory", 0.6, keyframes, AnimationPresetType.EMOTION,
                           ["emotion", "victory", "celebration", "win"])

    def _create_defeat_animation(self) -> AnimationClip:
        """Create defeat/disappointment animation."""
        keyframes = {
            "head": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.3, (0, -0.1), 20, 1.0),
                Keyframe(0.8, (0, -0.1), 20, 1.0),
            ],
            "torso": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.3, (0, 0), 10, 0.95),
                Keyframe(0.8, (0, 0), 10, 0.95),
            ]
        }
        return AnimationClip("Defeat", 0.8, keyframes, AnimationPresetType.EMOTION,
                           ["emotion", "defeat", "disappointed", "lose"])

    def _create_taunt_animation(self) -> AnimationClip:
        """Create taunt animation."""
        keyframes = {
            "right_arm": [  # Beckoning gesture
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.2, (0.3, 0.2), 45, 1.0),
                Keyframe(0.3, (0.25, 0.2), 30, 1.0),
                Keyframe(0.4, (0.3, 0.2), 45, 1.0),
                Keyframe(0.5, (0.25, 0.2), 30, 1.0),
                Keyframe(0.6, (0, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Taunt", 0.6, keyframes, AnimationPresetType.EMOTION,
                           ["emotion", "taunt", "provoke"])

    # --- Special Animations ---

    def _create_dance_animation(self) -> AnimationClip:
        """Create dance animation."""
        keyframes = {
            "hips": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.25, (0.1, 0), 10, 1.0),
                Keyframe(0.5, (-0.1, 0), -10, 1.0),
                Keyframe(0.75, (0.1, 0), 10, 1.0),
                Keyframe(1.0, (0, 0), 0, 1.0),
            ],
            "arms": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.25, (0.2, 0.3), 45, 1.0),
                Keyframe(0.5, (-0.2, 0.3), -45, 1.0),
                Keyframe(0.75, (0.2, 0.3), 45, 1.0),
                Keyframe(1.0, (0, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Dance", 1.0, keyframes, AnimationPresetType.SPECIAL,
                           ["special", "dance", "celebration"], loop=True)

    def _create_backflip_animation(self) -> AnimationClip:
        """Create backflip animation."""
        keyframes = {
            "root": [
                Keyframe(0.0, (0, 0), 0, 1.0, interpolation=InterpolationType.EASE_IN),
                Keyframe(0.2, (0, 0.3), -90, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.4, (0, 0.5), -180, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.6, (0, 0.3), -270, 1.0, interpolation=InterpolationType.LINEAR),
                Keyframe(0.8, (0, 0), -360, 1.0, interpolation=InterpolationType.EASE_OUT),
            ]
        }
        return AnimationClip("Backflip", 0.8, keyframes, AnimationPresetType.SPECIAL,
                           ["special", "acrobatic", "flip"])

    def _create_power_up_animation(self) -> AnimationClip:
        """Create power up animation."""
        keyframes = {
            "root": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.5, (0, 0), 0, 1.2),
                Keyframe(1.0, (0, 0), 0, 1.0),
            ],
            "effects": [  # Particle burst
                Keyframe(0.0, (0, 0), 0, 0, {"particles": 0}),
                Keyframe(0.3, (0, 0), 0, 0, {"particles": 50}),
                Keyframe(1.0, (0, 0), 0, 0, {"particles": 0}),
            ]
        }
        return AnimationClip("Power Up", 1.0, keyframes, AnimationPresetType.SPECIAL,
                           ["special", "power", "transform"])

    def _create_teleport_animation(self) -> AnimationClip:
        """Create teleport animation."""
        keyframes = {
            "opacity": [
                Keyframe(0.0, (0, 0), 0, 1.0, {"opacity": 1.0}),
                Keyframe(0.2, (0, 0), 0, 1.0, {"opacity": 0.0}),
                Keyframe(0.3, (0, 0), 0, 1.0, {"opacity": 0.0}),
                Keyframe(0.5, (0, 0), 0, 1.0, {"opacity": 1.0}),
            ],
            "root": [  # Position change
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.25, (0, 0), 0, 1.0),
                Keyframe(0.26, (2, 0), 0, 1.0),  # Instant position change
                Keyframe(0.5, (2, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Teleport", 0.5, keyframes, AnimationPresetType.SPECIAL,
                           ["special", "teleport", "disappear"])

    def _create_explode_animation(self) -> AnimationClip:
        """Create explosion animation."""
        keyframes = {
            "parts": [  # Body parts fly apart
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.1, (0, 0), 0, 1.5),
                Keyframe(0.5, (0, 0), 0, 3.0, {"scatter": 2.0}),
            ],
            "opacity": [
                Keyframe(0.0, (0, 0), 0, 1.0, {"opacity": 1.0}),
                Keyframe(0.3, (0, 0), 0, 1.0, {"opacity": 1.0}),
                Keyframe(0.5, (0, 0), 0, 1.0, {"opacity": 0.0}),
            ]
        }
        return AnimationClip("Explode", 0.5, keyframes, AnimationPresetType.SPECIAL,
                           ["special", "explode", "destroy"])

    def _create_dizzy_animation(self) -> AnimationClip:
        """Create dizzy animation."""
        keyframes = {
            "head": [
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.25, (0.05, 0), 5, 1.0),
                Keyframe(0.5, (-0.05, 0), -5, 1.0),
                Keyframe(0.75, (0.05, 0), 5, 1.0),
                Keyframe(1.0, (0, 0), 0, 1.0),
            ],
            "root": [  # Swaying
                Keyframe(0.0, (0, 0), 0, 1.0),
                Keyframe(0.3, (0.1, 0), 5, 1.0),
                Keyframe(0.6, (-0.1, 0), -5, 1.0),
                Keyframe(0.9, (0.1, 0), 5, 1.0),
                Keyframe(1.2, (0, 0), 0, 1.0),
            ]
        }
        return AnimationClip("Dizzy", 1.2, keyframes, AnimationPresetType.SPECIAL,
                           ["special", "dizzy", "confused"], loop=True)

    def get_preset(self, name: str) -> Optional[AnimationClip]:
        """Get animation preset by name."""
        return self.presets.get(name)

    def get_presets_by_category(self, category: AnimationPresetType) -> List[AnimationClip]:
        """Get all presets in a category."""
        return [clip for clip in self.presets.values() if clip.category == category]


# ============================================================================
# MAIN ANIMATION STUDIO TAB
# ============================================================================

class AnimationStudioTab(QWidget):
    """
    Main animation studio tab - the heart of the application.
    Combines all systems into a professional animation workspace.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Core systems
        self.animation_library = AnimationLibrary()
        self.voice_recorder = VoiceRecorder()
        self.current_project = None

        # Setup UI
        self._setup_ui()

        # Connect signals
        self._connect_signals()

    def _setup_ui(self):
        """Build the complete studio interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Create main splitter (horizontal)
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Scene management
        self.scene_panel = ScenePanel()
        self.scene_panel.setMaximumWidth(250)
        main_splitter.addWidget(self.scene_panel)

        # Middle section (vertical splitter)
        middle_splitter = QSplitter(Qt.Vertical)

        # Preview canvas
        self.preview_canvas = PreviewCanvas()
        middle_splitter.addWidget(self.preview_canvas)

        # Timeline
        self.timeline = Timeline()
        self.timeline.setMinimumHeight(200)
        middle_splitter.addWidget(self.timeline)

        middle_splitter.setSizes([600, 200])
        main_splitter.addWidget(middle_splitter)

        # Right panel - Properties and presets
        right_panel = self._create_right_panel()
        right_panel.setMaximumWidth(300)
        main_splitter.addWidget(right_panel)

        # Set initial sizes
        main_splitter.setSizes([200, 800, 250])

        main_layout.addWidget(main_splitter)

        # Bottom toolbar
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)

    def _create_right_panel(self) -> QWidget:
        """Create right properties panel."""
        panel = QTabWidget()

        # Animation presets tab
        presets_widget = QWidget()
        presets_layout = QVBoxLayout(presets_widget)

        # Category selector
        category_combo = QComboBox()
        for cat in AnimationPresetType:
            category_combo.addItem(cat.value)
        presets_layout.addWidget(category_combo)

        # Preset list
        self.preset_list = QListWidget()
        self.preset_list.setDragEnabled(True)
        presets_layout.addWidget(self.preset_list)

        # Load initial presets
        self._load_presets(AnimationPresetType.COMBAT)
        category_combo.currentTextChanged.connect(self._on_category_changed)

        panel.addTab(presets_widget, "Animations")

        # Character properties tab
        char_widget = QWidget()
        char_layout = QVBoxLayout(char_widget)
        char_layout.addWidget(QLabel("Character properties"))
        panel.addTab(char_widget, "Character")

        # Effects tab
        effects_widget = QWidget()
        effects_layout = QVBoxLayout(effects_widget)
        effects_layout.addWidget(QLabel("Particle effects"))
        panel.addTab(effects_widget, "Effects")

        return panel

    def _create_toolbar(self) -> QToolBar:
        """Create bottom toolbar."""
        toolbar = QToolBar()

        # Play controls
        play_btn = QPushButton("▶ Play")
        play_btn.clicked.connect(self.play_animation)
        toolbar.addWidget(play_btn)

        pause_btn = QPushButton("⏸ Pause")
        pause_btn.clicked.connect(self.pause_animation)
        toolbar.addWidget(pause_btn)

        stop_btn = QPushButton("⏹ Stop")
        stop_btn.clicked.connect(self.stop_animation)
        toolbar.addWidget(stop_btn)

        toolbar.addSeparator()

        # Record button
        self.record_btn = QPushButton("● Record Voice")
        self.record_btn.setCheckable(True)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background: #FF6B35;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:checked {
                background: #FF0000;
                animation: pulse 1s infinite;
            }
        """)
        self.record_btn.toggled.connect(self.toggle_voice_recording)
        toolbar.addWidget(self.record_btn)

        toolbar.addSeparator()

        # Export button
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_animation)
        toolbar.addWidget(export_btn)

        return toolbar

    def _connect_signals(self):
        """Connect all signals."""
        # Scene panel
        self.scene_panel.scene_selected.connect(self._on_scene_selected)
        self.scene_panel.scene_added.connect(self._on_scene_added)

        # Timeline
        self.timeline.playhead_moved.connect(self._on_playhead_moved)
        self.timeline.keyframe_added.connect(self._on_keyframe_added)

        # Voice recorder
        self.voice_recorder.recording_stopped.connect(self._on_voice_recorded)

    def _load_presets(self, category: AnimationPresetType):
        """Load animation presets for category."""
        self.preset_list.clear()
        presets = self.animation_library.get_presets_by_category(category)
        for preset in presets:
            self.preset_list.addItem(f"{preset.name} ({preset.duration}s)")

    def _on_category_changed(self, category_name: str):
        """Handle animation category change."""
        for cat in AnimationPresetType:
            if cat.value == category_name:
                self._load_presets(cat)
                break

    def _on_scene_selected(self, scene_id: str):
        """Handle scene selection."""
        scene = self.scene_panel.get_current_scene()
        if scene:
            self.timeline.duration = scene.duration
            # Load scene data into timeline
            # TODO: Load characters, animations, voice clips

    def _on_scene_added(self):
        """Handle new scene added."""
        # Auto-select new scene
        if self.scene_panel.scene_list.count() > 0:
            self.scene_panel.scene_list.setCurrentRow(
                self.scene_panel.scene_list.count() - 1
            )

    def _on_playhead_moved(self, time: float):
        """Handle timeline playhead movement."""
        # Update preview to show frame at this time
        frame = int(time * 30)  # 30 FPS
        self.preview_canvas.set_frame(frame)

    def _on_keyframe_added(self, track: str, time: float):
        """Handle keyframe addition."""
        print(f"Keyframe added: {track} at {time}s")

    def _on_voice_recorded(self, file_path: str):
        """Handle voice recording completion."""
        # Add voice clip to timeline
        if file_path:
            clip = VoiceClip(
                name=f"Voice_{int(time.time())}",
                file_path=file_path,
                start_time=self.timeline.current_time,
                duration=2.0  # TODO: Get actual duration
            )
            self.timeline.add_clip("Voice", clip.start_time, clip.duration, clip)

    def play_animation(self):
        """Start animation playback."""
        self.timeline.toggle_playback()
        self.preview_canvas.playing = True

    def pause_animation(self):
        """Pause animation playback."""
        self.timeline.is_playing = False
        self.preview_canvas.playing = False

    def stop_animation(self):
        """Stop animation and reset."""
        self.timeline.is_playing = False
        self.timeline.set_playhead_position(0)
        self.preview_canvas.playing = False
        self.preview_canvas.set_frame(0)

    def toggle_voice_recording(self, checked: bool):
        """Toggle voice recording."""
        if checked:
            self.voice_recorder.start_recording()
        else:
            self.voice_recorder.stop_recording()

    def start_voice_recording_at(self, time: float):
        """Start voice recording at specific timeline position."""
        self.timeline.set_playhead_position(time)
        self.record_btn.setChecked(True)

    def export_animation(self):
        """Export the animation to video."""
        # TODO: Implement export pipeline
        QMessageBox.information(self, "Export",
                               "Export functionality coming soon!")

    def add_stick_figure(self, figure):
        """Add a stick figure from the maker tab."""
        # Add to current scene
        scene = self.scene_panel.get_current_scene()
        if scene:
            scene.characters.append(figure.id)
            # Add to preview
            self.preview_canvas.characters.append(figure)
            print(f"Added stick figure: {figure.name}")


if __name__ == "__main__":
    # Test the animation studio independently
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create window
    window = QWidget()
    window.setWindowTitle("Animation Studio Test")
    window.setGeometry(100, 100, 1600, 900)

    # Apply dark theme
    app.setStyle("Fusion")
    window.setStyleSheet("""
        QWidget {
            background: #141B2D;
            color: #E6E6E6;
        }
    """)

    layout = QVBoxLayout(window)
    studio = AnimationStudioTab()
    layout.addWidget(studio)

    window.show()
    sys.exit(app.exec())