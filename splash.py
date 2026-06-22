# This is the splash.py (Do not remove line)
# Small frameless "loading" window shown on app launch, right after login,
# and right after logout. Self-contained so it can be shown before the
# rest of the app modules (which depend on the DB) are even imported.

import os
import time

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QTimer, QRectF, QEventLoop

CREAM  = QColor("#FFF8E7")
YELLOW = QColor("#FFD700")
GREEN  = QColor("#008000")


class _Spinner(QWidget):
    """Small rotating arc, redrawn on a timer."""

    def __init__(self, parent=None, diameter=30):
        super().__init__(parent)
        self._diameter = diameter
        self.setFixedSize(diameter, diameter)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(25)

    def _tick(self):
        self._angle = (self._angle + 8) % 360
        self.update()

    def stop(self):
        self._timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pad = 3
        rect = QRectF(pad, pad, self._diameter - 2 * pad, self._diameter - 2 * pad)

        # faint full track
        track_pen = QPen(QColor(0, 0, 0, 25), 4)
        track_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 0, 360 * 16)

        # bright moving arc
        pen = QPen(YELLOW, 4)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        span = 110
        painter.drawArc(rect, int(-self._angle * 16), int(span * 16))
        painter.end()


class LoadingScreen(QWidget):
    """Small frameless, always-on-top loading indicator.

    Usage:
        splash = LoadingScreen("Starting up...")
        splash.show()
        ... do work, optionally splash.set_message("...") ...
        splash.finish()   # closes, but only after a short minimum show time
    """

    def __init__(self, message="Loading..."):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setFixedSize(280, 160)
        self.setStyleSheet(
            "background-color: #FFF8E7; "
            "border: 1px solid #FFD700; "
            "border-radius: 12px;"
        )
        self._shown_at = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 16)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignHCenter)

        self.logo_lbl = QLabel()
        self.logo_lbl.setAlignment(Qt.AlignCenter)
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            if not pix.isNull():
                pix = pix.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_lbl.setPixmap(pix)
        layout.addWidget(self.logo_lbl)

        self.spinner = _Spinner(self)
        layout.addWidget(self.spinner, alignment=Qt.AlignHCenter)

        self.msg_lbl = QLabel(message)
        self.msg_lbl.setAlignment(Qt.AlignCenter)
        self.msg_lbl.setWordWrap(True)
        self.msg_lbl.setFont(QFont("Cambria", 10))
        self.msg_lbl.setStyleSheet("color: #333333; border: none;")
        layout.addWidget(self.msg_lbl)

        self._center_on_screen()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.x() + (screen.width() - self.width()) // 2,
            screen.y() + (screen.height() - self.height()) // 2,
        )

    def set_message(self, text):
        self.msg_lbl.setText(text)
        QApplication.processEvents()

    def show(self):
        super().show()
        self.raise_()
        self._shown_at = time.time()
        QApplication.processEvents()

    def finish(self, min_ms=500):
        """Close the splash, padding out to at least min_ms total visible
        time so quick operations don't just flash on screen."""
        if self._shown_at is not None:
            elapsed_ms = (time.time() - self._shown_at) * 1000
            remaining = min_ms - elapsed_ms
            if remaining > 0:
                loop = QEventLoop()
                QTimer.singleShot(int(remaining), loop.quit)
                loop.exec_()
        self.spinner.stop()
        self.close()
