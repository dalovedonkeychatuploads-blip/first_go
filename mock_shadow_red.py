"""
DONK Shadow Red Fighter - Second Toon
Chunky stick figure with 3D-style gradients and glowing red slit eyes
Corrected proportions: 4.2 heads tall (toy/chibi style, NOT realistic)
"""

import sys
import math
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QRadialGradient, QLinearGradient,
    QColor, QPen, QBrush, QPainterPath
)

# ========== PROPORTIONS (CHUNKY STICK FIGURE - 4.2 HEADS TALL) ==========
HEAD_R = 60                     # Base unit: head radius in pixels

# TORSO - short and wide (barrel-like, NOT tall and slim)
TORSO_WIDTH_MULT = 1.8          # Wide torso
TORSO_HEIGHT_MULT = 1.4         # SHORT torso (was 3.5 - WRONG!)

# LIMBS - short and thick (stubby toy proportions)
UPPER_ARM_LENGTH_MULT = 0.75    # Short upper arms
LOWER_ARM_LENGTH_MULT = 0.70    # Short forearms
ARM_THICKNESS_MULT = 0.35       # Thick arms

UPPER_LEG_LENGTH_MULT = 0.9     # Short thighs
LOWER_LEG_LENGTH_MULT = 0.8     # Short calves
LEG_THICKNESS_MULT = 0.38       # Thick legs

JOINT_SIZE_MULT = 0.30          # Bigger visible joints
HAND_WIDTH_MULT = 0.47          # Chunky hands
HAND_HEIGHT_MULT = 0.58
FOOT_WIDTH_MULT = 0.53          # Chunky feet
FOOT_HEIGHT_MULT = 0.42

NECK_GAP_MULT = 0.1             # Tiny gap between head and torso

# POSE ANGLES
ARM_ANGLE_DEG = 10              # Slight outward from vertical
ELBOW_BEND_DEG = 175            # Nearly straight
KNEE_BEND_DEG = 178             # Nearly straight

# EYES - menacing glowing slits
EYE_WIDTH_MULT = 0.5            # Eye width
EYE_HEIGHT_MULT = 0.10          # Very narrow (slit-like)
EYE_SPACING_MULT = 0.42         # Distance between eyes
EYE_GLOW_OUTER_MULT = 2.5       # Outer glow radius
EYE_GLOW_MID_MULT = 1.5         # Mid glow radius

EYE_RED_R = 255
EYE_RED_G = 20
EYE_RED_B = 20

# BACKGROUND
BG_CENTER_GREY = 100            # Medium grey center
BG_EDGE_GREY = 60               # Darker grey edges

# LIGHTING (top-left key light)
HEAD_HIGHLIGHT_GREY = 40
HEAD_SHADOW_GREY = 10
TORSO_HIGHLIGHT_GREY = 30
TORSO_SHADOW_GREY = 8
LIMB_HIGHLIGHT_GREY = 25
LIMB_SHADOW_GREY = 8
JOINT_HIGHLIGHT_GREY = 20
JOINT_SHADOW_GREY = 5
HAND_HIGHLIGHT_GREY = 18
HAND_SHADOW_GREY = 5

# SHADOW
SHADOW_OPACITY = 0.30
SHADOW_WIDTH_MULT = 0.7
SHADOW_HEIGHT_MULT = 0.18
SHADOW_OFFSET_X = 8

# CHARACTER POSITION
CHAR_CENTER_X = 640
CHAR_FEET_Y = 600


