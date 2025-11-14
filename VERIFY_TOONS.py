"""
VERIFY TOONS - Paginated Visual Verification (1 Toon Per Page)
================================================================

Shows each of the 3 default toons on separate pages with large scale
for perfect visual verification against reference images.

NAVIGATION:
- Next/Previous buttons to cycle through toons
- Page indicator shows which toon (1 of 3, 2 of 3, 3 of 3)

WHAT TO CHECK PER TOON:
1. Toon 1 (Neon Cyan): DARK body, cyan glows on joints + chest, 5 fingers
2. Toon 2 (Shadow Red): DARK body, red eyes ONLY, chunky proportions
3. Toon 3 (Googly Eyes): Pure black, googly eyes, minimalist

Press Next to compare each toon against its reference image!
"""

import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                                QLabel, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QFont

from toon_anatomy import create_neon_cyan_anatomy, create_shadow_red_anatomy, create_googly_eyes_anatomy
from rigged_renderer import RiggedRenderer
from rig_system import create_t_pose_skeleton_from_anatomy


class ToonDisplayPage(QWidget):
    """Full-page display for a single toon with large scale"""

    def __init__(self, toon_name, anatomy, checklist, reference_file, parent=None):
        super().__init__(parent)
        self.toon_name = toon_name
        self.anatomy = anatomy
        self.checklist = checklist
        self.reference_file = reference_file
        self.renderer = RiggedRenderer(anatomy)
        self.skeleton = create_t_pose_skeleton_from_anatomy(anatomy)

        self.setMinimumSize(1100, 750)  # Larger canvas for full toon
        self.setStyleSheet("background: #0d0d0f;")

    def paintEvent(self, event):
        """Render the full-page toon display"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ===== HEADER SECTION =====
        header_height = 80

        # Draw header background
        painter.fillRect(0, 0, self.width(), header_height, QColor(42, 42, 46))

        # Draw toon name (left side)
        font_title = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(font_title)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(30, 45, self.toon_name)

        # Draw reference filename (right side)
        font_ref = QFont("Arial", 14)
        painter.setFont(font_ref)
        painter.setPen(QColor(100, 200, 255))
        ref_text = f"📸 Compare with: {self.reference_file}"
        ref_width = painter.fontMetrics().horizontalAdvance(ref_text)
        painter.drawText(self.width() - ref_width - 30, 45, ref_text)

        # ===== MAIN DISPLAY AREA =====
        display_top = header_height + 20
        display_height = self.height() - header_height - 180  # Leave room for footer

        # Dark background for toon display
        painter.fillRect(20, display_top, self.width() - 40, display_height, QColor(26, 26, 30))

        # ===== COMPUTE REAL BOUNDING BOX FROM SKELETON =====
        # Get all joint positions in world space (before scaling)
        transforms = self.skeleton.get_joint_transforms()

        if not transforms:
            # Fallback if no transforms
            cx = self.width() / 2
            cy = display_top + display_height / 2
            self.renderer.render_from_skeleton(painter, self.skeleton, cx, cy, scale=1.0)
            painter.end()
            return

        # Find bounding box of all joints
        all_x = [pos[0] for pos in transforms.values()]
        all_y = [pos[1] for pos in transforms.values()]

        world_min_x = min(all_x)
        world_max_x = max(all_x)
        world_min_y = min(all_y)
        world_max_y = max(all_y)

        world_width = world_max_x - world_min_x
        world_height = world_max_y - world_min_y

        # World-space center of character
        world_center_x = (world_min_x + world_max_x) / 2
        world_center_y = (world_min_y + world_max_y) / 2

        # ===== CALCULATE SCALE TO FIT ENTIRE TOON =====
        # Available display area (with padding)
        display_left = 20
        display_rect_width = self.width() - 40
        display_rect_height = display_height

        # Use 85% of available space to leave margins
        usable_width = display_rect_width * 0.85
        usable_height = display_rect_height * 0.85

        # Calculate scale to fit width AND height
        scale_x = usable_width / world_width if world_width > 0 else 1.0
        scale_y = usable_height / world_height if world_height > 0 else 1.0

        # Use the smaller scale to ensure BOTH dimensions fit
        scale = min(scale_x, scale_y)

        # Cap at 3.0 to avoid absurd zoom, but NO lower limit (allow < 1.0 if needed)
        scale = min(3.0, scale)

        # ===== POSITION TOON IN CENTER OF DISPLAY AREA =====
        # Screen center of display area
        screen_center_x = self.width() / 2
        screen_center_y = display_top + display_height / 2

        # Offset to center the world-space center of the character
        # We want: screen_center = render_origin + (world_center * scale)
        # So: render_origin = screen_center - (world_center * scale)
        cx = screen_center_x - (world_center_x * scale)
        cy = screen_center_y - (world_center_y * scale)

        # Render with calculated scale and position
        self.renderer.render_from_skeleton(painter, self.skeleton, cx, cy, scale=scale)

        # ===== CHECKLIST SECTION =====
        checklist_top = display_top + display_height + 15

        # Draw checklist background
        painter.fillRect(20, checklist_top, self.width() - 40, 140, QColor(26, 26, 30))

        # Draw "VERIFICATION CHECKLIST" header
        font_checklist_header = QFont("Arial", 14, QFont.Weight.Bold)
        painter.setFont(font_checklist_header)
        painter.setPen(QColor(255, 200, 0))
        painter.drawText(35, checklist_top + 25, "🔍 VERIFICATION CHECKLIST:")

        # Draw checklist items
        font_checklist = QFont("Arial", 12)
        painter.setFont(font_checklist)
        painter.setPen(QColor(180, 180, 180))

        y_offset = checklist_top + 50
        for item in self.checklist:
            painter.drawText(50, y_offset, item)
            y_offset += 22

        painter.end()


class PaginatedVerificationWindow(QWidget):
    """Main window with paginated toon display (1 toon per page)"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VERIFY TOONS - Paginated Visual Verification")
        self.setGeometry(50, 50, 1200, 900)  # LARGER window for full toon visibility
        self.setStyleSheet("background: #0d0d0f;")

        self.current_page = 0  # Track current toon (0, 1, or 2)

        # ===== CREATE TOON DATA =====

        # Toon 1: Neon Cyan
        cyan_anatomy = create_neon_cyan_anatomy()
        toon1_checklist = [
            f"✓ Height: {cyan_anatomy.HEADS_TALL} heads tall (sleek athletic build)",
            "✓ Body: VERY DARK gray (almost black) - NOT medium gray!",
            "✓ Cyan glows on ALL joints (shoulders, elbows, wrists, hips, knees, ankles)",
            "✓ Cyan glow in center of chest/torso",
            "✓ Hands: 5 detailed fingers visible",
            "✓ Feet: Chunky boots (large, rounded)"
        ]

        # Toon 2: Shadow Red
        red_anatomy = create_shadow_red_anatomy()
        toon2_checklist = [
            f"✓ Height: {red_anatomy.HEADS_TALL} heads tall (chunky muscular build)",
            "✓ Body: Very dark (darker than Toon 1)",
            "✓ Red slit eyes ONLY - NO joint glows anywhere else",
            "✓ Hands: Simple mitten style (NO fingers)",
            "✓ Proportions: Wide shoulders, thick limbs (power stance)",
            "✓ Feet: Large chunky boots"
        ]

        # Toon 3: Googly Eyes
        googly_anatomy = create_googly_eyes_anatomy()
        toon3_checklist = [
            f"✓ Height: {googly_anatomy.HEADS_TALL} heads tall (classic stickman)",
            "✓ Body: Pure BLACK (no gradients, flat color only)",
            "✓ Eyes: White googly cartoon eyes (large circles)",
            "✓ NO glows anywhere (minimalist style)",
            "✓ Hands: Simple mitten style",
            "✓ Clean minimalist silhouette"
        ]

        # Store toon pages data
        self.pages = [
            {
                "name": "TOON 1: Neon Cyan Fighter",
                "anatomy": cyan_anatomy,
                "checklist": toon1_checklist,
                "reference": "toon1.jpeg"
            },
            {
                "name": "TOON 2: Shadow Red Fighter",
                "anatomy": red_anatomy,
                "checklist": toon2_checklist,
                "reference": "toon2.jpeg"
            },
            {
                "name": "TOON 3: Googly Eyes Fighter",
                "anatomy": googly_anatomy,
                "checklist": toon3_checklist,
                "reference": "toon3.jpeg"
            }
        ]

        # ===== CREATE UI =====

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toon display area (takes most of the space)
        self.display_widget = ToonDisplayPage(
            self.pages[0]["name"],
            self.pages[0]["anatomy"],
            self.pages[0]["checklist"],
            self.pages[0]["reference"]
        )
        layout.addWidget(self.display_widget)

        # Navigation bar at bottom
        nav_bar = QWidget()
        nav_bar.setStyleSheet("background: #1a1a1e;")
        nav_bar.setFixedHeight(70)

        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(30, 15, 30, 15)

        # Previous button
        self.btn_prev = QPushButton("◀ Previous")
        self.btn_prev.setStyleSheet("""
            QPushButton {
                background: #3a3a3e;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 30px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #4a4a4e;
            }
            QPushButton:disabled {
                background: #2a2a2e;
                color: #606060;
            }
        """)
        self.btn_prev.clicked.connect(self.go_to_previous)
        nav_layout.addWidget(self.btn_prev)

        # Page indicator (center)
        self.page_label = QLabel()
        self.page_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
        """)
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.page_label, 1)  # Stretch to fill center

        # Next button
        self.btn_next = QPushButton("Next ▶")
        self.btn_next.setStyleSheet("""
            QPushButton {
                background: #0066cc;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 30px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #0077ee;
            }
            QPushButton:disabled {
                background: #2a2a2e;
                color: #606060;
            }
        """)
        self.btn_next.clicked.connect(self.go_to_next)
        nav_layout.addWidget(self.btn_next)

        layout.addWidget(nav_bar)

        # Update UI for initial page
        self.update_page_display()

    def go_to_next(self):
        """Navigate to next toon"""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.update_page_display()

    def go_to_previous(self):
        """Navigate to previous toon"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page_display()

    def update_page_display(self):
        """Update display for current page"""
        page_data = self.pages[self.current_page]

        # Update display widget with new toon data
        self.display_widget.toon_name = page_data["name"]
        self.display_widget.anatomy = page_data["anatomy"]
        self.display_widget.checklist = page_data["checklist"]
        self.display_widget.reference_file = page_data["reference"]
        self.display_widget.renderer = RiggedRenderer(page_data["anatomy"])
        self.display_widget.skeleton = create_t_pose_skeleton_from_anatomy(page_data["anatomy"])
        self.display_widget.update()  # Trigger repaint

        # Update page indicator
        self.page_label.setText(f"Toon {self.current_page + 1} of {len(self.pages)}")

        # Update button states
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < len(self.pages) - 1)


