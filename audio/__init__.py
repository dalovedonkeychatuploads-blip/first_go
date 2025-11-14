"""
Audio Package
Recording and playback system using QtMultimedia.
Supports voiceover recording and timeline-synced audio for YouTube storytelling.
"""

from .recorder import AudioRecorder
from .playback import AudioPlayback

__all__ = ['AudioRecorder', 'AudioPlayback']
