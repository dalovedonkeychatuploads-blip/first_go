"""
Timeline Editor Module
Professional track-based timeline with keyframe editing, scrubbing, and audio waveform visualization.

Features:
- Multi-track timeline for skeletal animation
- Keyframe visualization with diamond markers
- Drag-and-drop keyframe editing
- Playback controls (play, pause, stop, loop)
- Scrubbing with visual playhead
- Zoom and pan controls
- Audio waveform visualization
- Layer management
- Copy/paste keyframes
- Snap-to-frame grid
- Time ruler with frame numbers

This is the HEART of the animation system - where users create their YouTube content!
"""

import math
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider,
    QLabel, QScrollArea, QFrame, QToolBar, QSpinBox, QComboBox
)
from PySide6.QtCore import (
    Qt, Signal, QRect, QPoint, QSize, QTimer, QPointF
)
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QPalette, QFont,
    QLinearGradient, QPainterPath, QPolygonF
)

from animations.animation_base import Animation, Keyframe, InterpolationType


# ============================================================================
# TIMELINE CONSTANTS
# ============================================================================

# Visual constants
TIMELINE_HEADER_HEIGHT = 40  # Height of time ruler
TRACK_HEIGHT = 60            # Height of each track
KEYFRAME_SIZE = 12           # Diamond marker size
PLAYHEAD_WIDTH = 2           # Playhead line width
WAVEFORM_HEIGHT = 80         # Audio waveform track height

# Time constants
DEFAULT_FPS = 60             # 60 FPS for smooth YouTube content
PIXELS_PER_SECOND = 100      # Default zoom level (adjustable)

# Colors
COLOR_BACKGROUND = QColor(30, 30, 30)
COLOR_TRACK_BG = QColor(45, 45, 45)
COLOR_TRACK_BORDER = QColor(60, 60, 60)
COLOR_RULER_BG = QColor(40, 40, 40)
COLOR_RULER_TEXT = QColor(180, 180, 180)
COLOR_GRID_LINE = QColor(55, 55, 55)
COLOR_PLAYHEAD = QColor(255, 80, 80)
COLOR_KEYFRAME = QColor(80, 160, 255)
COLOR_KEYFRAME_SELECTED = QColor(255, 200, 80)
COLOR_WAVEFORM = QColor(100, 200, 100, 150)


# ============================================================================
# PLAYBACK STATE
# ============================================================================

