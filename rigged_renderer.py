"""
Rigged Renderer - Skeleton-Driven Character Rendering
======================================================

This module renders toon characters using skeleton bone positions and
anatomy style definitions. It bridges the gap between:
  - StickmanRig (skeletal pose data)
  - ToonAnatomy (visual style data)
  - QPainter (actual rendering)

Architecture:
  Skeleton (bone positions) + Anatomy (style rules) → RiggedRenderer → Visual output

Key Features:
- Renders from T-pose or any animated pose
- Supports volumetric (gradient) and flat (solid) rendering
- Handles detailed 5-finger hands and simple mitten hands
- Multiple eye styles (slit, googly, dots)
- Optional joint glows (per-anatomy configuration)
- Proper depth layering (back to front)

Usage:
    anatomy = create_neon_cyan_anatomy()
    renderer = RiggedRenderer(anatomy)
    renderer.render_from_skeleton(painter, skeleton, cx, cy, scale=1.0)
"""

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QLinearGradient,
                           QRadialGradient, QPainterPath)
import math
from typing import Dict, Tuple, Optional

from toon_anatomy import (
    ToonAnatomy, RenderStyle, EyeStyle, HandStyle,
    NeonCyanAnatomy, ShadowRedAnatomy, GooglyEyesAnatomy
)
from rig_system import StickmanRig


# ============================================================================
# RIGGED RENDERER - Main Rendering Class
# ============================================================================

