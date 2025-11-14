"""
DONK STICKMAN ENGINE - Main Application Window
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QMenuBar, QMenu, QToolBar, QStatusBar, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QPalette, QColor

from tab1_ready_toon import Tab1ReadyToon


class DonkStickmanEngine(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DONK Stickman Engine - Professional Edition")
        self.setGeometry(100, 100, 1600, 900)

        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background: #1a1a1e;
            }
            QMenuBar {
                background: #242428;
                border-bottom: 1px solid #3a3a3e;
                padding: 4px;
            }
            QMenuBar::item {
                color: #d0d0d0;
                padding: 6px 12px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background: #3a3a3e;
                color: white;
            }
            QMenu {
                background: #2a2a2e;
                border: 1px solid #3a3a3e;
            }
            QMenu::item {
                color: #d0d0d0;
                padding: 8px 24px;
            }
            QMenu::item:selected {
                background: #3a3a4e;
                color: white;
            }
            QTabWidget {
                background: #1a1a1e;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a3e;
                background: #222226;
                border-top: none;
            }
            QTabBar::tab {
                background: #2a2a2e;
                color: #a0a0a0;
                padding: 10px 20px;
                margin: 0 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #3a3a4e;
                color: white;
            }
            QTabBar::tab:hover {
                background: #323238;
            }
            QTabBar::tab:disabled {
                background: #1a1a1e;
                color: #606060;
            }
            QStatusBar {
                background: #1a1a1e;
                border-top: 1px solid #3a3a3e;
                color: #a0a0a0;
            }
        """)

        # Create menu bar
        self.create_menu_bar()

        # Create central widget with tabs
        self.create_tabs()

        # Create status bar
        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(28)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Toon", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_toon)
        file_menu.addAction(new_action)

        open_action = QAction("Open Toon", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_toon)
        file_menu.addAction(open_action)

        save_action = QAction("Save Toon", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_toon)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        copy_action = QAction("Copy Pose", self)
        copy_action.setShortcut("Ctrl+C")
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste Pose", self)
        paste_action.setShortcut("Ctrl+V")
        edit_menu.addAction(paste_action)

        # View menu
        view_menu = menubar.addMenu("View")

        grid_action = QAction("Show Grid", self)
        grid_action.setCheckable(True)
        grid_action.setChecked(True)
        view_menu.addAction(grid_action)

        axes_action = QAction("Show Axes", self)
        axes_action.setCheckable(True)
        axes_action.setChecked(False)
        view_menu.addAction(axes_action)

        view_menu.addSeparator()

        reset_view_action = QAction("Reset View", self)
        reset_view_action.setShortcut("Home")
        view_menu.addAction(reset_view_action)

        # Tools menu (hamburger menu content)
        tools_menu = menubar.addMenu("☰")

        settings_action = QAction("Settings", self)
        tools_menu.addAction(settings_action)

        about_action = QAction("About", self)
        tools_menu.addAction(about_action)

    def create_tabs(self):
        """Create the tab widget."""
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tabs = QTabWidget()

        # Tab 1: Ready The Toon (fully implemented)
        self.tab1 = Tab1ReadyToon()
        self.tabs.addTab(self.tab1, "Ready The Toon")

        # Tab 2: Movie Maker (placeholder)
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_label = QLabel("Movie Maker\n\nComing Soon")
        tab2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab2_label.setStyleSheet("color: #606060; font-size: 24px;")
        tab2_layout.addWidget(tab2_label)
        self.tabs.addTab(tab2, "Movie Maker")
        self.tabs.setTabEnabled(1, False)

        # Tab 3: Export (placeholder)
        tab3 = QWidget()
        tab3_layout = QVBoxLayout(tab3)
        tab3_label = QLabel("Export Studio\n\nComing Soon")
        tab3_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab3_label.setStyleSheet("color: #606060; font-size: 24px;")
        tab3_layout.addWidget(tab3_label)
        self.tabs.addTab(tab3, "Export")
        self.tabs.setTabEnabled(2, False)

        layout.addWidget(self.tabs)
        self.setCentralWidget(central)

    def new_toon(self):
        """Create a new toon."""
        self.tab1.new_toon()
        self.status_bar.showMessage("Creating new toon...", 2000)

    def open_toon(self):
        """Open an existing toon."""
        self.tab1.open_toon()

    def save_toon(self):
        """Save the current toon."""
        self.tab1.save_toon()
        self.status_bar.showMessage("Toon saved", 2000)