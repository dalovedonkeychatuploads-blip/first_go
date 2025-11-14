"""
Shadow Red Fighter - Toon 2
Chunky demon-boss style with glowing red slit eyes
Reference-matched: Compact toy proportions (4.2 heads tall)
VISUALS PRESERVED - This code is perfect, DO NOT change rendering
"""

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QLinearGradient,
                           QRadialGradient, QPainterPath)
import math


class ShadowRedFighter:
    """
    Shadow Red Fighter - Chunky boss proportions
    All rendering code extracted from working implementation
    VISUALS ARE PERFECT - preserved exactly as is
    """

    # ===== PROPORTIONS (4.2 heads tall - chunky toy proportions) =====
    HEAD_RADIUS = 60          # Base size
    TORSO_WIDTH = 108         # 1.8× head (SHORT and WIDE)
    TORSO_HEIGHT = 84         # 1.4× head
    UPPER_ARM_LENGTH = 45     # 0.75× head (STUBBY)
    LOWER_ARM_LENGTH = 42     # 0.70× head
    ARM_THICKNESS = 21        # 0.35× head
    UPPER_LEG_LENGTH = 54     # 0.9× head
    LOWER_LEG_LENGTH = 48     # 0.8× head
    LEG_THICKNESS = 23        # 0.38× head
    JOINT_RADIUS = 18         # 0.30× head
    HAND_WIDTH = 28
    HAND_HEIGHT = 35
    FOOT_WIDTH = 32
    FOOT_HEIGHT = 25
    NECK_GAP = 6              # 0.1× head

    def __init__(self):
        """Initialize Shadow Red Fighter"""
        pass

    def render(self, painter, cx, cy, scale):
        """
        Main render method - draws complete Shadow Red fighter
        PERFECT VISUALS - preserved from working implementation

        Args:
            painter: QPainter instance
            cx, cy: Center position
            scale: Scale multiplier
        """
        # Scale all proportions
        s = scale
        head_r = self.HEAD_RADIUS * s
        torso_w = self.TORSO_WIDTH * s
        torso_h = self.TORSO_HEIGHT * s
        upper_arm_len = self.UPPER_ARM_LENGTH * s
        lower_arm_len = self.LOWER_ARM_LENGTH * s
        arm_thick = self.ARM_THICKNESS * s
        upper_leg_len = self.UPPER_LEG_LENGTH * s
        lower_leg_len = self.LOWER_LEG_LENGTH * s
        leg_thick = self.LEG_THICKNESS * s
        joint_r = self.JOINT_RADIUS * s
        hand_w = self.HAND_WIDTH * s
        hand_h = self.HAND_HEIGHT * s
        foot_w = self.FOOT_WIDTH * s
        foot_h = self.FOOT_HEIGHT * s
        neck_gap = self.NECK_GAP * s

        # Calculate key positions (bottom-up)
        feet_y = cy + upper_leg_len + lower_leg_len
        ankle_y = feet_y
        knee_y = ankle_y - lower_leg_len
        hip_y = knee_y - upper_leg_len
        torso_center_y = hip_y - torso_h / 2
        shoulder_y = hip_y - torso_h
        head_center_y = shoulder_y - neck_gap - head_r

        # Draw soft drop shadow
        self._draw_shadow_soft(painter, cx, feet_y + foot_h/2, torso_w * 1.5, 0.30)

        # Draw feet (chunky blocky boots)
        self._draw_shadow_foot(painter, cx - leg_thick*0.6, ankle_y, foot_w, foot_h, True)
        self._draw_shadow_foot(painter, cx + leg_thick*0.6, ankle_y, foot_w, foot_h, False)

        # Draw legs (thick capsules)
        self._draw_shadow_limb(painter, cx - leg_thick*0.6, hip_y,
                              cx - leg_thick*0.6, knee_y, leg_thick)
        self._draw_shadow_limb(painter, cx - leg_thick*0.6, knee_y,
                              cx - leg_thick*0.6, ankle_y, leg_thick * 0.92)
        self._draw_shadow_limb(painter, cx + leg_thick*0.6, hip_y,
                              cx + leg_thick*0.6, knee_y, leg_thick)
        self._draw_shadow_limb(painter, cx + leg_thick*0.6, knee_y,
                              cx + leg_thick*0.6, ankle_y, leg_thick * 0.92)

        # Draw joints (legs)
        self._draw_shadow_joint(painter, cx - leg_thick*0.6, hip_y, joint_r)
        self._draw_shadow_joint(painter, cx + leg_thick*0.6, hip_y, joint_r)
        self._draw_shadow_joint(painter, cx - leg_thick*0.6, knee_y, joint_r)
        self._draw_shadow_joint(painter, cx + leg_thick*0.6, knee_y, joint_r)
        self._draw_shadow_joint(painter, cx - leg_thick*0.6, ankle_y, joint_r * 0.85)
        self._draw_shadow_joint(painter, cx + leg_thick*0.6, ankle_y, joint_r * 0.85)

        # Draw torso (short wide barrel)
        self._draw_shadow_torso(painter, cx, torso_center_y, torso_w, torso_h)

        # Draw arms (relaxed hanging, slight outward angle)
        arm_angle_deg = 10
        arm_angle_rad = math.radians(arm_angle_deg)

        shoulder_l_x = cx - torso_w / 2
        shoulder_r_x = cx + torso_w / 2

        # Left arm
        elbow_l_x = shoulder_l_x - math.sin(arm_angle_rad) * upper_arm_len
        elbow_l_y = shoulder_y + math.cos(arm_angle_rad) * upper_arm_len
        wrist_l_x = elbow_l_x - math.sin(arm_angle_rad) * lower_arm_len
        wrist_l_y = elbow_l_y + math.cos(arm_angle_rad) * lower_arm_len

        # Right arm
        elbow_r_x = shoulder_r_x + math.sin(arm_angle_rad) * upper_arm_len
        elbow_r_y = shoulder_y + math.cos(arm_angle_rad) * upper_arm_len
        wrist_r_x = elbow_r_x + math.sin(arm_angle_rad) * lower_arm_len
        wrist_r_y = elbow_r_y + math.cos(arm_angle_rad) * lower_arm_len

        self._draw_shadow_limb(painter, shoulder_l_x, shoulder_y, elbow_l_x, elbow_l_y, arm_thick)
        self._draw_shadow_limb(painter, elbow_l_x, elbow_l_y, wrist_l_x, wrist_l_y, arm_thick * 0.86)
        self._draw_shadow_limb(painter, shoulder_r_x, shoulder_y, elbow_r_x, elbow_r_y, arm_thick)
        self._draw_shadow_limb(painter, elbow_r_x, elbow_r_y, wrist_r_x, wrist_r_y, arm_thick * 0.86)

        # Draw joints (arms)
        self._draw_shadow_joint(painter, shoulder_l_x, shoulder_y, joint_r)
        self._draw_shadow_joint(painter, shoulder_r_x, shoulder_y, joint_r)
        self._draw_shadow_joint(painter, elbow_l_x, elbow_l_y, joint_r * 0.9)
        self._draw_shadow_joint(painter, elbow_r_x, elbow_r_y, joint_r * 0.9)
        self._draw_shadow_joint(painter, wrist_l_x, wrist_l_y, joint_r * 0.75)
        self._draw_shadow_joint(painter, wrist_r_x, wrist_r_y, joint_r * 0.75)

        # Draw hands
        self._draw_shadow_hand(painter, wrist_l_x, wrist_l_y, hand_w, hand_h)
        self._draw_shadow_hand(painter, wrist_r_x, wrist_r_y, hand_w, hand_h)

        # Draw head (sphere with gradient)
        self._draw_shadow_head(painter, cx, head_center_y, head_r)

        # Draw neck joint
        self._draw_shadow_joint(painter, cx, shoulder_y - neck_gap/2, joint_r * 0.6)

        # Draw menacing glowing red SLIT eyes (most important!)
        self._draw_red_slit_eyes(painter, cx, head_center_y, head_r)

    # ===== HELPER METHODS (All preserved from working implementation) =====

    def _draw_shadow_soft(self, painter, cx, cy, width, opacity):
        """Draw soft elliptical drop shadow."""
        gradient = QRadialGradient(QPointF(cx, cy), width / 2)
        gradient.setColorAt(0.0, QColor(20, 20, 20, int(255 * opacity)))
        gradient.setColorAt(1.0, QColor(20, 20, 20, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(
            QRectF(cx - width/2, cy - width*0.15, width, width*0.3)
        )

    def _draw_shadow_limb(self, painter, x1, y1, x2, y2, thickness):
        """Draw limb with gradient shading (fake 3D cylinder)."""
        # Calculate perpendicular direction for gradient
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        if length < 0.1:
            return

        # Perpendicular vector
        px = -dy / length
        py = dx / length

        # Create gradient perpendicular to limb
        gradient = QLinearGradient(
            x1 + px * thickness * 0.5,
            y1 + py * thickness * 0.5,
            x1 - px * thickness * 0.5,
            y1 - py * thickness * 0.5
        )
        gradient.setColorAt(0.0, QColor(25, 25, 25))  # Lit edge
        gradient.setColorAt(1.0, QColor(8, 8, 8))     # Shadow edge

        # Draw as thick rounded line
        pen = QPen(QBrush(gradient), thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def _draw_shadow_joint(self, painter, x, y, radius):
        """Draw spherical joint with radial gradient."""
        offset = radius * 0.25

        gradient = QRadialGradient(
            QPointF(x - offset, y - offset),
            radius * 1.2
        )
        gradient.setColorAt(0.0, QColor(20, 20, 20))
        gradient.setColorAt(0.6, QColor(12, 12, 12))
        gradient.setColorAt(1.0, QColor(5, 5, 5))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(x, y), radius, radius)

    def _draw_shadow_torso(self, painter, cx, cy, width, height):
        """Draw torso with horizontal gradient (cylindrical)."""
        gradient = QLinearGradient(
            cx - width / 2, cy,
            cx + width / 2, cy
        )
        gradient.setColorAt(0.0, QColor(30, 30, 30))   # Left lit
        gradient.setColorAt(0.5, QColor(15, 15, 15))   # Center
        gradient.setColorAt(1.0, QColor(8, 8, 8))      # Right shadow

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))

        rect = QRectF(
            cx - width / 2,
            cy - height / 2,
            width,
            height
        )
        painter.drawRoundedRect(rect, width * 0.3, width * 0.3)

    def _draw_shadow_head(self, painter, cx, cy, radius):
        """Draw head sphere with offset gradient (fake 3D lighting)."""
        offset = radius * 0.25

        gradient = QRadialGradient(
            QPointF(cx - offset, cy - offset),
            radius * 1.2
        )
        gradient.setColorAt(0.0, QColor(40, 40, 40))   # Highlight
        gradient.setColorAt(1.0, QColor(10, 10, 10))   # Shadow

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

    def _draw_shadow_hand(self, painter, x, y, width, height):
        """Draw simple blocky hand with gradient."""
        gradient = QLinearGradient(x, y, x, y + height)
        gradient.setColorAt(0.0, QColor(18, 18, 18))
        gradient.setColorAt(1.0, QColor(5, 5, 5))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))

        rect = QRectF(x - width/2, y, width, height)
        painter.drawRoundedRect(rect, width * 0.3, width * 0.3)

    def _draw_shadow_foot(self, painter, x, y, width, height, is_left):
        """Draw simple blocky foot with gradient."""
        gradient = QLinearGradient(x, y - height*0.3, x, y + height*0.7)
        gradient.setColorAt(0.0, QColor(18, 18, 18))
        gradient.setColorAt(1.0, QColor(5, 5, 5))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))

        direction = -1 if is_left else 1
        rect = QRectF(
            x - width/2 + direction * width * 0.15,
            y - height * 0.3,
            width,
            height
        )
        painter.drawRoundedRect(rect, height * 0.3, height * 0.3)

    def _draw_red_slit_eyes(self, painter, cx, cy, head_radius):
        """Draw menacing glowing red slit eyes (THE defining feature)."""
        eye_w = head_radius * 0.5
        eye_h = head_radius * 0.10
        eye_spacing = head_radius * 0.42
        eye_y_offset = -head_radius * 0.15

        left_eye_x = cx - eye_spacing
        right_eye_x = cx + eye_spacing
        eye_y = cy + eye_y_offset

        # Draw both eyes
        self._draw_single_red_slit(painter, left_eye_x, eye_y, eye_w, eye_h)
        self._draw_single_red_slit(painter, right_eye_x, eye_y, eye_w, eye_h)

    def _draw_single_red_slit(self, painter, x, y, width, height):
        """Draw single glowing red slit eye (3-layer glow)."""
        painter.setPen(Qt.PenStyle.NoPen)

        # Layer 1: Outer glow (largest, faintest)
        outer_w = width * 2.5
        outer_h = height * 3.0

        outer_gradient = QRadialGradient(QPointF(x, y), outer_w / 2)
        outer_gradient.setColorAt(0.0, QColor(255, 0, 0, 102))  # 40% opacity
        outer_gradient.setColorAt(1.0, QColor(255, 0, 0, 0))

        painter.setBrush(QBrush(outer_gradient))
        painter.drawEllipse(
            QRectF(x - outer_w/2, y - outer_h/2, outer_w, outer_h)
        )

        # Layer 2: Mid glow (brighter)
        mid_w = width * 1.5
        mid_h = height * 2.0

        mid_gradient = QRadialGradient(QPointF(x, y), mid_w / 2)
        mid_gradient.setColorAt(0.0, QColor(255, 40, 40, 153))  # 60% opacity
        mid_gradient.setColorAt(1.0, QColor(255, 40, 40, 0))

        painter.setBrush(QBrush(mid_gradient))
        painter.drawEllipse(
            QRectF(x - mid_w/2, y - mid_h/2, mid_w, mid_h)
        )

        # Layer 3: Core slit (brightest, solid)
        painter.setBrush(QColor(255, 20, 20))
        painter.drawEllipse(
            QRectF(x - width/2, y - height/2, width, height)
        )
