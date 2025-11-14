"""
Professional Stick Figure Maker with Clean 2D Rendering
Matches reference images exactly - no weird 3D pipes!
"""

import sys
import json
import math
import os
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QSlider, QLabel, QComboBox, QSpinBox, QColorDialog,
    QListWidget, QSplitter, QFrame, QGridLayout, QCheckBox,
    QTabWidget, QLineEdit, QMessageBox, QFileDialog,
    QScrollArea, QButtonGroup, QRadioButton, QListWidgetItem,
    QApplication, QInputDialog
)
from PySide6.QtCore import (
    Qt, Signal, QTimer, QSize, QPropertyAnimation,
    QEasingCurve, QRect, QPointF, Property, QRectF
)
from PySide6.QtGui import (
    QColor, QPainter, QBrush, QPen, QFont, QLinearGradient,
    QRadialGradient, QPainterPath, QPixmap, QImage, QTransform
)
import numpy as np
from rig import StickRig, VisualStyle, Bone


class StyleThumbnail(QWidget):
    """Compact style selector thumbnail."""
    clicked = Signal(str)

    def __init__(self, name: str, style: VisualStyle, parent=None):
        super().__init__(parent)
        self.name = name
        self.style = style
        self.selected = False
        self.hover = False
        self.setFixedSize(70, 80)  # Much smaller!
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, event):
        self.hover = True
        self.update()

    def leaveEvent(self, event):
        self.hover = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.name)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        if self.selected:
            painter.fillRect(self.rect(), QColor(60, 100, 140))
        elif self.hover:
            painter.fillRect(self.rect(), QColor(50, 50, 60))
        else:
            painter.fillRect(self.rect(), QColor(40, 40, 45))

        # Draw mini stick figure
        painter.save()
        painter.translate(35, 35)
        painter.scale(0.6, 0.6)

        if self.style == VisualStyle.NEON_CYAN:
            # Cyan glowing joints
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 255, 255, 60))
            for x, y in [(0, -10), (-8, 3), (8, 3), (-5, 15), (5, 15)]:
                painter.drawEllipse(QPointF(x, y), 4, 4)

            # Black lines
            painter.setPen(QPen(QColor(20, 20, 20), 2))
            painter.drawLine(0, -10, 0, 5)
            painter.drawLine(0, -2, -8, 3)
            painter.drawLine(0, -2, 8, 3)
            painter.drawLine(0, 5, -5, 15)
            painter.drawLine(0, 5, 5, 15)

            # Head with cyan eyes
            painter.setBrush(QColor(20, 20, 20))
            painter.drawEllipse(QPointF(0, -10), 6, 6)
            painter.setPen(QPen(QColor(0, 255, 255), 1))
            painter.drawLine(-3, -10, -1, -10)
            painter.drawLine(1, -10, 3, -10)

        elif self.style == VisualStyle.SHADOW_RED:
            # Dark figure
            painter.setPen(QPen(QColor(30, 10, 10), 2))
            painter.drawLine(0, -10, 0, 5)
            painter.drawLine(0, -2, -8, 3)
            painter.drawLine(0, -2, 8, 3)
            painter.drawLine(0, 5, -5, 15)
            painter.drawLine(0, 5, 5, 15)

            # Head with red eyes
            painter.setBrush(QColor(30, 10, 10))
            painter.drawEllipse(QPointF(0, -10), 6, 6)
            painter.setBrush(QColor(255, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(-2, -10), 1, 1)
            painter.drawEllipse(QPointF(2, -10), 1, 1)

        else:  # Classic
            painter.setPen(QPen(QColor(30, 30, 30), 2.5, Qt.PenStyle.SolidLine,
                              Qt.PenCapStyle.RoundCap))
            painter.drawLine(0, -10, 0, 5)
            painter.drawLine(0, -2, -8, 3)
            painter.drawLine(0, -2, 8, 3)
            painter.drawLine(0, 5, -5, 15)
            painter.drawLine(0, 5, 5, 15)

            # Head with googly eyes
            painter.setBrush(QColor(30, 30, 30))
            painter.setPen(QPen(QColor(30, 30, 30)))
            painter.drawEllipse(QPointF(0, -10), 6, 6)
            painter.setBrush(Qt.GlobalColor.white)
            painter.drawEllipse(QPointF(-2, -10), 2, 2)
            painter.drawEllipse(QPointF(2, -10), 2, 2)
            painter.setBrush(Qt.GlobalColor.black)
            painter.drawEllipse(QPointF(-2, -10), 1, 1)
            painter.drawEllipse(QPointF(2, -10), 1, 1)

        painter.restore()

        # Label
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont("Segoe UI", 7))
        painter.drawText(self.rect().adjusted(0, 60, 0, 0),
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                        self.name)


