"""
Comprehensive Error Handling System
Friendly, actionable error messages for all failure scenarios.

Handles:
- File I/O errors (save/load)
- GPU/OpenGL errors
- Audio device errors
- Video export errors (ffmpeg)
- Animation data errors
- Memory/performance errors

Philosophy: No cryptic error messages! Every error should:
1. Explain WHAT went wrong in plain English
2. Explain WHY it happened
3. Suggest HOW to fix it
4. Provide recovery options when possible
"""

import sys
import traceback
import logging
from typing import Optional, Callable, Any
from enum import Enum
from pathlib import Path
from functools import wraps

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap


# ============================================================================
# ERROR CATEGORIES
# ============================================================================

class ErrorCategory(Enum):
    """Categories of errors for appropriate handling."""
    FILE_IO = "file_io"           # File read/write errors
    GPU_RENDER = "gpu_render"     # OpenGL/GPU errors
    AUDIO = "audio"               # Audio recording/playback errors
    VIDEO_EXPORT = "video_export" # ffmpeg export errors
    ANIMATION = "animation"       # Animation data errors
    MEMORY = "memory"             # Out of memory errors
    NETWORK = "network"           # Network/download errors
    UNKNOWN = "unknown"           # Uncategorized errors


class ErrorSeverity(Enum):
    """Severity levels for error handling."""
    INFO = "info"           # Informational, no action needed
    WARNING = "warning"     # Warning, user should be aware
    ERROR = "error"         # Error, feature failed but app continues
    CRITICAL = "critical"   # Critical, app may need to close


# ============================================================================
# FRIENDLY ERROR MESSAGES
# ============================================================================

class FriendlyErrorMessage:
    """
    Container for user-friendly error information.
    Transforms technical errors into actionable messages.
    """

    def __init__(
        self,
        title: str,
        message: str,
        details: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        suggestions: list[str],
        recovery_actions: Optional[dict[str, Callable]] = None
    ):
        """
        Initialize friendly error message.

        Args:
            title: Short error title (e.g., "File Not Found")
            message: User-friendly explanation
            details: Technical details for debugging
            category: Error category
            severity: Error severity
            suggestions: List of suggestions to fix the error
            recovery_actions: Dict of {action_name: callback_function}
        """
        self.title = title
        self.message = message
        self.details = details
        self.category = category
        self.severity = severity
        self.suggestions = suggestions
        self.recovery_actions = recovery_actions or {}


# ============================================================================
# ERROR MESSAGE TEMPLATES
# ============================================================================

def get_file_not_found_error(file_path: str) -> FriendlyErrorMessage:
    """Create friendly message for file not found error."""
    return FriendlyErrorMessage(
        title="File Not Found",
        message=f"Couldn't find the file:\n{file_path}",
        details=f"FileNotFoundError: {file_path}",
        category=ErrorCategory.FILE_IO,
        severity=ErrorSeverity.ERROR,
        suggestions=[
            "• Check if the file path is correct",
            "• Make sure the file hasn't been moved or deleted",
            "• Try using 'Browse' to select the file again",
            "• Check file permissions"
        ]
    )


def get_file_save_error(file_path: str, reason: str) -> FriendlyErrorMessage:
    """Create friendly message for file save error."""
    return FriendlyErrorMessage(
        title="Save Failed",
        message=f"Couldn't save the file:\n{file_path}\n\nReason: {reason}",
        details=f"Save error: {file_path} - {reason}",
        category=ErrorCategory.FILE_IO,
        severity=ErrorSeverity.ERROR,
        suggestions=[
            "• Check if you have permission to write to this location",
            "• Make sure the disk isn't full",
            "• Try saving to a different location",
            "• Close other programs that might be using the file"
        ]
    )


def get_gpu_error(error_msg: str) -> FriendlyErrorMessage:
    """Create friendly message for GPU/OpenGL error."""
    return FriendlyErrorMessage(
        title="Graphics Error",
        message="Encountered a graphics rendering error.\n\n"
                "Don't worry! We'll switch to a simpler rendering mode.",
        details=f"OpenGL error: {error_msg}",
        category=ErrorCategory.GPU_RENDER,
        severity=ErrorSeverity.WARNING,
        suggestions=[
            "• Update your graphics drivers",
            "• Try switching to Vector rendering mode (View menu)",
            "• Reduce the number of characters in the scene",
            "• Close other 3D applications"
        ]
    )