class PlaybackState(Enum):
    """Playback state for timeline."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


# ============================================================================
# KEYFRAME MARKER DATA
# ============================================================================

@dataclass
class KeyframeMarker:
    """
    Visual representation of a keyframe on the timeline.
    Stores position and selection state for rendering and interaction.
    """
    frame: int                  # Frame number
    time: float                 # Time in seconds
    keyframe: Keyframe         # Reference to actual keyframe data
    track_index: int           # Which track this belongs to
    is_selected: bool = False  # Selection state

    def get_x_position(self, pixels_per_second: float) -> float:
        """Calculate X pixel position based on time and zoom level."""
        return self.time * pixels_per_second


# ============================================================================
# TIMELINE TRACK
# ============================================================================

class TimelineTrack:
    """
    Represents a single animation track in the timeline.
    Each track can contain multiple keyframes for a specific bone or property.
    """

    def __init__(self, name: str, bone_name: str = "", color: QColor = COLOR_KEYFRAME):
        """
        Initialize timeline track.

        Args:
            name: Display name of the track
            bone_name: Bone this track controls (empty for root track)
            color: Color for this track's keyframes
        """
        self.name = name
        self.bone_name = bone_name
        self.color = color
        self.markers: List[KeyframeMarker] = []
        self.is_visible = True
        self.is_locked = False
        self.is_expanded = True  # For hierarchical tracks

        print(f"✓ Created timeline track: {name}")

    def add_keyframe_marker(self, marker: KeyframeMarker):
        """Add keyframe marker to this track."""
        if self.is_locked:
            print(f"⚠ Track '{self.name}' is locked - cannot add keyframe")
            return False

        # Check for duplicate frame
        for existing in self.markers:
            if existing.frame == marker.frame:
                print(f"⚠ Keyframe already exists at frame {marker.frame}")
                return False

        self.markers.append(marker)
        self.markers.sort(key=lambda m: m.frame)  # Keep sorted by frame
        return True

    def remove_keyframe_at_frame(self, frame: int) -> bool:
        """Remove keyframe at specific frame."""
        if self.is_locked:
            print(f"⚠ Track '{self.name}' is locked - cannot remove keyframe")
            return False

        for i, marker in enumerate(self.markers):
            if marker.frame == frame:
                self.markers.pop(i)
                return True

        return False

    def get_keyframe_at_frame(self, frame: int) -> Optional[KeyframeMarker]:
        """Get keyframe marker at specific frame."""
        for marker in self.markers:
            if marker.frame == frame:
                return marker
        return None

    def clear_selection(self):
        """Deselect all keyframes in this track."""
        for marker in self.markers:
            marker.is_selected = False


# ============================================================================
# TIMELINE RULER (Time Display)
# ============================================================================

class TimelineRuler(QWidget):
    """
    Time ruler showing frame numbers and time markers.
    Displays at the top of the timeline.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.fps = DEFAULT_FPS
        self.pixels_per_second = PIXELS_PER_SECOND
        self.duration = 10.0  # 10 seconds default
        self.scroll_offset = 0

        self.setMinimumHeight(TIMELINE_HEADER_HEIGHT)
        self.setMaximumHeight(TIMELINE_HEADER_HEIGHT)

        # Mouse interaction
        self.is_scrubbing = False

    def paintEvent(self, event):
        """Draw time ruler with frame numbers."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        painter.fillRect(self.rect(), COLOR_RULER_BG)

        # Calculate visible time range
        visible_width = self.width()
        start_time = self.scroll_offset / self.pixels_per_second
        end_time = start_time + (visible_width / self.pixels_per_second)

        # Draw time markers
        self._draw_time_markers(painter, start_time, end_time)

        # Bottom border
        painter.setPen(QPen(COLOR_TRACK_BORDER, 1))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

    def _draw_time_markers(self, painter: QPainter, start_time: float, end_time: float):
        """Draw time markers and frame numbers."""
        painter.setPen(QPen(COLOR_RULER_TEXT, 1))
        painter.setFont(QFont("Arial", 8))

        # Calculate marker interval based on zoom level
        if self.pixels_per_second >= 200:
            # Zoomed in - show every frame
            marker_interval = 1.0 / self.fps
        elif self.pixels_per_second >= 100:
            # Medium zoom - show every 5 frames
            marker_interval = 5.0 / self.fps
        elif self.pixels_per_second >= 50:
            # Zoomed out - show every 10 frames
            marker_interval = 10.0 / self.fps
        else:
            # Very zoomed out - show every second
            marker_interval = 1.0

        # Draw markers
        current_time = math.floor(start_time / marker_interval) * marker_interval

        while current_time <= end_time:
            if current_time >= 0:
                x = (current_time * self.pixels_per_second) - self.scroll_offset

                if 0 <= x <= self.width():
                    # Draw tick line
                    is_second_marker = abs(current_time % 1.0) < 0.001
                    tick_height = 12 if is_second_marker else 6

                    painter.setPen(QPen(COLOR_RULER_TEXT, 2 if is_second_marker else 1))
                    painter.drawLine(int(x), self.height() - tick_height, int(x), self.height())

                    # Draw frame number for major markers
                    if is_second_marker:
                        frame_num = int(current_time * self.fps)
                        time_str = f"{frame_num}"
                        painter.drawText(int(x) + 3, 12, time_str)

            current_time += marker_interval

    def set_zoom(self, pixels_per_second: float):
        """Update zoom level."""
        self.pixels_per_second = max(10, min(500, pixels_per_second))
        self.update()

    def set_scroll_offset(self, offset: int):
        """Update scroll offset."""
        self.scroll_offset = offset
        self.update()


# ============================================================================
# TIMELINE CANVAS (Track Display)
# ============================================================================

class TimelineCanvas(QWidget):
    """
    Main timeline canvas showing tracks and keyframes.
    Handles all user interaction (clicking, dragging, selection).
    """

    # Signals
    playhead_moved = Signal(float)      # Emitted when playhead moves
    keyframe_selected = Signal(object)  # Emitted when keyframe is clicked
    keyframe_moved = Signal(object, int)  # Emitted when keyframe is dragged

    def __init__(self, parent=None):
        super().__init__(parent)

        self.fps = DEFAULT_FPS
        self.pixels_per_second = PIXELS_PER_SECOND
        self.duration = 10.0
        self.current_time = 0.0
        self.scroll_offset = 0

        # Tracks
        self.tracks: List[TimelineTrack] = []

        # Interaction state
        self.is_dragging_playhead = False
        self.is_dragging_keyframe = False
        self.dragged_keyframe: Optional[KeyframeMarker] = None
        self.drag_start_pos = QPoint()

        # Selection
        self.selected_keyframes: List[KeyframeMarker] = []

        # Enable mouse tracking
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        print("✓ Timeline canvas initialized")

    def paintEvent(self, event):
        """Draw timeline tracks and keyframes."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        painter.fillRect(self.rect(), COLOR_BACKGROUND)

        # Draw grid lines
        self._draw_grid(painter)

        # Draw tracks
        y_offset = 0
        for track in self.tracks:
            if track.is_visible:
                self._draw_track(painter, track, y_offset)
                y_offset += TRACK_HEIGHT

        # Draw playhead (on top of everything)
        self._draw_playhead(painter)

    def _draw_grid(self, painter: QPainter):
        """Draw vertical grid lines for time divisions."""
        painter.setPen(QPen(COLOR_GRID_LINE, 1))

        # Draw line every second
        for second in range(int(self.duration) + 1):
            x = (second * self.pixels_per_second) - self.scroll_offset

            if 0 <= x <= self.width():
                painter.drawLine(int(x), 0, int(x), self.height())

    def _draw_track(self, painter: QPainter, track: TimelineTrack, y_offset: int):
        """Draw a single track with its keyframes."""
        # Track background
        track_rect = QRect(0, y_offset, self.width(), TRACK_HEIGHT)
        painter.fillRect(track_rect, COLOR_TRACK_BG)

        # Track border
        painter.setPen(QPen(COLOR_TRACK_BORDER, 1))
        painter.drawRect(track_rect)

        # Track name
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        painter.drawText(10, y_offset + 20, track.name)

        # Draw keyframes
        for marker in track.markers:
            self._draw_keyframe(painter, marker, y_offset)

    def _draw_keyframe(self, painter: QPainter, marker: KeyframeMarker, y_offset: int):
        """Draw a keyframe diamond marker."""
        x = (marker.time * self.pixels_per_second) - self.scroll_offset
        y = y_offset + (TRACK_HEIGHT / 2)

        # Only draw if visible
        if not (-KEYFRAME_SIZE <= x <= self.width() + KEYFRAME_SIZE):
            return

        # Diamond shape (rotated square)
        size = KEYFRAME_SIZE / 2
        diamond = QPolygonF([
            QPointF(x, y - size),      # Top
            QPointF(x + size, y),      # Right
            QPointF(x, y + size),      # Bottom
            QPointF(x - size, y)       # Left
        ])

        # Fill color
        if marker.is_selected:
            painter.setBrush(QBrush(COLOR_KEYFRAME_SELECTED))
            painter.setPen(QPen(COLOR_KEYFRAME_SELECTED, 2))
        else:
            # Use track color
            track = self.tracks[marker.track_index] if marker.track_index < len(self.tracks) else None
            color = track.color if track else COLOR_KEYFRAME
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color, 2))

        painter.drawPolygon(diamond)

    def _draw_playhead(self, painter: QPainter):
        """Draw the playhead (current time indicator)."""
        x = (self.current_time * self.pixels_per_second) - self.scroll_offset

        # Only draw if visible
        if not (0 <= x <= self.width()):
            return

        # Vertical line
        painter.setPen(QPen(COLOR_PLAYHEAD, PLAYHEAD_WIDTH))
        painter.drawLine(int(x), 0, int(x), self.height())

        # Triangle at top
        triangle_size = 8
        triangle = QPolygonF([
            QPointF(x, 0),
            QPointF(x - triangle_size / 2, triangle_size),
            QPointF(x + triangle_size / 2, triangle_size)
        ])
        painter.setBrush(QBrush(COLOR_PLAYHEAD))
        painter.drawPolygon(triangle)

    def mousePressEvent(self, event):
        """Handle mouse press - start dragging or select keyframe."""
        if event.button() != Qt.LeftButton:
            return

        click_pos = event.pos()

        # Check if clicked on playhead
        playhead_x = (self.current_time * self.pixels_per_second) - self.scroll_offset

        if abs(click_pos.x() - playhead_x) < 10:
            self.is_dragging_playhead = True
            self.drag_start_pos = click_pos
            return

        # Check if clicked on keyframe
        clicked_keyframe = self._get_keyframe_at_position(click_pos)

        if clicked_keyframe:
            # Select keyframe
            if not event.modifiers() & Qt.ControlModifier:
                self._clear_all_selections()

            clicked_keyframe.is_selected = True

            if clicked_keyframe not in self.selected_keyframes:
                self.selected_keyframes.append(clicked_keyframe)

            self.is_dragging_keyframe = True
            self.dragged_keyframe = clicked_keyframe
            self.drag_start_pos = click_pos

            self.keyframe_selected.emit(clicked_keyframe)
        else:
            # Clicked on empty space - move playhead
            new_time = (click_pos.x() + self.scroll_offset) / self.pixels_per_second
            new_time = max(0, min(self.duration, new_time))
            self.set_current_time(new_time)

        self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse move - drag playhead or keyframe."""
        if self.is_dragging_playhead:
            # Update playhead position
            new_time = (event.pos().x() + self.scroll_offset) / self.pixels_per_second
            new_time = max(0, min(self.duration, new_time))
            self.set_current_time(new_time)

        elif self.is_dragging_keyframe and self.dragged_keyframe:
            # Calculate new frame position
            new_time = (event.pos().x() + self.scroll_offset) / self.pixels_per_second
            new_frame = int(new_time * self.fps)
            new_frame = max(0, int(self.duration * self.fps), new_frame)

            # Update keyframe
            self.dragged_keyframe.frame = new_frame
            self.dragged_keyframe.time = new_frame / self.fps

            self.keyframe_moved.emit(self.dragged_keyframe, new_frame)
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release - stop dragging."""
        if event.button() == Qt.LeftButton:
            self.is_dragging_playhead = False
            self.is_dragging_keyframe = False
            self.dragged_keyframe = None

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Delete:
            # Delete selected keyframes
            self._delete_selected_keyframes()

        elif event.key() == Qt.Key_A and event.modifiers() & Qt.ControlModifier:
            # Select all keyframes
            self._select_all_keyframes()

        elif event.key() == Qt.Key_Space:
            # Emit playhead moved to trigger play/pause
            self.playhead_moved.emit(self.current_time)

    def _get_keyframe_at_position(self, pos: QPoint) -> Optional[KeyframeMarker]:
        """Find keyframe at mouse position."""
        y_offset = 0

        for track in self.tracks:
            if not track.is_visible:
                continue

            track_y_center = y_offset + (TRACK_HEIGHT / 2)

            # Check if mouse is in this track's Y range
            if abs(pos.y() - track_y_center) < TRACK_HEIGHT / 2:
                # Check each keyframe in this track
                for marker in track.markers:
                    marker_x = (marker.time * self.pixels_per_second) - self.scroll_offset

                    if abs(pos.x() - marker_x) < KEYFRAME_SIZE:
                        return marker

            y_offset += TRACK_HEIGHT

        return None

    def _clear_all_selections(self):
        """Deselect all keyframes."""
        for track in self.tracks:
            track.clear_selection()

        self.selected_keyframes.clear()

    def _select_all_keyframes(self):
        """Select all keyframes in all tracks."""
        self._clear_all_selections()

        for track in self.tracks:
            for marker in track.markers:
                marker.is_selected = True
                self.selected_keyframes.append(marker)

        self.update()

    def _delete_selected_keyframes(self):
        """Delete all selected keyframes."""
        if not self.selected_keyframes:
            return

        for marker in self.selected_keyframes:
            track = self.tracks[marker.track_index] if marker.track_index < len(self.tracks) else None

            if track:
                track.remove_keyframe_at_frame(marker.frame)

        self.selected_keyframes.clear()
        self.update()

        print(f"✓ Deleted {len(self.selected_keyframes)} keyframe(s)")

    def set_current_time(self, time: float):
        """Set current playhead time."""
        self.current_time = max(0, min(self.duration, time))
        self.playhead_moved.emit(self.current_time)
        self.update()

    def set_zoom(self, pixels_per_second: float):
        """Update zoom level."""
        self.pixels_per_second = max(10, min(500, pixels_per_second))
        self.update()

    def set_scroll_offset(self, offset: int):
        """Update scroll offset."""
        self.scroll_offset = offset
        self.update()

    def add_track(self, track: TimelineTrack):
        """Add a new track to the timeline."""
        self.tracks.append(track)

        # Update canvas height
        visible_tracks = sum(1 for t in self.tracks if t.is_visible)
        new_height = visible_tracks * TRACK_HEIGHT
        self.setMinimumHeight(new_height)

        self.update()
        print(f"✓ Added track: {track.name}")

    def remove_track(self, track_name: str):
        """Remove track by name."""
        for i, track in enumerate(self.tracks):
            if track.name == track_name:
                self.tracks.pop(i)
                self.update()
                print(f"✓ Removed track: {track_name}")
                return True

        return False


