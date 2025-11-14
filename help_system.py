"""
Interactive Help and Documentation System
Context-sensitive help, tooltips, and tutorials for YouTube content creation workflow.

Features:
- Tooltip system for all UI elements
- Interactive tutorials (step-by-step walkthroughs)
- Context-sensitive help
- Quick tips and shortcuts
- Video workflow guides
- First-time user onboarding

Philosophy: Every user should feel confident creating YouTube content!
"""

from typing import Optional, List, Callable
from enum import Enum
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QWidget, QTabWidget, QListWidget, QListWidgetItem,
    QScrollArea, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QPoint, QRect
from PySide6.QtGui import QFont, QPalette, QColor, QPainter, QLinearGradient


# ============================================================================
# HELP TOPICS
# ============================================================================

class HelpTopic(Enum):
    """Available help topics."""
    OVERVIEW = "overview"
    WEAPON_CREATOR = "weapon_creator"
    RIGGING = "rigging"
    ANIMATION = "animation"
    TIMELINE = "timeline"
    CAMERA = "camera"
    RENDERING = "rendering"
    AUDIO = "audio"
    VIDEO_EXPORT = "video_export"
    SHORTCUTS = "shortcuts"
    TROUBLESHOOTING = "troubleshooting"


@dataclass
class HelpContent:
    """Help content for a specific topic."""
    title: str
    summary: str
    sections: List[tuple[str, str]]  # (section_title, section_content)
    tips: List[str]
    shortcuts: List[tuple[str, str]]  # (key, description)


# ============================================================================
# HELP CONTENT DATABASE
# ============================================================================

