# This is the login.py (Do not remove line)

import sys
import os

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QCheckBox, QVBoxLayout, QHBoxLayout, QFormLayout,
    QDialog, QFrame, QMessageBox, QSizePolicy,
)
from PyQt5.QtGui import (
    QColor, QPixmap, QPainter, QBrush, QPen, QPolygonF,
    QFont,
)
from PyQt5.QtCore import Qt, QPointF

from db import hash_password, get_db_connection


# ---------------------------------------------------------------------------
# Reusable styled dialogs
# ---------------------------------------------------------------------------
DIALOG_STYLE = """
QDialog {
    background-color: #FFF8E7;
}
QLabel {
    color: #333333;
}
QLineEdit {
    border: 1px solid #ccc;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    background: white;
}
QLineEdit:focus {
    border: 1px solid #FFD700;
}
QPushButton#confirmBtn {
    background-color: #008000;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 0;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#confirmBtn:hover {
    background-color: #006600;
}
QCheckBox {
    color: #555;
    font-size: 12px;
}
"""


class CreateAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Account")
        self.setFixedSize(350, 300)
        self.setStyleSheet(DIALOG_STYLE)
        self._build()
        self._center_on_parent()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        title = QLabel("New Cashier Account")
        title.setFont(QFont("Cambria", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("username")
        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("password")
        self.pass_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Username:", self.user_edit)
        form.addRow("Password:", self.pass_edit)
        layout.addLayout(form)

        show_cb = QCheckBox("Show Password")
        show_cb.toggled.connect(
            lambda on: self.pass_edit.setEchoMode(
                QLineEdit.Normal if on else QLineEdit.Password
            )
        )
        layout.addWidget(show_cb)
        layout.addStretch()

        btn = QPushButton("Create")
        btn.setObjectName("confirmBtn")
        btn.setFixedHeight(38)
        btn.clicked.connect(self._register)
        layout.addWidget(btn)

    def _register(self):
        u = self.user_edit.text().strip()
        p = self.pass_edit.text()
        if not u or not p:
            QMessageBox.critical(self, "Error", "Please fill in both fields.")
            return
        try:
            db = get_db_connection()
            cur = db.cursor(buffered=True)
            cur.execute("SELECT username FROM users WHERE username = %s", (u,))
            if cur.fetchone():
                QMessageBox.critical(self, "Error", "Username already exists.")
                db.close()
                return
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'cashier')",
                (u, hash_password(p)),
            )
            db.commit()
            db.close()
            QMessageBox.information(self, "Success", f"Cashier account '{u}' created successfully!")
            self.accept()
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))

    def _center_on_parent(self):
        if self.parent():
            pg = self.parent().geometry()
            self.move(
                pg.x() + (pg.width() - self.width()) // 2,
                pg.y() + (pg.height() - self.height()) // 2,
            )


class ResetPasswordDialog(QDialog):
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("Reset Password")
        self.setFixedSize(350, 320)
        self.setStyleSheet(DIALOG_STYLE)
        self._build()
        self._center_on_parent()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        title = QLabel("Reset Password")
        title.setFont(QFont("Cambria", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        acct = QLabel(f"Account: {self.username}")
        acct.setAlignment(Qt.AlignCenter)
        acct.setStyleSheet("font-style: italic; font-size: 12px;")
        layout.addWidget(acct)

        form = QFormLayout()
        form.setSpacing(8)
        self.new_pass = QLineEdit()
        self.new_pass.setPlaceholderText("new password")
        self.new_pass.setEchoMode(QLineEdit.Password)
        self.re_pass = QLineEdit()
        self.re_pass.setPlaceholderText("re-enter new password")
        self.re_pass.setEchoMode(QLineEdit.Password)
        form.addRow("New Password:", self.new_pass)
        form.addRow("Re-Enter:", self.re_pass)
        layout.addLayout(form)

        show_cb = QCheckBox("Show Password")
        show_cb.toggled.connect(self._toggle_pw)
        layout.addWidget(show_cb)
        layout.addStretch()

        btn = QPushButton("Confirm")
        btn.setObjectName("confirmBtn")
        btn.setFixedHeight(38)
        btn.clicked.connect(self._confirm)
        layout.addWidget(btn)

    def _toggle_pw(self, on):
        mode = QLineEdit.Normal if on else QLineEdit.Password
        self.new_pass.setEchoMode(mode)
        self.re_pass.setEchoMode(mode)

    def _confirm(self):
        p1 = self.new_pass.text()
        p2 = self.re_pass.text()
        if not p1 or not p2:
            QMessageBox.critical(self, "Error", "Please fill in both fields.")
            return
        if p1 != p2:
            QMessageBox.critical(self, "Error", "Passwords do not match.")
            return
        try:
            db = get_db_connection()
            cur = db.cursor()
            cur.execute(
                "UPDATE users SET password_hash = %s WHERE username = %s",
                (hash_password(p1), self.username),
            )
            db.commit()
            db.close()
            QMessageBox.information(self, "Success", "Password updated successfully!")
            self.accept()
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))

    def _center_on_parent(self):
        if self.parent():
            pg = self.parent().geometry()
            self.move(
                pg.x() + (pg.width() - self.width()) // 2,
                pg.y() + (pg.height() - self.height()) // 2,
            )


