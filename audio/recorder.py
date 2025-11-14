"""
Audio Recorder
QtMultimedia-based audio recording for voiceovers and sound effects.

This is CRITICAL for YouTube content creation - enables users to record dialogue,
sound effects, and narration for their stick figure fight stories.

Features:
- Real-time audio recording
- Multiple input device support
- WAV/MP3 export formats
- Audio level monitoring
- Recording preview
- Automatic file naming
- Integration with timeline for sync

Workflow:
1. User clicks Record
2. Records voiceover while watching animation
3. Audio saved to project
4. Automatically added to timeline
5. Lip-sync can be generated from recorded audio
"""

import os
from typing import Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot, QTimer, QUrl, QIODevice
from PySide6.QtMultimedia import (
    QMediaRecorder,
    QAudioInput,
    QMediaCaptureSession,
    QMediaFormat
)


# ============================================================================
# RECORDING STATE
# ============================================================================

class RecordingState(Enum):
    """Current state of audio recorder."""
    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class RecordingSettings:
    """
    Audio recording configuration.
    Optimized for voice recording (YouTube dialogue).
    """
    # Format
    file_format: str = "wav"        # "wav", "mp3", "ogg"
    sample_rate: int = 44100        # Hz (CD quality)
    bit_rate: int = 128000          # bits/sec (128 kbps for voice)
    channels: int = 1               # Mono for voice (stereo = 2)

    # Quality
    quality: str = "high"           # "low", "normal", "high", "very_high"

    # Output
    output_directory: str = "audio/recorded"
    auto_generate_filename: bool = True
    filename_prefix: str = "voiceover"

    # Monitoring
    enable_level_monitoring: bool = True
    level_update_interval: int = 50  # ms


# ============================================================================
# AUDIO RECORDER
# ============================================================================

