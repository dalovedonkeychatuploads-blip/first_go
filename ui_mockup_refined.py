"""
Refined UI Layout Mockup - Optimized Hybrid Design
Based on user feedback - smarter space usage
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QFont, QPen

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
                border: 1px solid #404040;
                border-radius: 3px;
            }}
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        # Different text colors based on background
        if "4a7e" in self.bg_color or "5090" in self.bg_color:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
        else:
            painter.setPen(QPen(QColor(200, 200, 200), 1))

        painter.setFont(QFont("Segoe UI", 9))

        # Draw label
        rect = self.rect().adjusted(8, 8, -8, -8)
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self.label)


class RefinedMockup(QWidget):
    """Refined optimal layout based on feedback."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("DONK Animation Studio - Stick Figure Maker (Refined Layout)")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("background: #1a1a1a;")

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)

        # === COMPACT TOP BAR (35px) ===
        topbar_layout = QHBoxLayout()
        topbar_layout.setSpacing(10)

        # File operations
        file_bar = MockPanel("New | Save | Load | Import | Export", "#25252a")
        file_bar.setFixedHeight(35)
        file_bar.setFixedWidth(250)
        topbar_layout.addWidget(file_bar)

        # Quick actions
        actions_bar = MockPanel("Undo | Redo | Reset", "#25252a")
        actions_bar.setFixedHeight(35)
        actions_bar.setFixedWidth(120)
        topbar_layout.addWidget(actions_bar)

        # Style selector (compact dropdown style)
        style_bar = MockPanel("Style: [Neon ▼] [Shadow ▼] [Classic ▼]", "#25252a")
        style_bar.setFixedHeight(35)
        style_bar.setFixedWidth(250)
        topbar_layout.addWidget(style_bar)

        topbar_layout.addStretch()

        # View options
        view_bar = MockPanel("Grid: ☑  Snap: ☐  Guides: ☐", "#25252a")
        view_bar.setFixedHeight(35)
        view_bar.setFixedWidth(150)
        topbar_layout.addWidget(view_bar)

        main_layout.addLayout(topbar_layout)

        # === MAIN CONTENT AREA ===
        content_layout = QHBoxLayout()
        content_layout.setSpacing(3)

        # === LEFT PANEL (300px) ===
        left_panel_layout = QVBoxLayout()
        left_panel_layout.setSpacing(2)

        # Style thumbnails (compact 60px)
        style_thumbs = MockPanel("QUICK STYLES:  [Neon 👁] [Shadow 👁] [Classic 👁]", "#2a3040")
        style_thumbs.setFixedHeight(60)
        style_thumbs.setFixedWidth(300)
        left_panel_layout.addWidget(style_thumbs)

        # Tabbed properties (expandable sections)
        props_panel = MockPanel(
            "[Proportions] [Colors] [Accessories]\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "▼ PROPORTIONS\n"
            "├─ Overall\n"
            "│  Height:    ▬▬▬▬●▬▬  100%\n"
            "│  Scale:     ▬▬▬●▬▬▬  85%\n"
            "│\n"
            "├─ Body Parts\n"
            "│  Head:      ▬▬▬▬●▬▬  100%\n"
            "│  Torso:     ▬▬▬●▬▬▬  90%\n"
            "│  Arms:      ▬▬▬▬▬●▬  110%\n"
            "│  Legs:      ▬▬▬▬●▬▬  100%\n"
            "│\n"
            "├─ Fine Tuning\n"
            "│  Shoulders: ▬▬▬●▬▬▬  95%\n"
            "│  Hands:     ▬▬●▬▬▬▬  80%\n"
            "│  Feet:      ▬▬▬●▬▬▬  90%\n"
            "│\n"
            "└─ [Reset All] [Mirror L→R]",
            "#303545"
        )
        props_panel.setFixedWidth(300)
        left_panel_layout.addWidget(props_panel, 1)

        content_layout.addLayout(left_panel_layout)

        # === CENTER VIEWPORT (expandable) ===
        center_layout = QVBoxLayout()
        center_layout.setSpacing(1)

        # Viewport controls bar (30px)
        viewport_controls = MockPanel(
            "View: [Front|Side|Top|3D] │ Zoom: 100% [Reset] │ Camera: Left-Pan, Right-Rotate, Wheel-Zoom",
            "#2a2a30"
        )
        viewport_controls.setFixedHeight(30)
        center_layout.addWidget(viewport_controls)

        # Main viewport
        viewport = MockPanel(
            "\n\n\n\n"
            "                          VIEWPORT\n\n"
            "                    2.5D Stick Figure\n"
            "                         T-Pose\n\n"
            "                  ┌─────────────────┐\n"
            "                  │        O        │\n"
            "                  │       /│\\       │\n"
            "                  │      / │ \\      │\n"
            "                  │        │        │\n"
            "                  │       / \\       │\n"
            "                  │      /   \\      │\n"
            "                  └─────────────────┘\n\n"
            "                    Grid: Visible\n"
            "                    Depth: 2.5D\n"
            "                    Shadows: On",
            "#2a2a35"
        )
        center_layout.addWidget(viewport)

        # Status bar (25px)
        status_bar = MockPanel(
            "Pos: 0,0,0 │ Rot: 0° │ Scale: 1.0 │ Bones: 15 │ FPS: 60 │ Memory: 45MB",
            "#252530"
        )
        status_bar.setFixedHeight(25)
        center_layout.addWidget(status_bar)

        content_layout.addLayout(center_layout, 1)

        # === RIGHT PANEL (280px) ===
        right_panel_layout = QVBoxLayout()
        right_panel_layout.setSpacing(2)

        # Colors panel (compact)
        colors_panel = MockPanel(
            "═ COLORS ═\n"
            "Joints:    [■ Cyan ▼] + Glow: ●\n"
            "Eyes:      [■ Cyan ▼] Style: [Slits ▼]\n"
            "Body:      [■ Black ▼]\n"
            "Outline:   [□ None ▼]\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Team Colors: [■][■][■][■][■][■]\n"
            "            [■][■][■][■][+]",
            "#354045"
        )
        colors_panel.setFixedHeight(160)
        colors_panel.setFixedWidth(280)
        right_panel_layout.addWidget(colors_panel)

        # Saved Characters (collapsible dropdown)
        saved_chars = MockPanel(
            "═ LIBRARY ═\n"
            "Current: Hero_Blue\n"
            "[▼ Select Character...    ]\n"
            "├─ Hero_Blue\n"
            "├─ Enemy_Red\n"
            "├─ Boss_Dark\n"
            "└─ NPC_Green\n"
            "\n"
            "[+ New] [⟲ Duplicate] [🗑 Delete]\n"
            "[📁 Import] [💾 Export]",
            "#304045"
        )
        saved_chars.setFixedHeight(200)
        saved_chars.setFixedWidth(280)
        right_panel_layout.addWidget(saved_chars)

        # Advanced/Expert options (collapsible)
        advanced = MockPanel(
            "▶ Advanced Options\n"
            "  (click to expand)\n"
            "  • Bone constraints\n"
            "  • IK settings\n"
            "  • Export settings",
            "#2a3040"
        )
        advanced.setFixedHeight(80)
        advanced.setFixedWidth(280)
        right_panel_layout.addWidget(advanced)

        right_panel_layout.addStretch()

        # Create Figure button (prominent)
        create_section = QVBoxLayout()
        create_section.setSpacing(2)

        create_btn = MockPanel(
            "\n        [CREATE FIGURE]\n",
            "#4a7eff"
        )
        create_btn.setFixedHeight(50)
        create_btn.setFixedWidth(280)
        create_section.addWidget(create_btn)

        export_btn = MockPanel(
            "  [Export to Animation Tab →]",
            "#5090ff"
        )
        export_btn.setFixedHeight(35)
        export_btn.setFixedWidth(280)
        create_section.addWidget(export_btn)

        right_panel_layout.addLayout(create_section)

        content_layout.addLayout(right_panel_layout)

        main_layout.addLayout(content_layout)

        # === IMPROVEMENTS PANEL ===
        improvements = MockPanel(
            "KEY IMPROVEMENTS:\n"
            "• Saved Characters: Now a dropdown selector (not space-wasting list)\n"
            "• Compact top bar: Only 35px height\n"
            "• Style thumbnails: Small 60px strip\n"
            "• Props on left: Tabbed and collapsible\n"
            "• Colors compact: All in 160px height\n"
            "• Library smart: Dropdown + action buttons\n"
            "• Viewport maximized: Takes ~65% of screen\n"
            "• Status bar thin: Only 25px\n"
            "• Everything accessible but not cluttered",
            "#1a4030"
        )
        improvements.setFixedHeight(120)
        main_layout.addWidget(improvements)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mockup = RefinedMockup()
    mockup.show()

    sys.exit(app.exec())