class StickFigure2DViewport(QWidget):
    """Clean 2D viewport that actually looks like the reference images."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rig = StickRig()
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_pos = None
        self.grid_enabled = True
        self.setMinimumSize(600, 600)
        self.setStyleSheet("""
            QWidget {
                background: #2a2a30;
                border: 2px solid #404048;
                border-radius: 4px;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor(42, 42, 48))

        # Draw grid
        if self.grid_enabled:
            painter.setPen(QPen(QColor(55, 55, 60), 1, Qt.PenStyle.DotLine))
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

        # Draw stick figure
        painter.save()
        painter.translate(self.width() / 2 + self.pan_x, self.height() / 2 + self.pan_y)
        painter.scale(self.zoom * 3, self.zoom * 3)  # Make it bigger

        self.draw_stick_figure(painter)

        painter.restore()

        # Draw viewport info
        painter.setPen(QPen(QColor(150, 150, 160), 1))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(10, 20, f"Zoom: {int(self.zoom * 100)}%")

    def draw_stick_figure(self, painter):
        """Draw the stick figure matching the reference images."""
        style = self.rig.visual_style

        # Get joint positions from rig
        transforms = self.rig.get_joint_transform("pelvis")

        # Define connection pairs for drawing
        connections = [
            ("pelvis", "spine_lower"),
            ("spine_lower", "spine_upper"),
            ("spine_upper", "neck"),
            ("neck", "head"),
            ("spine_upper", "upper_arm_L"),
            ("upper_arm_L", "lower_arm_L"),
            ("lower_arm_L", "hand_L"),
            ("spine_upper", "upper_arm_R"),
            ("upper_arm_R", "lower_arm_R"),
            ("lower_arm_R", "hand_R"),
            ("pelvis", "thigh_L"),
            ("thigh_L", "shin_L"),
            ("shin_L", "foot_L"),
            ("pelvis", "thigh_R"),
            ("thigh_R", "shin_R"),
            ("shin_R", "foot_R")
        ]

        # Draw based on style
        if style == VisualStyle.NEON_CYAN:
            # Draw glow at joints first
            painter.setPen(Qt.PenStyle.NoPen)
            for bone_name, transform in transforms.items():
                if bone_name in ["pelvis", "spine_upper", "upper_arm_L", "upper_arm_R",
                                "lower_arm_L", "lower_arm_R", "thigh_L", "thigh_R",
                                "shin_L", "shin_R"]:
                    end = transform['end']
                    # Outer glow
                    gradient = QRadialGradient(end[0], -end[1], 8)
                    gradient.setColorAt(0, QColor(0, 255, 255, 80))
                    gradient.setColorAt(1, QColor(0, 255, 255, 0))
                    painter.setBrush(QBrush(gradient))
                    painter.drawEllipse(QPointF(end[0], -end[1]), 8, 8)

                    # Inner bright spot
                    painter.setBrush(QColor(0, 255, 255, 200))
                    painter.drawEllipse(QPointF(end[0], -end[1]), 2, 2)

            # Draw limbs
            painter.setPen(QPen(QColor(10, 10, 15), 3, Qt.PenStyle.SolidLine,
                              Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)

        elif style == VisualStyle.SHADOW_RED:
            # Dark style with subtle joints
            painter.setPen(QPen(QColor(20, 5, 5), 3, Qt.PenStyle.SolidLine,
                              Qt.PenCapStyle.RoundCap))

            # Small dark joints
            painter.setBrush(QColor(40, 10, 10))
            for bone_name, transform in transforms.items():
                if bone_name in ["pelvis", "spine_upper", "upper_arm_L", "upper_arm_R",
                                "lower_arm_L", "lower_arm_R", "thigh_L", "thigh_R"]:
                    end = transform['end']
                    painter.drawEllipse(QPointF(end[0], -end[1]), 3, 3)

            painter.setBrush(Qt.BrushStyle.NoBrush)

        else:  # Classic
            # Simple black lines
            painter.setPen(QPen(QColor(30, 30, 30), 4, Qt.PenStyle.SolidLine,
                              Qt.PenCapStyle.RoundCap))

        # Draw connections
        for start_bone, end_bone in connections:
            if start_bone in transforms and end_bone in transforms:
                start_pos = transforms[start_bone]['end']
                end_pos = transforms[end_bone]['end']
                painter.drawLine(QPointF(start_pos[0], -start_pos[1]),
                               QPointF(end_pos[0], -end_pos[1]))

        # Draw head
        if "head" in transforms:
            head_pos = transforms["head"]['end']
            head_size = 8

            if style == VisualStyle.NEON_CYAN:
                # Black head with cyan eyes
                painter.setBrush(QColor(10, 10, 15))
                painter.setPen(QPen(QColor(10, 10, 15), 2))
                painter.drawEllipse(QPointF(head_pos[0], -head_pos[1]), head_size, head_size)

                # Cyan slit eyes
                painter.setPen(QPen(QColor(0, 255, 255), 2))
                painter.drawLine(head_pos[0] - 4, -head_pos[1], head_pos[0] - 1, -head_pos[1])
                painter.drawLine(head_pos[0] + 1, -head_pos[1], head_pos[0] + 4, -head_pos[1])

            elif style == VisualStyle.SHADOW_RED:
                # Dark head with red eyes
                painter.setBrush(QColor(20, 5, 5))
                painter.setPen(QPen(QColor(20, 5, 5), 2))
                painter.drawEllipse(QPointF(head_pos[0], -head_pos[1]), head_size, head_size)

                # Red glowing eyes
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(255, 0, 0))
                painter.drawEllipse(QPointF(head_pos[0] - 3, -head_pos[1]), 2, 2)
                painter.drawEllipse(QPointF(head_pos[0] + 3, -head_pos[1]), 2, 2)

            else:  # Classic
                # Black head
                painter.setBrush(QColor(30, 30, 30))
                painter.setPen(QPen(QColor(30, 30, 30), 2))
                painter.drawEllipse(QPointF(head_pos[0], -head_pos[1]), head_size, head_size)

                # Googly eyes
                painter.setBrush(Qt.GlobalColor.white)
                painter.setPen(QPen(Qt.GlobalColor.black, 1))
                painter.drawEllipse(QPointF(head_pos[0] - 3, -head_pos[1]), 3, 3)
                painter.drawEllipse(QPointF(head_pos[0] + 3, -head_pos[1]), 3, 3)

                painter.setBrush(Qt.GlobalColor.black)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(head_pos[0] - 3, -head_pos[1] + 0.5), 1.5, 1.5)
                painter.drawEllipse(QPointF(head_pos[0] + 3, -head_pos[1] + 0.5), 1.5, 1.5)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.position().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            # Reset view
            self.zoom = 1.0
            self.pan_x = 0
            self.pan_y = 0
            self.update()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos:
            delta = event.position().toPoint() - self.last_mouse_pos
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self.last_mouse_pos = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        self.last_mouse_pos = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.zoom = max(0.3, min(3.0, self.zoom + delta * 0.1))
        self.update()


