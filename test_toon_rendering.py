"""
Test Toon Rendering - Quick Verification of All 3 Toons
========================================================

This test script verifies that all 3 default toons render correctly in T-pose:
- Toon 1: Neon Cyan Fighter (6.5 heads, cyan glows, 5 fingers)
- Toon 2: Shadow Red Fighter (4.2 heads, chunky, red eyes)
- Toon 3: Googly Eyes Fighter (7 heads, minimalist, googly eyes)

Run this to visually confirm proportions, colors, and features match references.
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor

from toon_anatomy import create_neon_cyan_anatomy, create_shadow_red_anatomy, create_googly_eyes_anatomy
from rigged_renderer import RiggedRenderer
from rig_system import create_t_pose_skeleton_from_anatomy


class ToonPreviewWidget(QWidget):
    """Widget that renders a single toon in T-pose"""

    def __init__(self, toon_name, anatomy, parent=None):
        super().__init__(parent)
        self.toon_name = toon_name
        self.anatomy = anatomy
        self.renderer = RiggedRenderer(anatomy)
        self.skeleton = create_t_pose_skeleton_from_anatomy(anatomy)

        self.setMinimumSize(300, 500)
        self.setStyleSheet("background: #2a2a2e;")

    def paintEvent(self, event):
        """Render the toon in T-pose"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Center of widget
        cx = self.width() / 2
        cy = self.height() / 2

        # Render toon at center with scale 1.5 for visibility
        self.renderer.render_from_skeleton(painter, self.skeleton, cx, cy, scale=1.5)

        # Draw toon name at bottom
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(10, self.height() - 10, self.toon_name)

        painter.end()


class ToonComparisonWindow(QWidget):
    """Window showing all 3 toons side by side for comparison"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toon Rendering Test - All 3 Default Toons")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background: #1a1a1e;")

        # Create layout
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("DONK STICKMAN ENGINE - 3 Default Toons (T-Pose)")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Toon previews side by side
        toon_layout = QHBoxLayout()

        # Toon 1: Neon Cyan
        cyan_anatomy = create_neon_cyan_anatomy()
        self.toon1 = ToonPreviewWidget("Toon 1: Neon Cyan (6.5 heads)", cyan_anatomy)
        toon_layout.addWidget(self.toon1)

        # Toon 2: Shadow Red
        red_anatomy = create_shadow_red_anatomy()
        self.toon2 = ToonPreviewWidget("Toon 2: Shadow Red (4.2 heads)", red_anatomy)
        toon_layout.addWidget(self.toon2)

        # Toon 3: Googly Eyes
        googly_anatomy = create_googly_eyes_anatomy()
        self.toon3 = ToonPreviewWidget("Toon 3: Googly Eyes (7.0 heads)", googly_anatomy)
        toon_layout.addWidget(self.toon3)

        layout.addLayout(toon_layout)

        # Instructions
        instructions = QLabel("Check: Proportions, Colors, Eyes, Hands, T-Pose")
        instructions.setStyleSheet("color: #808080; font-size: 12px; padding: 10px;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)


def main():
    """Run the toon rendering test"""
    app = QApplication(sys.argv)

    window = ToonComparisonWindow()
    window.show()

    print("\n" + "="*60)
    print("   TOON RENDERING TEST")
    print("="*60)
    print("\nDisplaying all 3 default toons in T-pose:")
    print("  - Toon 1 (Left): Neon Cyan - 6.5 heads, cyan glows, 5 fingers")
    print("  - Toon 2 (Middle): Shadow Red - 4.2 heads, chunky, red eyes")
    print("  - Toon 3 (Right): Googly Eyes - 7 heads, minimalist, googly eyes")
    print("\nVisually verify:")
    print("  [x] Proportions match reference images")
    print("  [x] Colors are accurate (cyan vs red vs black)")
    print("  [x] Toon 1 has detailed 5-finger hands")
    print("  [x] Toon 2 & 3 have simple hands")
    print("  [x] Eyes render correctly (slits vs googly)")
    print("  [x] T-pose is neutral (arms horizontal, legs down)")
    print("\nClose window when done.\n")
    print("="*60 + "\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