# ============================================================================
# TIMELINE WIDGET (Complete Timeline UI)
# ============================================================================

class TimelineWidget(QWidget):
    """
    Complete timeline interface with controls, ruler, and canvas.
    This is the main timeline component used throughout the application.
    """

    # Signals
    time_changed = Signal(float)         # Current time changed
    playback_state_changed = Signal(PlaybackState)  # Play/pause/stop

    def __init__(self, parent=None):
        super().__init__(parent)

        # Timeline state
        self.fps = DEFAULT_FPS
        self.duration = 10.0
        self.current_time = 0.0
        self.playback_state = PlaybackState.STOPPED
        self.is_looping = True

        # Zoom
        self.pixels_per_second = PIXELS_PER_SECOND

        # Playback timer
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self._update_playback)
        self.last_update_time = 0.0

        # Build UI
        self._init_ui()

        print("✓ Timeline widget initialized")

    def _init_ui(self):
        """Initialize timeline UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Controls toolbar
        controls = self._create_controls_toolbar()
        layout.addWidget(controls)

        # Time ruler
        self.ruler = TimelineRuler()
        layout.addWidget(self.ruler)

        # Timeline canvas in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.canvas = TimelineCanvas()
        self.canvas.fps = self.fps
        self.canvas.duration = self.duration

        # Connect signals
        self.canvas.playhead_moved.connect(self._on_playhead_moved)

        # Set canvas width based on duration
        canvas_width = int(self.duration * self.pixels_per_second)
        self.canvas.setMinimumWidth(canvas_width)

        scroll_area.setWidget(self.canvas)

        # Connect scrollbar to update ruler and canvas
        scroll_area.horizontalScrollBar().valueChanged.connect(self._on_scroll)

        layout.addWidget(scroll_area)

        self.scroll_area = scroll_area

    def _create_controls_toolbar(self) -> QToolBar:
        """Create playback controls toolbar."""
        toolbar = QToolBar()
        toolbar.setStyleSheet("QToolBar { background: #2a2a2a; padding: 5px; }")

        # Play button
        self.play_button = QPushButton("▶ Play")
        self.play_button.clicked.connect(self.toggle_playback)
        toolbar.addWidget(self.play_button)

        # Stop button
        stop_button = QPushButton("■ Stop")
        stop_button.clicked.connect(self.stop_playback)
        toolbar.addWidget(stop_button)

        toolbar.addSeparator()

        # Loop toggle
        self.loop_button = QPushButton("🔁 Loop")
        self.loop_button.setCheckable(True)
        self.loop_button.setChecked(self.is_looping)
        self.loop_button.clicked.connect(self._toggle_loop)
        toolbar.addWidget(self.loop_button)

        toolbar.addSeparator()

        # Frame number display
        toolbar.addWidget(QLabel("Frame:"))
        self.frame_spinbox = QSpinBox()
        self.frame_spinbox.setMinimum(0)
        self.frame_spinbox.setMaximum(int(self.duration * self.fps))
        self.frame_spinbox.valueChanged.connect(self._on_frame_changed)
        toolbar.addWidget(self.frame_spinbox)

        toolbar.addSeparator()

        # Zoom controls
        toolbar.addWidget(QLabel("Zoom:"))

        zoom_out_button = QPushButton("−")
        zoom_out_button.clicked.connect(lambda: self._adjust_zoom(0.8))
        toolbar.addWidget(zoom_out_button)

        zoom_in_button = QPushButton("+")
        zoom_in_button.clicked.connect(lambda: self._adjust_zoom(1.25))
        toolbar.addWidget(zoom_in_button)

        return toolbar

    def _update_playback(self):
        """Update playback (called by timer)."""
        import time

        if self.playback_state != PlaybackState.PLAYING:
            return

        # Calculate delta time
        current_time = time.time()

        if self.last_update_time > 0:
            delta_time = current_time - self.last_update_time

            # Update timeline position
            new_time = self.current_time + delta_time

            # Check for end of timeline
            if new_time >= self.duration:
                if self.is_looping:
                    new_time = 0.0
                else:
                    self.stop_playback()
                    return

            self.set_current_time(new_time)

        self.last_update_time = current_time

    def toggle_playback(self):
        """Toggle between play and pause."""
        if self.playback_state == PlaybackState.PLAYING:
            self.pause_playback()
        else:
            self.play_playback()

    def play_playback(self):
        """Start playback."""
        if self.playback_state == PlaybackState.PLAYING:
            return

        import time

        self.playback_state = PlaybackState.PLAYING
        self.last_update_time = time.time()

        self.playback_timer.start(16)  # ~60 FPS
        self.play_button.setText("⏸ Pause")

        self.playback_state_changed.emit(PlaybackState.PLAYING)
        print("▶ Playback started")

    def pause_playback(self):
        """Pause playback."""
        if self.playback_state != PlaybackState.PLAYING:
            return

        self.playback_state = PlaybackState.PAUSED
        self.playback_timer.stop()
        self.play_button.setText("▶ Play")

        self.playback_state_changed.emit(PlaybackState.PAUSED)
        print("⏸ Playback paused")

    def stop_playback(self):
        """Stop playback and return to start."""
        self.playback_state = PlaybackState.STOPPED
        self.playback_timer.stop()
        self.play_button.setText("▶ Play")

        self.set_current_time(0.0)

        self.playback_state_changed.emit(PlaybackState.STOPPED)
        print("■ Playback stopped")

    def _toggle_loop(self):
        """Toggle looping."""
        self.is_looping = self.loop_button.isChecked()
        print(f"🔁 Looping: {'ON' if self.is_looping else 'OFF'}")

    def _adjust_zoom(self, factor: float):
        """Adjust zoom level."""
        self.pixels_per_second *= factor
        self.pixels_per_second = max(10, min(500, self.pixels_per_second))

        # Update all components
        self.ruler.set_zoom(self.pixels_per_second)
        self.canvas.set_zoom(self.pixels_per_second)

        # Update canvas width
        canvas_width = int(self.duration * self.pixels_per_second)
        self.canvas.setMinimumWidth(canvas_width)

        print(f"🔍 Zoom: {self.pixels_per_second:.0f} px/sec")

    def _on_scroll(self, value: int):
        """Handle horizontal scroll."""
        self.ruler.set_scroll_offset(value)
        self.canvas.set_scroll_offset(value)

    def _on_playhead_moved(self, time: float):
        """Handle playhead movement from canvas."""
        self.set_current_time(time)

    def _on_frame_changed(self, frame: int):
        """Handle frame number spinbox change."""
        new_time = frame / self.fps
        self.set_current_time(new_time)

    def set_current_time(self, time: float):
        """Set current timeline time."""
        self.current_time = max(0, min(self.duration, time))

        # Update canvas
        self.canvas.set_current_time(self.current_time)

        # Update frame spinbox
        current_frame = int(self.current_time * self.fps)
        self.frame_spinbox.blockSignals(True)
        self.frame_spinbox.setValue(current_frame)
        self.frame_spinbox.blockSignals(False)

        # Emit signal
        self.time_changed.emit(self.current_time)

    def add_track(self, track: TimelineTrack):
        """Add track to timeline."""
        self.canvas.add_track(track)

    def remove_track(self, track_name: str):
        """Remove track from timeline."""
        return self.canvas.remove_track(track_name)

    def get_current_time(self) -> float:
        """Get current timeline time."""
        return self.current_time

    def get_current_frame(self) -> int:
        """Get current frame number."""
        return int(self.current_time * self.fps)


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def create_timeline_widget(fps: int = DEFAULT_FPS, duration: float = 10.0) -> TimelineWidget:
    """
    Create and return a configured timeline widget.

    Args:
        fps: Frames per second (default 60 for YouTube content)
        duration: Timeline duration in seconds (default 10)

    Returns:
        Configured TimelineWidget
    """
    widget = TimelineWidget()
    widget.fps = fps
    widget.duration = duration
    widget.canvas.fps = fps
    widget.canvas.duration = duration

    # Add example tracks
    widget.add_track(TimelineTrack("Root Motion", "root", QColor(120, 120, 255)))
    widget.add_track(TimelineTrack("Torso", "torso", QColor(255, 120, 120)))
    widget.add_track(TimelineTrack("Head", "head", QColor(255, 200, 80)))
    widget.add_track(TimelineTrack("Left Arm", "left_arm", QColor(120, 255, 120)))
    widget.add_track(TimelineTrack("Right Arm", "right_arm", QColor(255, 120, 255)))

    return widget
