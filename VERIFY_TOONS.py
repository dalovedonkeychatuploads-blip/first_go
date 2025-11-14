"""
VERIFY TOONS - Final Visual Verification Before Testing
========================================================

This script shows all 3 toons side-by-side with dark background
to match reference images. Use this to verify visuals are PERFECT
before integrating into Tab 1.

WHAT TO CHECK:
1. Toon 1: DARK body (almost black), cyan glows on joints + chest
2. Toon 2: DARK body, red eyes ONLY (no joint glows), chunky
3. Toon 3: Pure black, googly eyes, minimalist
4. All have chunky feet/boots
5. T-pose is clean (arms horizontal, legs down)

Run this, verify they match your reference images, then proceed!
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QFont

from toon_anatomy import create_neon_cyan_anatomy, create_shadow_red_anatomy, create_googly_eyes_anatomy
from rigged_renderer import RiggedRenderer
from rig_system import create_t_pose_skeleton_from_anatomy


class ToonCard(QWidget):
    """Card showing a single toon with name and details"""

    def __init__(self, toon_name, anatomy, details, parent=None):
        super().__init__(parent)
        self.toon_name = toon_name
        self.anatomy = anatomy
        self.details = details
        self.renderer = RiggedRenderer(anatomy)
        self.skeleton = create_t_pose_skeleton_from_anatomy(anatomy)

        self.setMinimumSize(350, 550)
        # Dark background to match reference images
        self.setStyleSheet("background: #1a1a1e; border: 2px solid #3a3a3e; border-radius: 8px;")

    def paintEvent(self, event):
        """Render the toon card"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Center position for toon (slightly higher to leave room for text)
        cx = self.width() / 2
        cy = self.height() / 2 - 20

        # Render toon at center with scale 1.8 for better visibility
        self.renderer.render_from_skeleton(painter, self.skeleton, cx, cy, scale=1.8)

        # Draw title at top
        font_title = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font_title)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(10, 30, self.toon_name)

        # Draw details at bottom
        font_details = QFont("Arial", 10)
        painter.setFont(font_details)
        painter.setPen(QColor(180, 180, 180))
        y_offset = self.height() - 80
        for line in self.details:
            painter.drawText(10, y_offset, line)
            y_offset += 18

        painter.end()


class VerificationWindow(QWidget):
    """Main verification window with all 3 toons"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VERIFY TOONS - Match Against Reference Images")
        self.setGeometry(50, 50, 1150, 700)
        self.setStyleSheet("background: #0d0d0f;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Main title
        title = QLabel("🎯 VISUAL VERIFICATION - Compare Against Reference Images")
        title.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 15px;
            background: #2a2a2e;
            border-radius: 6px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(15)

        # Toon cards in horizontal layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        # Toon 1: Neon Cyan
        cyan_anatomy = create_neon_cyan_anatomy()
        toon1_details = [
            f"✓ {cyan_anatomy.HEADS_TALL} heads tall (sleek)",
            "✓ DARK body (almost black)",
            "✓ Cyan glows: joints + chest",
            "✓ 5-finger detailed hands",
            "✓ Chunky boots"
        ]
        self.card1 = ToonCard("TOON 1: Neon Cyan", cyan_anatomy, toon1_details)
        cards_layout.addWidget(self.card1)

        # Toon 2: Shadow Red
        red_anatomy = create_shadow_red_anatomy()
        toon2_details = [
            f"✓ {red_anatomy.HEADS_TALL} heads tall (chunky)",
            "✓ Very dark body",
            "✓ Red EYES ONLY (no joint glows)",
            "✓ Simple mitten hands",
            "✓ Wide power stance"
        ]
        self.card2 = ToonCard("TOON 2: Shadow Red", red_anatomy, toon2_details)
        cards_layout.addWidget(self.card2)

        # Toon 3: Googly Eyes
        googly_anatomy = create_googly_eyes_anatomy()
        toon3_details = [
            f"✓ {googly_anatomy.HEADS_TALL} heads tall (classic)",
            "✓ Pure black body",
            "✓ White googly eyes",
            "✓ NO gradients (flat)",
            "✓ Minimalist style"
        ]
        self.card3 = ToonCard("TOON 3: Googly Eyes", googly_anatomy, toon3_details)
        cards_layout.addWidget(self.card3)

        layout.addLayout(cards_layout)

        layout.addSpacing(15)

        # Instructions
        instructions = QLabel(
            "📋 CHECKLIST: Compare each toon against reference images (toon1.jpeg, toon2.jpeg, toon3.jpeg)\n"
            "   ✓ Body colors match (darkness level, gradients)\n"
            "   ✓ Glows in correct locations (cyan vs red vs none)\n"
            "   ✓ Proportions correct (tall vs chunky vs classic)\n"
            "   ✓ Hands match (detailed vs simple)\n"
            "   ✓ Eyes match (slits vs googly)\n\n"
            "Close window when satisfied, then proceed to Tab 1 integration!"
        )
        instructions.setStyleSheet("""
            color: #b0b0b0;
            font-size: 11px;
            padding: 15px;
            background: #1a1a1e;
            border-radius: 6px;
            line-height: 1.6;
        """)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)


def main():
    """Run verification"""
    app = QApplication(sys.argv)

    window = VerificationWindow()
    window.show()

    print("\n" + "="*70)
    print("   🎯 TOON VISUAL VERIFICATION")
    print("="*70)
    print("\n📸 Compare the rendered toons against your reference images:")
    print("   - toon1.jpeg: Neon Cyan (dark body, cyan glows)")
    print("   - toon2.jpeg: Shadow Red (dark body, red eyes)")
    print("   - toon3.jpeg: Googly Eyes (black body, googly eyes)")
    print("\n🔍 What to check:")
    print("   [x] Body darkness level (Toon 1 & 2 should be VERY dark)")
    print("   [x] Glow locations (Toon 1: joints+chest, Toon 2: eyes only)")
    print("   [x] Proportions (Toon 1: 6.5h, Toon 2: 4.2h, Toon 3: 7h)")
    print("   [x] Hand detail (Toon 1: 5 fingers, others: simple)")
    print("   [x] Feet size (all have chunky boots)")
    print("   [x] Eye style (Toon 1&2: slits, Toon 3: googly)")
    print("\n✅ If everything matches, close window and proceed!")
    print("❌ If something is off, note it and we'll fix it.")
    print("\n" + "="*70 + "\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
