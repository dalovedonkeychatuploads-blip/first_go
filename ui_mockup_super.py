"""
SUPER OPTIMIZED UI MOCKUP
Maximum efficiency, zero waste
Every pixel has a purpose
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush

class SmartPanel(QFrame):
    """Smart panel with better text rendering."""

    def __init__(self, content, color="#2a2a35", text_size=8, parent=None):
        super().__init__(parent)
        self.content = content
        self.text_size = text_size
        self.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border: 1px solid #3a3a3a;
                border-radius: 2px;
            }}
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Text color based on background
        if "4a7e" in self.styleSheet() or "5090" in self.styleSheet():
            painter.setPen(QPen(QColor(255, 255, 255), 1))
        elif "1a40" in self.styleSheet():
            painter.setPen(QPen(QColor(100, 255, 100), 1))
        else:
            painter.setPen(QPen(QColor(180, 180, 185), 1))

        painter.setFont(QFont("Consolas", self.text_size))

        # Draw content
        rect = self.rect().adjusted(5, 5, -5, -5)
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self.content)


class SuperMockup(QWidget):
    """The perfect, ultra-optimized layout."""

    def __init__(self):
        super().__init__()
        self.viewport_scale = 100
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("DONK Studio - Stick Figure Maker [SUPER OPTIMIZED]")
        self.setGeometry(50, 50, 1500, 850)
        self.setStyleSheet("background: #18181a;")

        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(1, 1, 1, 1)
        root.setSpacing(1)

        # ═══════════════════════════════════════════════
        # ULTRA-COMPACT TOP BAR (28px only!)
        # ═══════════════════════════════════════════════
        top_bar = QHBoxLayout()
        top_bar.setSpacing(2)

        # File ops (mini buttons)
        file_ops = SmartPanel("New|Save|Load", "#202025", 7)
        file_ops.setFixedSize(100, 28)
        top_bar.addWidget(file_ops)

        # Style selector (radio style)
        styles = SmartPanel("◉Neon ○Shadow ○Classic", "#252530", 7)
        styles.setFixedSize(150, 28)
        top_bar.addWidget(styles)

        # Library dropdown (COMPACT!)
        library_btn = SmartPanel("Library:Hero_01▼", "#303035", 7)
        library_btn.setFixedSize(120, 28)
        top_bar.addWidget(library_btn)

        top_bar.addStretch()

        # View controls
        view_ctrl = SmartPanel("Grid☑ Snap☐ 100%", "#202025", 7)
        view_ctrl.setFixedSize(100, 28)
        top_bar.addWidget(view_ctrl)

        # CREATE button (always visible)
        create_btn = SmartPanel("CREATE→", "#4a7eff", 8)
        create_btn.setFixedSize(70, 28)
        top_bar.addWidget(create_btn)

        root.addLayout(top_bar)

        # ═══════════════════════════════════════════════
        # MAIN CONTENT (Everything else)
        # ═══════════════════════════════════════════════
        content = QHBoxLayout()
        content.setSpacing(2)

        # ────────────────────
        # LEFT: Controls (260px ONLY)
        # ────────────────────
        left_panel = QVBoxLayout()
        left_panel.setSpacing(1)

        # Quick style preview (45px)
        style_preview = SmartPanel(
            "STYLE: [👁N][👁S][👁C]",
            "#2a3040", 8
        )
        style_preview.setFixedSize(260, 45)
        left_panel.addWidget(style_preview)

        # Tabbed controls (auto-expanding)
        controls = SmartPanel(
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "[BODY][COLOR][EXTRA]\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "▼ PROPORTIONS\n"
            " Height    ●━━━━ 100\n"
            " Bulk      ━●━━━  75\n"
            " Head      ━━●━━  90\n"
            " Torso     ━●━━━  85\n"
            " Arms      ━━━●━ 110\n"
            " Legs      ━━●━━ 100\n"
            "\n"
            "▼ FINE TUNE\n"
            " Shoulders ━●━━━  95\n"
            " Hands     ●━━━━  80\n"
            " Feet      ━●━━━  90\n"
            " Neck      ━━●━━ 100\n"
            "\n"
            "[Reset][Random][Mirror]",
            "#2a3545", 7
        )
        controls.setFixedWidth(260)
        left_panel.addWidget(controls)

        content.addLayout(left_panel)

        # ────────────────────
        # CENTER: VIEWPORT (MAXIMIZED!)
        # ────────────────────
        center = QVBoxLayout()
        center.setSpacing(0)

        # Mini view bar (22px)
        view_bar = SmartPanel(
            "Front|Side|Top|◉3D ┊ Zoom:100% Reset ┊ L-Pan M-Rotate R-Menu",
            "#1a1a20", 7
        )
        view_bar.setFixedHeight(22)
        center.addWidget(view_bar)

        # THE GLORIOUS VIEWPORT
        viewport = QFrame()
        viewport.setStyleSheet("""
            QFrame {
                background: #252530;
                border: 2px solid #3a3a45;
            }
        """)

        # Draw the stick figure properly sized
        viewport_content = SmartPanel(
            "\n\n\n\n\n"
            "                           ╔════════════════════════════════╗\n"
            "                           ║                                ║\n"
            "                           ║            ◉  <- Head          ║\n"
            "                           ║           ╱│╲                  ║\n"
            "                           ║          ╱ │ ╲  <- Arms        ║\n"
            "                           ║         ●  │  ●                ║\n"
            "                           ║           ─┼─   <- Torso       ║\n"
            "                           ║            │                   ║\n"
            "                           ║            │                   ║\n"
            "                           ║           ╱ ╲                  ║\n"
            "                           ║          ╱   ╲  <- Legs        ║\n"
            "                           ║         ●     ●                ║\n"
            "                           ║        ╱       ╲               ║\n"
            "                           ║                                ║\n"
            "                           ║     Grid: ON   Depth: 2.5D     ║\n"
            "                           ║     Figure Height: ~40% VP     ║\n"
            "                           ╚════════════════════════════════╝\n\n\n"
            "                                  PERFECT SIZE RATIO\n"
            "                            Not too big, not too small\n"
            "                              Room to pan and work",
            "#252530", 9
        )
        viewport.setLayout(QVBoxLayout())
        viewport.layout().addWidget(viewport_content)

        center.addWidget(viewport)

        # Micro status (18px)
        status = SmartPanel("x:0 y:0 z:0|r:0°|s:1.0|60fps", "#1a1a20", 6)
        status.setFixedHeight(18)
        center.addWidget(status)

        content.addLayout(center, 1)  # Viewport gets all extra space!

        # ────────────────────
        # RIGHT: Colors & Actions (220px ONLY)
        # ────────────────────
        right_panel = QVBoxLayout()
        right_panel.setSpacing(1)

        # Compact color controls
        colors = SmartPanel(
            "═ COLORS ═\n"
            "Joint  [■]◉ +glow\n"
            "Eyes   [■]▼ Style:▼\n"
            "Body   [■]━━●━━\n"
            "━━━━━━━━━━━━━━━━\n"
            "Teams: ■■■■■■■■+\n"
            "━━━━━━━━━━━━━━━━\n"
            "Saves: 12 figures",
            "#304045", 7
        )
        colors.setFixedSize(220, 140)
        right_panel.addWidget(colors)

        # Accessories (collapsible)
        accessories = SmartPanel(
            "▶ Accessories\n"
            "  Hat: None\n"
            "  Weapon: None\n"
            "  Effects: None",
            "#2a3545", 7
        )
        accessories.setFixedSize(220, 60)
        right_panel.addWidget(accessories)

        # Expert (hidden by default)
        expert = SmartPanel(
            "▶ Expert Mode",
            "#252530", 7
        )
        expert.setFixedSize(220, 25)
        right_panel.addWidget(expert)

        right_panel.addStretch()

        # Action zone
        actions = SmartPanel(
            "\nDuplicate Current\n\nExport Selection",
            "#3a5070", 8
        )
        actions.setFixedSize(220, 60)
        right_panel.addWidget(actions)

        content.addLayout(right_panel)

        root.addLayout(content)

        # ═══════════════════════════════════════════════
        # ANALYSIS PANEL (Remove in final)
        # ═══════════════════════════════════════════════
        analysis = SmartPanel(
            "SPACE EFFICIENCY ANALYSIS:\n"
            "• Top bar: 28px (was 35px) = SAVED 7px\n"
            "• Library: Now dropdown button in top bar = SAVED 180px!\n"
            "• Left panel: 260px (was 300px) = SAVED 40px\n"
            "• Right panel: 220px (was 280px) = SAVED 60px\n"
            "• Viewport: ~70% of screen (was ~65%) = GAINED 5%\n"
            "• Stick figure: 40% of viewport height = PERFECT RATIO\n"
            "• Total saved: 287px more for viewport!\n"
            "• Zero wasted space, everything accessible",
            "#1a4030", 7
        )
        analysis.setFixedHeight(100)
        root.addWidget(analysis)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mockup = SuperMockup()
    mockup.show()

    sys.exit(app.exec())