# ---------------------------------------------------------------------------
# Custom painted background widget
# ---------------------------------------------------------------------------
class LoginBackground(QWidget):
    CREAM  = QColor("#FFF8E7")
    YELLOW = QColor("#FFD700")
    GREEN  = QColor("#008000")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._logo_pixmap = None
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            self._logo_pixmap = QPixmap(logo_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        painter.fillRect(0, 0, w, h, self.CREAM)

        poly = QPolygonF([
            QPointF(0.75 * w, 0),
            QPointF(w, 0),
            QPointF(w, h),
            QPointF(0.55 * w, h),
        ])
        painter.setBrush(QBrush(self.YELLOW))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(poly)

        pen = QPen(self.GREEN, 6)
        painter.setPen(pen)
        painter.drawLine(QPointF(0.75 * w, 0), QPointF(0.55 * w, h))

        if self._logo_pixmap and not self._logo_pixmap.isNull():
            logo_w, logo_h = 220, 220
            scaled = self._logo_pixmap.scaled(
                logo_w, logo_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            x = int(0.27 * w - scaled.width() / 2)
            y = int(h / 2 - scaled.height() / 2)
            painter.drawPixmap(x, y, scaled)

        painter.end()


# ---------------------------------------------------------------------------
# Main Login Window
# ---------------------------------------------------------------------------
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.result_data = None
        self.setWindowTitle("System Login")
        self.resize(1200, 600)
        self.setMinimumSize(800, 480)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.bg = LoginBackground(self)
        root.addWidget(self.bg)

        self._build_form()
        self.form_widget.adjustSize()
        self._center_window()

    def get_result(self):
        return self.result_data

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg.resize(self.size())
        self._reposition_form()

    def _build_form(self):
        self.form_widget = QWidget(self.bg)
        self.form_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.form_widget.setFixedWidth(280)

        layout = QVBoxLayout(self.form_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        title = QLabel("Log-In")
        title.setFont(QFont("Cambria", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333333;")
        layout.addWidget(title)

        field_style = """
        QLineEdit {
            background: white;
            border: 1px solid #ccc;
            border-radius: 14px;
            padding: 7px 14px;
            font-size: 13px;
            color: #333;
        }
        QLineEdit:focus {
            border: 1px solid #FFD700;
        }
        """

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("username")
        self.username_edit.setFixedHeight(38)
        self.username_edit.setStyleSheet(field_style)
        layout.addWidget(self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setFixedHeight(38)
        self.password_edit.setStyleSheet(field_style)
        self.password_edit.returnPressed.connect(self.authenticate)
        layout.addWidget(self.password_edit)

        links_row = QHBoxLayout()
        forgot_btn = self._link_button("Forgot Password?")
        forgot_btn.clicked.connect(self.handle_forgot_password)
        create_btn = self._link_button("Create Cashier Account")
        create_btn.clicked.connect(self.show_create_account)
        links_row.addWidget(forgot_btn)
        links_row.addStretch()
        links_row.addWidget(create_btn)
        layout.addLayout(links_row)

        login_btn = QPushButton("Let's Go!")
        login_btn.setFixedHeight(42)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setFont(QFont("Cambria", 13, QFont.Bold))
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #E8D28C;
                color: #333;
                border: none;
                border-radius: 14px;
            }
            QPushButton:hover { background-color: #D9BE70; }
            QPushButton:pressed { background-color: #C9A850; }
        """)
        login_btn.clicked.connect(self.authenticate)
        layout.addWidget(login_btn)

    def _link_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFlat(True)
        btn.setStyleSheet("""
            QPushButton {
                color: #444;
                font-size: 11px;
                text-decoration: underline;
                background: transparent;
                border: none;
                padding: 0;
            }
            QPushButton:hover { color: #008000; }
        """)
        return btn

    def _reposition_form(self):
        self.form_widget.adjustSize()
        w = self.bg.width()
        h = self.bg.height()
        right_x = int(0.55 * w)
        right_w = w - right_x
        form_x = right_x + (right_w - self.form_widget.width()) // 2
        form_y = (h - self.form_widget.height()) // 2
        self.form_widget.move(form_x, form_y)

    def showEvent(self, event):
        super().showEvent(event)
        self.form_widget.adjustSize()
        self._reposition_form()

    def _center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            screen.x() + (screen.width() - self.width()) // 2,
            screen.y() + (screen.height() - self.height()) // 2,
        )

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def authenticate(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        if not username or not password:
            QMessageBox.critical(self, "Error", "Please enter your username and password.")
            return

        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True, buffered=True)
            cur.execute(
                "SELECT role FROM users WHERE username = %s AND password_hash = %s",
                (username, hash_password(password)),
            )
            user = cur.fetchone()
            db.close()

            if user:
                self.result_data = {"username": username, "role": user["role"]}
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Invalid username or password.")
        except Exception as err:
            QMessageBox.critical(self, "Database Connection Error", f"Cannot connect to DB:\n{err}")

    def handle_forgot_password(self):
        username = self.username_edit.text().strip()
        if not username:
            QMessageBox.warning(self, "Warning", "Please enter your username first.")
            return
        if username.lower() == "admin":
            QMessageBox.critical(self, "Access Denied", "Admin password cannot be changed via this feature.")
            return
        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute("SELECT role FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            db.close()
            if user and user["role"] == "cashier":
                dlg = ResetPasswordDialog(username, parent=self)
                dlg.exec_()
            else:
                QMessageBox.critical(self, "Error", "User not found or unauthorized.")
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))

    def show_create_account(self):
        dlg = CreateAccountDialog(parent=self)
        dlg.exec_()