class StickFigureMaker(QWidget):
    """Redesigned stick figure maker with proper UI."""
    figure_created = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rig = StickRig()
        self.preset_library = []
        self.load_presets()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI with better layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Top toolbar with style selection
        toolbar = QWidget()
        toolbar.setMaximumHeight(100)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)

        # Visual Style section
        style_group = QGroupBox("Visual Style")
        style_group.setMaximumHeight(100)
        style_layout = QHBoxLayout()
        style_layout.setSpacing(5)

        self.style_thumbnails = []
        styles = [
            ("Neon", VisualStyle.NEON_CYAN),
            ("Shadow", VisualStyle.SHADOW_RED),
            ("Classic", VisualStyle.CLASSIC_CAPSULE)
        ]

        for name, style in styles:
            thumb = StyleThumbnail(name, style)
            thumb.clicked.connect(self.on_style_selected)
            style_layout.addWidget(thumb)
            self.style_thumbnails.append(thumb)

        self.style_thumbnails[0].selected = True

        style_layout.addStretch()
        style_group.setLayout(style_layout)
        toolbar_layout.addWidget(style_group)

        toolbar_layout.addStretch()

        # Quick actions
        actions_layout = QVBoxLayout()
        self.create_btn = QPushButton("Create Figure")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background: #4a9eff;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background: #5aaeef; }
            QPushButton:pressed { background: #3a7ec8; }
        """)
        self.create_btn.clicked.connect(self.create_figure)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_to_default)

        actions_layout.addWidget(self.create_btn)
        actions_layout.addWidget(self.reset_btn)
        toolbar_layout.addLayout(actions_layout)

        main_layout.addWidget(toolbar)

        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # LEFT: Controls
        controls_widget = QWidget()
        controls_widget.setMaximumWidth(350)
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        self.control_tabs = QTabWidget()
        self.control_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #404040;
                background: #2a2a2a;
            }
            QTabBar::tab {
                background: #353535;
                color: #b0b0b0;
                padding: 6px 12px;
            }
            QTabBar::tab:selected {
                background: #404050;
                color: white;
            }
        """)

        # Proportions tab
        prop_widget = QWidget()
        prop_layout = QVBoxLayout(prop_widget)

        # Compact slider groups
        for group_name, sliders in [
            ("Overall", [
                ("Height", "height", 50, 150, 100),
                ("Bulk", "bulk", 50, 150, 100)
            ]),
            ("Upper Body", [
                ("Head", "head_size", 70, 130, 100),
                ("Torso", "torso", 80, 120, 100),
                ("Shoulders", "shoulders", 80, 120, 100)
            ]),
            ("Arms", [
                ("Length", "arm_length", 70, 130, 100),
                ("Thickness", "arm_thick", 70, 130, 100)
            ]),
            ("Legs", [
                ("Length", "leg_length", 70, 130, 100),
                ("Thickness", "leg_thick", 70, 130, 100)
            ])
        ]:
            group = QGroupBox(group_name)
            group_layout = QVBoxLayout()

            for label, key, min_val, max_val, default in sliders:
                row = QHBoxLayout()
                lbl = QLabel(label)
                lbl.setMinimumWidth(60)
                row.addWidget(lbl)

                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setRange(min_val, max_val)
                slider.setValue(default)
                slider.valueChanged.connect(lambda v, k=key: self.on_slider_changed(k, v))
                row.addWidget(slider)

                val_lbl = QLabel(f"{default}%")
                val_lbl.setMinimumWidth(35)
                val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
                slider.valueChanged.connect(lambda v, l=val_lbl: l.setText(f"{v}%"))
                row.addWidget(val_lbl)

                group_layout.addLayout(row)

            group.setLayout(group_layout)
            prop_layout.addWidget(group)

        prop_layout.addStretch()
        scroll = QScrollArea()
        scroll.setWidget(prop_widget)
        scroll.setWidgetResizable(True)
        self.control_tabs.addTab(scroll, "Proportions")

        # Effects tab
        effects_widget = QWidget()
        effects_layout = QVBoxLayout(effects_widget)

        self.glow_check = QCheckBox("Enable Glow Effects")
        self.glow_check.setChecked(True)
        effects_layout.addWidget(self.glow_check)

        effects_layout.addStretch()
        self.control_tabs.addTab(effects_widget, "Effects")

        # Library tab
        library_widget = QWidget()
        library_layout = QVBoxLayout(library_widget)

        self.preset_list = QListWidget()
        library_layout.addWidget(QLabel("Saved Presets:"))
        library_layout.addWidget(self.preset_list)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        load_btn = QPushButton("Load")
        delete_btn = QPushButton("Delete")

        save_btn.clicked.connect(self.save_preset)
        load_btn.clicked.connect(self.load_preset)
        delete_btn.clicked.connect(self.delete_preset)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(delete_btn)
        library_layout.addLayout(btn_layout)

        self.control_tabs.addTab(library_widget, "Library")

        controls_layout.addWidget(self.control_tabs)

        # RIGHT: Viewport
        viewport_container = QWidget()
        viewport_layout = QVBoxLayout(viewport_container)
        viewport_layout.setContentsMargins(0, 0, 0, 0)

        # Viewport controls bar
        controls_bar = QWidget()
        controls_bar.setMaximumHeight(35)
        controls_bar.setStyleSheet("background: #353538; padding: 5px;")
        controls_bar_layout = QHBoxLayout(controls_bar)

        controls_bar_layout.addWidget(QLabel("View:"))
        view_combo = QComboBox()
        view_combo.addItems(["Front", "Side", "3/4 View"])
        controls_bar_layout.addWidget(view_combo)

        controls_bar_layout.addStretch()

        grid_check = QCheckBox("Grid")
        grid_check.setChecked(True)
        controls_bar_layout.addWidget(grid_check)

        info_label = QLabel("Left-drag: Pan | Wheel: Zoom | Right-click: Reset")
        info_label.setStyleSheet("color: #888; font-size: 10px;")
        controls_bar_layout.addWidget(info_label)

        viewport_layout.addWidget(controls_bar)

        # The actual viewport
        self.viewport = StickFigure2DViewport()
        self.viewport.rig = self.rig
        grid_check.toggled.connect(lambda checked: setattr(self.viewport, 'grid_enabled', checked) or self.viewport.update())

        viewport_layout.addWidget(self.viewport)

        # Add to splitter
        content_splitter.addWidget(controls_widget)
        content_splitter.addWidget(viewport_container)
        content_splitter.setStretchFactor(0, 0)
        content_splitter.setStretchFactor(1, 1)

        main_layout.addWidget(content_splitter)

        # Apply overall dark theme
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #e0e0e0; }
            QGroupBox {
                border: 1px solid #404040;
                border-radius: 3px;
                margin-top: 8px;
                padding-top: 8px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #404040;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 12px;
                background: #808090;
                border-radius: 6px;
                margin: -4px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #9090a0;
            }
            QPushButton {
                background: #404048;
                border: 1px solid #505058;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background: #505058;
            }
            QListWidget {
                background: #2a2a2a;
                border: 1px solid #404040;
            }
            QCheckBox { spacing: 5px; }
            QCheckBox::indicator { width: 15px; height: 15px; }
        """)

    def on_style_selected(self, style_name: str):
        """Handle style selection."""
        for thumb in self.style_thumbnails:
            thumb.selected = thumb.name == style_name
            thumb.update()

        style_map = {
            "Neon": VisualStyle.NEON_CYAN,
            "Shadow": VisualStyle.SHADOW_RED,
            "Classic": VisualStyle.CLASSIC_CAPSULE
        }

        if style_name in style_map:
            self.rig.apply_visual_style(style_map[style_name])
            self.viewport.update()

    def on_slider_changed(self, key: str, value: int):
        """Handle slider changes."""
        multiplier = value / 100.0

        if key == "height":
            self.rig.overall_scale = multiplier
        elif key == "bulk":
            for bone in self.rig.bones.values():
                bone.thickness = bone.thickness * multiplier

        self.viewport.update()

    def reset_to_default(self):
        """Reset to default T-pose."""
        self.rig = StickRig()
        self.viewport.rig = self.rig
        self.viewport.update()

    def save_preset(self):
        """Save current preset."""
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name:
            preset = {
                'name': name,
                'rig_data': self.rig.to_json(),
                'timestamp': datetime.now().isoformat()
            }
            self.preset_library.append(preset)
            self.preset_list.addItem(name)
            self.save_presets_to_file()

    def load_preset(self):
        """Load selected preset."""
        current = self.preset_list.currentItem()
        if current:
            name = current.text()
            for preset in self.preset_library:
                if preset['name'] == name:
                    self.rig.from_json(preset['rig_data'])
                    self.viewport.update()
                    break

    def delete_preset(self):
        """Delete selected preset."""
        current = self.preset_list.currentRow()
        if current >= 0:
            self.preset_list.takeItem(current)
            del self.preset_library[current]
            self.save_presets_to_file()

    def save_presets_to_file(self):
        """Save presets to file."""
        Path("assets/characters").mkdir(parents=True, exist_ok=True)
        with open("assets/characters/presets.json", "w") as f:
            json.dump(self.preset_library, f, indent=2)

    def load_presets(self):
        """Load presets from file."""
        preset_file = Path("assets/characters/presets.json")
        if preset_file.exists():
            with open(preset_file, "r") as f:
                self.preset_library = json.load(f)
                for preset in self.preset_library:
                    self.preset_list.addItem(preset['name'])

    def create_figure(self):
        """Create the figure."""
        figure_data = {
            'rig': self.rig.to_json(),
            'name': f"Figure_{datetime.now().strftime('%H%M%S')}",
            'style': self.rig.visual_style.value
        }
        self.figure_created.emit(figure_data)
        QMessageBox.information(self, "Success", "Figure created!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StickFigureMaker()
    window.resize(1200, 700)
    window.show()
    sys.exit(app.exec())