def get_ffmpeg_not_found_error() -> FriendlyErrorMessage:
    """Create friendly message for ffmpeg not found."""
    return FriendlyErrorMessage(
        title="FFmpeg Not Installed",
        message="FFmpeg is required to export videos, but it's not installed.\n\n"
                "FFmpeg is a free video encoding tool used by professionals worldwide.",
        details="FFmpeg executable not found in system PATH",
        category=ErrorCategory.VIDEO_EXPORT,
        severity=ErrorSeverity.ERROR,
        suggestions=[
            "• Download FFmpeg from: https://ffmpeg.org/download.html",
            "• On Windows, install with: choco install ffmpeg",
            "• On Mac, install with: brew install ffmpeg",
            "• Make sure FFmpeg is in your system PATH",
            "• Restart the application after installing"
        ]
    )


def get_video_export_error(error_msg: str) -> FriendlyErrorMessage:
    """Create friendly message for video export error."""
    return FriendlyErrorMessage(
        title="Video Export Failed",
        message="Couldn't export the video.\n\n"
                "This usually happens when FFmpeg encounters an encoding issue.",
        details=f"Export error: {error_msg}",
        category=ErrorCategory.VIDEO_EXPORT,
        severity=ErrorSeverity.ERROR,
        suggestions=[
            "• Try a different video codec (H.264 is most compatible)",
            "• Reduce the resolution or bitrate",
            "• Make sure you have enough disk space",
            "• Check the console output for FFmpeg errors",
            "• Try exporting a shorter animation first"
        ]
    )


def get_audio_device_error(error_msg: str) -> FriendlyErrorMessage:
    """Create friendly message for audio device error."""
    return FriendlyErrorMessage(
        title="Audio Device Error",
        message="Couldn't access the audio device.\n\n"
                "This might be because another application is using it.",
        details=f"Audio error: {error_msg}",
        category=ErrorCategory.AUDIO,
        severity=ErrorSeverity.WARNING,
        suggestions=[
            "• Close other applications using audio (Zoom, Discord, etc.)",
            "• Check if your microphone is properly connected",
            "• Try selecting a different audio device",
            "• Check Windows sound settings",
            "• You can still create animations without audio!"
        ]
    )


def get_memory_error(item_count: int) -> FriendlyErrorMessage:
    """Create friendly message for out of memory error."""
    return FriendlyErrorMessage(
        title="Out of Memory",
        message=f"Too many items in the scene ({item_count})!\n\n"
                "Your computer is running low on memory.",
        details=f"MemoryError: Too many objects ({item_count})",
        category=ErrorCategory.MEMORY,
        severity=ErrorSeverity.ERROR,
        suggestions=[
            "• Remove some characters from the scene",
            "• Simplify weapon geometry",
            "• Close other applications to free up memory",
            "• Switch to Vector rendering mode (uses less memory)",
            "• Save your work and restart the application"
        ]
    )


def get_animation_data_error(error_msg: str) -> FriendlyErrorMessage:
    """Create friendly message for animation data error."""
    return FriendlyErrorMessage(
        title="Invalid Animation Data",
        message="The animation data is corrupted or invalid.\n\n"
                "This might be from an older version or a manual edit.",
        details=f"Animation error: {error_msg}",
        category=ErrorCategory.ANIMATION,
        severity=ErrorSeverity.ERROR,
        suggestions=[
            "• Try loading a different animation file",
            "• Check if the file was manually edited",
            "• Export the animation again from the source",
            "• Create a new animation from scratch",
            "• If this is a Spine JSON file, validate it first"
        ]
    )


def get_spine_import_error(error_msg: str) -> FriendlyErrorMessage:
    """Create friendly message for Spine JSON import error."""
    return FriendlyErrorMessage(
        title="Spine Import Failed",
        message="Couldn't import the Spine JSON file.\n\n"
                "Make sure it's a valid Spine 4.0 format file.",
        details=f"Spine import error: {error_msg}",
        category=ErrorCategory.ANIMATION,
        severity=ErrorSeverity.ERROR,
        suggestions=[
            "• Verify the JSON file is valid (check for syntax errors)",
            "• Make sure it's exported from Spine 4.0+",
            "• Try exporting from Spine again",
            "• Check if all required bones are present",
            "• Look for the specific error in the console output"
        ]
    )


# ============================================================================
# ERROR HANDLER
# ============================================================================

