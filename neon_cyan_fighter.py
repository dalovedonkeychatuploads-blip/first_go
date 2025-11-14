"""
Neon Cyan Fighter - Toon 1
Sleek technical fighter with cyan glowing joints
Reference-matched to 3D model: medium-gray body, subtle cyan joint glows
"""

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QLinearGradient,
                           QRadialGradient, QPainterPath)
import math


class NeonCyanFighter:
    """
    Neon Cyan Fighter - Deep detailed implementation
    Every body part, color, and glow meticulously coded to match reference
    """

    # ===== COLOR SYSTEM (EXACT reference-matched from image analysis) =====
    # Extracted from reference image: RGB(46,46,46) -> RGB(69,69,69) -> RGB(145,145,145)
    BODY_HIGHLIGHT = QColor(145, 145, 145)   # Brightest lit edge (EXACT from reference)
    BODY_MIDTONE = QColor(69, 69, 69)        # Median body color (EXACT from reference)
    BODY_SHADOW = QColor(46, 46, 46)         # Darkest shadow (EXACT from reference)

    # Head uses same color range (no separate values in reference)
    HEAD_HIGHLIGHT = QColor(145, 145, 145)
    HEAD_MIDTONE = QColor(69, 69, 69)
    HEAD_SHADOW = QColor(46, 46, 46)

    # ===== GLOW SYSTEM (SUBTLE - lit ON skin, not harsh outward) =====
    GLOW_CYAN = QColor(0, 255, 255)
    GLOW_JOINT_RADIUS = 18                    # Small subtle glow
    GLOW_OUTER_OPACITY = 0.12                # Very soft outer (~30/255)
    GLOW_INNER_OPACITY = 0.30                # Subtle inner (~75/255)

    GLOW_EYE_RADIUS = 16                     # Eye glow radius
    GLOW_EYE_OUTER_OPACITY = 0.15
    GLOW_EYE_INNER_OPACITY = 0.40

    # ===== PROPORTIONS (6.5 heads tall - realistic fighter) =====
    HEAD_DIAMETER = 80
    NECK_HEIGHT = 18
    NECK_THICKNESS = 28
    TORSO_HEIGHT = 140
    TORSO_WIDTH = 80

    UPPER_ARM_LENGTH = 70
    LOWER_ARM_LENGTH = 65
    UPPER_ARM_THICKNESS = 36
    LOWER_ARM_THICKNESS = 32

    UPPER_LEG_LENGTH = 85
    LOWER_LEG_LENGTH = 80
    UPPER_LEG_THICKNESS = 42
    LOWER_LEG_THICKNESS = 38

    HAND_WIDTH = 32
    HAND_HEIGHT = 38
    FOOT_WIDTH = 56
    FOOT_HEIGHT = 32

    def __init__(self):
        """Initialize Neon Cyan Fighter"""
        pass

    def render(self, painter, cx, cy, scale):
        """
        Main render method - draws complete Neon Cyan fighter

        Args:
            painter: QPainter instance
            cx, cy: Center position
            scale: Scale multiplier
        """
        # Scale all proportions
        s = scale

        # Calculate joint positions (fighting stance - guard up)
        # Bottom-up calculation from feet

        # Feet positions (wide stance)
        front_foot_x = cx - 105 * s
        front_foot_y = cy + 100 * s
        back_foot_x = cx + 95 * s
        back_foot_y = cy + 95 * s

        # Ankles
        front_ankle = (front_foot_x, front_foot_y)
        back_ankle = (back_foot_x, back_foot_y)

        # Knees (front knee bent more for stance)
        front_knee = (front_foot_x + 10 * s, front_foot_y - 80 * s)
        back_knee = (back_foot_x - 5 * s, back_foot_y - 80 * s)

        # Hips
        front_hip = (front_foot_x + 20 * s, front_foot_y - 165 * s)
        back_hip = (back_foot_x - 10 * s, back_foot_y - 165 * s)

        # Pelvis center
        pelvis_x = (front_hip[0] + back_hip[0]) / 2
        pelvis_y = (front_hip[1] + back_hip[1]) / 2

        # Torso (slight forward lean)
        shoulder_center_x = pelvis_x - 10 * s
        shoulder_center_y = pelvis_y - self.TORSO_HEIGHT * s

        # Shoulders
        shoulder_offset = self.TORSO_WIDTH * s / 2
        left_shoulder = (shoulder_center_x - shoulder_offset, shoulder_center_y)
        right_shoulder = (shoulder_center_x + shoulder_offset, shoulder_center_y)

        # Arms in guard position (raised fists)
        left_elbow = (left_shoulder[0] - 47 * s, left_shoulder[1] + 43 * s)
        left_wrist = (left_elbow[0] + 15 * s, left_elbow[1] - 70 * s)

        right_elbow = (right_shoulder[0] + 13 * s, right_shoulder[1] + 48 * s)
        right_wrist = (right_elbow[0] - 2 * s, right_elbow[1] - 70 * s)

        # Neck and head
        neck_base = (shoulder_center_x, shoulder_center_y)
        neck_top = (shoulder_center_x, shoulder_center_y - self.NECK_HEIGHT * s)
        head_center = (shoulder_center_x, neck_top[1] - self.HEAD_DIAMETER * s / 2)

        # ===== RENDERING (back to front for proper depth) =====

        # Shadow
        self._draw_soft_shadow(painter, pelvis_x, front_foot_y + self.FOOT_HEIGHT * s / 2,
                              180 * s, 0.6)

        # Back leg
        self._draw_upper_leg(painter, back_hip, back_knee, self.UPPER_LEG_THICKNESS * s)
        self._draw_lower_leg(painter, back_knee, back_ankle, self.LOWER_LEG_THICKNESS * s)
        self._draw_foot(painter, back_ankle[0], back_ankle[1],
                       self.FOOT_WIDTH * s, self.FOOT_HEIGHT * s, False)

        # Back leg joints (SUBTLE glows)
        self._draw_joint_glow_subtle(painter, back_hip[0], back_hip[1], self.GLOW_JOINT_RADIUS * s)
        self._draw_joint_glow_subtle(painter, back_knee[0], back_knee[1], self.GLOW_JOINT_RADIUS * s)
        self._draw_joint_glow_subtle(painter, back_ankle[0], back_ankle[1],
                                     self.GLOW_JOINT_RADIUS * s * 0.85)

        # Torso and neck
        self._draw_torso(painter, pelvis_x, pelvis_y, shoulder_center_x, shoulder_center_y,
                        self.TORSO_WIDTH * s)
        self._draw_neck(painter, neck_base, neck_top, self.NECK_THICKNESS * s)

        # Front leg
        self._draw_upper_leg(painter, front_hip, front_knee, self.UPPER_LEG_THICKNESS * s)
        self._draw_lower_leg(painter, front_knee, front_ankle, self.LOWER_LEG_THICKNESS * s)
        self._draw_foot(painter, front_ankle[0], front_ankle[1],
                       self.FOOT_WIDTH * s, self.FOOT_HEIGHT * s, True)

        # Front leg joints
        self._draw_joint_glow_subtle(painter, front_hip[0], front_hip[1], self.GLOW_JOINT_RADIUS * s)
        self._draw_joint_glow_subtle(painter, front_knee[0], front_knee[1], self.GLOW_JOINT_RADIUS * s)
        self._draw_joint_glow_subtle(painter, front_ankle[0], front_ankle[1],
                                     self.GLOW_JOINT_RADIUS * s * 0.85)

        # Back arm
        self._draw_upper_arm(painter, right_shoulder, right_elbow, self.UPPER_ARM_THICKNESS * s)
        self._draw_lower_arm(painter, right_elbow, right_wrist, self.LOWER_ARM_THICKNESS * s)
        self._draw_hand(painter, right_wrist[0], right_wrist[1],
                       self.HAND_WIDTH * s, self.HAND_HEIGHT * s)

        # Back arm joints
        self._draw_joint_glow_subtle(painter, right_shoulder[0], right_shoulder[1],
                                     self.GLOW_JOINT_RADIUS * s)
        self._draw_joint_glow_subtle(painter, right_elbow[0], right_elbow[1],
                                     self.GLOW_JOINT_RADIUS * s * 0.9)
        self._draw_joint_glow_subtle(painter, right_wrist[0], right_wrist[1],
                                     self.GLOW_JOINT_RADIUS * s * 0.75)

        # Head
        self._draw_head(painter, head_center[0], head_center[1],
                       self.HEAD_DIAMETER * s / 2)

        # Front arm (on top)
        self._draw_upper_arm(painter, left_shoulder, left_elbow, self.UPPER_ARM_THICKNESS * s)
        self._draw_lower_arm(painter, left_elbow, left_wrist, self.LOWER_ARM_THICKNESS * s)
        self._draw_hand(painter, left_wrist[0], left_wrist[1],
                       self.HAND_WIDTH * s, self.HAND_HEIGHT * s)

        # Front arm joints
        self._draw_joint_glow_subtle(painter, left_shoulder[0], left_shoulder[1],
                                     self.GLOW_JOINT_RADIUS * s)
        self._draw_joint_glow_subtle(painter, left_elbow[0], left_elbow[1],
                                     self.GLOW_JOINT_RADIUS * s * 0.9)
        self._draw_joint_glow_subtle(painter, left_wrist[0], left_wrist[1],
                                     self.GLOW_JOINT_RADIUS * s * 0.75)

        # Eyes (top layer)
        self._draw_cyan_slit_eyes(painter, head_center[0], head_center[1],
                                 self.HEAD_DIAMETER * s / 2)

    # ===== BODY PART RENDERING METHODS =====

    def _draw_head(self, painter, cx, cy, radius):
        """Draw head sphere with volumetric gradient"""
        # Highlight offset (top-left for 3D effect)
        offset_x = -radius * 0.3
        offset_y = -radius * 0.3

        gradient = QRadialGradient(
            QPointF(cx + offset_x, cy + offset_y),
            radius * 1.4
        )
        gradient.setColorAt(0.0, self.HEAD_HIGHLIGHT)
        gradient.setColorAt(0.5, self.HEAD_MIDTONE)
        gradient.setColorAt(1.0, self.HEAD_SHADOW)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

    def _draw_neck(self, painter, start_pos, end_pos, thickness):
        """Draw neck as cylinder"""
        self._draw_limb_capsule(painter, start_pos[0], start_pos[1],
                               end_pos[0], end_pos[1], thickness)

    def _draw_torso(self, painter, x1, y1, x2, y2, width):
        """Draw torso as thick capsule"""
        self._draw_limb_capsule(painter, x1, y1, x2, y2, width)

    def _draw_upper_arm(self, painter, shoulder, elbow, thickness):
        """Draw upper arm cylinder"""
        self._draw_limb_capsule(painter, shoulder[0], shoulder[1],
                               elbow[0], elbow[1], thickness)

    def _draw_lower_arm(self, painter, elbow, wrist, thickness):
        """Draw lower arm cylinder"""
        self._draw_limb_capsule(painter, elbow[0], elbow[1],
                               wrist[0], wrist[1], thickness)

    def _draw_upper_leg(self, painter, hip, knee, thickness):
        """Draw upper leg (thigh) cylinder"""
        self._draw_limb_capsule(painter, hip[0], hip[1],
                               knee[0], knee[1], thickness)

    def _draw_lower_leg(self, painter, knee, ankle, thickness):
        """Draw lower leg (shin) cylinder"""
        self._draw_limb_capsule(painter, knee[0], knee[1],
                               ankle[0], ankle[1], thickness)

    def _draw_hand(self, painter, x, y, width, height):
        """Draw detailed hand with 4 fingers + thumb (fist pose)"""
        painter.setPen(Qt.PenStyle.NoPen)

        # Palm base
        palm_w = width * 0.85
        palm_h = height * 0.65

        palm_gradient = QLinearGradient(x - palm_w/2, y, x + palm_w/2, y)
        palm_gradient.setColorAt(0.0, self.BODY_HIGHLIGHT)
        palm_gradient.setColorAt(0.5, self.BODY_MIDTONE)
        palm_gradient.setColorAt(1.0, self.BODY_SHADOW)

        painter.setBrush(QBrush(palm_gradient))
        palm_rect = QRectF(x - palm_w/2, y - palm_h/2, palm_w, palm_h)
        painter.drawRoundedRect(palm_rect, palm_w * 0.3, palm_w * 0.3)

        # Finger dimensions (compact fist)
        finger_w = width * 0.18
        finger_h = height * 0.50
        finger_y_offset = -palm_h * 0.4  # Fingers curl on top

        # 4 fingers (index, middle, ring, pinky) - curled on top of palm
        finger_positions = [
            x - palm_w * 0.32,  # Index (leftmost)
            x - palm_w * 0.12,  # Middle
            x + palm_w * 0.08,  # Ring
            x + palm_w * 0.28   # Pinky (rightmost)
        ]

        for finger_x in finger_positions:
            self._draw_finger(painter, finger_x, y + finger_y_offset, finger_w, finger_h)

        # Thumb (angled outward from side)
        thumb_w = width * 0.20
        thumb_h = height * 0.42
        thumb_x = x - palm_w * 0.50  # Left side of palm
        thumb_y = y + palm_h * 0.15   # Lower than fingers

        self._draw_finger(painter, thumb_x, thumb_y, thumb_w, thumb_h)

    def _draw_finger(self, painter, x, y, width, height):
        """Draw single finger segment with gradient"""
        gradient = QLinearGradient(x - width/2, y, x + width/2, y)
        gradient.setColorAt(0.0, self.BODY_MIDTONE)
        gradient.setColorAt(0.5, self.BODY_SHADOW)
        gradient.setColorAt(1.0, QColor(
            self.BODY_SHADOW.red() - 10,
            self.BODY_SHADOW.green() - 10,
            self.BODY_SHADOW.blue() - 10
        ))

        painter.setBrush(QBrush(gradient))
        finger_rect = QRectF(x - width/2, y - height/2, width, height)
        painter.drawRoundedRect(finger_rect, width * 0.4, width * 0.4)

    def _draw_foot(self, painter, x, y, width, height, is_left):
        """Draw foot/shoe as rounded capsule"""
        direction = -1 if is_left else 1
        center_x = x + direction * width * 0.15

        gradient = QLinearGradient(center_x - width/2, y, center_x + width/2, y)
        gradient.setColorAt(0.0, self.BODY_HIGHLIGHT)
        gradient.setColorAt(0.5, self.BODY_MIDTONE)
        gradient.setColorAt(1.0, self.BODY_SHADOW)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))

        rect = QRectF(center_x - width/2, y - height/2, width, height)
        painter.drawRoundedRect(rect, height * 0.4, height * 0.4)

    # ===== CORE RENDERING PRIMITIVES =====

    def _draw_limb_capsule(self, painter, x1, y1, x2, y2, thickness):
        """
        Draw volumetric limb as filled capsule with gradient
        Core method used by all cylindrical body parts
        """
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        if length < 0.1:
            return

        # Perpendicular unit vector
        px = -dy / length
        py = dx / length

        radius = thickness / 2

        # Create capsule path
        path = QPainterPath()
        path.moveTo(x1 + px * radius, y1 + py * radius)
        path.lineTo(x2 + px * radius, y2 + py * radius)

        # Round end cap at x2,y2
        path.arcTo(
            x2 - radius, y2 - radius,
            thickness, thickness,
            math.degrees(math.atan2(dy, dx)) - 90,
            180
        )

        path.lineTo(x1 - px * radius, y1 - py * radius)

        # Round end cap at x1,y1
        path.arcTo(
            x1 - radius, y1 - radius,
            thickness, thickness,
            math.degrees(math.atan2(dy, dx)) + 90,
            180
        )

        path.closeSubpath()

        # Perpendicular gradient for 3D cylinder effect
        gradient = QLinearGradient(
            x1 + px * radius, y1 + py * radius,
            x1 - px * radius, y1 - py * radius
        )
        gradient.setColorAt(0.0, self.BODY_HIGHLIGHT)
        gradient.setColorAt(0.5, self.BODY_MIDTONE)
        gradient.setColorAt(1.0, self.BODY_SHADOW)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)

    def _draw_soft_shadow(self, painter, cx, cy, width, opacity):
        """Draw soft ground shadow"""
        gradient = QRadialGradient(QPointF(cx + 8, cy + 5), width / 2)
        gradient.setColorAt(0.0, QColor(20, 20, 20, int(255 * opacity)))
        gradient.setColorAt(0.5, QColor(20, 20, 20, int(255 * opacity * 0.5)))
        gradient.setColorAt(1.0, QColor(20, 20, 20, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(
            QRectF(cx - width/2, cy - width*0.167, width, width*0.334)
        )

    # ===== GLOW SYSTEM (SUBTLE - lit ON skin) =====

    def _draw_joint_glow_subtle(self, painter, x, y, radius):
        """
        Draw SUBTLE cyan glow at joint
        2-layer system: soft outer + brighter inner
        Effect: looks like light ON the skin, not harsh outward glow
        """
        painter.setPen(Qt.PenStyle.NoPen)

        # Layer 1: Soft outer diffuse glow
        outer_gradient = QRadialGradient(QPointF(x, y), radius)
        outer_color = self.GLOW_CYAN
        outer_gradient.setColorAt(0.0, QColor(outer_color.red(), outer_color.green(),
                                              outer_color.blue(),
                                              int(255 * self.GLOW_OUTER_OPACITY)))
        outer_gradient.setColorAt(1.0, QColor(outer_color.red(), outer_color.green(),
                                              outer_color.blue(), 0))

        painter.setBrush(QBrush(outer_gradient))
        painter.drawEllipse(QPointF(x, y), radius, radius)

        # Layer 2: Brighter inner core (smaller, subtle)
        inner_radius = radius * 0.4
        inner_gradient = QRadialGradient(QPointF(x, y), inner_radius)
        inner_gradient.setColorAt(0.0, QColor(outer_color.red(), outer_color.green(),
                                              outer_color.blue(),
                                              int(255 * self.GLOW_INNER_OPACITY)))
        inner_gradient.setColorAt(1.0, QColor(outer_color.red(), outer_color.green(),
                                              outer_color.blue(), 0))

        painter.setBrush(QBrush(inner_gradient))
        painter.drawEllipse(QPointF(x, y), inner_radius, inner_radius)

    def _draw_cyan_slit_eyes(self, painter, cx, cy, head_radius):
        """Draw horizontal cyan slit eyes with subtle glow"""
        eye_w = head_radius * 0.35  # 28px at standard scale
        eye_h = head_radius * 0.05  # 4px - very narrow horizontal slit
        eye_spacing = head_radius * 0.40
        eye_y_offset = -head_radius * 0.125  # Upper part of head

        left_eye_x = cx - eye_spacing
        right_eye_x = cx + eye_spacing
        eye_y = cy + eye_y_offset

        # Draw both eyes
        self._draw_single_eye_slit(painter, left_eye_x, eye_y, eye_w, eye_h)
        self._draw_single_eye_slit(painter, right_eye_x, eye_y, eye_w, eye_h)

    def _draw_single_eye_slit(self, painter, x, y, width, height):
        """Draw single horizontal slit eye with subtle glow"""
        painter.setPen(Qt.PenStyle.NoPen)

        # Layer 1: Soft outer glow
        outer_w = width * 2.0
        outer_h = height * 2.5

        outer_gradient = QRadialGradient(QPointF(x, y), outer_w / 2)
        glow_color = self.GLOW_CYAN
        outer_gradient.setColorAt(0.0, QColor(glow_color.red(), glow_color.green(),
                                              glow_color.blue(),
                                              int(255 * self.GLOW_EYE_OUTER_OPACITY)))
        outer_gradient.setColorAt(1.0, QColor(glow_color.red(), glow_color.green(),
                                              glow_color.blue(), 0))

        painter.setBrush(QBrush(outer_gradient))
        painter.drawEllipse(QRectF(x - outer_w/2, y - outer_h/2, outer_w, outer_h))

        # Layer 2: Inner glow
        mid_w = width * 1.3
        mid_h = height * 1.8

        mid_gradient = QRadialGradient(QPointF(x, y), mid_w / 2)
        mid_gradient.setColorAt(0.0, QColor(glow_color.red(), glow_color.green(),
                                           glow_color.blue(),
                                           int(255 * self.GLOW_EYE_INNER_OPACITY)))
        mid_gradient.setColorAt(1.0, QColor(glow_color.red(), glow_color.green(),
                                           glow_color.blue(), 0))

        painter.setBrush(QBrush(mid_gradient))
        painter.drawEllipse(QRectF(x - mid_w/2, y - mid_h/2, mid_w, mid_h))

        # Layer 3: Sharp bright slit core
        painter.setBrush(QColor(150, 255, 255))  # Bright cyan-white
        painter.drawEllipse(QRectF(x - width/2, y - height/2, width, height))
