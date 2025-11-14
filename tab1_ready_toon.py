"""
Tab 1: Ready The Toon - Complete Character Creation Interface
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QFrame, QSlider, QComboBox,
    QListWidget, QGroupBox, QRadioButton, QButtonGroup,
    QCheckBox, QColorDialog, QScrollArea, QGridLayout,
    QTabWidget, QStackedWidget, QToolButton, QMenu
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QIcon

from viewport_3d import Viewport3D
from rig_system import StickmanRig, VisualStyle


class ColorButton(QToolButton):
    """Color picker button that shows current color."""
    color_changed = Signal(QColor)

    def __init__(self, color=QColor(0, 255, 255)):
        super().__init__()
        self.color = color
        self.setFixedSize(24, 24)
        self.clicked.connect(self.pick_color)
        self.update_color()

    def update_color(self):
        """Update button appearance."""
        self.setStyleSheet(f"""
            QToolButton {{
                background: {self.color.name()};
                border: 2px solid #4a4a4e;
                border-radius: 3px;
            }}
            QToolButton:hover {{
                border: 2px solid #6a6a6e;
            }}
        """)

    def pick_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(self.color, self, "Choose Color")
        if color.isValid():
            self.color = color
            self.update_color()
            self.color_changed.emit(color)


class StyleSelector(QFrame):
    """Character style selector with visual previews."""
    style_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QFrame {
                background: #2a2a2e;
                border: 1px solid #3a3a3e;
                border-radius: 4px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Style buttons
        self.button_group = QButtonGroup()

        styles = [
            ("Neon", "◉", "#00ffff"),
            ("Shadow", "◉", "#ff0000"),
            ("Classic", "○○", "#ffffff")
        ]

        for i, (name, icon, color) in enumerate(styles):
            btn = QRadioButton(name)
            btn.setStyleSheet(f"""
                QRadioButton {{
                    color: #d0d0d0;
                    spacing: 8px;
                }}
                QRadioButton::indicator {{
                    width: 16px;
                    height: 16px;
                }}
                QRadioButton::indicator:checked {{
                    background: {color};
                    border: 2px solid #4a7eff;
                    border-radius: 8px;
                }}
                QRadioButton::indicator:unchecked {{
                    background: #3a3a3e;
                    border: 2px solid #4a4a4e;
                    border-radius: 8px;
                }}
            """)
            self.button_group.addButton(btn, i)
            layout.addWidget(btn)

            if i == 0:  # Default to Neon
                btn.setChecked(True)

        layout.addStretch()

        # Connect signal
        self.button_group.idClicked.connect(self.on_style_selected)

    def on_style_selected(self, id):
        """Handle style selection."""
        styles = ["Neon", "Shadow", "Classic"]
        self.style_changed.emit(styles[id])


class PropertyPanel(QFrame):
    """Left panel with character properties."""

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(320)
        self.setMaximumWidth(400)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Style selector at top
        self.style_selector = StyleSelector()
        layout.addWidget(self.style_selector)

        # Properties tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3e;
                background: #2a2a2e;
            }
            QTabBar::tab {
                background: #353538;
                color: #a0a0a0;
                padding: 6px 12px;
                margin: 1px;
            }
            QTabBar::tab:selected {
                background: #3a3a4e;
                color: white;
            }
        """)

        # Body tab
        self.create_body_tab()

        # Color tab
        self.create_color_tab()

        # Extra tab
        self.create_extra_tab()

        layout.addWidget(self.tabs)

        # IK/FK and Symmetry toggles
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()

        # IK/FK toggles
        ik_layout = QHBoxLayout()
        ik_layout.addWidget(QLabel("IK/FK:"))
        self.ik_left_arm = QCheckBox("L Arm")
        self.ik_right_arm = QCheckBox("R Arm")
        self.ik_left_leg = QCheckBox("L Leg")
        self.ik_right_leg = QCheckBox("R Leg")
        ik_layout.addWidget(self.ik_left_arm)
        ik_layout.addWidget(self.ik_right_arm)
        ik_layout.addWidget(self.ik_left_leg)
        ik_layout.addWidget(self.ik_right_leg)
        controls_layout.addLayout(ik_layout)

        # Symmetry toggle
        self.symmetry_check = QCheckBox("Symmetry Mode")
        self.symmetry_check.setChecked(True)
        controls_layout.addWidget(self.symmetry_check)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Action buttons
        button_layout = QHBoxLayout()

        reset_btn = QPushButton("Reset")
        reset_btn.setStyleSheet(self.button_style())
        button_layout.addWidget(reset_btn)

        random_btn = QPushButton("Random")
        random_btn.setStyleSheet(self.button_style())
        button_layout.addWidget(random_btn)

        mirror_btn = QPushButton("Mirror L↔R")
        mirror_btn.setStyleSheet(self.button_style())
        button_layout.addWidget(mirror_btn)

        layout.addLayout(button_layout)

        layout.addStretch()

    def create_body_tab(self):
        """Create body proportions tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Body sliders
        sliders = [
            ("Height", "height", 50, 150, 100),
            ("Bulk", "bulk", 70, 130, 100),
            ("Head", "head_size", 80, 120, 100),
            ("Torso", "torso_height", 80, 120, 100),
            ("Shoulders", "shoulder_width", 80, 120, 100),
            ("Arms", "arm_length", 80, 120, 100),
            ("Legs", "leg_length", 80, 120, 100)
        ]

        for label, key, min_val, max_val, default in sliders:
            row = QHBoxLayout()

            lbl = QLabel(label)
            lbl.setFixedWidth(80)
            row.addWidget(lbl)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(min_val, max_val)
            slider.setValue(default)
            row.addWidget(slider)

            value = QLabel(f"{default}%")
            value.setFixedWidth(40)
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            slider.valueChanged.connect(lambda v, l=value: l.setText(f"{v}%"))
            row.addWidget(value)

            layout.addLayout(row)

        layout.addStretch()
        self.tabs.addTab(widget, "Body")

    def create_color_tab(self):
        """Create color customization tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Color controls
        colors_group = QGroupBox("Colors")
        colors_layout = QGridLayout()

        # Joint color
        colors_layout.addWidget(QLabel("Joints:"), 0, 0)
        self.joint_color = ColorButton(QColor(0, 255, 255))
        colors_layout.addWidget(self.joint_color, 0, 1)
        self.joint_glow = QCheckBox("Glow")
        self.joint_glow.setChecked(True)
        colors_layout.addWidget(self.joint_glow, 0, 2)

        # Eye color
        colors_layout.addWidget(QLabel("Eyes:"), 1, 0)
        self.eye_color = ColorButton(QColor(0, 255, 255))
        colors_layout.addWidget(self.eye_color, 1, 1)
        self.eye_style = QComboBox()
        self.eye_style.addItems(["Dots", "Slits", "Angry", "X"])
        colors_layout.addWidget(self.eye_style, 1, 2)

        # Body color
        colors_layout.addWidget(QLabel("Body:"), 2, 0)
        self.body_color = ColorButton(QColor(20, 20, 20))
        colors_layout.addWidget(self.body_color, 2, 1)

        colors_group.setLayout(colors_layout)
        layout.addWidget(colors_group)

        layout.addStretch()
        self.tabs.addTab(widget, "Color")

    def create_extra_tab(self):
        """Create extra options tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Expression sliders
        expr_group = QGroupBox("Expression")
        expr_layout = QVBoxLayout()

        # Eye expression
        eye_layout = QHBoxLayout()
        eye_layout.addWidget(QLabel("Eyes:"))
        self.eye_slider = QSlider(Qt.Orientation.Horizontal)
        self.eye_slider.setRange(0, 100)
        self.eye_slider.setValue(50)
        eye_layout.addWidget(self.eye_slider)
        expr_layout.addLayout(eye_layout)

        # Mouth expression
        mouth_layout = QHBoxLayout()
        mouth_layout.addWidget(QLabel("Mouth:"))
        self.mouth_slider = QSlider(Qt.Orientation.Horizontal)
        self.mouth_slider.setRange(0, 100)
        self.mouth_slider.setValue(50)
        mouth_layout.addWidget(self.mouth_slider)
        expr_layout.addLayout(mouth_layout)

        expr_group.setLayout(expr_layout)
        layout.addWidget(expr_group)

        # Hand poses
        hand_group = QGroupBox("Hand Poses")
        hand_layout = QHBoxLayout()

        self.left_hand = QComboBox()
        self.left_hand.addItems(["Open", "Fist", "Point", "Grab"])
        hand_layout.addWidget(QLabel("Left:"))
        hand_layout.addWidget(self.left_hand)

        self.right_hand = QComboBox()
        self.right_hand.addItems(["Open", "Fist", "Point", "Grab"])
        hand_layout.addWidget(QLabel("Right:"))
        hand_layout.addWidget(self.right_hand)

        hand_group.setLayout(hand_layout)
        layout.addWidget(hand_group)

        layout.addStretch()
        self.tabs.addTab(widget, "Extra")

    def button_style(self):
        """Return button stylesheet."""
        return """
            QPushButton {
                background: #3a3a4e;
                color: white;
                border: 1px solid #4a4a5e;
                border-radius: 3px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #4a4a5e;
            }
            QPushButton:pressed {
                background: #2a2a3e;
            }
        """


class LibraryPanel(QFrame):
    """Right panel with smart context library."""

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(240)
        self.setMaximumWidth(300)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Library header with dropdown
        header_layout = QHBoxLayout()

        self.library_label = QLabel("LIBRARY:")
        self.library_label.setStyleSheet("font-weight: bold; color: #d0d0d0;")
        header_layout.addWidget(self.library_label)

        # Library dropdown
        self.library_dropdown = QComboBox()
        self.library_dropdown.setMinimumWidth(120)
        self.library_dropdown.addItems([
            "Hero_Blue",
            "Enemy_Red",
            "Boss_Dark",
            "NPC_Green",
            "+ New Character..."
        ])
        header_layout.addWidget(self.library_dropdown)

        layout.addLayout(header_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        save_btn = QToolButton()
        save_btn.setText("💾")
        save_btn.setToolTip("Save")
        save_btn.setFixedSize(28, 28)
        button_layout.addWidget(save_btn)

        open_btn = QToolButton()
        open_btn.setText("📁")
        open_btn.setToolTip("Open")
        open_btn.setFixedSize(28, 28)
        button_layout.addWidget(open_btn)

        delete_btn = QToolButton()
        delete_btn.setText("🗑")
        delete_btn.setToolTip("Delete")
        delete_btn.setFixedSize(28, 28)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Separator
        separator = QFrame()
        separator.setFrameStyle(QFrame.Shape.HLine | QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Category tabs for content
        self.content_tabs = QTabWidget()
        self.content_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3e;
                background: #2a2a2e;
            }
            QTabBar::tab {
                background: #353538;
                color: #a0a0a0;
                padding: 4px 8px;
                margin: 0px;
                font-size: 11px;
            }
            QTabBar::tab:selected {
                background: #3a3a4e;
                color: white;
            }
        """)

        # Equipment tab
        self.create_equipment_tab()

        # Expressions tab
        self.create_expressions_tab()

        # Poses tab
        self.create_poses_tab()

        # Hands tab
        self.create_hands_tab()

        layout.addWidget(self.content_tabs)
        layout.addStretch()

        # Main action buttons
        self.create_btn = QPushButton("CREATE TOON")
        self.create_btn.setFixedHeight(45)
        self.create_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3a5a8a, stop:1 #2a4a7a);
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4a6a9a, stop:1 #3a5a8a);
            }
            QPushButton:pressed {
                background: #2a4a7a;
            }
        """)
        layout.addWidget(self.create_btn)

        send_btn = QPushButton("Send to Animation →")
        send_btn.setFixedHeight(35)
        send_btn.setStyleSheet("""
            QPushButton {
                background: #2a5a4a;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #3a6a5a;
            }
        """)
        layout.addWidget(send_btn)

    def create_equipment_tab(self):
        """Create equipment/accessories tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        placeholder = QLabel("Equipment & Accessories\n\n[Coming after character styles are complete]")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #606060; font-style: italic;")
        layout.addWidget(placeholder)
        layout.addStretch()

        self.content_tabs.addTab(widget, "Equip")

    def create_expressions_tab(self):
        """Create facial expressions tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        placeholder = QLabel("Facial Expressions\n\n[Coming after character styles are complete]")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #606060; font-style: italic;")
        layout.addWidget(placeholder)
        layout.addStretch()

        self.content_tabs.addTab(widget, "Face")

    def create_poses_tab(self):
        """Create poses tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        placeholder = QLabel("Pose Presets\n\n[Coming after character styles are complete]")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #606060; font-style: italic;")
        layout.addWidget(placeholder)
        layout.addStretch()

        self.content_tabs.addTab(widget, "Pose")

    def create_hands_tab(self):
        """Create hands tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        placeholder = QLabel("Hand Poses\n\n[Coming after character styles are complete]")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #606060; font-style: italic;")
        layout.addWidget(placeholder)
        layout.addStretch()

        self.content_tabs.addTab(widget, "Hands")


class Tab1ReadyToon(QWidget):
    """Main Tab 1 interface - Ready The Toon."""

    def __init__(self):
        super().__init__()
        self.rig = StickmanRig()
        self.init_ui()

    def init_ui(self):
        """Initialize the complete UI."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top control bar
        self.create_top_bar()

        # Main content area with splitters
        content = QSplitter(Qt.Orientation.Horizontal)
        content.setStyleSheet("""
            QSplitter::handle {
                background: #3a3a3e;
                width: 2px;
            }
        """)

        # Left panel - Properties
        self.property_panel = PropertyPanel()
        content.addWidget(self.property_panel)

        # Center - Viewport
        self.viewport = Viewport3D()
        self.viewport.rig = self.rig
        content.addWidget(self.viewport)

        # Right panel - Library
        self.library_panel = LibraryPanel()
        content.addWidget(self.library_panel)

        # Set splitter sizes (proportions)
        content.setSizes([320, 900, 280])
        content.setStretchFactor(0, 0)  # Left panel doesn't stretch
        content.setStretchFactor(1, 1)  # Center viewport stretches
        content.setStretchFactor(2, 0)  # Right panel doesn't stretch

        layout.addWidget(content)

        # Connect signals
        self.property_panel.style_selector.style_changed.connect(self.on_style_changed)

    def create_top_bar(self):
        """Create the top control bar."""
        top_bar = QFrame()
        top_bar.setFixedHeight(32)
        top_bar.setStyleSheet("""
            QFrame {
                background: #242428;
                border-bottom: 1px solid #3a3a3e;
            }
        """)

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(8, 0, 8, 0)

        # Grid toggle
        grid_check = QCheckBox("Grid")
        grid_check.setChecked(True)
        grid_check.setStyleSheet("color: #d0d0d0;")
        layout.addWidget(grid_check)

        # Snap toggle
        snap_check = QCheckBox("Snap")
        snap_check.setStyleSheet("color: #d0d0d0;")
        layout.addWidget(snap_check)

        layout.addStretch()

        # View controls
        layout.addWidget(QLabel("View:"))
        view_combo = QComboBox()
        view_combo.addItems(["3D", "Front", "Side", "Top"])
        view_combo.setMinimumWidth(80)
        layout.addWidget(view_combo)

        # Zoom control
        layout.addWidget(QLabel("Zoom:"))
        zoom_label = QLabel("100%")
        zoom_label.setStyleSheet("color: #d0d0d0; font-weight: bold;")
        layout.addWidget(zoom_label)

        reset_btn = QPushButton("Reset View")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #3a3a3e;
                color: #d0d0d0;
                border: 1px solid #4a4a4e;
                border-radius: 2px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background: #4a4a4e;
            }
        """)
        layout.addWidget(reset_btn)

        self.layout().addWidget(top_bar)

    def on_style_changed(self, style_name):
        """Handle style change."""
        style_map = {
            "Neon": VisualStyle.NEON_CYAN,
            "Shadow": VisualStyle.SHADOW_RED,
            "Classic": VisualStyle.CLASSIC_CAPSULE
        }

        if style_name in style_map:
            self.rig.apply_visual_style(style_map[style_name])
            self.viewport.update()

    def new_toon(self):
        """Create a new toon."""
        self.rig = StickmanRig()
        self.viewport.rig = self.rig
        self.viewport.update()

    def open_toon(self):
        """Open an existing toon."""
        # TODO: Implement file dialog
        pass

    def save_toon(self):
        """Save the current toon."""
        # TODO: Implement save logic
        pass