HELP_DATABASE = {
    HelpTopic.OVERVIEW: HelpContent(
        title="Welcome to Stick Man Animation Editor!",
        summary="A professional tool for creating YouTube stick figure fight content.",
        sections=[
            ("What is this?", """
This is a complete animation studio designed specifically for creating
YouTube stick figure fight videos. Think of it as "Blender for stick figures"!

You can:
• Design custom weapons with flame effects
• Rig and animate stick figure characters
• Create multi-character fight scenes
• Add camera movements and shake effects
• Export professional 1080p/4K videos for YouTube
            """),
            ("The 3-Tab Workflow", """
Tab 1: 🗡 Weapon Creator
- Design weapons (swords, maces, crossbows)
- Add procedural flame effects
- Export weapons for use in animations

Tab 2: 🦴 Rigging & Animation
- Rig stick figures with inverse kinematics
- Create keyframe animations
- Use preset dances (Floss, Carlton, Moonwalk, etc.)
- Test animations in real-time

Tab 3: 🎬 Animation Studio
- Multi-character scenes
- Camera controls (follow, shake, pan)
- Timeline editing
- Video export to YouTube
            """),
            ("Getting Started", """
1. Go to Tab 1 and create a weapon (or skip this step)
2. Go to Tab 2 and create an animation
3. Go to Tab 3 to compose your full scene
4. Export to video for YouTube upload!

It's that simple! Check the tutorials for detailed walkthroughs.
            """)
        ],
        tips=[
            "Press Ctrl+E to export video at any time",
            "Use Vector mode for editing, HD mode for export",
            "Save your work frequently with Ctrl+S",
            "The Timeline is your best friend - learn to love it!"
        ],
        shortcuts=[
            ("Ctrl+N", "New Project"),
            ("Ctrl+S", "Save Project"),
            ("Ctrl+E", "Export Video"),
            ("Space", "Play/Pause Animation"),
            ("Ctrl+Z", "Undo"),
            ("Ctrl+Y", "Redo")
        ]
    ),

    HelpTopic.WEAPON_CREATOR: HelpContent(
        title="Weapon Creator (Tab 1)",
        summary="Design AAA-quality weapons with procedural geometry and flame effects.",
        sections=[
            ("Available Weapons", """
• Sword - Classic knight's sword
• Katana - Japanese curved blade
• Mace - Spiked medieval mace
• Maul - Two-handed hammer
• Crossbow - Ranged weapon with bolt

Each weapon has professionally designed geometry with proper proportions.
            """),
            ("Flame Effects", """
Weapons can have procedural flame effects:

• Enable/disable flames
• Adjust intensity (0.0 - 2.0)
• Change colors (red, blue, green, purple)
• Real-time GLSL shader rendering

Flames use Simplex noise for realistic animation!
            """),
            ("Exporting Weapons", """
1. Design your weapon
2. Add flame effects if desired
3. Click "Export Weapon"
4. Your weapon is now available in Tab 2 and Tab 3!

Weapons are saved to the assets/weapons/ folder.
            """)
        ],
        tips=[
            "Start with the Sword - it's the most versatile",
            "Blue flames look amazing for ice/magic themes",
            "Crossbows don't need flame effects usually",
            "Experiment with intensity values between 0.5 and 1.5"
        ],
        shortcuts=[
            ("1-5", "Switch between weapon types"),
            ("F", "Toggle flames"),
            ("[/]", "Adjust flame intensity"),
            ("C", "Cycle flame colors")
        ]
    ),

    HelpTopic.TIMELINE: HelpContent(
        title="Timeline System",
        summary="Professional multi-track timeline for keyframe animation editing.",
        sections=[
            ("Understanding the Timeline", """
The timeline is where you create animations frame-by-frame.

Key concepts:
• Time flows left to right
• Each track represents a bone or property
• Diamond markers are keyframes
• Blue line is the playhead (current time)

Think of it like a video editor timeline!
            """),
            ("Working with Keyframes", """
Adding keyframes:
1. Move playhead to desired time
2. Adjust character pose
3. Click "Add Keyframe" (or press K)

Editing keyframes:
• Click and drag diamonds to move them
• Right-click to delete
• Shift+click to select multiple
• Interpolation types: Linear, Ease In/Out, Bezier

The animation system automatically interpolates between keyframes!
            """),
            ("Playback Controls", """
▶ Play - Start playing the animation
■ Stop - Stop and return to start
⏸ Pause - Pause at current time

Scrubbing:
• Click anywhere on the ruler to jump to that time
• Drag the playhead for fine control
• Use arrow keys to step frame-by-frame

Loop mode: Animation repeats automatically
            """),
            ("Zoom and Pan", """
Timeline is fully zoomable:

Zoom: Mouse wheel or +/- keys
Pan: Click and drag the timeline background
Reset: Home key

Zoom levels: 10x to 500x pixels per second
Find the zoom level that works best for your animation!
            """)
        ],
        tips=[
            "Start with fewer keyframes - you can always add more",
            "Use Ease In/Out for smooth, natural movements",
            "Step interpolation is perfect for robotic moves",
            "Zoom in close when fine-tuning timing",
            "Save versions as you work - try different timings!"
        ],
        shortcuts=[
            ("Space", "Play/Pause"),
            ("K", "Add Keyframe"),
            ("Delete", "Delete Selected Keyframe"),
            ("+/-", "Zoom Timeline"),
            ("Arrow Keys", "Step Frame by Frame"),
            ("Home", "Reset Zoom")
        ]
    ),

    HelpTopic.ANIMATION: HelpContent(
        title="Animation System",
        summary="Create smooth character animations with keyframes and preset dances.",
        sections=[
            ("Keyframe Animation", """
Keyframe animation is the foundation of all movement:

1. Posing: Adjust bones to create a pose
2. Keyframing: Save that pose at a specific time
3. Interpolation: The system fills in the frames between keyframes

This is the same technique used in professional 3D animation!
            """),
            ("Interpolation Types", """
Different interpolation types create different feels:

• LINEAR - Constant speed (robotic, mechanical)
• EASE_IN - Starts slow, speeds up (falling objects)
• EASE_OUT - Starts fast, slows down (coming to rest)
• EASE_IN_OUT - Smooth start and end (natural movement)
• BEZIER - Full control with custom curves (advanced)
• STEP - No interpolation (instant change)

Experiment to find what looks best!
            """),
            ("Preset Animations", """
We've included 5 iconic dances ready to use:

• Floss - Fortnite's famous arm-swing dance
• Carlton - Fresh Prince's signature move
• Take the L - Cheeky taunt dance
• Moonwalk - Michael Jackson's smooth slide
• Dab - Classic celebration pose

These are perfect for:
- Learning how animations work
- Quick character personality
- Victory/taunt animations in fight scenes
            """),
            ("Inverse Kinematics (IK)", """
IK makes animation easier by automatically calculating bone rotations:

Two-Bone IK:
- Perfect for arms and legs
- Just position the hand/foot, bones follow
- Example: Character reaching for an object

CCD (Cyclic Coordinate Descent):
- Advanced multi-bone IK
- Good for tentacles, tails, spine

Look-at IK:
- Makes bones face a target
- Perfect for head tracking, aiming weapons
            """)
        ],
        tips=[
            "Watch reference videos on YouTube for fight choreography",
            "Exaggerate movements - subtle doesn't read well on screen",
            "Add 'anticipation' before big movements (wind-up)",
            "Follow-through makes movements feel less robotic",
            "Squash and stretch adds energy to impacts"
        ],
        shortcuts=[
            ("K", "Add Keyframe"),
            ("Ctrl+K", "Add Keyframe All Bones"),
            ("R", "Rotate Bone Mode"),
            ("G", "Grab/Move Mode"),
            ("Alt+A", "Play Animation"),
            ("Shift+D", "Duplicate Keyframes")
        ]
    ),

    HelpTopic.VIDEO_EXPORT: HelpContent(
        title="Video Export for YouTube",
        summary="Export professional 1080p/4K videos optimized for YouTube upload.",
        sections=[
            ("Export Settings", """
Resolution Options:
• 720p (1280x720) - HD, smaller file size
• 1080p (1920x1080) - Full HD, recommended
• 1440p (2560x1440) - 2K, high quality
• 4K (3840x2160) - Ultra HD, maximum quality

Frame Rate:
• 24 FPS - Cinematic feel
• 30 FPS - Standard YouTube
• 60 FPS - Smooth action (recommended for fights!)

Codec:
• H.264 - Universal compatibility (recommended)
• H.265 - Better compression, smaller files
• VP9 - Google's codec (WebM format)
            """),
            ("Quality Presets", """
• DRAFT - Fast export for previewing (low quality)
• GOOD - Balanced quality and speed
• HIGH - High quality, slower export
• YOUTUBE - Optimized for YouTube (recommended!)
• MAXIMUM - Best possible quality (very slow)

For YouTube uploads, use YOUTUBE or HIGH preset.
            """),
            ("Export Process", """
1. Click "Export Video" (Ctrl+E)
2. Choose output file name
3. Select quality preset (YOUTUBE recommended)
4. Click "Export"
5. Wait for encoding (watch progress bar)
6. Done! Upload to YouTube!

Export uses FFmpeg for professional encoding.
The first export will check if FFmpeg is installed.
            """),
            ("FFmpeg Installation", """
FFmpeg is a free, professional video encoder.

Windows:
1. Download from https://ffmpeg.org/download.html
2. Or install via: choco install ffmpeg
3. Restart the application

Mac:
brew install ffmpeg

Linux:
sudo apt install ffmpeg

The application will guide you if FFmpeg is missing!
            """),
            ("YouTube Upload Tips", """
After exporting:

1. Title: Make it catchy! "Stick Figure Fight Scene"
2. Description: Explain your animation style
3. Tags: "stick figure", "animation", "fight scene"
4. Thumbnail: Use a cool frame from your video
5. Category: Film & Animation

Upload in 1080p 60fps for best results!
            """)
        ],
        tips=[
            "Always export a draft version first to check timing",
            "1080p 60fps is the sweet spot for YouTube",
            "Higher bitrate = larger file but better quality",
            "GPU acceleration (NVENC) makes exports much faster",
            "Keep source files - you might want to re-export later"
        ],
        shortcuts=[
            ("Ctrl+E", "Export Video"),
            ("Ctrl+Shift+E", "Quick Export (last settings)")
        ]
    ),

    HelpTopic.SHORTCUTS: HelpContent(
        title="Keyboard Shortcuts",
        summary="Speed up your workflow with keyboard shortcuts.",
        sections=[
            ("File Operations", """
Ctrl+N - New Project
Ctrl+O - Open Project
Ctrl+S - Save Project
Ctrl+Shift+S - Save As
Ctrl+E - Export Video
Ctrl+Q - Quit
            """),
            ("Edit Operations", """
Ctrl+Z - Undo
Ctrl+Y - Redo
Ctrl+C - Copy
Ctrl+V - Paste
Ctrl+X - Cut
Delete - Delete Selected
            """),
            ("Playback", """
Space - Play/Pause
Home - Go to Start
End - Go to End
Arrow Left/Right - Step Frame
K - Add Keyframe
            """),
            ("View", """
+/- - Zoom In/Out
0 - Reset Zoom
F - Frame Selected
A - Frame All
Tab - Switch Tabs
            """),
            ("Tools", """
R - Rotate Mode
G - Grab/Move Mode
S - Scale Mode
Ctrl+R - Record Audio
Ctrl+T - Toggle Timeline
            """)
        ],
        tips=[
            "Learn 5 shortcuts a week - you'll be a pro in no time!",
            "Space bar is your best friend for quick playback",
            "Ctrl+S after every major change - save often!",
            "Use Tab to quickly switch between workflow tabs"
        ],
        shortcuts=[]  # This is the shortcuts page itself
    ),

    HelpTopic.TROUBLESHOOTING: HelpContent(
        title="Troubleshooting",
        summary="Solutions to common problems.",
        sections=[
            ("Performance Issues", """
If the app feels slow:

1. Switch to Vector rendering mode (View menu)
2. Reduce number of characters in scene
3. Lower animation frame rate to 30 FPS
4. Close other applications
5. Update graphics drivers
6. Check Performance Optimizer for recommendations

The app targets 60 FPS on RTX 3060M.
            """),
            ("Export Failures", """
If video export fails:

1. Make sure FFmpeg is installed
2. Try H.264 codec instead of H.265
3. Lower resolution or bitrate
4. Check available disk space
5. Try a shorter animation first
6. Look at console output for error details

See error message suggestions for specific fixes!
            """),
            ("Graphics Errors", """
If you see graphics glitches:

1. Update GPU drivers
2. Switch to Vector mode
3. Restart the application
4. Reduce MSAA quality (HD mode)
5. Disable GPU acceleration

The app will automatically fall back to safe mode.
            """),
            ("Animation Issues", """
If animations look wrong:

1. Check keyframe interpolation types
2. Verify keyframes are at correct times
3. Make sure all required bones have keyframes
4. Try resetting the animation
5. Check if IK solvers are configured correctly

Use the Timeline zoom to fine-tune timing!
            """),
            ("Audio Problems", """
If audio recording fails:

1. Close other apps using microphone (Zoom, Discord)
2. Check Windows sound settings
3. Try different audio device
4. Restart the application
5. You can still make videos without audio!

Audio is optional - great animations work without it!
            """)
        ],
        tips=[
            "Check errors.log file for detailed error information",
            "Most issues are solved by updating graphics drivers",
            "Save backup copies before major changes",
            "Join the community Discord for help (coming soon!)"
        ],
        shortcuts=[]
    )
}