class ShadowRedFighter(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1280, 720)
        self.setWindowTitle("DONK Shadow Red Fighter - Second Toon")
        self.setStyleSheet("background-color: black;")

        # Calculate body part dimensions
        self.head_r = HEAD_R
        self.torso_w = HEAD_R * TORSO_WIDTH_MULT
        self.torso_h = HEAD_R * TORSO_HEIGHT_MULT
        self.upper_arm_len = HEAD_R * UPPER_ARM_LENGTH_MULT
        self.lower_arm_len = HEAD_R * LOWER_ARM_LENGTH_MULT
        self.arm_thick = HEAD_R * ARM_THICKNESS_MULT
        self.upper_leg_len = HEAD_R * UPPER_LEG_LENGTH_MULT
        self.lower_leg_len = HEAD_R * LOWER_LEG_LENGTH_MULT
        self.leg_thick = HEAD_R * LEG_THICKNESS_MULT
        self.joint_r = HEAD_R * JOINT_SIZE_MULT
        self.hand_w = HEAD_R * HAND_WIDTH_MULT
        self.hand_h = HEAD_R * HAND_HEIGHT_MULT
        self.foot_w = HEAD_R * FOOT_WIDTH_MULT
        self.foot_h = HEAD_R * FOOT_HEIGHT_MULT
        self.neck_gap = HEAD_R * NECK_GAP_MULT

        # Calculate character skeleton positions
        self.calc_skeleton()

    def calc_skeleton(self):
        """Calculate all joint positions for the character"""
        cx = CHAR_CENTER_X

        # Bottom to top calculation
        feet_y = CHAR_FEET_Y

        # Legs (vertical, slight knee bend)
        self.left_ankle = QPointF(cx - self.leg_thick * 0.6, feet_y)
        self.right_ankle = QPointF(cx + self.leg_thick * 0.6, feet_y)

        self.left_knee = QPointF(cx - self.leg_thick * 0.6, feet_y - self.lower_leg_len)
        self.right_knee = QPointF(cx + self.leg_thick * 0.6, feet_y - self.lower_leg_len)

        hip_y = self.left_knee.y() - self.upper_leg_len
        self.left_hip = QPointF(cx - self.torso_w * 0.3, hip_y)
        self.right_hip = QPointF(cx + self.torso_w * 0.3, hip_y)

        # Torso
        self.torso_center = QPointF(cx, hip_y - self.torso_h / 2)
        shoulder_y = hip_y - self.torso_h

        self.left_shoulder = QPointF(cx - self.torso_w / 2, shoulder_y)
        self.right_shoulder = QPointF(cx + self.torso_w / 2, shoulder_y)

        # Head
        head_center_y = shoulder_y - self.neck_gap - self.head_r
        self.head_center = QPointF(cx, head_center_y)

        # Arms (hanging down with slight outward angle)
        arm_angle_rad = math.radians(ARM_ANGLE_DEG)
        elbow_bend_rad = math.radians(180 - ELBOW_BEND_DEG)  # External angle

        # Left arm
        self.left_elbow = QPointF(
            self.left_shoulder.x() - math.sin(arm_angle_rad) * self.upper_arm_len,
            self.left_shoulder.y() + math.cos(arm_angle_rad) * self.upper_arm_len
        )

        # Forearm continues nearly straight down
        self.left_wrist = QPointF(
            self.left_elbow.x() - math.sin(arm_angle_rad) * self.lower_arm_len,
            self.left_elbow.y() + math.cos(arm_angle_rad) * self.lower_arm_len
        )

        # Right arm (mirror)
        self.right_elbow = QPointF(
            self.right_shoulder.x() + math.sin(arm_angle_rad) * self.upper_arm_len,
            self.right_shoulder.y() + math.cos(arm_angle_rad) * self.upper_arm_len
        )

        self.right_wrist = QPointF(
            self.right_elbow.x() + math.sin(arm_angle_rad) * self.lower_arm_len,
            self.right_elbow.y() + math.cos(arm_angle_rad) * self.lower_arm_len
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # 1. Background
        self.draw_background(painter)

        # 2. Ground shadow
        self.draw_shadow(painter)

        # 3. Body parts (back to front)
        self.draw_torso(painter)
        self.draw_legs(painter)
        self.draw_arms(painter)
        self.draw_head(painter)

        # 4. Eyes (on top of everything)
        self.draw_eyes(painter)

    def draw_background(self, painter):
        """Radial gradient studio background"""
        gradient = QRadialGradient(640, 360, 800)
        gradient.setColorAt(0.0, QColor(BG_CENTER_GREY, BG_CENTER_GREY, BG_CENTER_GREY))
        gradient.setColorAt(1.0, QColor(BG_EDGE_GREY, BG_EDGE_GREY, BG_EDGE_GREY))

        painter.fillRect(0, 0, 1280, 720, QBrush(gradient))

    def draw_shadow(self, painter):
        """Soft drop shadow beneath character"""
        shadow_w = self.torso_w * 2 * SHADOW_WIDTH_MULT
        shadow_h = shadow_w * SHADOW_HEIGHT_MULT

        shadow_x = CHAR_CENTER_X + SHADOW_OFFSET_X
        shadow_y = CHAR_FEET_Y

        gradient = QRadialGradient(shadow_x, shadow_y, shadow_w / 2)
        gradient.setColorAt(0.0, QColor(20, 20, 20, int(255 * SHADOW_OPACITY)))
        gradient.setColorAt(1.0, QColor(20, 20, 20, 0))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            QRectF(
                shadow_x - shadow_w / 2,
                shadow_y - shadow_h / 2,
                shadow_w,
                shadow_h
            )
        )

    def draw_limb(self, painter, p1, p2, thickness, highlight, shadow):
        """Draw a cylindrical limb with gradient"""
        # Calculate perpendicular direction for gradient
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        length = math.sqrt(dx*dx + dy*dy)

        if length < 0.1:
            return

        # Perpendicular vector (rotated 90 degrees)
        px = -dy / length
        py = dx / length

        # Gradient perpendicular to limb (lit side to shadow side)
        gradient = QLinearGradient(
            p1.x() + px * thickness * 0.5,
            p1.y() + py * thickness * 0.5,
            p1.x() - px * thickness * 0.5,
            p1.y() - py * thickness * 0.5
        )
        gradient.setColorAt(0.0, QColor(highlight, highlight, highlight))
        gradient.setColorAt(1.0, QColor(shadow, shadow, shadow))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)

        # Draw rounded capsule
        path = QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)

        pen = QPen(QBrush(gradient), thickness, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(p1, p2)

    def draw_joint(self, painter, center, radius):
        """Draw a spherical joint with gradient"""
        offset = radius * 0.25
        gradient = QRadialGradient(
            center.x() - offset,
            center.y() - offset,
            radius * 1.2
        )
        gradient.setColorAt(0.0, QColor(JOINT_HIGHLIGHT_GREY, JOINT_HIGHLIGHT_GREY, JOINT_HIGHLIGHT_GREY))
        gradient.setColorAt(0.6, QColor(JOINT_HIGHLIGHT_GREY // 2, JOINT_HIGHLIGHT_GREY // 2, JOINT_HIGHLIGHT_GREY // 2))
        gradient.setColorAt(1.0, QColor(JOINT_SHADOW_GREY, JOINT_SHADOW_GREY, JOINT_SHADOW_GREY))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)

    def draw_torso(self, painter):
        """Draw torso with horizontal gradient (cylindrical)"""
        gradient = QLinearGradient(
            self.torso_center.x() - self.torso_w / 2,
            self.torso_center.y(),
            self.torso_center.x() + self.torso_w / 2,
            self.torso_center.y()
        )
        gradient.setColorAt(0.0, QColor(TORSO_HIGHLIGHT_GREY, TORSO_HIGHLIGHT_GREY, TORSO_HIGHLIGHT_GREY))
        gradient.setColorAt(0.5, QColor((TORSO_HIGHLIGHT_GREY + TORSO_SHADOW_GREY) // 2,
                                       (TORSO_HIGHLIGHT_GREY + TORSO_SHADOW_GREY) // 2,
                                       (TORSO_HIGHLIGHT_GREY + TORSO_SHADOW_GREY) // 2))
        gradient.setColorAt(1.0, QColor(TORSO_SHADOW_GREY, TORSO_SHADOW_GREY, TORSO_SHADOW_GREY))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)

        # Draw rounded rectangle (capsule)
        rect = QRectF(
            self.torso_center.x() - self.torso_w / 2,
            self.torso_center.y() - self.torso_h / 2,
            self.torso_w,
            self.torso_h
        )
        painter.drawRoundedRect(rect, self.torso_w * 0.3, self.torso_w * 0.3)

    def draw_legs(self, painter):
        """Draw legs with joints"""
        # Left leg
        self.draw_limb(painter, self.left_hip, self.left_knee,
                      self.leg_thick, LIMB_HIGHLIGHT_GREY, LIMB_SHADOW_GREY)
        self.draw_limb(painter, self.left_knee, self.left_ankle,
                      self.leg_thick * 0.92, LIMB_HIGHLIGHT_GREY, LIMB_SHADOW_GREY)

        # Right leg
        self.draw_limb(painter, self.right_hip, self.right_knee,
                      self.leg_thick, LIMB_HIGHLIGHT_GREY, LIMB_SHADOW_GREY)
        self.draw_limb(painter, self.right_knee, self.right_ankle,
                      self.leg_thick * 0.92, LIMB_HIGHLIGHT_GREY, LIMB_SHADOW_GREY)

        # Joints
        self.draw_joint(painter, self.left_hip, self.joint_r)
        self.draw_joint(painter, self.right_hip, self.joint_r)
        self.draw_joint(painter, self.left_knee, self.joint_r)
        self.draw_joint(painter, self.right_knee, self.joint_r)
        self.draw_joint(painter, self.left_ankle, self.joint_r * 0.85)
        self.draw_joint(painter, self.right_ankle, self.joint_r * 0.85)

        # Feet
        self.draw_foot(painter, self.left_ankle, -1)
        self.draw_foot(painter, self.right_ankle, 1)

    def draw_foot(self, painter, ankle, direction):
        """Draw a simple blocky foot"""
        gradient = QLinearGradient(
            ankle.x(),
            ankle.y() - self.foot_h * 0.3,
            ankle.x(),
            ankle.y() + self.foot_h * 0.7
        )
        gradient.setColorAt(0.0, QColor(HAND_HIGHLIGHT_GREY, HAND_HIGHLIGHT_GREY, HAND_HIGHLIGHT_GREY))
        gradient.setColorAt(1.0, QColor(HAND_SHADOW_GREY, HAND_SHADOW_GREY, HAND_SHADOW_GREY))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)

        rect = QRectF(
            ankle.x() - self.foot_w / 2 + direction * self.foot_w * 0.15,
            ankle.y() - self.foot_h * 0.3,
            self.foot_w,
            self.foot_h
        )
        painter.drawRoundedRect(rect, self.foot_h * 0.3, self.foot_h * 0.3)

    def draw_arms(self, painter):
        """Draw arms with joints"""
        # Left arm
        self.draw_limb(painter, self.left_shoulder, self.left_elbow,
                      self.arm_thick, LIMB_HIGHLIGHT_GREY, LIMB_SHADOW_GREY)
        self.draw_limb(painter, self.left_elbow, self.left_wrist,
                      self.arm_thick * 0.86, LIMB_HIGHLIGHT_GREY, LIMB_SHADOW_GREY)

        # Right arm
        self.draw_limb(painter, self.right_shoulder, self.right_elbow,
                      self.arm_thick, LIMB_HIGHLIGHT_GREY, LIMB_SHADOW_GREY)
        self.draw_limb(painter, self.right_elbow, self.right_wrist,
                      self.arm_thick * 0.86, LIMB_HIGHLIGHT_GREY, LIMB_SHADOW_GREY)

        # Joints
        self.draw_joint(painter, self.left_shoulder, self.joint_r)
        self.draw_joint(painter, self.right_shoulder, self.joint_r)
        self.draw_joint(painter, self.left_elbow, self.joint_r * 0.9)
        self.draw_joint(painter, self.right_elbow, self.joint_r * 0.9)
        self.draw_joint(painter, self.left_wrist, self.joint_r * 0.75)
        self.draw_joint(painter, self.right_wrist, self.joint_r * 0.75)

        # Hands
        self.draw_hand(painter, self.left_wrist)
        self.draw_hand(painter, self.right_wrist)

    def draw_hand(self, painter, wrist):
        """Draw a simple blocky hand"""
        gradient = QLinearGradient(
            wrist.x(),
            wrist.y(),
            wrist.x(),
            wrist.y() + self.hand_h
        )
        gradient.setColorAt(0.0, QColor(HAND_HIGHLIGHT_GREY, HAND_HIGHLIGHT_GREY, HAND_HIGHLIGHT_GREY))
        gradient.setColorAt(1.0, QColor(HAND_SHADOW_GREY, HAND_SHADOW_GREY, HAND_SHADOW_GREY))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)

        rect = QRectF(
            wrist.x() - self.hand_w / 2,
            wrist.y(),
            self.hand_w,
            self.hand_h
        )
        painter.drawRoundedRect(rect, self.hand_w * 0.3, self.hand_w * 0.3)

    def draw_head(self, painter):
        """Draw head sphere with offset gradient"""
        offset = self.head_r * 0.25
        gradient = QRadialGradient(
            self.head_center.x() - offset,
            self.head_center.y() - offset,
            self.head_r * 1.2
        )
        gradient.setColorAt(0.0, QColor(HEAD_HIGHLIGHT_GREY, HEAD_HIGHLIGHT_GREY, HEAD_HIGHLIGHT_GREY))
        gradient.setColorAt(1.0, QColor(HEAD_SHADOW_GREY, HEAD_SHADOW_GREY, HEAD_SHADOW_GREY))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.head_center, self.head_r, self.head_r)

        # Neck joint
        neck_y = self.head_center.y() + self.head_r + self.neck_gap / 2
        self.draw_joint(painter, QPointF(self.head_center.x(), neck_y), self.joint_r * 0.6)

    def draw_eyes(self, painter):
        """Draw menacing glowing red slit eyes (3-layer)"""
        eye_w = self.head_r * EYE_WIDTH_MULT
        eye_h = self.head_r * EYE_HEIGHT_MULT
        eye_spacing = self.head_r * EYE_SPACING_MULT

        # Eyes positioned in upper-middle of head
        eye_y_offset = -self.head_r * 0.15

        left_eye_center = QPointF(
            self.head_center.x() - eye_spacing,
            self.head_center.y() + eye_y_offset
        )
        right_eye_center = QPointF(
            self.head_center.x() + eye_spacing,
            self.head_center.y() + eye_y_offset
        )

        # Draw both eyes
        self.draw_eye(painter, left_eye_center, eye_w, eye_h)
        self.draw_eye(painter, right_eye_center, eye_w, eye_h)

    def draw_eye(self, painter, center, width, height):
        """Draw single eye with 3-layer glow"""
        painter.setPen(Qt.NoPen)

        # Layer 1: Outer glow (largest, faintest)
        outer_w = width * EYE_GLOW_OUTER_MULT
        outer_h = height * EYE_GLOW_OUTER_MULT * 1.2

        outer_gradient = QRadialGradient(center, outer_w / 2)
        outer_gradient.setColorAt(0.0, QColor(EYE_RED_R, EYE_RED_G, EYE_RED_B, 102))  # 40% opacity
        outer_gradient.setColorAt(1.0, QColor(EYE_RED_R, EYE_RED_G, EYE_RED_B, 0))

        painter.setBrush(QBrush(outer_gradient))
        painter.drawEllipse(
            QRectF(
                center.x() - outer_w / 2,
                center.y() - outer_h / 2,
                outer_w,
                outer_h
            )
        )

        # Layer 2: Mid glow (brighter)
        mid_w = width * EYE_GLOW_MID_MULT
        mid_h = height * EYE_GLOW_MID_MULT * 1.2

        mid_gradient = QRadialGradient(center, mid_w / 2)
        mid_gradient.setColorAt(0.0, QColor(EYE_RED_R, 40, 40, 153))  # 60% opacity
        mid_gradient.setColorAt(1.0, QColor(EYE_RED_R, 40, 40, 0))

        painter.setBrush(QBrush(mid_gradient))
        painter.drawEllipse(
            QRectF(
                center.x() - mid_w / 2,
                center.y() - mid_h / 2,
                mid_w,
                mid_h
            )
        )

        # Layer 3: Core slit (brightest, solid)
        painter.setBrush(QColor(EYE_RED_R, EYE_RED_G, EYE_RED_B))
        painter.drawEllipse(
            QRectF(
                center.x() - width / 2,
                center.y() - height / 2,
                width,
                height
            )
        )


def main():
    app = QApplication(sys.argv)
    window = ShadowRedFighter()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
