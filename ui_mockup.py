"""
UI Layout Mockup Viewer
Shows different layout options for the Stick Figure Maker
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush

class MockPanel(QFrame):
    """A mock panel showing a UI element."""

    def __init__(self, label, color, parent=None):
        super().__init__(parent)
        self.label = label
        self.bg_color = color
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border: 2px solid #333;
                border-radius: 4px;
            }}
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        # Draw label in center
        rect = self.rect()
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.label)


class MockupViewer(QWidget):
    """Main mockup viewer window."""

    def __init__(self):
        super().__init__()
        self.current_mockup = 0
        self.mockups = [
            self.create_mockup_1,  # Adobe-style
            self.create_mockup_2,  # Blender-style
            self.create_mockup_3,  # Hybrid optimal
            self.create_mockup_4   # Compact style
        ]
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("UI Layout Mockups - Click Next to Browse")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("background: #1a1a1a;")

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Container for mockup
        self.mockup_container = QWidget()
        self.mockup_layout = QVBoxLayout(self.mockup_container)
        main_layout.addWidget(self.mockup_container)

        # Navigation
        nav_widget = QWidget()
        nav_widget.setMaximumHeight(60)
        nav_widget.setStyleSheet("background: #2a2a2a; border-top: 2px solid #444;")
        nav_layout = QHBoxLayout(nav_widget)

        self.info_label = QLabel("Mockup 1 of 4: Adobe-Style Layout")
        self.info_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        nav_layout.addWidget(self.info_label)

        nav_layout.addStretch()

        prev_btn = QPushButton("← Previous")
        prev_btn.clicked.connect(self.show_previous)
        prev_btn.setStyleSheet("""
            QPushButton {
                background: #404040;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
            }
            QPushButton:hover { background: #505050; }
        """)
        nav_layout.addWidget(prev_btn)

        next_btn = QPushButton("Next →")
        next_btn.clicked.connect(self.show_next)
        next_btn.setStyleSheet("""
            QPushButton {
                background: #4a7eff;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
            }
            QPushButton:hover { background: #5a8eff; }
        """)
        nav_layout.addWidget(next_btn)

        main_layout.addWidget(nav_widget)

        # Show first mockup
        self.show_mockup()

    def clear_layout(self, layout):
        """Clear all widgets from a layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_mockup(self):
        """Display current mockup."""
        self.clear_layout(self.mockup_layout)
        self.mockups[self.current_mockup]()

    def show_next(self):
        """Show next mockup."""
        self.current_mockup = (self.current_mockup + 1) % len(self.mockups)
        self.show_mockup()
        self.update_label()

    def show_previous(self):
        """Show previous mockup."""
        self.current_mockup = (self.current_mockup - 1) % len(self.mockups)
        self.show_mockup()
        self.update_label()

    def update_label(self):
        """Update info label."""
        labels = [
            "Adobe-Style Layout (Photoshop/Animate inspired)",
            "Blender-Style Layout (Professional 3D software)",
            "Hybrid Optimal Layout (Best of both)",
            "Compact Layout (Maximum viewport)"
        ]
        self.info_label.setText(f"Mockup {self.current_mockup + 1} of {len(self.mockups)}: {labels[self.current_mockup]}")

    def create_mockup_1(self):
        """Adobe-style layout."""
        # Main horizontal layout
        main_h_layout = QHBoxLayout()
        main_h_layout.setSpacing(2)

        # LEFT: Vertical toolbar
        toolbar = MockPanel("TOOLS\n\nSelect\nMove\nRotate\nScale\n\nBrush\nEraser\n\nZoom\nPan", "#2a2a35")
        toolbar.setFixedWidth(60)
        main_h_layout.addWidget(toolbar)

        # CENTER: Main work area
        center_layout = QVBoxLayout()
        center_layout.setSpacing(2)

        # Top menubar
        menubar = MockPanel("FILE | EDIT | VIEW | CHARACTER | HELP", "#252530")
        menubar.setFixedHeight(35)
        center_layout.addWidget(menubar)

        # Viewport with rulers
        viewport_container = QVBoxLayout()
        viewport_container.setSpacing(0)

        h_ruler = MockPanel("← Ruler (pixels/units) →", "#2a2a35")
        h_ruler.setFixedHeight(20)
        viewport_container.addWidget(h_ruler)

        viewport_h = QHBoxLayout()
        viewport_h.setSpacing(0)

        v_ruler = MockPanel("↑\nR\nu\nl\ne\nr\n↓", "#2a2a35")
        v_ruler.setFixedWidth(20)
        viewport_h.addWidget(v_ruler)

        viewport = MockPanel("VIEWPORT\n\nStick Figure Display\n(2.5D Rendering)\n\n• Grid On/Off\n• Zoom: 100%\n• Camera controls", "#35353f")
        viewport_h.addWidget(viewport)

        viewport_container.addLayout(viewport_h)
        center_layout.addLayout(viewport_container)

        main_h_layout.addLayout(center_layout)

        # RIGHT: Properties panels
        right_layout = QVBoxLayout()
        right_layout.setSpacing(2)

        # Character properties
        props = MockPanel("CHARACTER PROPS\n\nStyle: [Neon ▼]\n\n═ PROPORTIONS ═\nHeight: ████░\nBulk: ███░░\nHead: ████░\n\n═ COLORS ═\nJoints: [■ Cyan]\nEyes: [■ Cyan]\nBody: [■ Black]\n\n═ ACCESSORIES ═\nHat: [None ▼]\nGloves: [None ▼]", "#303040")
        props.setFixedWidth(280)
        right_layout.addWidget(props, 2)

        # Library panel
        library = MockPanel("CHARACTER LIBRARY\n\n• Fighter_01\n• Enemy_Red\n• Boss_Shadow\n• Player_Blue\n\n[+ New] [Import] [Export]", "#2a3040")
        library.setFixedWidth(280)
        right_layout.addWidget(library, 1)

        main_h_layout.addLayout(right_layout)

        self.mockup_layout.addLayout(main_h_layout)

    def create_mockup_2(self):
        """Blender-style layout."""
        # Main layout
        main_v_layout = QVBoxLayout()
        main_v_layout.setSpacing(2)

        # Top bar
        topbar = MockPanel("DONK Studio | File Edit Add Character View Help | Layout: Modeling ▼", "#2a2a35")
        topbar.setFixedHeight(35)
        main_v_layout.addWidget(topbar)

        # Main content
        main_h_layout = QHBoxLayout()
        main_h_layout.setSpacing(2)

        # LEFT: Outliner/Library
        left_panel = MockPanel("OUTLINER\n\n▼ Scene\n  ▷ StickFigure_01\n    • Head\n    • Body\n    • Arms\n    • Legs\n\n══════════\n\nLIBRARY\n• Saved_01\n• Saved_02", "#2a2a35")
        left_panel.setFixedWidth(250)
        main_h_layout.addWidget(left_panel)

        # CENTER: Viewport
        viewport = MockPanel("3D VIEWPORT\n\nStick Figure\n(Perspective View)\n\n[View: Front | Side | Top | 3D]\n\nGrid | Snap | Proportional", "#303035")
        main_h_layout.addWidget(viewport)

        # RIGHT: Properties
        right_tabs = MockPanel("PROPERTIES\n\n[Object | Modifiers | Materials | Rig]\n\n═ Transform ═\nLocation: 0, 0, 0\nRotation: 0, 0, 0\nScale: 1, 1, 1\n\n═ Proportions ═\nHeight: ███░░\nBulk: ████░\n\n═ Style ═\nType: [Neon ▼]\nJoint Color: [■]", "#2a2a35")
        right_tabs.setFixedWidth(300)
        main_h_layout.addWidget(right_tabs)

        main_v_layout.addLayout(main_h_layout)
        self.mockup_layout.addLayout(main_v_layout)

    def create_mockup_3(self):
        """Hybrid optimal layout - RECOMMENDED."""
        main_v_layout = QVBoxLayout()
        main_v_layout.setSpacing(3)

        # Compact top toolbar
        toolbar = MockPanel("New | Save | Load | Import | Export  ||  Undo Redo  ||  Style: [Neon ▼] [Shadow ▼] [Classic ▼]  ||  Grid: ☑  Snap: ☐", "#25252a")
        toolbar.setFixedHeight(40)
        main_v_layout.addWidget(toolbar)

        # Main content area
        content_h_layout = QHBoxLayout()
        content_h_layout.setSpacing(3)

        # LEFT: Tabbed panels (can collapse)
        left_container = QVBoxLayout()
        left_container.setSpacing(2)

        # Quick presets (thumbnails)
        presets = MockPanel("QUICK STYLES\n[Neon] [Shadow] [Classic]\n  ◉       ○        ○", "#2a3545")
        presets.setFixedHeight(80)
        left_container.addWidget(presets)

        # Properties tabs
        props_tabs = MockPanel("[Proportions | Colors | Accessories]\n\n═ PROPORTIONS ═\nOverall\n  Height: ████░░░\n  Scale:  ███████\n\nBody Parts\n  Head:   █████░░\n  Torso:  ████░░░\n  Arms:   ███████\n  Legs:   ████░░░\n\n[Reset] [Randomize]", "#303545")
        props_tabs.setFixedWidth(320)
        left_container.addWidget(props_tabs)

        content_h_layout.addLayout(left_container)

        # CENTER: Large viewport
        center_v_layout = QVBoxLayout()
        center_v_layout.setSpacing(2)

        # View controls bar
        view_bar = MockPanel("View: [Front|Side|Top|3D] | Zoom: 100% | [Reset View] | Mouse: Left-Pan, Right-Rotate, Wheel-Zoom", "#2a2a30")
        view_bar.setFixedHeight(35)
        center_v_layout.addWidget(view_bar)

        # Main viewport
        viewport = MockPanel("VIEWPORT\n\n\n2.5D Stick Figure\n\n(Clean, Large, Focused)\n\nNo clutter\nProper borders\nSmooth pan/zoom\n\n\nGrid visible", "#35354a")
        center_v_layout.addWidget(viewport)

        # Quick info bar
        info_bar = MockPanel("Position: 0,0 | Rotation: 0° | Scale: 1.0 | FPS: 60", "#2a2a30")
        info_bar.setFixedHeight(25)
        center_v_layout.addWidget(info_bar)

        content_h_layout.addLayout(center_v_layout)

        # RIGHT: Library & Actions
        right_container = QVBoxLayout()
        right_container.setSpacing(2)

        # Color customization
        colors = MockPanel("═ COLORS ═\nJoints:  [■ Cyan ▼]\nEyes:    [■ Cyan ▼]\nBody:    [■ Black ▼]\nGlow:    ████░░░\n\nTeam Color: [■ ■ ■ ■]\n         [■ ■ ■ ■]", "#354045")
        colors.setFixedHeight(180)
        colors.setFixedWidth(250)
        right_container.addWidget(colors)

        # Saved characters
        library = MockPanel("═ SAVED CHARACTERS ═\n\n📁 My Characters\n  • Hero_Blue\n  • Enemy_Red\n  • Boss_Dark\n  • NPC_Green\n\n[Create New]\n[Duplicate]\n[Delete]", "#304045")
        library.setFixedWidth(250)
        right_container.addWidget(library)

        # Action buttons
        actions = MockPanel("[CREATE FIGURE]\n\n[Export to Animation]", "#4a7eff")
        actions.setFixedHeight(80)
        actions.setFixedWidth(250)
        right_container.addWidget(actions)

        content_h_layout.addLayout(right_container)

        main_v_layout.addLayout(content_h_layout)
        self.mockup_layout.addLayout(main_v_layout)

    def create_mockup_4(self):
        """Compact layout - Maximum viewport."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(2)

        # Minimal top bar
        topbar = MockPanel("☰ Menu | Style: Neon ▼ | Joint Color: [■] | Eye Style: ▼ | [Save] [Load]", "#202025")
        topbar.setFixedHeight(35)
        main_layout.addWidget(topbar)

        # Main area
        main_h = QHBoxLayout()
        main_h.setSpacing(2)

        # Collapsible left panel
        left_panel = MockPanel("◂\n\nP\nR\nO\nP\nS\n\n(collapsed)", "#252530")
        left_panel.setFixedWidth(30)
        main_h.addWidget(left_panel)

        # Massive viewport
        viewport = MockPanel("LARGE VIEWPORT\n\n\n\nMaximum Space for Character\n\n\n2.5D Stick Figure\n\n\n(90% of screen)\n\n\nFloating panels can overlay", "#2a2a35")
        main_h.addWidget(viewport)

        # Floating overlays (represented as right panel here)
        overlay = MockPanel("Float ×\n\nHeight: ███\nBulk: ███\nHead: ███\n\n[Create]", "#303040aa")
        overlay.setFixedWidth(150)
        main_h.addWidget(overlay)

        main_layout.addLayout(main_h)
        self.mockup_layout.addLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MockupViewer()
    viewer.show()
    sys.exit(app.exec())