# ============================================================================
# TOOLTIP SYSTEM
# ============================================================================

class SmartTooltip:
    """
    Enhanced tooltip system with rich formatting.
    """

    @staticmethod
    def set_tooltip(widget: QWidget, text: str, shortcut: Optional[str] = None):
        """
        Set tooltip on a widget with optional keyboard shortcut.

        Args:
            widget: Widget to add tooltip to
            text: Tooltip text
            shortcut: Optional keyboard shortcut (e.g., "Ctrl+S")
        """
        if shortcut:
            tooltip = f"{text}\n\n<b>Shortcut:</b> {shortcut}"
        else:
            tooltip = text

        widget.setToolTip(tooltip)
        widget.setToolTipDuration(5000)  # 5 seconds


# ============================================================================
# HELP DIALOG
# ============================================================================

class HelpDialog(QDialog):
    """
    Interactive help browser with searchable topics.
    """

    def __init__(self, initial_topic: Optional[HelpTopic] = None):
        super().__init__()

        self.setWindowTitle("Stick Man Animation Editor - Help")
        self.setMinimumSize(900, 600)
        self.setModal(False)  # Allow working while help is open

        self._build_ui()

        # Show initial topic
        if initial_topic:
            self._show_topic(initial_topic)
        else:
            self._show_topic(HelpTopic.OVERVIEW)

    def _build_ui(self):
        """Build the help dialog UI."""
        layout = QHBoxLayout()

        # Left sidebar - topic list
        sidebar = self._create_sidebar()
        layout.addWidget(sidebar, 1)

        # Right content area
        self.content_area = self._create_content_area()
        layout.addWidget(self.content_area, 3)

        self.setLayout(layout)

    def _create_sidebar(self) -> QWidget:
        """Create topic sidebar."""
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()

        # Title
        title = QLabel("Help Topics")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        sidebar_layout.addWidget(title)

        # Topic list
        self.topic_list = QListWidget()
        self.topic_list.addItems([
            "📚 Overview",
            "🗡 Weapon Creator",
            "🦴 Rigging",
            "🎬 Animation",
            "⏱ Timeline",
            "📷 Camera",
            "🎨 Rendering",
            "🎵 Audio",
            "📹 Video Export",
            "⌨️ Shortcuts",
            "🔧 Troubleshooting"
        ])
        self.topic_list.currentRowChanged.connect(self._on_topic_selected)
        sidebar_layout.addWidget(self.topic_list)

        # Quick tips checkbox
        self.show_tips_checkbox = QCheckBox("Show Quick Tips")
        self.show_tips_checkbox.setChecked(True)
        sidebar_layout.addWidget(self.show_tips_checkbox)

        sidebar.setLayout(sidebar_layout)
        sidebar.setMaximumWidth(250)

        return sidebar

    def _create_content_area(self) -> QWidget:
        """Create content display area."""
        content_widget = QWidget()
        content_layout = QVBoxLayout()

        # Scrollable content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        scroll_area.setWidget(self.content_text)

        content_layout.addWidget(scroll_area)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        content_layout.addLayout(button_layout)

        content_widget.setLayout(content_layout)
        return content_widget

    def _on_topic_selected(self, index: int):
        """Handle topic selection."""
        topic_map = [
            HelpTopic.OVERVIEW,
            HelpTopic.WEAPON_CREATOR,
            HelpTopic.RIGGING,
            HelpTopic.ANIMATION,
            HelpTopic.TIMELINE,
            HelpTopic.CAMERA,
            HelpTopic.RENDERING,
            HelpTopic.AUDIO,
            HelpTopic.VIDEO_EXPORT,
            HelpTopic.SHORTCUTS,
            HelpTopic.TROUBLESHOOTING
        ]

        if 0 <= index < len(topic_map):
            self._show_topic(topic_map[index])

    def _show_topic(self, topic: HelpTopic):
        """Display help content for a topic."""
        content = HELP_DATABASE.get(topic)
        if not content:
            return

        # Build HTML content
        html = f"<h1>{content.title}</h1>"
        html += f"<p><i>{content.summary}</i></p>"
        html += "<hr>"

        # Sections
        for section_title, section_content in content.sections:
            html += f"<h2>{section_title}</h2>"
            html += f"<p>{section_content.strip()}</p>"

        # Tips
        if content.tips and self.show_tips_checkbox.isChecked():
            html += "<hr>"
            html += "<h2>💡 Quick Tips</h2>"
            html += "<ul>"
            for tip in content.tips:
                html += f"<li>{tip}</li>"
            html += "</ul>"

        # Shortcuts
        if content.shortcuts:
            html += "<hr>"
            html += "<h2>⌨️ Keyboard Shortcuts</h2>"
            html += "<table style='width:100%'>"
            for key, description in content.shortcuts:
                html += f"<tr><td><b>{key}</b></td><td>{description}</td></tr>"
            html += "</table>"

        self.content_text.setHtml(html)
        self.content_text.verticalScrollBar().setValue(0)  # Scroll to top