class RiggedRenderer:
    """
    Renders a toon character from skeleton bone positions using anatomy style.

    This is the core rendering engine that takes skeletal poses and converts
    them to visual output. It uses ToonAnatomy data to determine colors,
    proportions, and rendering style.
    """

    def __init__(self, anatomy: ToonAnatomy):
        """
        Initialize renderer with specific toon anatomy.

        Args:
            anatomy: ToonAnatomy instance (Neon Cyan, Shadow Red, or Googly Eyes)
        """
        self.anatomy = anatomy

    def render_from_skeleton(self, painter: QPainter, skeleton: StickmanRig,
                            cx: float, cy: float, scale: float = 1.0):
        """
        Main rendering method - draws complete character from skeleton pose.

        Args:
            painter: QPainter instance for drawing
            skeleton: StickmanRig with current pose
            cx, cy: Center position in screen coordinates
            scale: Overall scale multiplier
        """
        # Get all joint world positions from skeleton
        transforms = skeleton.get_joint_transforms()

        # Apply offset and scale to all positions
        joints = {}
        for name, (x, y) in transforms.items():
            joints[name] = (cx + x * scale, cy + y * scale)

        # ===== RENDERING ORDER (Back to Front for proper layering) =====

        # 1. Ground shadow
        pelvis = joints.get("pelvis", (cx, cy))
        self._draw_ground_shadow(painter, pelvis[0], pelvis[1] + 200 * scale, scale)

        # 2. Back leg (left side)
        if "foot_L" in joints and "shin_L" in joints and "thigh_L" in joints:
            hip_l = joints.get("pelvis", pelvis)  # Hips attach to pelvis
            knee_l = joints["shin_L"]  # Joint between thigh and shin
            ankle_l = joints["foot_L"]

            # Draw leg segments
            self._render_limb(painter, hip_l, knee_l,
                            self.anatomy.get_upper_leg_thickness(scale), scale)
            self._render_limb(painter, knee_l, ankle_l,
                            self.anatomy.get_lower_leg_thickness(scale), scale)

            # Draw foot
            foot_w, foot_h = self.anatomy.get_foot_dimensions(scale)
            self._render_foot(painter, ankle_l[0], ankle_l[1], foot_w, foot_h,is_left=True)

            # Draw joints
            self._render_joint(painter, hip_l, self.anatomy.get_joint_radius(scale), scale, "hip_L")
            self._render_joint(painter, knee_l, self.anatomy.get_joint_radius(scale), scale, "knee_L")
            self._render_joint(painter, ankle_l, self.anatomy.get_joint_radius(scale, 0.85), scale, "ankle_L")

        # 3. Back arm (right side in T-pose)
        if "hand_R" in joints and "lower_arm_R" in joints and "upper_arm_R" in joints:
            shoulder_r = joints.get("spine_upper", pelvis)
            elbow_r = joints["lower_arm_R"]
            wrist_r = joints["hand_R"]

            # Draw arm segments
            self._render_limb(painter, shoulder_r, elbow_r,
                            self.anatomy.get_upper_arm_thickness(scale), scale)
            self._render_limb(painter, elbow_r, wrist_r,
                            self.anatomy.get_lower_arm_thickness(scale), scale)

            # Draw hand
            hand_w, hand_h = self.anatomy.get_hand_dimensions(scale)
            hand_angle = math.atan2(wrist_r[1] - elbow_r[1], wrist_r[0] - elbow_r[0])
            self._render_hand(painter, wrist_r[0], wrist_r[1], hand_w, hand_h, hand_angle)

            # Draw joints
            self._render_joint(painter, shoulder_r, self.anatomy.get_joint_radius(scale), scale, "shoulder_R")
            self._render_joint(painter, elbow_r, self.anatomy.get_joint_radius(scale, 0.9), scale, "elbow_R")
            self._render_joint(painter, wrist_r, self.anatomy.get_joint_radius(scale, 0.75), scale, "wrist_R")

        # 4. Torso and neck
        if "spine_lower" in joints and "spine_upper" in joints:
            spine_lower = joints["spine_lower"]
            spine_upper = joints["spine_upper"]

            # Draw torso
            torso_w = self.anatomy.get_torso_width(scale)
            self._render_torso(painter, spine_lower, spine_upper, torso_w, scale)

        if "neck" in joints and "spine_upper" in joints:
            neck_base = joints["spine_upper"]
            neck_top = joints["neck"]
            neck_thick = self.anatomy.get_neck_thickness(scale)
            self._render_limb(painter, neck_base, neck_top, neck_thick, scale)

        # 5. Front leg (right side)
        if "foot_R" in joints and "shin_R" in joints and "thigh_R" in joints:
            hip_r = joints.get("pelvis", pelvis)
            knee_r = joints["shin_R"]
            ankle_r = joints["foot_R"]

            # Draw leg segments
            self._render_limb(painter, hip_r, knee_r,
                            self.anatomy.get_upper_leg_thickness(scale), scale)
            self._render_limb(painter, knee_r, ankle_r,
                            self.anatomy.get_lower_leg_thickness(scale), scale)

            # Draw foot
            foot_w, foot_h = self.anatomy.get_foot_dimensions(scale)
            self._render_foot(painter, ankle_r[0], ankle_r[1], foot_w, foot_h, is_left=False)

            # Draw joints
            self._render_joint(painter, hip_r, self.anatomy.get_joint_radius(scale), scale, "hip_R")
            self._render_joint(painter, knee_r, self.anatomy.get_joint_radius(scale), scale, "knee_R")
            self._render_joint(painter, ankle_r, self.anatomy.get_joint_radius(scale, 0.85), scale, "ankle_R")

        # 6. Front arm (left side in T-pose)
        if "hand_L" in joints and "lower_arm_L" in joints and "upper_arm_L" in joints:
            shoulder_l = joints.get("spine_upper", pelvis)
            elbow_l = joints["lower_arm_L"]
            wrist_l = joints["hand_L"]

            # Draw arm segments
            self._render_limb(painter, shoulder_l, elbow_l,
                            self.anatomy.get_upper_arm_thickness(scale), scale)
            self._render_limb(painter, elbow_l, wrist_l,
                            self.anatomy.get_lower_arm_thickness(scale), scale)

            # Draw hand
            hand_w, hand_h = self.anatomy.get_hand_dimensions(scale)
            hand_angle = math.atan2(wrist_l[1] - elbow_l[1], wrist_l[0] - elbow_l[0])
            self._render_hand(painter, wrist_l[0], wrist_l[1], hand_w, hand_h, hand_angle)

            # Draw joints
            self._render_joint(painter, shoulder_l, self.anatomy.get_joint_radius(scale), scale, "shoulder_L")
            self._render_joint(painter, elbow_l, self.anatomy.get_joint_radius(scale, 0.9), scale, "elbow_L")
            self._render_joint(painter, wrist_l, self.anatomy.get_joint_radius(scale, 0.75), scale, "wrist_L")

        # 7. Head
        if "head" in joints:
            head_pos = joints["head"]
            head_r = self.anatomy.get_head_radius(scale)
            self._render_head(painter, head_pos[0], head_pos[1], head_r)

            # 8. Eyes (top layer)
            self._render_eyes(painter, head_pos[0], head_pos[1], head_r)

        # 9. Neck joint
        if "neck" in joints:
            neck_pos = joints["neck"]
            self._render_joint(painter, neck_pos, self.anatomy.get_joint_radius(scale, 0.6), scale, "neck")

    # ===== HIGH-LEVEL RENDERING METHODS =====

    def _render_limb(self, painter: QPainter, start_pos: Tuple[float, float],
                    end_pos: Tuple[float, float], thickness: float, scale: float):
        """Render limb between two joints using anatomy style"""
        if self.anatomy.RENDER_STYLE == RenderStyle.VOLUMETRIC:
            self._draw_volumetric_capsule(painter, start_pos, end_pos, thickness)
        else:  # FLAT
            self._draw_flat_cylinder(painter, start_pos, end_pos, thickness)

    def _render_joint(self, painter: QPainter, pos: Tuple[float, float],
                     radius: float, scale: float, joint_name: str):
        """Render joint sphere with optional glow"""
        # Draw base joint sphere
        if self.anatomy.RENDER_STYLE == RenderStyle.VOLUMETRIC:
            self._draw_volumetric_joint(painter, pos[0], pos[1], radius)
        else:
            self._draw_flat_joint(painter, pos[0], pos[1], radius)

        # Draw glow if this joint should glow
        if self.anatomy.HAS_GLOWS and joint_name in self.anatomy.GLOW_JOINTS:
            self._draw_joint_glow(painter, pos[0], pos[1], radius * 1.2)

    def _render_torso(self, painter: QPainter, bottom_pos: Tuple[float, float],
                     top_pos: Tuple[float, float], width: float, scale: float):
        """Render torso as thick rounded capsule"""
        if self.anatomy.RENDER_STYLE == RenderStyle.VOLUMETRIC:
            self._draw_volumetric_torso(painter, bottom_pos, top_pos, width)
        else:
            self._draw_flat_torso(painter, bottom_pos, top_pos, width)

        # Draw torso center glow if enabled (Toon 1 has this!)
        if hasattr(self.anatomy, 'HAS_TORSO_GLOW') and self.anatomy.HAS_TORSO_GLOW:
            cx = (bottom_pos[0] + top_pos[0]) / 2
            cy = (bottom_pos[1] + top_pos[1]) / 2
            glow_radius = width * 0.5  # Glow size
            self._draw_torso_glow(painter, cx, cy, glow_radius)

    def _render_hand(self, painter: QPainter, x: float, y: float,
                    width: float, height: float, angle: float):
        """Render hand (detailed fingers or simple mitten)"""
        if self.anatomy.HAND_STYLE == HandStyle.DETAILED_FINGERS:
            self._draw_detailed_hand_5_fingers(painter, x, y, width, height, angle)
        else:
            self._draw_simple_mitten_hand(painter, x, y, width, height)

    def _render_foot(self, painter: QPainter, x: float, y: float,
                    width: float, height: float, is_left: bool):
        """Render foot"""
        if self.anatomy.RENDER_STYLE == RenderStyle.VOLUMETRIC:
            self._draw_volumetric_foot(painter, x, y, width, height, is_left)
        else:
            self._draw_flat_foot(painter, x, y, width, height, is_left)

    def _render_head(self, painter: QPainter, cx: float, cy: float, radius: float):
        """Render head sphere"""
        if self.anatomy.RENDER_STYLE == RenderStyle.VOLUMETRIC:
            self._draw_volumetric_head(painter, cx, cy, radius)
        else:
            self._draw_flat_head(painter, cx, cy, radius)

    def _render_eyes(self, painter: QPainter, cx: float, cy: float, head_radius: float):
        """Render eyes based on anatomy style"""
        if self.anatomy.EYE_STYLE == EyeStyle.SLIT:
            self._draw_slit_eyes(painter, cx, cy, head_radius)
        elif self.anatomy.EYE_STYLE == EyeStyle.GOOGLY:
            self._draw_googly_eyes(painter, cx, cy, head_radius)
        elif self.anatomy.EYE_STYLE == EyeStyle.DOTS:
            self._draw_dot_eyes(painter, cx, cy, head_radius)

    # ===== VOLUMETRIC RENDERING PRIMITIVES (Toon 1 & 2) =====

    def _draw_volumetric_capsule(self, painter: QPainter, start_pos: Tuple[float, float],
                                end_pos: Tuple[float, float], thickness: float):
        """Draw limb capsule with perpendicular gradient (3D cylinder effect)"""
        x1, y1 = start_pos
        x2, y2 = end_pos

        # Calculate perpendicular direction for gradient
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        if length < 0.1:
            return

        # Perpendicular unit vector
        px = -dy / length
        py = dx / length

        # Create gradient perpendicular to limb (left lit, right shadow)
        gradient = QLinearGradient(
            x1 + px * thickness * 0.5,
            y1 + py * thickness * 0.5,
            x1 - px * thickness * 0.5,
            y1 - py * thickness * 0.5
        )
        gradient.setColorAt(0.0, self.anatomy.BODY_HIGHLIGHT)
        gradient.setColorAt(0.5, self.anatomy.BODY_MIDTONE)
        gradient.setColorAt(1.0, self.anatomy.BODY_SHADOW)

        # Draw as thick rounded line
        pen = QPen(QBrush(gradient), thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def _draw_volumetric_joint(self, painter: QPainter, x: float, y: float, radius: float):
        """Draw joint sphere with radial gradient (3D sphere)"""
        # Offset highlight for 3D effect
        offset_x = -radius * 0.25
        offset_y = -radius * 0.25

        gradient = QRadialGradient(
            QPointF(x + offset_x, y + offset_y),
            radius * 1.2
        )
        gradient.setColorAt(0.0, self.anatomy.BODY_HIGHLIGHT)
        gradient.setColorAt(0.6, self.anatomy.BODY_MIDTONE)
        gradient.setColorAt(1.0, self.anatomy.BODY_SHADOW)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(x, y), radius, radius)

    def _draw_volumetric_torso(self, painter: QPainter, bottom_pos: Tuple[float, float],
                              top_pos: Tuple[float, float], width: float):
        """Draw torso as rounded rectangle with horizontal gradient"""
        x1, y1 = bottom_pos
        x2, y2 = top_pos
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        height = abs(y2 - y1)

        # Horizontal gradient (left lit, right shadow)
        gradient = QLinearGradient(cx - width / 2, cy, cx + width / 2, cy)
        gradient.setColorAt(0.0, self.anatomy.BODY_HIGHLIGHT)
        gradient.setColorAt(0.5, self.anatomy.BODY_MIDTONE)
        gradient.setColorAt(1.0, self.anatomy.BODY_SHADOW)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))

        rect = QRectF(cx - width / 2, min(y1, y2), width, height)
        painter.drawRoundedRect(rect, width * 0.3, width * 0.3)

    def _draw_volumetric_head(self, painter: QPainter, cx: float, cy: float, radius: float):
        """Draw head sphere with offset radial gradient"""
        offset_x = -radius * 0.25
        offset_y = -radius * 0.25

        gradient = QRadialGradient(
            QPointF(cx + offset_x, cy + offset_y),
            radius * 1.2
        )
        gradient.setColorAt(0.0, self.anatomy.BODY_HIGHLIGHT)
        gradient.setColorAt(1.0, self.anatomy.BODY_SHADOW)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

    def _draw_volumetric_foot(self, painter: QPainter, x: float, y: float,
                             width: float, height: float, is_left: bool):
        """Draw foot with vertical gradient"""
        gradient = QLinearGradient(x, y - height*0.3, x, y + height*0.7)
        gradient.setColorAt(0.0, self.anatomy.BODY_MIDTONE)
        gradient.setColorAt(1.0, self.anatomy.BODY_SHADOW)

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

    # ===== FLAT RENDERING PRIMITIVES (Toon 3 - Googly Eyes) =====

    def _draw_flat_cylinder(self, painter: QPainter, start_pos: Tuple[float, float],
                           end_pos: Tuple[float, float], thickness: float):
        """Draw limb as solid black cylinder (no gradient)"""
        x1, y1 = start_pos
        x2, y2 = end_pos

        pen = QPen(self.anatomy.BODY_HIGHLIGHT, thickness, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def _draw_flat_joint(self, painter: QPainter, x: float, y: float, radius: float):
        """Draw joint as solid black circle"""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.anatomy.BODY_HIGHLIGHT))
        painter.drawEllipse(QPointF(x, y), radius, radius)

    def _draw_flat_torso(self, painter: QPainter, bottom_pos: Tuple[float, float],
                        top_pos: Tuple[float, float], width: float):
        """Draw torso as solid black rounded rectangle"""
        x1, y1 = bottom_pos
        x2, y2 = top_pos
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        height = abs(y2 - y1)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.anatomy.BODY_HIGHLIGHT))

        rect = QRectF(cx - width / 2, min(y1, y2), width, height)
        painter.drawRoundedRect(rect, width * 0.25, width * 0.25)

    def _draw_flat_head(self, painter: QPainter, cx: float, cy: float, radius: float):
        """Draw head as solid black circle"""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.anatomy.BODY_HIGHLIGHT))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

    def _draw_flat_foot(self, painter: QPainter, x: float, y: float,
                       width: float, height: float, is_left: bool):
        """Draw foot as solid black rounded rectangle"""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.anatomy.BODY_HIGHLIGHT))

        direction = -1 if is_left else 1
        rect = QRectF(
            x - width/2 + direction * width * 0.15,
            y - height * 0.3,
            width,
            height
        )
        painter.drawRoundedRect(rect, height * 0.35, height * 0.35)

    # ===== HAND RENDERING =====

    def _draw_simple_mitten_hand(self, painter: QPainter, x: float, y: float,
                                width: float, height: float):
        """Draw simple blocky hand (Toon 2 & 3)"""
        if self.anatomy.RENDER_STYLE == RenderStyle.VOLUMETRIC:
            gradient = QLinearGradient(x, y, x, y + height)
            gradient.setColorAt(0.0, self.anatomy.BODY_MIDTONE)
            gradient.setColorAt(1.0, self.anatomy.BODY_SHADOW)
            painter.setBrush(QBrush(gradient))
        else:
            painter.setBrush(QBrush(self.anatomy.BODY_HIGHLIGHT))

        painter.setPen(Qt.PenStyle.NoPen)
        rect = QRectF(x - width/2, y, width, height)
        painter.drawRoundedRect(rect, width * 0.3, width * 0.3)

    def _draw_detailed_hand_5_fingers(self, painter: QPainter, x: float, y: float,
                                     width: float, height: float, angle: float):
        """Draw detailed hand with 5 fingers (Toon 1)"""
        painter.setPen(Qt.PenStyle.NoPen)

        # Palm base
        palm_w = width * 0.85
        palm_h = height * 0.65

        palm_gradient = QLinearGradient(x - palm_w/2, y, x + palm_w/2, y)
        palm_gradient.setColorAt(0.0, self.anatomy.BODY_HIGHLIGHT)
        palm_gradient.setColorAt(0.5, self.anatomy.BODY_MIDTONE)
        palm_gradient.setColorAt(1.0, self.anatomy.BODY_SHADOW)

        painter.setBrush(QBrush(palm_gradient))
        palm_rect = QRectF(x - palm_w/2, y - palm_h/2, palm_w, palm_h)
        painter.drawRoundedRect(palm_rect, palm_w * 0.3, palm_w * 0.3)

        # Finger dimensions
        finger_w = width * 0.18
        finger_h = height * 0.50
        finger_y_offset = -palm_h * 0.4

        # 4 fingers on top of palm
        finger_positions = [
            x - palm_w * 0.32,  # Index
            x - palm_w * 0.12,  # Middle
            x + palm_w * 0.08,  # Ring
            x + palm_w * 0.28   # Pinky
        ]

        for finger_x in finger_positions:
            self._draw_finger(painter, finger_x, y + finger_y_offset, finger_w, finger_h)

        # Thumb (side of palm)
        thumb_w = width * 0.20
        thumb_h = height * 0.42
        thumb_x = x - palm_w * 0.50
        thumb_y = y + palm_h * 0.15
        self._draw_finger(painter, thumb_x, thumb_y, thumb_w, thumb_h)

    def _draw_finger(self, painter: QPainter, x: float, y: float,
                    width: float, height: float):
        """Draw single finger segment"""
        gradient = QLinearGradient(x - width/2, y, x + width/2, y)
        gradient.setColorAt(0.0, self.anatomy.BODY_MIDTONE)
        gradient.setColorAt(0.5, self.anatomy.BODY_SHADOW)
        gradient.setColorAt(1.0, QColor(
            max(0, self.anatomy.BODY_SHADOW.red() - 10),
            max(0, self.anatomy.BODY_SHADOW.green() - 10),
            max(0, self.anatomy.BODY_SHADOW.blue() - 10)
        ))

        painter.setBrush(QBrush(gradient))
        finger_rect = QRectF(x - width/2, y - height/2, width, height)
        painter.drawRoundedRect(finger_rect, width * 0.4, width * 0.4)

    # ===== EYE RENDERING =====

    def _draw_slit_eyes(self, painter: QPainter, cx: float, cy: float, head_radius: float):
        """Draw horizontal glowing slit eyes (Toon 1 & 2)"""
        eye_w = head_radius * self.anatomy.EYE_WIDTH_RATIO
        eye_h = head_radius * self.anatomy.EYE_HEIGHT_RATIO
        eye_spacing = head_radius * self.anatomy.EYE_SPACING_RATIO
        eye_y_offset = head_radius * self.anatomy.EYE_Y_OFFSET_RATIO

        left_eye_x = cx - eye_spacing
        right_eye_x = cx + eye_spacing
        eye_y = cy + eye_y_offset

        # Draw both eyes
        self._draw_single_slit_eye(painter, left_eye_x, eye_y, eye_w, eye_h)
        self._draw_single_slit_eye(painter, right_eye_x, eye_y, eye_w, eye_h)

    def _draw_single_slit_eye(self, painter: QPainter, x: float, y: float,
                             width: float, height: float):
        """Draw single glowing slit eye (2-3 layer glow)"""
        painter.setPen(Qt.PenStyle.NoPen)

        glow_intensity = self.anatomy.glow_intensity

        # Layer 1: Outer glow (soft)
        outer_w = width * 2.0
        outer_h = height * 2.5

        outer_gradient = QRadialGradient(QPointF(x, y), outer_w / 2)
        outer_gradient.setColorAt(0.0, QColor(
            self.anatomy.EYE_COLOR.red(),
            self.anatomy.EYE_COLOR.green(),
            self.anatomy.EYE_COLOR.blue(),
            int(255 * 0.15 * glow_intensity)
        ))
        outer_gradient.setColorAt(1.0, QColor(
            self.anatomy.EYE_COLOR.red(),
            self.anatomy.EYE_COLOR.green(),
            self.anatomy.EYE_COLOR.blue(),
            0
        ))

        painter.setBrush(QBrush(outer_gradient))
        painter.drawEllipse(QRectF(x - outer_w/2, y - outer_h/2, outer_w, outer_h))

        # Layer 2: Mid glow (brighter)
        mid_w = width * 1.3
        mid_h = height * 1.8

        mid_gradient = QRadialGradient(QPointF(x, y), mid_w / 2)
        mid_gradient.setColorAt(0.0, QColor(
            self.anatomy.EYE_COLOR.red(),
            self.anatomy.EYE_COLOR.green(),
            self.anatomy.EYE_COLOR.blue(),
            int(255 * 0.40 * glow_intensity)
        ))
        mid_gradient.setColorAt(1.0, QColor(
            self.anatomy.EYE_COLOR.red(),
            self.anatomy.EYE_COLOR.green(),
            self.anatomy.EYE_COLOR.blue(),
            0
        ))

        painter.setBrush(QBrush(mid_gradient))
        painter.drawEllipse(QRectF(x - mid_w/2, y - mid_h/2, mid_w, mid_h))

        # Layer 3: Core slit (bright solid)
        painter.setBrush(self.anatomy.EYE_COLOR)
        painter.drawEllipse(QRectF(x - width/2, y - height/2, width, height))

    def _draw_googly_eyes(self, painter: QPainter, cx: float, cy: float, head_radius: float):
        """Draw googly cartoon eyes with movable pupils (Toon 3)"""
        eye_size = head_radius * self.anatomy.EYE_WIDTH_RATIO * self.anatomy.eye_size_multiplier
        eye_spacing = head_radius * self.anatomy.EYE_SPACING_RATIO
        eye_y_offset = head_radius * self.anatomy.EYE_Y_OFFSET_RATIO

        left_eye_x = cx - eye_spacing
        right_eye_x = cx + eye_spacing
        eye_y = cy + eye_y_offset

        # Draw both eyes
        self._draw_single_googly_eye(painter, left_eye_x, eye_y, eye_size)
        self._draw_single_googly_eye(painter, right_eye_x, eye_y, eye_size)

    def _draw_single_googly_eye(self, painter: QPainter, cx: float, cy: float, size: float):
        """Draw single googly eye (white with black pupil)"""
        painter.setPen(Qt.PenStyle.NoPen)

        # White eye background
        painter.setBrush(self.anatomy.EYE_COLOR)
        painter.drawEllipse(QPointF(cx, cy), size, size)

        # Black pupil (can be offset for derpy effect)
        pupil_size = size * 0.4
        pupil_x = cx + self.anatomy.pupil_offset_x * size * 0.5
        pupil_y = cy + self.anatomy.pupil_offset_y * size * 0.5

        painter.setBrush(self.anatomy.EYE_PUPIL_COLOR)
        painter.drawEllipse(QPointF(pupil_x, pupil_y), pupil_size, pupil_size)

    def _draw_dot_eyes(self, painter: QPainter, cx: float, cy: float, head_radius: float):
        """Draw simple dot eyes"""
        eye_size = head_radius * 0.15
        eye_spacing = head_radius * 0.4
        eye_y_offset = head_radius * -0.1

        left_eye_x = cx - eye_spacing
        right_eye_x = cx + eye_spacing
        eye_y = cy + eye_y_offset

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.anatomy.EYE_COLOR)
        painter.drawEllipse(QPointF(left_eye_x, eye_y), eye_size, eye_size)
        painter.drawEllipse(QPointF(right_eye_x, eye_y), eye_size, eye_size)

    # ===== GLOW & EFFECTS =====

    def _draw_joint_glow(self, painter: QPainter, x: float, y: float, radius: float):
        """Draw subtle glow around joint (for Toon 1)"""
        painter.setPen(Qt.PenStyle.NoPen)

        glow_intensity = self.anatomy.glow_intensity

        # Layer 1: Outer glow (soft)
        outer_gradient = QRadialGradient(QPointF(x, y), radius)
        outer_gradient.setColorAt(0.0, QColor(
            self.anatomy.GLOW_COLOR.red(),
            self.anatomy.GLOW_COLOR.green(),
            self.anatomy.GLOW_COLOR.blue(),
            int(255 * 0.12 * glow_intensity)
        ))
        outer_gradient.setColorAt(1.0, QColor(
            self.anatomy.GLOW_COLOR.red(),
            self.anatomy.GLOW_COLOR.green(),
            self.anatomy.GLOW_COLOR.blue(),
            0
        ))

        painter.setBrush(QBrush(outer_gradient))
        painter.drawEllipse(QPointF(x, y), radius, radius)

        # Layer 2: Inner glow (brighter)
        inner_radius = radius * 0.4
        inner_gradient = QRadialGradient(QPointF(x, y), inner_radius)
        inner_gradient.setColorAt(0.0, QColor(
            self.anatomy.GLOW_COLOR.red(),
            self.anatomy.GLOW_COLOR.green(),
            self.anatomy.GLOW_COLOR.blue(),
            int(255 * 0.30 * glow_intensity)
        ))
        inner_gradient.setColorAt(1.0, QColor(
            self.anatomy.GLOW_COLOR.red(),
            self.anatomy.GLOW_COLOR.green(),
            self.anatomy.GLOW_COLOR.blue(),
            0
        ))

        painter.setBrush(QBrush(inner_gradient))
        painter.drawEllipse(QPointF(x, y), inner_radius, inner_radius)

    def _draw_torso_glow(self, painter: QPainter, cx: float, cy: float, radius: float):
        """Draw glowing center of torso (Toon 1 has cyan chest glow)"""
        painter.setPen(Qt.PenStyle.NoPen)

        glow_intensity = self.anatomy.glow_intensity

        # Layer 1: Outer glow (soft)
        outer_radius = radius * 1.5
        outer_gradient = QRadialGradient(QPointF(cx, cy), outer_radius)
        outer_gradient.setColorAt(0.0, QColor(
            self.anatomy.GLOW_COLOR.red(),
            self.anatomy.GLOW_COLOR.green(),
            self.anatomy.GLOW_COLOR.blue(),
            int(255 * 0.20 * glow_intensity)
        ))
        outer_gradient.setColorAt(1.0, QColor(
            self.anatomy.GLOW_COLOR.red(),
            self.anatomy.GLOW_COLOR.green(),
            self.anatomy.GLOW_COLOR.blue(),
            0
        ))

        painter.setBrush(QBrush(outer_gradient))
        painter.drawEllipse(QPointF(cx, cy), outer_radius, outer_radius)

        # Layer 2: Inner glow (brighter core)
        inner_radius = radius * 0.6
        inner_gradient = QRadialGradient(QPointF(cx, cy), inner_radius)
        inner_gradient.setColorAt(0.0, QColor(
            self.anatomy.GLOW_COLOR.red(),
            self.anatomy.GLOW_COLOR.green(),
            self.anatomy.GLOW_COLOR.blue(),
            int(255 * 0.40 * glow_intensity)
        ))
        inner_gradient.setColorAt(1.0, QColor(
            self.anatomy.GLOW_COLOR.red(),
            self.anatomy.GLOW_COLOR.green(),
            self.anatomy.GLOW_COLOR.blue(),
            0
        ))

        painter.setBrush(QBrush(inner_gradient))
        painter.drawEllipse(QPointF(cx, cy), inner_radius, inner_radius)

    def _draw_ground_shadow(self, painter: QPainter, cx: float, cy: float, scale: float):
        """Draw soft elliptical ground shadow"""
        width = 180 * scale
        opacity = 0.3

        gradient = QRadialGradient(QPointF(cx, cy), width / 2)
        gradient.setColorAt(0.0, QColor(20, 20, 20, int(255 * opacity)))
        gradient.setColorAt(0.5, QColor(20, 20, 20, int(255 * opacity * 0.5)))
        gradient.setColorAt(1.0, QColor(20, 20, 20, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(
            QRectF(cx - width/2, cy - width*0.15, width, width*0.3)
        )


# ============================================================================
# FACTORY FUNCTIONS - Convenience Constructors
# ============================================================================

def create_neon_cyan_renderer() -> RiggedRenderer:
    """Create renderer for Toon 1: Neon Cyan Fighter"""
    from toon_anatomy import create_neon_cyan_anatomy
    return RiggedRenderer(create_neon_cyan_anatomy())


def create_shadow_red_renderer() -> RiggedRenderer:
    """Create renderer for Toon 2: Shadow Red Fighter"""
    from toon_anatomy import create_shadow_red_anatomy
    return RiggedRenderer(create_shadow_red_anatomy())


def create_googly_eyes_renderer() -> RiggedRenderer:
    """Create renderer for Toon 3: Googly Eyes Fighter"""
    from toon_anatomy import create_googly_eyes_anatomy
    return RiggedRenderer(create_googly_eyes_anatomy())
