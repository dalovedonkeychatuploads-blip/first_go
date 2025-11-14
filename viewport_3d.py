"""
3D Viewport for stick figure visualization
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QTransform

import math
from stick_renderer import StickRenderer


class Viewport3D(QWidget):
    """2.5D viewport showing the stick figure."""

    def __init__(self):
        super().__init__()
        self.rig = None
        self.rotation_x = 0
        self.rotation_y = 0
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_pos = None
        self.grid_enabled = True
        self.selected_bone = None

        # Initialize stick renderer
        self.renderer = StickRenderer(scale=0.5)

        # Style - lighter background for visibility
        self.setStyleSheet("""
            QWidget {
                background: #4a4a4e;
                border: 1px solid #3a3a3e;
            }
        """)

        # Set minimum size
        self.setMinimumSize(600, 600)

        # Update timer for smooth interaction
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)

    def paintEvent(self, event):
        """Paint the viewport."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor(38, 38, 42))

        # Draw grid
        if self.grid_enabled:
            self.draw_grid(painter)

        # Draw axes
        self.draw_axes(painter)

        # Draw ruler
        self.draw_ruler(painter)

        # Draw stick figure
        if self.rig:
            painter.save()
            painter.translate(self.width() / 2 + self.pan_x,
                            self.height() / 2 + self.pan_y)
            painter.scale(self.zoom, self.zoom)

            # Apply rotation
            transform = QTransform()
            transform.rotate(self.rotation_y, Qt.Axis.YAxis)
            transform.rotate(self.rotation_x, Qt.Axis.XAxis)

            self.draw_stick_figure(painter)
            painter.restore()

        # Draw viewport info
        self.draw_info(painter)

    def draw_grid(self, painter):
        """Draw the reference grid."""
        painter.setPen(QPen(QColor(50, 50, 55), 1, Qt.PenStyle.DotLine))

        grid_size = 50 * self.zoom

        # Vertical lines
        x = self.width() / 2 + self.pan_x
        while x > 0:
            painter.drawLine(int(x), 0, int(x), self.height())
            x -= grid_size

        x = self.width() / 2 + self.pan_x + grid_size
        while x < self.width():
            painter.drawLine(int(x), 0, int(x), self.height())
            x += grid_size

        # Horizontal lines
        y = self.height() / 2 + self.pan_y
        while y > 0:
            painter.drawLine(0, int(y), self.width(), int(y))
            y -= grid_size

        y = self.height() / 2 + self.pan_y + grid_size
        while y < self.height():
            painter.drawLine(0, int(y), self.width(), int(y))
            y += grid_size

    def draw_axes(self, painter):
        """Draw the coordinate axes."""
        center_x = self.width() / 2 + self.pan_x
        center_y = self.height() / 2 + self.pan_y

        # X axis (red)
        painter.setPen(QPen(QColor(150, 50, 50), 2))
        painter.drawLine(center_x, center_y, center_x + 50 * self.zoom, center_y)

        # Y axis (green)
        painter.setPen(QPen(QColor(50, 150, 50), 2))
        painter.drawLine(center_x, center_y, center_x, center_y - 50 * self.zoom)

    def draw_ruler(self, painter):
        """Draw height ruler on the left side."""
        painter.setPen(QPen(QColor(100, 100, 105), 1))
        painter.setFont(QFont("Consolas", 8))

        # Draw ruler background
        painter.fillRect(0, 0, 40, self.height(), QColor(32, 32, 36))

        # Draw measurements
        center_y = self.height() / 2 + self.pan_y
        unit_size = 30 * self.zoom  # 30 pixels = 10cm

        for i in range(-10, 11):
            y = center_y - i * unit_size * 2
            if 0 <= y <= self.height():
                height_cm = i * 20
                if height_cm % 50 == 0:
                    painter.setPen(QPen(QColor(150, 150, 155), 1))
                    painter.drawLine(30, int(y), 40, int(y))
                    if height_cm >= 0:
                        painter.drawText(5, int(y) + 3, f"{height_cm}")
                else:
                    painter.setPen(QPen(QColor(80, 80, 85), 1))
                    painter.drawLine(35, int(y), 40, int(y))

    def draw_stick_figure(self, painter):
        """Draw the stick figure using the new renderer."""
        if not self.rig:
            return

        # Calculate base scale from zoom
        base_scale = self.zoom * 0.5

        # Apply style-specific scale multipliers for default sizes
        style = self.rig.visual_style
        if style.name == "SHADOW_RED":
            # Shadow Red Fighter: 84.8% larger than base (chunky boss proportions)
            # Massive, imposing presence - fills viewport
            # Big-headed toy aesthetic emphasized
            style_multiplier = 1.848
        elif style.name == "NEON_CYAN":
            # Neon Cyan Fighter: 10% smaller than base (sleek hero proportions)
            # Compact, nimble technical fighter
            # Creates strong size contrast with Shadow (2× ratio)
            style_multiplier = 0.9
        else:
            # Classic uses standard size
            style_multiplier = 1.0

        # Apply combined scale
        self.renderer.scale = base_scale * style_multiplier
        self.renderer.update_measurements()

        # Center position (already translated by paintEvent)
        cx = 0
        cy = 0

        # Draw based on style
        if style.name == "NEON_CYAN":
            self.renderer.render_neon_cyan(painter, cx, cy)
        elif style.name == "SHADOW_RED":
            self.renderer.render_shadow_red(painter, cx, cy)
        else:  # CLASSIC_CAPSULE
            self.renderer.render_classic_capsule(painter, cx, cy)


    def draw_info(self, painter):
        """Draw viewport information."""
        painter.setPen(QPen(QColor(150, 150, 160), 1))
        painter.setFont(QFont("Segoe UI", 9))

        info = f"Zoom: {int(self.zoom * 100)}% | Rotation: ({int(self.rotation_x)}°, {int(self.rotation_y)}°)"
        painter.drawText(50, 20, info)

    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.position().toPoint()

            # Check for bone selection
            # TODO: Implement ray casting for bone selection

        elif event.button() == Qt.MouseButton.RightButton:
            # Context menu or reset view
            self.reset_view()

    def mouseMoveEvent(self, event):
        """Handle mouse move."""
        if self.last_mouse_pos and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.position().toPoint() - self.last_mouse_pos

            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # Pan
                self.pan_x += delta.x()
                self.pan_y += delta.y()
            else:
                # Rotate
                self.rotation_y += delta.x() * 0.5
                self.rotation_x += delta.y() * 0.5
                self.rotation_x = max(-90, min(90, self.rotation_x))

            self.last_mouse_pos = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self.last_mouse_pos = None

    def wheelEvent(self, event):
        """Handle mouse wheel for zoom."""
        delta = event.angleDelta().y() / 120
        self.zoom = max(0.3, min(3.0, self.zoom + delta * 0.1))
        self.update()

    def reset_view(self):
        """Reset viewport to default view."""
        self.rotation_x = 0
        self.rotation_y = 0
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.update()