# ============================================================================
# TUTORIAL SYSTEM
# ============================================================================

@dataclass
class TutorialStep:
    """Single step in a tutorial."""
    title: str
    instruction: str
    highlight_widget: Optional[str] = None  # Widget to highlight
    action_required: Optional[str] = None   # Action user must perform


class Tutorial:
    """Interactive step-by-step tutorial."""

    def __init__(self, name: str, steps: List[TutorialStep]):
        self.name = name
        self.steps = steps
        self.current_step = 0
        self.completed = False

    def get_current_step(self) -> Optional[TutorialStep]:
        """Get current tutorial step."""
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None

    def next_step(self):
        """Advance to next step."""
        self.current_step += 1
        if self.current_step >= len(self.steps):
            self.completed = True

    def previous_step(self):
        """Go back to previous step."""
        if self.current_step > 0:
            self.current_step -= 1

    def reset(self):
        """Reset tutorial to beginning."""
        self.current_step = 0
        self.completed = False


# ============================================================================
# QUICK TIP SYSTEM
# ============================================================================

class QuickTipDialog(QDialog):
    """
    Quick tip popup that shows helpful hints.
    """

    def __init__(self, tip_text: str):
        super().__init__()

        self.setWindowTitle("💡 Quick Tip")
        self.setModal(False)
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Icon and tip
        tip_layout = QHBoxLayout()

        icon_label = QLabel("💡")
        icon_label.setStyleSheet("font-size: 32px;")
        tip_layout.addWidget(icon_label)

        tip_label = QLabel(tip_text)
        tip_label.setWordWrap(True)
        tip_layout.addWidget(tip_label, 1)

        layout.addLayout(tip_layout)

        # Don't show again checkbox
        self.dont_show_checkbox = QCheckBox("Don't show tips")
        layout.addWidget(self.dont_show_checkbox)

        # OK button
        ok_button = QPushButton("Got it!")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)

        # Auto-close after 10 seconds
        QTimer.singleShot(10000, self.accept)