def main():
    """Run paginated verification"""
    app = QApplication(sys.argv)

    window = PaginatedVerificationWindow()
    window.show()

    print("\n" + "="*70)
    print("   🎯 PAGINATED TOON VERIFICATION")
    print("="*70)
    print("\n✨ NEW DESIGN: One toon per page with LARGE scale!")
    print("\n📋 Instructions:")
    print("   1. Compare the rendered toon against its reference image")
    print("   2. Check ALL items in the verification checklist")
    print("   3. Press 'Next' to verify the next toon")
    print("   4. Go through all 3 toons systematically")
    print("\n📸 Reference Images:")
    print("   - Page 1: toon1.jpeg (Neon Cyan - dark body, cyan glows)")
    print("   - Page 2: toon2.jpeg (Shadow Red - dark body, red eyes only)")
    print("   - Page 3: toon3.jpeg (Googly Eyes - pure black, googly eyes)")
    print("\n🔍 LARGE SCALE (3.5x) - You can see every detail!")
    print("   - Glow effects are clearly visible")
    print("   - 5-finger hands on Toon 1 are distinct")
    print("   - Body darkness levels are accurate")
    print("   - Chunky boots are prominent")
    print("\n✅ If all 3 toons match references perfectly, you're ready!")
    print("❌ If something looks wrong, note which toon and what's off.")
    print("\n" + "="*70 + "\n")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
