"""
Classic Capsule Fighter - Toon 3
Placeholder for future implementation
Awaiting reference image from user
"""

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor)


class ClassicCapsuleFighter:
    """
    Classic Capsule Fighter - Toon 3
    PLACEHOLDER - Will be implemented when reference image is provided
    """

    def __init__(self):
        """Initialize Classic Capsule Fighter"""
        pass

    def render(self, painter, cx, cy, scale):
        """
        Main render method - placeholder

        Args:
            painter: QPainter instance
            cx, cy: Center position
            scale: Scale multiplier
        """
        # Placeholder - simple message
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setFont(painter.font())
        painter.drawText(int(cx - 100), int(cy), "Classic Capsule")
        painter.drawText(int(cx - 100), int(cy + 20), "(Awaiting reference)")