QUICK_TIPS = [
    "Press Space to quickly play/pause your animation!",
    "Use Vector mode while editing, HD mode for final export.",
    "Zoom the timeline with mouse wheel for precise keyframe editing.",
    "Exaggerate movements - they look better on camera!",
    "Save often with Ctrl+S - don't lose your work!",
    "The Floss animation is perfect for victory celebrations!",
    "Try the camera shake effect for impact punches!",
    "Export a draft version first to check your timing.",
    "60 FPS makes fight scenes look incredibly smooth!",
    "Add anticipation before big movements for better feel.",
]


# ============================================================================
# FIRST-TIME USER WELCOME
# ============================================================================

class WelcomeDialog(QDialog):
    """
    Welcome dialog for first-time users.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Welcome to Stick Man Animation Editor!")
        self.setMinimumSize(600, 400)
        self.setModal(True)

        self._build_ui()

    def _build_ui(self):
        """Build welcome UI."""
        layout = QVBoxLayout()

        # Title
        title = QLabel("🎬 Welcome to Stick Man Animation Editor!")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Create professional stick figure fight videos for YouTube!")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Quick start guide
        guide_text = QLabel("""
<h3>Quick Start Guide:</h3>

<p><b>1. Design Weapons</b> (Tab 1)<br>
Create cool weapons with flame effects</p>