class ErrorHandler:
    """
    Centralized error handling system.
    Logs errors, shows friendly messages, and tracks error patterns.
    """

    def __init__(self):
        """Initialize error handler with logging."""
        # Setup logging
        self.logger = logging.getLogger("StickManAnimator")
        self.logger.setLevel(logging.DEBUG)

        # File handler for error log
        log_path = Path("errors.log")
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.WARNING)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler for debugging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Error tracking
        self.error_count = 0
        self.error_history = []

        print("[OK] Error handler initialized")
        print(f"  Error log: {log_path.absolute()}")

    def handle_error(
        self,
        error: Exception,
        friendly_message: Optional[FriendlyErrorMessage] = None,
        show_dialog: bool = True
    ):
        """
        Handle an error with friendly message.

        Args:
            error: The exception that occurred
            friendly_message: Optional friendly message override
            show_dialog: Whether to show error dialog to user
        """
        # Increment error count
        self.error_count += 1

        # Get friendly message if not provided
        if friendly_message is None:
            friendly_message = self._create_friendly_message(error)

        # Log the error
        self._log_error(error, friendly_message)

        # Track in history
        self.error_history.append({
            'error': error,
            'message': friendly_message,
            'count': self.error_count
        })

        # Show dialog if requested
        if show_dialog:
            self._show_error_dialog(friendly_message)

        # Print to console
        print(f"[ERROR] {friendly_message.title}: {friendly_message.message}")

    def _create_friendly_message(self, error: Exception) -> FriendlyErrorMessage:
        """Create friendly message from exception."""
        error_type = type(error).__name__
        error_str = str(error)

        # File errors
        if isinstance(error, FileNotFoundError):
            return get_file_not_found_error(error_str)
        elif isinstance(error, PermissionError):
            return get_file_save_error(error_str, "Permission denied")
        elif isinstance(error, IOError):
            return get_file_save_error(error_str, error_str)

        # Memory errors
        elif isinstance(error, MemoryError):
            return get_memory_error(0)

        # Generic error
        else:
            return FriendlyErrorMessage(
                title=f"{error_type}",
                message=f"An unexpected error occurred:\n{error_str}",
                details=traceback.format_exc(),
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.ERROR,
                suggestions=[
                    "• Try restarting the application",
                    "• Check the error log for details",
                    "• Save your work frequently",
                    "• Report this bug if it happens again"
                ]
            )

    def _log_error(self, error: Exception, friendly_message: FriendlyErrorMessage):
        """Log error to file and console."""
        # Log based on severity
        if friendly_message.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(
                f"{friendly_message.title}: {friendly_message.message}\n"
                f"Details: {friendly_message.details}"
            )
        elif friendly_message.severity == ErrorSeverity.ERROR:
            self.logger.error(
                f"{friendly_message.title}: {friendly_message.message}\n"
                f"Details: {friendly_message.details}"
            )
        elif friendly_message.severity == ErrorSeverity.WARNING:
            self.logger.warning(
                f"{friendly_message.title}: {friendly_message.message}"
            )
        else:
            self.logger.info(friendly_message.message)

    def _show_error_dialog(self, friendly_message: FriendlyErrorMessage):
        """Show error dialog to user."""
        dialog = ErrorDialog(friendly_message)
        dialog.exec()


# ============================================================================
# ERROR DIALOG
# ============================================================================

