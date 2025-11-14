"""
FINAL PERFECTED UI MOCKUP
LEFT = WHAT (character properties)
RIGHT = ACTIONS (save/load/operations)
Perfect viewport size with ruler
Sexy, professional color scheme
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient

class ProPanel(QFrame):
    """Professional panel with gradient effects."""

    def __init__(self, content, bg_color="#2a2a35", accent=None, text_size=8, parent=None):
        super().__init__(parent)
        self.content = content
        self.text_size = text_size
        self.accent = accent
        self.bg_color = bg_color

        # Professional styling
        if accent == "blue":
            self.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #3a5a8a, stop:1 #2a4a7a);
                    border: 1px solid #4a6a9a;
                    border-radius: 4px;
                }}
            """)
        elif accent == "green":
            self.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2a5a4a, stop:1 #1a4a3a);
                    border: 1px solid #3a6a5a;
                    border-radius: 3px;
                }}
            """)
        elif accent == "dark":
            self.setStyleSheet(f"""
                QFrame {{
                    background: #1a1a20;
                    border: 1px solid #2a2a30;
                    border-radius: 2px;
                }}
            """)
        elif accent == "selected":
            self.setStyleSheet(f"""
                QFrame {{
                    background: #3a4a5a;
                    border: 2px solid #5a7a9a;
                    border-radius: 6px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background: {bg_color};
                    border: 1px solid #3a3a40;
                    border-radius: 3px;
                }}
            """)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Text color based on accent
        if self.accent in ["blue", "green"]:
            painter.setPen(QPen(QColor(230, 235, 240), 1))
        elif self.accent == "selected":
            painter.setPen(QPen(QColor(100, 200, 255), 1))
        else:
            painter.setPen(QPen(QColor(180, 185, 190), 1))

        painter.setFont(QFont("Segoe UI", self.text_size))

        # Draw content
        rect = self.rect().adjusted(8, 6, -8, -6)
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self.content)


class FinalMockup(QWidget):
    """The final, perfect layout."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("DONK Animation Studio - Stick Figure Maker [FINAL DESIGN]")
        self.setGeometry(50, 50, 1450, 820)

        # Dark professional background
        self.setStyleSheet("background: #16161a;")

        # Root
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        # ═══════════════════════════════════════════════════════════
        # MAIN HORIZONTAL LAYOUT
        # ═══════════════════════════════════════════════════════════
        main_h = QHBoxLayout()
        main_h.setSpacing(4)

        # ╔══════════════════════════════════╗
        # ║ LEFT: WHAT (Character Definition)║
        # ╚══════════════════════════════════╝
        left_container = QVBoxLayout()
        left_container.setSpacing(3)

        # ─── Sexy Character Selector (Top) ───
        char_selector = QFrame()
        char_selector.setFixedSize(320, 100)
        char_selector.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a35, stop:1 #1f1f25);
                border: 1px solid #3a3a45;
                border-radius: 6px;
            }
        """)

        selector_content = ProPanel(
            " SELECT CHARACTER STYLE\n"
            " ━━━━━━━━━━━━━━━━━━━━━\n"
            "   ┌────┐  ┌────┐  ┌────┐\n"
            "   │ 👁  │  │ 👁  │  │ ⚪  │\n"
            "   │ /|\\ │  │ /|\\ │  │ /|\\ │\n"
            "   │ / \\ │  │ / \\ │  │ / \\ │\n"
            "   └────┘  └────┘  └────┘\n"
            "    NEON   SHADOW  CLASSIC\n"
            "      ●       ○       ○",
            accent="selected", text_size=9
        )
        char_selector.setLayout(QVBoxLayout())
        char_selector.layout().addWidget(selector_content)
        char_selector.layout().setContentsMargins(0, 0, 0, 0)

        left_container.addWidget(char_selector)

        # ─── Character Properties (WHAT) ───
        properties = ProPanel(
            "╔═ CHARACTER PROPERTIES ═╗\n"
            "\n"
            "▼ BODY PROPORTIONS\n"
            "  Overall Height   ▬▬▬●▬▬▬ 100%\n"
            "  Overall Scale    ▬▬●▬▬▬▬  85%\n"
            "  \n"
            "  Head Size        ▬▬▬●▬▬▬ 100%\n"
            "  Neck Length      ▬▬●▬▬▬▬  90%\n"
            "  Torso Height     ▬▬▬●▬▬▬ 100%\n"
            "  Shoulder Width   ▬▬●▬▬▬▬  95%\n"
            "  \n"
            "  Arm Length       ▬▬▬▬●▬▬ 110%\n"
            "  Arm Thickness    ▬▬●▬▬▬▬  90%\n"
            "  Hand Size        ▬●▬▬▬▬▬  85%\n"
            "  \n"
            "  Leg Length       ▬▬▬●▬▬▬ 100%\n"
            "  Leg Thickness    ▬▬●▬▬▬▬  95%\n"
            "  Foot Size        ▬▬●▬▬▬▬  90%\n"
            "\n"
            "▼ COLORS & MATERIALS\n"
            "  Joint Color     [■ Cyan  ▼]\n"
            "  Joint Glow      ▬▬▬●▬▬▬  ON\n"
            "  \n"
            "  Eye Color       [■ Cyan  ▼]\n"
            "  Eye Style       [Slits   ▼]\n"
            "  \n"
            "  Body Color      [■ Black ▼]\n"
            "  Body Opacity    ▬▬▬▬▬●▬ 100%\n"
            "  \n"
            "  Outline         [□ None  ▼]\n"
            "\n"
            "▼ TEAM COLORS\n"
            "  Primary:   ■ ■ ■ ■ ■ ■ +\n"
            "  Secondary: □ □ □ □ □ □ +",
            "#242430", text_size=7
        )
        properties.setFixedWidth(320)

        left_container.addWidget(properties)

        # Quick adjustments
        quick_adjust = ProPanel(
            "[Reset All] [Randomize] [Mirror L↔R]",
            accent="dark", text_size=7
        )
        quick_adjust.setFixedSize(320, 32)
        left_container.addWidget(quick_adjust)

        main_h.addLayout(left_container)

        # ╔════════════════════════════════╗
        # ║ CENTER: VIEWPORT WITH RULER    ║
        # ╚════════════════════════════════╝
        center_container = QVBoxLayout()
        center_container.setSpacing(2)

        # View control bar
        view_controls = ProPanel(
            "View: [Front] [Side] [Top] [●3D]  |  Zoom: 100% [Reset]  |  Grid: ☑  Depth: ☑  Shadows: ☑",
            "#1a1a22", text_size=7
        )
        view_controls.setFixedHeight(26)
        center_container.addWidget(view_controls)

        # Viewport with ruler
        viewport_frame = QFrame()
        viewport_frame.setStyleSheet("""
            QFrame {
                background: #22222a;
                border: 2px solid #32323a;
                border-radius: 4px;
            }
        """)

        viewport_layout = QHBoxLayout(viewport_frame)
        viewport_layout.setContentsMargins(0, 0, 0, 0)
        viewport_layout.setSpacing(0)

        # Height ruler (left side)
        ruler = ProPanel(
            "200┤\n"
            "   │\n"
            "180┤\n"
            "   │\n"
            "160┤\n"
            "   │\n"
            "140┤\n"
            "   │\n"
            "120┤\n"
            "   │\n"
            "100┤\n"
            "   │\n"
            " 80┤\n"
            "   │\n"
            " 60┤\n"
            "   │\n"
            " 40┤\n"
            "   │\n"
            " 20┤\n"
            "   │\n"
            "  0└",
            "#1a1a22", text_size=6
        )
        ruler.setFixedWidth(35)
        viewport_layout.addWidget(ruler)

        # Main viewport area
        viewport = ProPanel(
            "\n\n\n\n\n"
            "                    ╔═══════════════════════╗\n"
            "                    ║                       ║\n"
            "                    ║         ◉             ║  ← 180cm\n"
            "                    ║        ╱│╲            ║\n"
            "                    ║       ╱ │ ╲           ║\n"
            "                    ║      ●  │  ●          ║\n"
            "                    ║        ─┼─            ║  ← 120cm\n"
            "                    ║         │             ║\n"
            "                    ║         │             ║\n"
            "                    ║        ╱ ╲            ║\n"
            "                    ║       ╱   ╲           ║  ← 60cm\n"
            "                    ║      ●     ●          ║\n"
            "                    ║     ╱       ╲         ║\n"
            "                    ║    ╱         ╲        ║\n"
            "                    ║   ▼           ▼       ║  ← 0cm\n"
            "                    ╚═══════════════════════╝\n\n"
            "              Figure Height: 180cm (6 feet)\n"
            "              Perfect default size for work",
            "#26262e", text_size=8
        )
        viewport_layout.addWidget(viewport)

        center_container.addWidget(viewport_frame)

        # Status bar
        status = ProPanel(
            "Position: (0, 0, 0)  |  Rotation: 0°  |  Scale: 1.0  |  Bones: 15  |  60 FPS",
            "#1a1a22", text_size=6
        )
        status.setFixedHeight(22)
        center_container.addWidget(status)

        main_h.addLayout(center_container, 1)

        # ╔═════════════════════════════════╗
        # ║ RIGHT: ACTIONS (What to DO)     ║
        # ╚═════════════════════════════════╝
        right_container = QVBoxLayout()
        right_container.setSpacing(3)

        # Character Management
        char_mgmt = ProPanel(
            "═ CHARACTER LIBRARY ═\n"
            "\n"
            "Current: Hero_Blue\n"
            "\n"
            "[▼ Load Character...]\n"
            "├─ Hero_Blue\n"
            "├─ Enemy_Red\n"
            "├─ Boss_Shadow\n"
            "├─ NPC_Green\n"
            "└─ + New Character\n"
            "\n"
            "[📁 Import] [💾 Export]\n"
            "[📋 Duplicate] [🗑 Delete]",
            "#2a2a35", text_size=7
        )
        char_mgmt.setFixedSize(240, 200)
        right_container.addWidget(char_mgmt)

        # Rigging & Advanced
        rigging = ProPanel(
            "═ RIGGING TOOLS ═\n"
            "\n"
            "[⚙ Bone Constraints]\n"
            "[🔗 IK Chain Setup]\n"
            "[📐 Auto-Rig]\n"
            "[🎯 Test Pose]\n"
            "\n"
            "═ EXPORT OPTIONS ═\n"
            "\n"
            "Format: [Spine JSON ▼]\n"
            "Scale:  [1.0x ▼]\n"
            "[📤 Export Settings]",
            "#2a2530", text_size=7
        )
        rigging.setFixedSize(240, 180)
        right_container.addWidget(rigging)

        right_container.addStretch()

        # Main action buttons
        create_btn = ProPanel(
            "\n      CREATE FIGURE\n",
            accent="blue", text_size=10
        )
        create_btn.setFixedSize(240, 45)
        right_container.addWidget(create_btn)

        send_btn = ProPanel(
            "  Send to Animation →",
            accent="green", text_size=9
        )
        send_btn.setFixedSize(240, 35)
        right_container.addWidget(send_btn)

        main_h.addLayout(right_container)

        root.addLayout(main_h)

        # ═══════════════════════════════════════════════════════════
        # KEY IMPROVEMENTS (Remove in final)
        # ═══════════════════════════════════════════════════════════
        improvements = ProPanel(
            "FINAL DESIGN IMPROVEMENTS:\n"
            "• LEFT = WHAT: All character properties & colors (define the character)\n"
            "• RIGHT = ACTIONS: Save/Load/Export/Rigging (do things with character)\n"
            "• TOP-LEFT: Clean 3-character style selector with visual preview\n"
            "• VIEWPORT: Perfect size with height ruler (0-200cm scale)\n"
            "• COLORS: Professional dark theme with blue/green accents\n"
            "• FIGURE SIZE: ~40% of viewport = ideal working size\n"
            "• Zero clutter, maximum clarity, sexy design",
            accent="green", text_size=7
        )
        improvements.setFixedHeight(80)
        root.addWidget(improvements)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Dark theme
    app.setStyle("Fusion")

    mockup = FinalMockup()
    mockup.show()

    sys.exit(app.exec())