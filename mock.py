#!/usr/bin/env python3
"""
DONK Stickman Engine - Shadow Red Fighter Mock
Second toon style - Dark demon with red accents
"""

import sys
sys.dont_write_bytecode = True

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QRadialGradient
import math


class ShadowRedFighter(QWidget):
    """Shadow Red demon fighter style."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shadow Red Fighter - Second Toon")
        self.setFixedSize(900, 900)
        # Grey background like reference
        self.setStyleSheet("background: #7a7a7e;")
        self.current_style = "shadow_red"

    def paintEvent(self, event):
        """Draw the fighter with EXACT proportions."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Center point
        cx = self.width() / 2
        cy = self.height() / 2 - 30

        # EXACT MEASUREMENTS (same proportions as Neon)
        HEAD_DIAMETER = 180
        TORSO_WIDTH = 90
        TORSO_HEIGHT = 220
        ARM_THICKNESS = 22
        LEG_THICKNESS = 28
        UPPER_ARM_LENGTH = 165
        LOWER_ARM_LENGTH = 165
        THIGH_LENGTH = 220
        SHIN_LENGTH = 220
        FOOT_WIDTH = 100
        FOOT_HEIGHT = 60
        NECK_HEIGHT = 18
        JOINT_SIZE = 24  # Smaller for Shadow style
        GLOW_RADIUS = 8   # Smaller glow

        # Scale
        scale = 0.8

        # Apply scale
        head_d = HEAD_DIAMETER * scale
        torso_w = TORSO_WIDTH * scale
        torso_h = TORSO_HEIGHT * scale
        arm_thick = ARM_THICKNESS * scale
        leg_thick = LEG_THICKNESS * scale
        upper_arm = UPPER_ARM_LENGTH * scale
        lower_arm = LOWER_ARM_LENGTH * scale
        thigh = THIGH_LENGTH * scale
        shin = SHIN_LENGTH * scale
        foot_w = FOOT_WIDTH * scale
        foot_h = FOOT_HEIGHT * scale
        neck_h = NECK_HEIGHT * scale
        joint_size = JOINT_SIZE * scale
        glow_r = GLOW_RADIUS * scale

        # Define key positions
        head_center = cy - torso_h/2 - neck_h - head_d/2
        chest_top = cy - torso_h/2
        pelvis = cy + torso_h/2

        # SHADOW RED COLORS
        body_color = QColor(10, 10, 10)  # Pure black like reference
        eye_color = QColor(255, 0, 0)  # Bright red eyes

        # Draw shadow (standard)
        shadow_color = QColor(0, 0, 0, 80)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        shadow_y = pelvis + thigh + shin + foot_h/2
        painter.drawEllipse(QPointF(cx, shadow_y + 10), foot_w * 1.5, 15)

        # DRAW FEET (same as Neon - wedge blocks)
        self.draw_foot(painter, cx - 30 * scale, pelvis + thigh + shin,
                      foot_w, foot_h, body_color, True)
        self.draw_foot(painter, cx + 30 * scale, pelvis + thigh + shin,
                      foot_w, foot_h, body_color, False)

        # DRAW LEGS (same as Neon)
        self.draw_limb(painter, cx - 20 * scale, pelvis,
                      cx - 25 * scale, pelvis + thigh,
                      leg_thick, body_color)
        self.draw_limb(painter, cx - 25 * scale, pelvis + thigh,
                      cx - 30 * scale, pelvis + thigh + shin,
                      leg_thick, body_color)
        self.draw_limb(painter, cx + 20 * scale, pelvis,
                      cx + 25 * scale, pelvis + thigh,
                      leg_thick, body_color)
        self.draw_limb(painter, cx + 25 * scale, pelvis + thigh,
                      cx + 30 * scale, pelvis + thigh + shin,
                      leg_thick, body_color)

        # DRAW TORSO (same rounded capsule as Neon)
        self.draw_torso(painter, cx, chest_top, torso_w, torso_h, body_color)

        # DRAW ARMS (same T-pose as Neon)
        shoulder_l_x = cx - torso_w/2
        shoulder_l_y = chest_top + 30 * scale
        elbow_l_x = shoulder_l_x - upper_arm
        elbow_l_y = shoulder_l_y
        wrist_l_x = elbow_l_x - lower_arm
        wrist_l_y = shoulder_l_y

        shoulder_r_x = cx + torso_w/2
        shoulder_r_y = chest_top + 30 * scale
        elbow_r_x = shoulder_r_x + upper_arm
        elbow_r_y = shoulder_r_y
        wrist_r_x = elbow_r_x + lower_arm
        wrist_r_y = shoulder_r_y

        self.draw_limb(painter, shoulder_l_x, shoulder_l_y, elbow_l_x, elbow_l_y,
                      arm_thick, body_color)
        self.draw_limb(painter, elbow_l_x, elbow_l_y, wrist_l_x, wrist_l_y,
                      arm_thick, body_color)
        self.draw_limb(painter, shoulder_r_x, shoulder_r_y, elbow_r_x, elbow_r_y,
                      arm_thick, body_color)
        self.draw_limb(painter, elbow_r_x, elbow_r_y, wrist_r_x, wrist_r_y,
                      arm_thick, body_color)

        # Draw neck
        self.draw_limb(painter, cx, chest_top, cx, chest_top - neck_h,
                      arm_thick * 0.8, body_color)

        # Draw head (same size as Neon)
        self.draw_head(painter, cx, head_center, head_d, body_color)

        # NO JOINT DOTS - Shadow Red is clean

        # Draw glowing red eyes (ONLY red accent)
        self.draw_red_eyes(painter, cx, head_center, head_d, eye_color)

    def draw_limb(self, painter, x1, y1, x2, y2, thickness, color):
        """Draw thick cylindrical limb (same as Neon)."""
        # Edge highlight for visibility
        edge_pen = QPen(QColor(30, 30, 35), thickness + 2, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(edge_pen)
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Main limb
        pen = QPen(color, thickness, Qt.PenStyle.SolidLine,
                  Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def draw_torso(self, painter, cx, top_y, width, height, color):
        """Draw rounded capsule torso (same as Neon)."""
        # Edge highlight
        painter.setPen(QPen(QColor(30, 30, 35), 2))
        painter.setBrush(QBrush(QColor(30, 30, 35)))
        torso_rect_edge = QRectF(cx - width/2 - 1, top_y - 1, width + 2, height + 2)
        painter.drawRoundedRect(torso_rect_edge, width/3, width/3)

        # Main torso
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        torso_rect = QRectF(cx - width/2, top_y, width, height)
        painter.drawRoundedRect(torso_rect, width/3, width/3)

    def draw_foot(self, painter, x, y, width, height, color, is_left):
        """Draw wedge-shaped foot (same as Neon)."""
        # Edge highlight
        painter.setPen(QPen(QColor(30, 30, 35), 2))
        painter.setBrush(QBrush(QColor(30, 30, 35)))

        path = QPainterPath()
        if is_left:
            path.moveTo(x - width/3 - 1, y - 1)
            path.lineTo(x + width/3 + 1, y - 1)
            path.lineTo(x + width/2 + 1, y + height + 1)
            path.lineTo(x - width/2 - 1, y + height + 1)
        else:
            path.moveTo(x + width/3 + 1, y - 1)
            path.lineTo(x - width/3 - 1, y - 1)
            path.lineTo(x - width/2 - 1, y + height + 1)
            path.lineTo(x + width/2 + 1, y + height + 1)
        path.closeSubpath()
        painter.drawPath(path)

        # Main foot
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        path = QPainterPath()
        if is_left:
            path.moveTo(x - width/3, y)
            path.lineTo(x + width/3, y)
            path.lineTo(x + width/2, y + height)
            path.lineTo(x - width/2, y + height)
        else:
            path.moveTo(x + width/3, y)
            path.lineTo(x - width/3, y)
            path.lineTo(x - width/2, y + height)
            path.lineTo(x + width/2, y + height)
        path.closeSubpath()
        painter.drawPath(path)

    def draw_head(self, painter, cx, cy, diameter, color):
        """Draw matte head (same as Neon)."""
        # Edge highlight
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(30, 30, 35)))
        painter.drawEllipse(QPointF(cx, cy), diameter/2 + 1, diameter/2 + 1)

        # Main head
        painter.setBrush(QBrush(color))
        painter.drawEllipse(QPointF(cx, cy), diameter/2, diameter/2)

    def draw_red_eyes(self, painter, cx, cy, head_diameter, color):
        """Draw glowing red eyes (only visual difference from Neon)."""
        eye_width = head_diameter * 0.35
        eye_y = cy - head_diameter * 0.1

        # Left eye
        left_eye_x = cx - eye_width/3
        self.draw_glowing_eye(painter, left_eye_x, eye_y, eye_width/4, color)

        # Right eye
        right_eye_x = cx + eye_width/3
        self.draw_glowing_eye(painter, right_eye_x, eye_y, eye_width/4, color)

    def draw_glowing_eye(self, painter, x, y, radius, color):
        """Draw single glowing red eye."""
        # Outer glow
        gradient = QRadialGradient(QPointF(x, y), radius * 3)
        gradient.setColorAt(0, QColor(255, 0, 0, 120))
        gradient.setColorAt(0.3, QColor(255, 0, 0, 60))
        gradient.setColorAt(0.6, QColor(200, 0, 0, 30))
        gradient.setColorAt(1, QColor(100, 0, 0, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(x, y), radius * 3, radius * 3)

        # Bright core
        painter.setBrush(QColor(255, 0, 0, 255))
        painter.drawEllipse(QPointF(x, y), radius, radius)

        # White hot center
        painter.setBrush(QColor(255, 150, 150, 255))
        painter.drawEllipse(QPointF(x, y), radius/3, radius/3)


class ToonSwitcher(QWidget):
    """Widget to switch between toon styles."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DONK Fighter Styles - Mock")
        self.setFixedSize(900, 950)

        layout = QVBoxLayout()

        # Create viewport
        self.viewport = ShadowRedFighter()
        layout.addWidget(self.viewport)

        # Style buttons
        button_layout = QHBoxLayout()

        neon_btn = QPushButton("Neon Cyan")
        neon_btn.clicked.connect(lambda: self.switch_style("neon"))
        button_layout.addWidget(neon_btn)

        shadow_btn = QPushButton("Shadow Red")
        shadow_btn.clicked.connect(lambda: self.switch_style("shadow"))
        button_layout.addWidget(shadow_btn)

        classic_btn = QPushButton("Classic Capsule")
        classic_btn.clicked.connect(lambda: self.switch_style("classic"))
        button_layout.addWidget(classic_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def switch_style(self, style):
        """Switch between styles (placeholder for now)."""
        print(f"Switching to {style} style")


def main():
    """Run the Shadow Red mock."""
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("DONK Shadow Red Fighter - Second Toon")
    window.setStyleSheet("""
        QMainWindow {
            background: #0a0a0e;
        }
    """)

    viewport = ShadowRedFighter()
    window.setCentralWidget(viewport)
    window.resize(900, 900)
    window.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())