<p><b>2. Create Animations</b> (Tab 2)<br>
Rig characters and make them move</p>

<p><b>3. Compose Your Scene</b> (Tab 3)<br>
Multi-character fights with camera controls</p>

<p><b>4. Export to Video</b><br>
1080p 60fps ready for YouTube upload!</p>

<hr>

<p><i>Tip: Press F1 anytime to open the help system!</i></p>
        """)
        guide_text.setWordWrap(True)
        layout.addWidget(guide_text)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        show_tutorial_button = QPushButton("Show Tutorial")
        show_tutorial_button.clicked.connect(self._show_tutorial)
        button_layout.addWidget(show_tutorial_button)

        start_button = QPushButton("Let's Create!")
        start_button.clicked.connect(self.accept)
        start_button.setDefault(True)
        button_layout.addWidget(start_button)

        layout.addLayout(button_layout)

        # Don't show again
        self.dont_show_checkbox = QCheckBox("Don't show this again")
        layout.addWidget(self.dont_show_checkbox)

        self.setLayout(layout)

    def _show_tutorial(self):
        """Show interactive tutorial."""
        self.accept()
        # TODO: Launch interactive tutorial
        print("[INFO] Tutorial system coming soon!")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    print("=" * 60)
    print("HELP SYSTEM TEST")
    print("=" * 60)

    app = QApplication(sys.argv)

    # Test help dialog
    print("\n1. Testing help dialog...")
    help_dialog = HelpDialog(HelpTopic.OVERVIEW)
    help_dialog.show()

    # Test quick tip
    print("\n2. Testing quick tip...")
    tip_dialog = QuickTipDialog(QUICK_TIPS[0])
    QTimer.singleShot(1000, tip_dialog.show)

    # Test welcome dialog
    print("\n3. Testing welcome dialog...")
    welcome_dialog = WelcomeDialog()
    QTimer.singleShot(2000, welcome_dialog.show)

    print("\n[OK] Help system initialized!")
    print(f"  {len(HELP_DATABASE)} help topics available")
    print(f"  {len(QUICK_TIPS)} quick tips loaded")
    print("\nPress F1 in the app to open help!")

    sys.exit(app.exec())