class ErrorDialog(QDialog):
    """
    User-friendly error dialog with suggestions and recovery options.
    """

    def __init__(self, error_message: FriendlyErrorMessage):
        super().__init__()

        self.error_message = error_message

        self.setWindowTitle(error_message.title)
        self.setMinimumWidth(500)
        self.setModal(True)

        self._build_ui()

    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout()

        # Icon and message
        header_layout = QHBoxLayout()

        # Icon based on severity
        icon_label = QLabel()
        if self.error_message.severity == ErrorSeverity.CRITICAL:
            icon_label.setText("🛑")
        elif self.error_message.severity == ErrorSeverity.ERROR:
            icon_label.setText("❌")
        elif self.error_message.severity == ErrorSeverity.WARNING:
            icon_label.setText("⚠️")
        else:
            icon_label.setText("ℹ️")

        icon_label.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(icon_label)

        # Message
        message_label = QLabel(self.error_message.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 12px;")
        header_layout.addWidget(message_label, 1)

        layout.addLayout(header_layout)

        # Suggestions
        if self.error_message.suggestions:
            layout.addSpacing(10)
            suggestions_label = QLabel("<b>How to fix this:</b>")
            layout.addWidget(suggestions_label)

            suggestions_text = "\n".join(self.error_message.suggestions)
            suggestions_widget = QLabel(suggestions_text)
            suggestions_widget.setWordWrap(True)
            suggestions_widget.setStyleSheet(
                "background-color: #2b2b2b; "
                "padding: 10px; "
                "border-radius: 5px;"
            )
            layout.addWidget(suggestions_widget)

        # Technical details (collapsible)
        layout.addSpacing(10)
        details_button = QPushButton("Show Technical Details")
        details_button.clicked.connect(self._toggle_details)
        layout.addWidget(details_button)

        self.details_text = QTextEdit()
        self.details_text.setPlainText(self.error_message.details)
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        self.details_text.setVisible(False)
        layout.addWidget(self.details_text)

        # Recovery actions
        if self.error_message.recovery_actions:
            layout.addSpacing(10)
            actions_layout = QHBoxLayout()

            for action_name, action_callback in self.error_message.recovery_actions.items():
                action_button = QPushButton(action_name)
                action_button.clicked.connect(action_callback)
                actions_layout.addWidget(action_button)

            layout.addLayout(actions_layout)

        # OK button
        layout.addSpacing(10)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _toggle_details(self):
        """Toggle technical details visibility."""
        self.details_text.setVisible(not self.details_text.isVisible())


# ============================================================================
# DECORATORS FOR SAFE EXECUTION
# ============================================================================

def safe_execute(
    friendly_message: Optional[FriendlyErrorMessage] = None,
    show_dialog: bool = True,
    return_on_error: Any = None
):
    """
    Decorator to wrap functions with error handling.

    Args:
        friendly_message: Optional friendly message to show
        show_dialog: Whether to show error dialog
        return_on_error: Value to return if error occurs

    Example:
        @safe_execute(show_dialog=True)
        def save_file(path):
            # ... file saving code ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get global error handler
                handler = get_global_error_handler()
                handler.handle_error(e, friendly_message, show_dialog)
                return return_on_error
        return wrapper
    return decorator


def fallback_on_error(fallback_func: Callable):
    """
    Decorator to provide fallback function on error.

    Args:
        fallback_func: Function to call if main function fails

    Example:
        @fallback_on_error(load_default_settings)
        def load_settings(path):
            # ... loading code ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"[WARNING] {func.__name__} failed, using fallback")
                handler = get_global_error_handler()
                handler.handle_error(e, show_dialog=False)
                return fallback_func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# GLOBAL ERROR HANDLER
# ============================================================================

_global_error_handler: Optional[ErrorHandler] = None


def get_global_error_handler() -> ErrorHandler:
    """Get or create global error handler."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def setup_global_exception_handler():
    """Setup global exception handler for uncaught exceptions."""
    def exception_hook(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't catch Ctrl+C
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Handle the error
        handler = get_global_error_handler()

        friendly_message = FriendlyErrorMessage(
            title="Unexpected Error",
            message=f"An unexpected error occurred:\n{exc_value}\n\n"
                    "The application will try to recover.",
            details=''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)),
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.CRITICAL,
            suggestions=[
                "• Save your work immediately",
                "• Try restarting the application",
                "• Check the error log for details",
                "• Report this bug if it happens repeatedly"
            ]
        )

        handler.handle_error(exc_value, friendly_message, show_dialog=True)

    sys.excepthook = exception_hook


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ERROR HANDLING SYSTEM TEST")
    print("=" * 60)

    # Initialize handler
    handler = get_global_error_handler()

    # Test file error
    print("\n1. Testing file not found error...")
    try:
        with open("nonexistent_file.txt", "r") as f:
            pass
    except Exception as e:
        handler.handle_error(e, show_dialog=False)

    # Test GPU error
    print("\n2. Testing GPU error...")
    gpu_error = get_gpu_error("GL_INVALID_OPERATION at glDrawArrays")
    handler.handle_error(Exception("GPU error"), gpu_error, show_dialog=False)

    # Test ffmpeg error
    print("\n3. Testing ffmpeg not found...")
    ffmpeg_error = get_ffmpeg_not_found_error()
    handler.handle_error(Exception("FFmpeg error"), ffmpeg_error, show_dialog=False)

    # Test memory error
    print("\n4. Testing memory error...")
    memory_error = get_memory_error(1000)
    handler.handle_error(Exception("Memory error"), memory_error, show_dialog=False)

    # Test decorator
    print("\n5. Testing safe_execute decorator...")

    @safe_execute(show_dialog=False, return_on_error="FALLBACK_VALUE")
    def risky_function():
        """Function that might fail."""
        raise ValueError("This is a test error")

    result = risky_function()
    print(f"   Returned: {result}")

    print(f"\n[OK] All tests completed!")
    print(f"  Total errors handled: {handler.error_count}")
    print(f"  Error log: errors.log")
    print("\nError handling system ready to catch all failures!")
