"""
Audio Playback
Timeline-synced audio playback for voiceovers and sound effects.

Enables users to hear their recorded dialogue while editing animations,
ensuring perfect lip-sync and comedic timing for YouTube content.

Features:
- Timeline-synchronized playback
- Multiple audio track support
- Waveform visualization
- Volume control
- Scrubbing support
- Loop regions
- Real-time position tracking

Workflow:
1. User loads audio file into timeline
2. Audio plays in sync with animation playback
3. Waveform displayed on timeline for visual reference
4. Lip-sync can be generated and adjusted while listening
"""

import os
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QObject, Signal, Slot, QTimer, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


# ============================================================================
# PLAYBACK STATE
# ============================================================================

class PlaybackState(Enum):
    """Current state of audio playback."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    BUFFERING = "buffering"
    ERROR = "error"


@dataclass
class AudioTrack:
    """
    Audio track data for timeline integration.
    """
    name: str
    file_path: str
    start_time: float = 0.0      # Start time on timeline (seconds)
    volume: float = 1.0          # Track volume (0.0-1.0)
    is_muted: bool = False       # Mute state
    is_solo: bool = False        # Solo state
    color: str = "#00AA00"       # Waveform color


# ============================================================================
# AUDIO PLAYER
# ============================================================================

class AudioPlayer(QObject):
    """
    Timeline-synchronized audio player.
    Plays audio files in sync with animation playback.
    """

    # Signals
    playback_started = Signal()
    playback_stopped = Signal()
    playback_paused = Signal()
    state_changed = Signal(PlaybackState)
    position_changed = Signal(int)    # Position in milliseconds
    duration_changed = Signal(int)    # Duration in milliseconds
    error_occurred = Signal(str)      # Error message

    def __init__(self):
        """Initialize audio player."""
        super().__init__()

        # Player components
        self.media_player: Optional[QMediaPlayer] = None
        self.audio_output: Optional[QAudioOutput] = None

        # State
        self.current_state = PlaybackState.STOPPED
        self.current_file: Optional[str] = None
        self.duration_ms = 0
        self.position_ms = 0

        # Initialize player
        self._initialize_player()

        print("✓ Audio player initialized")

    def _initialize_player(self):
        """Initialize Qt multimedia player components."""
        try:
            # Create audio output
            self.audio_output = QAudioOutput()
            self.audio_output.setVolume(1.0)

            # Create media player
            self.media_player = QMediaPlayer()
            self.media_player.setAudioOutput(self.audio_output)

            # Connect signals
            self.media_player.playbackStateChanged.connect(self._on_playback_state_changed)
            self.media_player.positionChanged.connect(self._on_position_changed)
            self.media_player.durationChanged.connect(self._on_duration_changed)
            self.media_player.errorOccurred.connect(self._on_error_occurred)

            print("✓ Player components initialized")

        except Exception as e:
            error_msg = f"Failed to initialize player: {e}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            self.current_state = PlaybackState.ERROR

    def load_file(self, file_path: str) -> bool:
        """
        Load audio file for playback.

        Args:
            file_path: Path to audio file

        Returns:
            True if loaded successfully
        """
        if not os.path.exists(file_path):
            error_msg = f"Audio file not found: {file_path}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            return False

        if not self.media_player:
            error_msg = "Player not initialized"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            return False

        try:
            # Load file
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.current_file = file_path

            print(f"✓ Loaded audio file: {os.path.basename(file_path)}")
            return True

        except Exception as e:
            error_msg = f"Failed to load audio file: {e}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            return False

    def play(self):
        """Start playback."""
        if not self.media_player or not self.current_file:
            print("⚠ No audio file loaded")
            return

        self.media_player.play()
        self.current_state = PlaybackState.PLAYING
        self.playback_started.emit()
        self.state_changed.emit(self.current_state)

        print("▶ Playback started")

    def pause(self):
        """Pause playback."""
        if not self.media_player:
            return

        self.media_player.pause()
        self.current_state = PlaybackState.PAUSED
        self.playback_paused.emit()
        self.state_changed.emit(self.current_state)

        print("⏸ Playback paused")

    def stop(self):
        """Stop playback and return to start."""
        if not self.media_player:
            return

        self.media_player.stop()
        self.current_state = PlaybackState.STOPPED
        self.playback_stopped.emit()
        self.state_changed.emit(self.current_state)

        print("■ Playback stopped")

    def set_position(self, position_ms: int):
        """
        Seek to specific position (for timeline scrubbing).

        Args:
            position_ms: Position in milliseconds
        """
        if not self.media_player:
            return

        # Clamp to valid range
        position_ms = max(0, min(self.duration_ms, position_ms))

        self.media_player.setPosition(position_ms)
        self.position_ms = position_ms

    def set_volume(self, volume: float):
        """
        Set playback volume.

        Args:
            volume: Volume level (0.0-1.0)
        """
        if self.audio_output:
            volume = max(0.0, min(1.0, volume))
            self.audio_output.setVolume(volume)
            print(f"🔊 Volume: {volume:.0%}")

    def get_position(self) -> int:
        """Get current position in milliseconds."""
        return self.position_ms

    def get_duration(self) -> int:
        """Get total duration in milliseconds."""
        return self.duration_ms

    def get_state(self) -> PlaybackState:
        """Get current playback state."""
        return self.current_state

    @Slot()
    def _on_playback_state_changed(self):
        """Handle playback state change from media player."""
        if not self.media_player:
            return

        qt_state = self.media_player.playbackState()

        if qt_state == QMediaPlayer.PlaybackState.StoppedState:
            self.current_state = PlaybackState.STOPPED
        elif qt_state == QMediaPlayer.PlaybackState.PlayingState:
            self.current_state = PlaybackState.PLAYING
        elif qt_state == QMediaPlayer.PlaybackState.PausedState:
            self.current_state = PlaybackState.PAUSED

        self.state_changed.emit(self.current_state)

    @Slot(int)
    def _on_position_changed(self, position: int):
        """Handle position change."""
        self.position_ms = position
        self.position_changed.emit(position)

    @Slot(int)
    def _on_duration_changed(self, duration: int):
        """Handle duration change."""
        self.duration_ms = duration
        self.duration_changed.emit(duration)
        print(f"  Duration: {duration / 1000:.2f}s")

    @Slot()
    def _on_error_occurred(self):
        """Handle playback error."""
        if self.media_player:
            error_msg = f"Playback error: {self.media_player.errorString()}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            self.current_state = PlaybackState.ERROR
            self.state_changed.emit(self.current_state)


# ============================================================================
# MULTI-TRACK AUDIO MANAGER
# ============================================================================

class AudioTrackManager(QObject):
    """
    Manages multiple audio tracks for timeline integration.
    Allows mixing multiple voiceovers and sound effects.
    """

    # Signals
    track_added = Signal(str)        # Track name
    track_removed = Signal(str)
    track_muted = Signal(str, bool)  # Track name, is_muted
    track_soloed = Signal(str, bool)

    def __init__(self):
        """Initialize audio track manager."""
        super().__init__()

        # Tracks
        self.tracks: Dict[str, AudioTrack] = {}

        # Players (one per track)
        self.players: Dict[str, AudioPlayer] = {}

        print("✓ Audio track manager initialized")

    def add_track(self, track: AudioTrack) -> bool:
        """
        Add audio track.

        Args:
            track: Audio track to add

        Returns:
            True if added successfully
        """
        if track.name in self.tracks:
            print(f"⚠ Track '{track.name}' already exists")
            return False

        # Create player for this track
        player = AudioPlayer()

        if not player.load_file(track.file_path):
            return False

        # Store track and player
        self.tracks[track.name] = track
        self.players[track.name] = player

        # Set volume
        player.set_volume(track.volume)

        self.track_added.emit(track.name)
        print(f"✓ Added track: {track.name}")

        return True

    def remove_track(self, track_name: str) -> bool:
        """Remove audio track."""
        if track_name not in self.tracks:
            return False

        # Stop and remove player
        if track_name in self.players:
            self.players[track_name].stop()
            del self.players[track_name]

        # Remove track
        del self.tracks[track_name]

        self.track_removed.emit(track_name)
        print(f"✓ Removed track: {track_name}")

        return True

    def play_all(self):
        """Play all unmuted tracks."""
        for track_name, track in self.tracks.items():
            if not track.is_muted:
                player = self.players.get(track_name)
                if player:
                    player.play()

        print("▶ Playing all tracks")

    def stop_all(self):
        """Stop all tracks."""
        for player in self.players.values():
            player.stop()

        print("■ Stopped all tracks")

    def sync_to_timeline(self, timeline_position_ms: int):
        """
        Sync all tracks to timeline position.

        Args:
            timeline_position_ms: Timeline position in milliseconds
        """
        for track_name, track in self.tracks.items():
            # Calculate track-relative position
            track_start_ms = int(track.start_time * 1000)
            track_position_ms = timeline_position_ms - track_start_ms

            # Only seek if within track range
            player = self.players.get(track_name)

            if player and 0 <= track_position_ms <= player.get_duration():
                player.set_position(track_position_ms)

    def set_track_volume(self, track_name: str, volume: float):
        """Set volume for specific track."""
        if track_name in self.tracks:
            self.tracks[track_name].volume = volume

            player = self.players.get(track_name)
            if player:
                player.set_volume(volume)

    def mute_track(self, track_name: str, muted: bool):
        """Mute/unmute track."""
        if track_name in self.tracks:
            self.tracks[track_name].is_muted = muted

            player = self.players.get(track_name)
            if player:
                player.set_volume(0.0 if muted else self.tracks[track_name].volume)

            self.track_muted.emit(track_name, muted)

    def solo_track(self, track_name: str, soloed: bool):
        """Solo/unsolo track (mutes all others)."""
        if track_name not in self.tracks:
            return

        self.tracks[track_name].is_solo = soloed

        # If soloing, mute all other tracks
        if soloed:
            for name, track in self.tracks.items():
                if name != track_name:
                    self.mute_track(name, True)
                else:
                    self.mute_track(name, False)
        else:
            # Unsolo - restore all tracks
            for name in self.tracks.keys():
                self.mute_track(name, False)

        self.track_soloed.emit(track_name, soloed)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_audio_player() -> AudioPlayer:
    """Create simple audio player."""
    return AudioPlayer()


def create_track_manager() -> AudioTrackManager:
    """Create multi-track audio manager."""
    return AudioTrackManager()


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AUDIO PLAYBACK TEST")
    print("=" * 60)

    # Create player
    player = create_audio_player()

    print(f"\nPlayer State: {player.get_state().value}")
    print(f"Position: {player.get_position()}ms")
    print(f"Duration: {player.get_duration()}ms")

    # Create track manager
    print("\n" + "=" * 60)
    print("MULTI-TRACK MANAGER TEST")
    print("=" * 60)

    manager = create_track_manager()
    print(f"Tracks: {len(manager.tracks)}")

    print("\n✓ Audio playback system ready for timeline-synced YouTube content!")