class AudioRecorder(QObject):
    """
    High-level audio recorder for voiceover recording.
    Uses QtMultimedia for cross-platform audio capture.
    """

    # Signals
    recording_started = Signal()
    recording_stopped = Signal(str)      # Emits output file path
    recording_paused = Signal()
    recording_resumed = Signal()
    state_changed = Signal(RecordingState)
    audio_level_changed = Signal(float)  # Audio level (0.0-1.0)
    error_occurred = Signal(str)         # Error message
    duration_changed = Signal(int)       # Duration in milliseconds

    def __init__(self, settings: Optional[RecordingSettings] = None):
        """
        Initialize audio recorder.

        Args:
            settings: Recording settings (uses defaults if None)
        """
        super().__init__()

        self.settings = settings if settings else RecordingSettings()

        # Recorder components
        self.audio_input: Optional[QAudioInput] = None
        self.capture_session: Optional[QMediaCaptureSession] = None
        self.media_recorder: Optional[QMediaRecorder] = None

        # State
        self.current_state = RecordingState.IDLE
        self.current_output_file: Optional[str] = None
        self.recording_start_time = 0
        self.recording_duration = 0

        # Level monitoring
        self.level_timer = QTimer()
        self.level_timer.timeout.connect(self._update_audio_level)
        self.current_level = 0.0

        # Initialize recorder
        self._initialize_recorder()

        print("✓ Audio recorder initialized")

    def _initialize_recorder(self):
        """Initialize Qt multimedia recorder components."""
        try:
            # Create audio input
            self.audio_input = QAudioInput()

            # Create media recorder
            self.media_recorder = QMediaRecorder()

            # Create capture session and connect components
            self.capture_session = QMediaCaptureSession()
            self.capture_session.setAudioInput(self.audio_input)
            self.capture_session.setRecorder(self.media_recorder)

            # Connect signals
            self.media_recorder.recorderStateChanged.connect(self._on_recorder_state_changed)
            self.media_recorder.durationChanged.connect(self._on_duration_changed)
            self.media_recorder.errorOccurred.connect(self._on_error_occurred)

            # Apply settings
            self._apply_settings()

            print("✓ Recorder components initialized")

        except Exception as e:
            error_msg = f"Failed to initialize recorder: {e}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            self.current_state = RecordingState.ERROR

    def _apply_settings(self):
        """Apply recording settings to media recorder."""
        if not self.media_recorder:
            return

        # Set media format
        media_format = QMediaFormat()

        # File format
        if self.settings.file_format == "wav":
            media_format.setFileFormat(QMediaFormat.FileFormat.Wave)
        elif self.settings.file_format == "mp3":
            media_format.setFileFormat(QMediaFormat.FileFormat.MP3)
        elif self.settings.file_format == "ogg":
            media_format.setFileFormat(QMediaFormat.FileFormat.Ogg)

        # Audio codec
        media_format.setAudioCodec(QMediaFormat.AudioCodec.Wave)

        self.media_recorder.setMediaFormat(media_format)

        # Quality settings
        if self.settings.quality == "low":
            self.media_recorder.setQuality(QMediaRecorder.Quality.VeryLowQuality)
        elif self.settings.quality == "normal":
            self.media_recorder.setQuality(QMediaRecorder.Quality.NormalQuality)
        elif self.settings.quality == "high":
            self.media_recorder.setQuality(QMediaRecorder.Quality.HighQuality)
        elif self.settings.quality == "very_high":
            self.media_recorder.setQuality(QMediaRecorder.Quality.VeryHighQuality)

        # Bit rate
        self.media_recorder.setAudioBitRate(self.settings.bit_rate)

        # Sample rate
        self.media_recorder.setAudioSampleRate(self.settings.sample_rate)

        # Channels
        self.media_recorder.setAudioChannelCount(self.settings.channels)

        print(f"✓ Recording settings applied: {self.settings.file_format}, "
              f"{self.settings.sample_rate}Hz, {self.settings.bit_rate}bps")

    def start_recording(self, output_path: Optional[str] = None):
        """
        Start audio recording.

        Args:
            output_path: Output file path (auto-generated if None)
        """
        if self.current_state == RecordingState.RECORDING:
            print("⚠ Already recording")
            return

        if not self.media_recorder:
            error_msg = "Recorder not initialized"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            return

        try:
            # Determine output path
            if output_path:
                self.current_output_file = output_path
            else:
                self.current_output_file = self._generate_output_path()

            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.current_output_file), exist_ok=True)

            # Set output location
            self.media_recorder.setOutputLocation(QUrl.fromLocalFile(self.current_output_file))

            # Start recording
            self.media_recorder.record()

            # Start level monitoring
            if self.settings.enable_level_monitoring:
                self.level_timer.start(self.settings.level_update_interval)

            self.current_state = RecordingState.RECORDING
            self.recording_started.emit()
            self.state_changed.emit(self.current_state)

            print(f"▶ Recording started: {self.current_output_file}")

        except Exception as e:
            error_msg = f"Failed to start recording: {e}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            self.current_state = RecordingState.ERROR
            self.state_changed.emit(self.current_state)

    def stop_recording(self):
        """Stop audio recording."""
        if self.current_state != RecordingState.RECORDING:
            print("⚠ Not currently recording")
            return

        if not self.media_recorder:
            return

        try:
            # Stop recording
            self.media_recorder.stop()

            # Stop level monitoring
            self.level_timer.stop()

            self.current_state = RecordingState.STOPPED
            self.recording_stopped.emit(self.current_output_file)
            self.state_changed.emit(self.current_state)

            print(f"■ Recording stopped: {self.current_output_file}")
            print(f"  Duration: {self.recording_duration / 1000:.2f}s")

            # Reset to idle after brief delay
            QTimer.singleShot(500, self._reset_to_idle)

        except Exception as e:
            error_msg = f"Failed to stop recording: {e}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)

    def pause_recording(self):
        """Pause recording (can be resumed)."""
        if self.current_state != RecordingState.RECORDING:
            return

        if self.media_recorder:
            self.media_recorder.pause()
            self.level_timer.stop()

            self.current_state = RecordingState.PAUSED
            self.recording_paused.emit()
            self.state_changed.emit(self.current_state)

            print("⏸ Recording paused")

    def resume_recording(self):
        """Resume paused recording."""
        if self.current_state != RecordingState.PAUSED:
            return

        if self.media_recorder:
            self.media_recorder.record()

            if self.settings.enable_level_monitoring:
                self.level_timer.start(self.settings.level_update_interval)

            self.current_state = RecordingState.RECORDING
            self.recording_resumed.emit()
            self.state_changed.emit(self.current_state)

            print("▶ Recording resumed")

    def _reset_to_idle(self):
        """Reset recorder to idle state."""
        self.current_state = RecordingState.IDLE
        self.current_output_file = None
        self.recording_duration = 0
        self.current_level = 0.0
        self.state_changed.emit(self.current_state)

    def _generate_output_path(self) -> str:
        """
        Generate automatic output file path.

        Returns:
            Full path to output file
        """
        # Ensure output directory exists
        output_dir = self.settings.output_directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate unique filename
        if self.settings.auto_generate_filename:
            # Find next available number
            counter = 1

            while True:
                filename = f"{self.settings.filename_prefix}_{counter:03d}.{self.settings.file_format}"
                filepath = os.path.join(output_dir, filename)

                if not os.path.exists(filepath):
                    return filepath

                counter += 1

                # Safety check
                if counter > 9999:
                    filename = f"{self.settings.filename_prefix}_temp.{self.settings.file_format}"
                    return os.path.join(output_dir, filename)
        else:
            filename = f"{self.settings.filename_prefix}.{self.settings.file_format}"
            return os.path.join(output_dir, filename)

    def _update_audio_level(self):
        """Update audio level monitoring."""
        if not self.audio_input:
            return

        # Get current volume level
        volume = self.audio_input.volume()

        # Update current level
        self.current_level = volume

        # Emit signal
        self.audio_level_changed.emit(volume)

    @Slot(int)
    def _on_duration_changed(self, duration: int):
        """Handle duration change."""
        self.recording_duration = duration
        self.duration_changed.emit(duration)

    @Slot()
    def _on_recorder_state_changed(self):
        """Handle recorder state change."""
        # State is managed internally, this is for sync
        pass

    @Slot()
    def _on_error_occurred(self):
        """Handle recording error."""
        if self.media_recorder:
            error_msg = f"Recording error: {self.media_recorder.errorString()}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            self.current_state = RecordingState.ERROR
            self.state_changed.emit(self.current_state)

    def get_state(self) -> RecordingState:
        """Get current recording state."""
        return self.current_state

    def get_output_file(self) -> Optional[str]:
        """Get current output file path."""
        return self.current_output_file

    def get_duration(self) -> int:
        """Get recording duration in milliseconds."""
        return self.recording_duration

    def get_audio_level(self) -> float:
        """Get current audio level (0.0-1.0)."""
        return self.current_level

    def set_input_volume(self, volume: float):
        """
        Set input volume (microphone gain).

        Args:
            volume: Volume level (0.0-1.0)
        """
        if self.audio_input:
            self.audio_input.setVolume(max(0.0, min(1.0, volume)))
            print(f"🎤 Input volume: {volume:.0%}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_voice_recorder(output_dir: str = "audio/voiceovers") -> AudioRecorder:
    """
    Create recorder optimized for voice recording (YouTube dialogue).

    Args:
        output_dir: Directory to save recordings

    Returns:
        Configured AudioRecorder
    """
    settings = RecordingSettings()
    settings.output_directory = output_dir
    settings.filename_prefix = "voiceover"
    settings.file_format = "wav"      # Uncompressed for editing
    settings.sample_rate = 44100
    settings.bit_rate = 128000
    settings.channels = 1             # Mono for voice
    settings.quality = "high"

    return AudioRecorder(settings)


def create_sfx_recorder(output_dir: str = "audio/sound_effects") -> AudioRecorder:
    """
    Create recorder for sound effects.

    Args:
        output_dir: Directory to save recordings

    Returns:
        Configured AudioRecorder
    """
    settings = RecordingSettings()
    settings.output_directory = output_dir
    settings.filename_prefix = "sfx"
    settings.file_format = "wav"
    settings.sample_rate = 44100
    settings.bit_rate = 192000        # Higher quality for SFX
    settings.channels = 2             # Stereo for effects
    settings.quality = "very_high"

    return AudioRecorder(settings)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AUDIO RECORDER TEST")
    print("=" * 60)

    # Create recorder
    recorder = create_voice_recorder()

    print(f"\nRecorder State: {recorder.get_state().value}")
    print(f"Output Format: {recorder.settings.file_format}")
    print(f"Sample Rate: {recorder.settings.sample_rate} Hz")
    print(f"Bit Rate: {recorder.settings.bit_rate} bps")
    print(f"Channels: {recorder.settings.channels} ({'Mono' if recorder.settings.channels == 1 else 'Stereo'})")

    print("\n✓ Audio recorder ready for YouTube voiceover recording!")
