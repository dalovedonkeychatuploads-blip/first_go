#!/usr/bin/env python3
"""
DONK STICKMAN ENGINE - Professional Animation Studio
Main Entry Point
"""

import sys
import os
from pathlib import Path

# Prevent bytecode generation
sys.dont_write_bytecode = True


def check_requirements():
    """Check and report missing packages."""
    required = {
        'PySide6': 'PySide6',
        'numpy': 'numpy',
        'PIL': 'Pillow'
    }

    missing = []
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        print("\n" + "="*60)
        print("DONK STICKMAN ENGINE - Package Requirements")
        print("="*60)
        print("\nMissing required packages:")
        for pkg in missing:
            print(f"  • {pkg}")
        print("\nPlease install with:")
        print(f"  pip install {' '.join(missing)}")
        print("="*60 + "\n")
        return False

    return True


def setup_directories():
    """Create required directories."""
    dirs = [
        'data/toons',
        'data/presets/expressions',
        'data/presets/poses',
        'data/presets/hands',
        'data/temp',
        'assets/icons'
    ]

    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def main():
    """Launch the application."""
    # Check requirements
    if not check_requirements():
        input("\nPress Enter to exit...")
        return 1

    # Setup environment
    os.environ['QT_API'] = 'pyside6'
    if sys.platform == 'win32':
        os.environ['QT_OPENGL'] = 'desktop'

    # Create directories
    setup_directories()

    # Launch application
    try:
        from app import DonkStickmanEngine
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt

        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("DONK Stickman Engine")
        app.setOrganizationName("DONK Studios")

        # Enable high DPI support
        if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):
            app.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )

        # Create and show main window
        print("\n" + "="*60)
        print("   DONK STICKMAN ENGINE - Professional Edition")
        print("   Tab 1: Ready The Toon")
        print("="*60 + "\n")

        window = DonkStickmanEngine()
        window.show()

        # Run application
        return app.exec()

    except Exception as e:
        print(f"\n[ERROR] Failed to launch: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return 1


if __name__ == '__main__':
    sys.exit(main())