"""
Weapon Creator Tab UI
Tab 1 of the main application - weapon design with flame effects.

Features:
- Weapon template selection (Sword, Katana, Mace, Maul, Crossbow)
- Live weapon preview with rendering
- Flame effect parameter sliders (14 adjustable parameters)
- Flame preset buttons (5 preset styles)
- PNG import for custom weapons
- Save/Export weapon to library
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QSlider, QComboBox, QSpinBox, QDoubleSpinBox,
    QFileDialog, QScrollArea, QFrame, QGridLayout, QSplitter,
    QColorDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor

from canvas import RenderCanvas
from effects.flame_effect import FlameEffect, FlamePreset, FlameParameters
from weapons.sword import ShortSword
from weapons.katana import Katana
from weapons.mace import Mace
from weapons.maul import Maul
from weapons.crossbow import Crossbow


class WeaponCreatorTab(QWidget):
    """
    Weapon Creator tab interface.
    Allows users to select weapon templates, customize them, and apply flame effects.
    """

    # Signals
    weapon_created = Signal(object)  # Emitted when weapon is finalized
    weapon_modified = Signal()       # Emitted when weapon parameters change

    def __init__(self, parent=None):
        super().__init__(parent)

        # Current state
        self.current_weapon = None
        self.current_flame_effect = None
        self.current_weapon_type = "sword"
        self.flame_enabled = False  # Flames OFF by default

        # UI components (will be populated)
        self.preview_canvas = None
        self.flame_sliders = {}
        self.weapon_buttons = {}

        # Build the UI
        self._build_ui()

        # Initialize with default weapon
        self._select_weapon("sword")

        print("✓ Weapon Creator Tab initialized")

    # ========================================================================
    # UI CONSTRUCTION
    # ========================================================================

    def _build_ui(self):
        """Build the complete weapon creator UI."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Left side: Preview canvas (60% width)
        preview_group = self._create_preview_section()
        main_layout.addWidget(preview_group, 6)

        # Right side: Controls (40% width)
        controls_scroll = self._create_controls_section()
        main_layout.addWidget(controls_scroll, 4)

    def _create_preview_section(self):
        """Create the weapon preview canvas section."""
        group = QGroupBox("Weapon Preview")
        layout = QVBoxLayout(group)

        # Preview canvas (OpenGL)
        self.preview_canvas = RenderCanvas()
        self.preview_canvas.setMinimumSize(400, 400)
        layout.addWidget(self.preview_canvas)

        # Preview controls
        controls_layout = QHBoxLayout()

        reset_camera_btn = QPushButton("Reset Camera")
        reset_camera_btn.clicked.connect(self.preview_canvas.reset_camera)
        controls_layout.addWidget(reset_camera_btn)

        rotate_left_btn = QPushButton("↶ Rotate Left")
        rotate_left_btn.clicked.connect(lambda: self._rotate_weapon(-15))
        controls_layout.addWidget(rotate_left_btn)

        rotate_right_btn = QPushButton("↷ Rotate Right")
        rotate_right_btn.clicked.connect(lambda: self._rotate_weapon(15))
        controls_layout.addWidget(rotate_right_btn)

        layout.addLayout(controls_layout)

        # Rotation mode and flame toggle
        rotation_mode_layout = QHBoxLayout()

        self.rotation_mode_toggle = QPushButton("2D Spin: OFF")
        self.rotation_mode_toggle.setCheckable(True)
        self.rotation_mode_toggle.setChecked(False)
        self.rotation_mode_toggle.clicked.connect(self._toggle_rotation_mode)
        self.rotation_mode_toggle.setToolTip("Toggle between 3D rotation and 2D spin (Z-axis only)")
        self.rotation_mode_toggle.setMinimumHeight(30)
        rotation_mode_layout.addWidget(self.rotation_mode_toggle)

        # Flame effects toggle button
        self.flame_toggle = QPushButton("🔥 Flames: OFF")
        self.flame_toggle.setCheckable(True)
        self.flame_toggle.setChecked(False)
        self.flame_toggle.clicked.connect(self._toggle_flames)
        self.flame_toggle.setToolTip("Toggle flame effects on/off")
        self.flame_toggle.setMinimumHeight(30)
        rotation_mode_layout.addWidget(self.flame_toggle)

        layout.addLayout(rotation_mode_layout)

        # Weapon info label
        self.weapon_info_label = QLabel("No weapon selected")
        self.weapon_info_label.setStyleSheet("font-weight: bold; color: #2a82da;")
        layout.addWidget(self.weapon_info_label)

        return group

    def _create_controls_section(self):
        """Create the controls panel (scrollable)."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        controls_widget = QWidget()
        layout = QVBoxLayout(controls_widget)
        layout.setSpacing(15)

        # Section 1: Weapon Template Selection
        layout.addWidget(self._create_weapon_selection_group())

        # Section 2: Flame Effect Presets
        layout.addWidget(self._create_flame_presets_group())

        # Section 3: Flame Parameters
        layout.addWidget(self._create_flame_parameters_group())

        # Section 4: Weapon Actions
        layout.addWidget(self._create_actions_group())

        # Add stretch at bottom
        layout.addStretch()

        scroll.setWidget(controls_widget)
        return scroll

    # ========================================================================
    # WEAPON SELECTION GROUP
    # ========================================================================

    def _create_weapon_selection_group(self):
        """Create weapon template selection buttons."""
        group = QGroupBox("Weapon Templates")
        layout = QGridLayout(group)

        # Weapon templates (name, class, description)
        weapons = [
            ("sword", ShortSword, "Short Sword\nMedieval blade"),
            ("katana", Katana, "Katana\nJapanese curved sword"),
            ("mace", Mace, "Mace\nSpiked crushing weapon"),
            ("maul", Maul, "War Maul\nTwo-handed hammer"),
            ("crossbow", Crossbow, "Crossbow\nRanged weapon"),
        ]

        row, col = 0, 0
        for weapon_type, weapon_class, description in weapons:
            btn = QPushButton(description)
            btn.setMinimumHeight(60)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, wt=weapon_type: self._select_weapon(wt))

            self.weapon_buttons[weapon_type] = btn
            layout.addWidget(btn, row, col)

            col += 1
            if col > 1:  # 2 columns
                col = 0
                row += 1

        # Import PNG button
        import_btn = QPushButton("📁 Import PNG")
        import_btn.setMinimumHeight(60)
        import_btn.clicked.connect(self._import_png_weapon)
        layout.addWidget(import_btn, row, col)

        return group

    # ========================================================================
    # FLAME PRESETS GROUP
    # ========================================================================

    def _create_flame_presets_group(self):
        """Create flame effect preset buttons."""
        group = QGroupBox("Flame Presets")
        layout = QGridLayout(group)

        presets = [
            (FlamePreset.REALISTIC_FIRE, "🔥 Realistic Fire", "Classic orange/yellow flames"),
            (FlamePreset.MAGIC_FIRE, "✨ Magic Fire", "Purple/cyan mystical flames"),
            (FlamePreset.PLASMA, "⚡ Plasma", "Pink/blue energy flames"),
            (FlamePreset.ENERGY, "💠 Energy", "Cyan/white power flames"),
            (FlamePreset.COLD_FIRE, "❄️ Cold Fire", "Blue ice flames"),
        ]

        row = 0
        for preset, label, tooltip in presets:
            btn = QPushButton(label)
            btn.setToolTip(tooltip)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, p=preset: self._apply_flame_preset(p))
            layout.addWidget(btn, row, 0, 1, 2)
            row += 1

        return group

    # ========================================================================
    # FLAME PARAMETERS GROUP
    # ========================================================================

    def _create_flame_parameters_group(self):
        """Create sliders for all flame parameters."""
        group = QGroupBox("Flame Parameters")
        layout = QVBoxLayout(group)

        # Parameter definitions (name, min, max, default, step)
        params = [
            ("Intensity", 0.0, 2.0, 1.0, 0.1),
            ("Speed", 0.1, 5.0, 1.0, 0.1),
            ("Turbulence", 0.0, 2.0, 1.0, 0.1),
            ("Flicker", 0.0, 1.0, 0.3, 0.05),
            ("Height", 0.1, 3.0, 1.0, 0.1),
            ("Width", 0.1, 2.0, 0.5, 0.1),
            ("Opacity", 0.0, 1.0, 0.85, 0.05),
        ]

        for param_name, min_val, max_val, default, step in params:
            param_layout = QHBoxLayout()

            label = QLabel(f"{param_name}:")
            label.setMinimumWidth(100)
            param_layout.addWidget(label)

            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(int(min_val / step))
            slider.setMaximum(int(max_val / step))
            slider.setValue(int(default / step))
            slider.valueChanged.connect(
                lambda val, name=param_name.lower(), s=step: self._on_flame_param_changed(name, val * s)
            )
            param_layout.addWidget(slider, stretch=3)

            value_label = QLabel(f"{default:.2f}")
            value_label.setMinimumWidth(50)
            slider.valueChanged.connect(
                lambda val, lbl=value_label, s=step: lbl.setText(f"{val * s:.2f}")
            )
            param_layout.addWidget(value_label)

            self.flame_sliders[param_name.lower()] = (slider, value_label)
            layout.addLayout(param_layout)

        # Color pickers
        layout.addWidget(QLabel("Flame Colors:"))

        color_layout = QHBoxLayout()

        bottom_color_btn = QPushButton("Bottom Color")
        bottom_color_btn.clicked.connect(lambda: self._pick_flame_color("bottom"))
        color_layout.addWidget(bottom_color_btn)

        top_color_btn = QPushButton("Top Color")
        top_color_btn.clicked.connect(lambda: self._pick_flame_color("top"))
        color_layout.addWidget(top_color_btn)

        layout.addLayout(color_layout)

        return group

    # ========================================================================
    # ACTIONS GROUP
    # ========================================================================

    def _create_actions_group(self):
        """Create save/export action buttons."""
        group = QGroupBox("Actions")
        layout = QVBoxLayout(group)

        save_btn = QPushButton("💾 Save Weapon to Library")
        save_btn.setMinimumHeight(50)
        save_btn.clicked.connect(self._save_weapon)
        layout.addWidget(save_btn)

        export_btn = QPushButton("📤 Export Weapon (JSON)")
        export_btn.setMinimumHeight(50)
        export_btn.clicked.connect(self._export_weapon)
        layout.addWidget(export_btn)

        clear_btn = QPushButton("🗑️ Clear & Start Over")
        clear_btn.setMinimumHeight(50)
        clear_btn.clicked.connect(self._clear_weapon)
        layout.addWidget(clear_btn)

        return group

    # ========================================================================
    # WEAPON SELECTION HANDLERS
    # ========================================================================

    @Slot(str)
    def _select_weapon(self, weapon_type: str):
        """Select and load a weapon template."""
        print(f"Loading weapon template: {weapon_type}")

        # Uncheck all buttons
        for btn in self.weapon_buttons.values():
            btn.setChecked(False)

        # Check selected button
        if weapon_type in self.weapon_buttons:
            self.weapon_buttons[weapon_type].setChecked(True)

        # Create weapon instance
        if weapon_type == "sword":
            self.current_weapon = ShortSword()
        elif weapon_type == "katana":
            self.current_weapon = Katana()
        elif weapon_type == "mace":
            self.current_weapon = Mace()
        elif weapon_type == "maul":
            self.current_weapon = Maul()
        elif weapon_type == "crossbow":
            self.current_weapon = Crossbow()
        else:
            print(f"Unknown weapon type: {weapon_type}")
            return

        self.current_weapon_type = weapon_type

        # Reset transforms to default centered state
        self.current_weapon.set_position(0.0, -3.8, 0.0)  # Center entire weapon in viewport (2 boxes lower)
        self.current_weapon.set_rotation(0.0, 0.0, 0.0)  # No rotation
        self.current_weapon.set_scale(4.5)  # Large scale for clear weapon preview

        # Create flame effect if it doesn't exist (but keep it disabled by default)
        if self.current_flame_effect is None:
            self.current_flame_effect = FlameEffect()

        # Reset flame toggle to OFF when loading new weapon
        self.flame_enabled = False
        self.flame_toggle.setChecked(False)
        self.flame_toggle.setText("🔥 Flames: OFF")

        # Update info label
        self.weapon_info_label.setText(
            f"{self.current_weapon.name}\n"
            f"Type: {self.current_weapon.weapon_type}\n"
            f"{self.current_weapon.description}"
        )

        # Update preview (will be implemented when canvas integration is done)
        self._update_preview()

        print(f"✓ Loaded {self.current_weapon.name}")

    # ========================================================================
    # FLAME EFFECT HANDLERS
    # ========================================================================

    @Slot(object)
    def _apply_flame_preset(self, preset: FlamePreset):
        """Apply a flame effect preset and auto-enable flames to show result."""
        if self.current_flame_effect is None:
            self.current_flame_effect = FlameEffect()

        self.current_flame_effect.apply_preset(preset)

        # Update sliders to match preset values
        self._update_sliders_from_flame()

        # Auto-enable flames when user clicks a preset (better UX - immediate visual feedback)
        if not self.flame_enabled:
            self.flame_enabled = True
            self.flame_toggle.setChecked(True)
            self.flame_toggle.setText("🔥 Flames: ON")

        self._update_preview()

        print(f"✓ Applied flame preset: {preset.value}")

    @Slot(str, float)
    def _on_flame_param_changed(self, param_name: str, value: float):
        """Handle flame parameter slider changes."""
        if self.current_flame_effect is None:
            return

        # Map parameter name to flame effect property
        param_map = {
            "intensity": "intensity",
            "speed": "speed",
            "turbulence": "turbulence",
            "flicker": "flicker_intensity",
            "height": "height",
            "width": "width",
            "opacity": "opacity",
        }

        if param_name in param_map:
            attr_name = param_map[param_name]
            setattr(self.current_flame_effect.parameters, attr_name, value)

            # Regenerate flame geometry if size changed
            if param_name in ["height", "width"]:
                self.current_flame_effect.cleanup()
                self.current_flame_effect.vao = None  # Force geometry rebuild

            self._update_preview()
            self.weapon_modified.emit()

    def _update_sliders_from_flame(self):
        """Update slider values to match current flame parameters."""
        if self.current_flame_effect is None:
            return

        params = self.current_flame_effect.parameters

        slider_map = {
            "intensity": (params.intensity, 0.1),
            "speed": (params.speed, 0.1),
            "turbulence": (params.turbulence, 0.1),
            "flicker": (params.flicker_intensity, 0.05),
            "height": (params.height, 0.1),
            "width": (params.width, 0.1),
            "opacity": (params.opacity, 0.05),
        }

        for name, (value, step) in slider_map.items():
            if name in self.flame_sliders:
                slider, label = self.flame_sliders[name]
                slider.setValue(int(value / step))
                label.setText(f"{value:.2f}")

    @Slot(str)
    def _pick_flame_color(self, position: str):
        """Open color picker for flame color."""
        if self.current_flame_effect is None:
            return

        params = self.current_flame_effect.parameters

        # Get initial color
        if position == "bottom":
            initial = QColor.fromRgbF(*params.color_bottom[:3])
        else:
            initial = QColor.fromRgbF(*params.color_top[:3])

        # Open color picker
        color = QColorDialog.getColor(initial, self, f"Pick {position.title()} Flame Color")

        if color.isValid():
            r, g, b = color.redF(), color.greenF(), color.blueF()

            if position == "bottom":
                params.color_bottom = (r, g, b, 1.0)
            else:
                params.color_top = (r, g, b, 0.8)

            self._update_preview()
            self.weapon_modified.emit()

    # ========================================================================
    # WEAPON MANIPULATION
    # ========================================================================

    @Slot(float)
    def _rotate_weapon(self, angle: float):
        """Rotate the current weapon."""
        if self.current_weapon is None:
            return

        self.current_weapon.rotate(0, 0, angle)
        self._update_preview()

    @Slot(bool)
    def _toggle_rotation_mode(self, checked: bool):
        """Toggle between 3D rotation and 2D spin mode."""
        if checked:
            # Enable 2D spin mode
            self.preview_canvas.set_weapon_rotation_mode("2D")
            self.rotation_mode_toggle.setText("2D Spin: ON")
        else:
            # Enable 3D rotation mode
            self.preview_canvas.set_weapon_rotation_mode("3D")
            self.rotation_mode_toggle.setText("2D Spin: OFF")

    @Slot(bool)
    def _toggle_flames(self, checked: bool):
        """Toggle flame effects on/off."""
        self.flame_enabled = checked

        if checked:
            self.flame_toggle.setText("🔥 Flames: ON")
            # Create flame effect if it doesn't exist
            if self.current_flame_effect is None:
                self.current_flame_effect = FlameEffect()
        else:
            self.flame_toggle.setText("🔥 Flames: OFF")

        # Update preview to show/hide flames
        self._update_preview()

    def _update_preview(self):
        """Update the preview canvas with current weapon and flame."""
        if self.preview_canvas is None:
            return

        # Set weapon in canvas
        self.preview_canvas.set_weapon(self.current_weapon)

        # Set flame effect in canvas ONLY if flames are enabled
        if self.flame_enabled and self.current_flame_effect is not None:
            self.preview_canvas.set_flame_effect(self.current_flame_effect)
        else:
            # Pass None to disable flames
            self.preview_canvas.set_flame_effect(None)

        print("Preview updated")

    # ========================================================================
    # IMPORT/EXPORT
    # ========================================================================

    @Slot()
    def _import_png_weapon(self):
        """Import a custom PNG weapon image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Weapon PNG",
            "",
            "PNG Images (*.png);;All Files (*)"
        )

        if file_path:
            print(f"Importing PNG weapon: {file_path}")
            # TODO: Implement PNG import logic
            QMessageBox.information(
                self,
                "PNG Import",
                f"PNG import will be implemented in next update.\nFile: {file_path}"
            )

    @Slot()
    def _save_weapon(self):
        """Save current weapon to library."""
        if self.current_weapon is None:
            QMessageBox.warning(self, "No Weapon", "Please select a weapon first.")
            return

        print("Saving weapon to library...")

        # TODO: Implement weapon library save
        QMessageBox.information(
            self,
            "Weapon Saved",
            f"{self.current_weapon.name} saved to library!"
        )

        self.weapon_created.emit(self.current_weapon)

    @Slot()
    def _export_weapon(self):
        """Export weapon to JSON file."""
        if self.current_weapon is None:
            QMessageBox.warning(self, "No Weapon", "Please select a weapon first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Weapon",
            f"{self.current_weapon.name}.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                import json

                weapon_data = self.current_weapon.to_dict()

                # Add flame effect data
                if self.current_flame_effect:
                    weapon_data['flame_effect'] = {
                        'intensity': self.current_flame_effect.parameters.intensity,
                        'speed': self.current_flame_effect.parameters.speed,
                        'turbulence': self.current_flame_effect.parameters.turbulence,
                        'color_bottom': self.current_flame_effect.parameters.color_bottom,
                        'color_top': self.current_flame_effect.parameters.color_top,
                    }

                with open(file_path, 'w') as f:
                    json.dump(weapon_data, f, indent=2)

                print(f"✓ Weapon exported to {file_path}")

                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Weapon exported to:\n{file_path}"
                )

            except Exception as e:
                print(f"❌ Export failed: {e}")
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export weapon:\n{str(e)}"
                )

    @Slot()
    def _clear_weapon(self):
        """Clear current weapon and start over."""
        reply = QMessageBox.question(
            self,
            "Clear Weapon",
            "Are you sure you want to clear the current weapon?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.current_weapon = None
            self.current_flame_effect = None

            for btn in self.weapon_buttons.values():
                btn.setChecked(False)

            self.weapon_info_label.setText("No weapon selected")
            self._update_preview()

            print("Weapon cleared")

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def get_current_weapon(self):
        """Get the current weapon instance."""
        return self.current_weapon

    def get_current_flame_effect(self):
        """Get the current flame effect instance."""
        return self.current_flame_effect
