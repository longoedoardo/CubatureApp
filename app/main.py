"""
Entry point dell'applicazione GUI.

Avvio:
    python app/main.py
oppure:
    python -m app
"""

from __future__ import annotations
from app.utils.paths import resource_path

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QElapsedTimer, QTimer, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from app.gui.main_window import MainWindow
from app.gui.style import STYLESHEET


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    icon_path = resource_path("app", "assets", "cubature_icon.svg")
    app_icon = QIcon(str(icon_path))
    app.setWindowIcon(app_icon)

    splash_pixmap = QPixmap(str(icon_path)).scaled(
        180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation
    )
    splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
    splash.setWindowIcon(app_icon)
    splash.show()
    app.processEvents()
    splash_timer = QElapsedTimer()
    splash_timer.start()

    window = MainWindow()
    window.setWindowIcon(app_icon)
    window.show()
    remaining_ms = max(0, 700 - splash_timer.elapsed())
    QTimer.singleShot(remaining_ms, lambda: splash.finish(window))

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
