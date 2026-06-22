# This is the login.py (Do not remove line)

import sys
import os
import re
import secrets
import time

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QCheckBox, QVBoxLayout, QHBoxLayout, QFormLayout,
    QDialog, QFrame, QMessageBox, QSizePolicy,
)
from PyQt5.QtGui import (
    QColor, QPixmap, QPainter, QBrush, QPen, QPolygonF, QFont,
)
from PyQt5.QtCore import Qt, QPointF, QTimer

from db import (
    hash_password, hash_password_pbkdf2, verify_password, gen_salt,
    get_db_connection, log_login, start_session, audit,
    MAX_ATTEMPTS, LOCKOUT_SECS,
)
from licensing import (
    is_dev_credentials, mark_dev_verified,
    register_first_use_if_needed, is_locked, trial_seconds_remaining,
)


# ─────────────────────────────────────────────────────────────────────────────
# Shared dialog style
# ─────────────────────────────────────────────────────────────────────────────
DIALOG_STYLE = """
QDialog { background-color: #FFF8E7; }
QLabel  { color: #333333; }
QLineEdit {
    border: 1px solid #ccc;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    background: white;
}
QLineEdit:focus { border: 1px solid #FFD700; }
QPushButton#confirmBtn {
    background-color: #008000;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 0;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#confirmBtn:hover { background-color: #006600; }
QCheckBox { color: #555; font-size: 12px; }
"""


# ─────────────────────────────────────────────────────────────────────────────
# Reset Password Dialog  (Forgot Password flow — cashiers only)
# ─────────────────────────────────────────────────────────────────────────────
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
        form.addRow("Re-Enter:",     self.re_pass)
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

    def _toggle_pw(self, on: bool):
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
        # ── Password complexity check ─────────────────────────────────────
        errors = []
        if not re.search(r'[A-Z]', p1):
            errors.append("• At least one uppercase letter (A–Z)")
        if not re.search(r'[a-z]', p1):
            errors.append("• At least one lowercase letter (a–z)")
        if not re.search(r'[0-9]', p1):
            errors.append("• At least one number (0–9)")
        if not re.search(r'[^A-Za-z0-9]', p1):
            errors.append("• At least one special character (!@#$%…)")
        if errors:
            QMessageBox.critical(
                self, "Weak Password",
                "Password must contain:\n" + "\n".join(errors)
            )
            return
        try:
            salt  = gen_salt()
            phash = hash_password_pbkdf2(p1, salt)
            db    = get_db_connection()
            cur   = db.cursor()
            cur.execute(
                "UPDATE users SET password_hash=%s, salt=%s WHERE username=%s",
                (phash, salt, self.username),
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
                pg.x() + (pg.width()  - self.width())  // 2,
                pg.y() + (pg.height() - self.height()) // 2,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Custom painted background widget
# ─────────────────────────────────────────────────────────────────────────────
class LoginBackground(QWidget):
    CREAM  = QColor("#FFF8E7")
    YELLOW = QColor("#FFD700")
    GREEN  = QColor("#008000")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._logo_pixmap = None
        if os.path.exists("logo.png"):
            self._logo_pixmap = QPixmap("logo.png")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        painter.fillRect(0, 0, w, h, self.CREAM)

        poly = QPolygonF([
            QPointF(0.75 * w, 0), QPointF(w, 0),
            QPointF(w, h),        QPointF(0.55 * w, h),
        ])
        painter.setBrush(QBrush(self.YELLOW))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(poly)

        painter.setPen(QPen(self.GREEN, 6))
        painter.drawLine(QPointF(0.75 * w, 0), QPointF(0.55 * w, h))

        if self._logo_pixmap and not self._logo_pixmap.isNull():
            logo_w, logo_h = 220, 220
            scaled = self._logo_pixmap.scaled(
                logo_w, logo_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            painter.drawPixmap(
                int(0.27 * w - scaled.width() / 2),
                int(h / 2 - scaled.height() / 2),
                scaled,
            )
        painter.end()


# ─────────────────────────────────────────────────────────────────────────────
# Main Login Window
# ─────────────────────────────────────────────────────────────────────────────
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.result_data = None
        self.setWindowTitle("System Login")

        # Frameless fullscreen — use Qt.Window so QDialog modality still works
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.bg = LoginBackground(self)
        root.addWidget(self.bg)

        self._build_form()
        self.form_widget.adjustSize()

        # Small status label positioned beside the logo. Hidden unless the
        # trial window has actually started; stays hidden forever once the
        # override account has been used.
        self.trial_lbl = QLabel("", self.bg)
        self.trial_lbl.setAlignment(Qt.AlignCenter)
        self.trial_lbl.setStyleSheet(
            "color: #555555; font-size: 11px; font-style: italic; "
            "background: transparent;"
        )
        self.trial_lbl.hide()
        self._refresh_trial_label()

        self._trial_timer = QTimer(self)
        self._trial_timer.timeout.connect(self._refresh_trial_label)
        self._trial_timer.start(30_000)

    def get_result(self):
        return self.result_data

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg.resize(self.size())
        self._reposition_form()
        self._position_trial_label()

    # ── Form construction ─────────────────────────────────────────────────
    def _build_form(self):
        self.form_widget = QWidget(self.bg)
        self.form_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.form_widget.setFixedWidth(290)

        layout = QVBoxLayout(self.form_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
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
        QLineEdit:focus { border: 1px solid #FFD700; }
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

        # Inline status label — shows lockout/wrong-password messages
        self.status_lbl = QLabel("")
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setFixedWidth(290)
        self.status_lbl.setStyleSheet(
            "color: #c0392b; font-size: 11px; "
            "background: transparent; padding: 2px;"
        )
        layout.addWidget(self.status_lbl)

        # Only "Forgot Password?" — Create Cashier Account removed for security
        # Shown only when exactly 1 login attempt remains
        links_row = QHBoxLayout()
        self.forgot_btn = self._link_btn("Forgot Password?")
        self.forgot_btn.clicked.connect(self.handle_forgot_password)
        self.forgot_btn.setVisible(False)
        links_row.addStretch()
        links_row.addWidget(self.forgot_btn)
        links_row.addStretch()
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
            QPushButton:hover   { background-color: #D9BE70; }
            QPushButton:pressed { background-color: #C9A850; }
        """)
        login_btn.clicked.connect(self.authenticate)
        layout.addWidget(login_btn)

    def _link_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFlat(True)
        btn.setStyleSheet("""
            QPushButton {
                color: #444; font-size: 11px;
                text-decoration: underline;
                background: transparent; border: none; padding: 0;
            }
            QPushButton:hover { color: #008000; }
        """)
        return btn

    def _reposition_form(self):
        self.form_widget.adjustSize()
        w = self.bg.width(); h = self.bg.height()
        rx = int(0.55 * w)
        form_x = rx + (w - rx - self.form_widget.width()) // 2
        form_y = (h - self.form_widget.height()) // 2
        self.form_widget.move(form_x, form_y)

    def showEvent(self, event):
        super().showEvent(event)
        self.form_widget.adjustSize()
        self._reposition_form()
        self._refresh_trial_label()

    # ── Trial-window label (sits just under the logo) ──────────────────────
    def _refresh_trial_label(self):
        remaining = trial_seconds_remaining()
        if remaining is None:
            if self.trial_lbl.isVisible() or self.trial_lbl.text():
                self.trial_lbl.setText("")
                self.trial_lbl.hide()
                # Force the custom-painted background to redraw the region
                # the label used to occupy, in case the widget toolkit
                # doesn't fully clear it on its own.
                self.bg.update()
            return
        if remaining <= 0:
            text = "Trial expired"
        else:
            days, rem = divmod(remaining, 86400)
            hours, rem = divmod(rem, 3600)
            minutes = rem // 60
            text = f"Trial: {days}d {hours}h {minutes}m left"
        self.trial_lbl.setText(text)
        self.trial_lbl.adjustSize()
        self._position_trial_label()
        self.trial_lbl.show()
        self.trial_lbl.raise_()

    def _position_trial_label(self):
        if not hasattr(self, "trial_lbl"):
            return
        w, h = self.bg.width(), self.bg.height()
        logo_half_h = 110  # half of the 220px logo box drawn in LoginBackground
        x = int(0.27 * w - self.trial_lbl.width() / 2)
        y = int(h / 2 + logo_half_h + 14)
        self.trial_lbl.move(x, y)

    # ── Authentication ────────────────────────────────────────────────────
    def authenticate(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        self.status_lbl.setText("")

        if not username or not password:
            self.status_lbl.setText("Please enter your username and password.")
            return

        # ── Hidden offline override check (no DB call, no network) ────────
        if is_dev_credentials(username, password):
            mark_dev_verified()
            self.username_edit.clear()
            self.password_edit.clear()
            self.trial_lbl.setText("")
            self.trial_lbl.hide()
            self._refresh_trial_label()
            self.bg.update()
            return

        # ── Trial-window gate ───────────────────────────────────────────────
        if is_locked():
            self.status_lbl.setText(
                "This system is currently unavailable. Please contact your administrator."
            )
            self.password_edit.clear()
            return

        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True, buffered=True)
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()

            if user is None:
                # Dummy hash prevents timing-based user enumeration
                hash_password_pbkdf2(password, gen_salt())
                log_login(db, username, False, "User not found")
                db.commit(); db.close()
                self.status_lbl.setText("Invalid username or password.")
                return

            # ── Case-sensitive username enforcement ───────────────────────
            # MySQL collation may be case-insensitive; enforce exact match here
            if user["username"] != username:
                hash_password_pbkdf2(password, gen_salt())
                log_login(db, username, False, "Username case mismatch")
                db.commit(); db.close()
                self.status_lbl.setText("Invalid username or password.")
                return

            uid      = user["id"]
            now_ts   = int(time.time())

            # ── Lockout check ─────────────────────────────────────────────
            locked_until = int(user.get("locked_until") or 0)
            if locked_until > now_ts:
                remaining = locked_until - now_ts
                m, s = divmod(remaining, 60)
                log_login(db, username, False,
                          f"Account locked ({m}m {s}s remaining)")
                db.commit(); db.close()
                self.status_lbl.setText(
                    f"Account locked. Try again in {m}m {s}s."
                )
                return

            # ── Password verification with transparent SHA-256 → PBKDF2 migration ──
            salt = (user.get("salt") or "").strip()
            if not salt:
                # Legacy plain-SHA-256 hash — verify, then upgrade in-place
                valid = secrets.compare_digest(
                    hash_password(password), user["password_hash"]
                )
                if valid:
                    new_salt  = gen_salt()
                    new_hash  = hash_password_pbkdf2(password, new_salt)
                    cur.execute(
                        "UPDATE users SET password_hash=%s, salt=%s WHERE id=%s",
                        (new_hash, new_salt, uid),
                    )
            else:
                valid = verify_password(password, user["password_hash"], salt)

            if not valid:
                failed = int(user.get("failed_attempts") or 0) + 1
                if failed >= MAX_ATTEMPTS:
                    lock_ts = now_ts + LOCKOUT_SECS
                    cur.execute(
                        "UPDATE users SET failed_attempts=%s, locked_until=%s "
                        "WHERE id=%s",
                        (failed, lock_ts, uid),
                    )
                    log_login(db, username, False,
                              "Account locked after max failed attempts")
                    db.commit(); db.close()
                    self.status_lbl.setText(
                        f"Too many failed attempts. "
                        f"Account locked for {LOCKOUT_SECS // 60} minutes."
                    )
                else:
                    cur.execute(
                        "UPDATE users SET failed_attempts=%s WHERE id=%s",
                        (failed, uid),
                    )
                    left = MAX_ATTEMPTS - failed
                    log_login(db, username, False,
                              f"Wrong password ({failed}/{MAX_ATTEMPTS})")
                    db.commit(); db.close()
                    self.status_lbl.setText(
                        f"Invalid username or password. "
                        f"{left} attempt{'s' if left != 1 else ''} remaining."
                    )
                    # Show "Forgot Password?" only when 1 attempt remains
                    self.forgot_btn.setVisible(left == 1)
                self.password_edit.clear()
                return

            # ── Success ───────────────────────────────────────────────────
            self.forgot_btn.setVisible(False)
            import datetime as _dt
            session_id = secrets.token_hex(16)
            now_str    = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cur.execute(
                "UPDATE users SET failed_attempts=0, locked_until=0, "
                "last_login=%s WHERE id=%s",
                (now_str, uid),
            )
            log_login(db, username, True, "Login successful", session_id)
            start_session(db, uid, username, session_id)
            audit(db, uid, username, "LOGIN", f"Session {session_id}")
            db.commit(); db.close()

            self.result_data = {
                "username":   username,
                "role":       user["role"],
                "uid":        uid,
                "session_id": session_id,
            }
            register_first_use_if_needed()
            self.accept()

        except Exception as err:
            QMessageBox.critical(
                self, "Database Connection Error",
                f"Cannot connect to DB:\n{err}"
            )

    # ── Forgot password ───────────────────────────────────────────────────
    def handle_forgot_password(self):
        username = self.username_edit.text().strip()
        if not username:
            QMessageBox.warning(self, "Warning",
                                "Please enter your username first.")
            return
        if username.lower() == "admin":
            QMessageBox.critical(self, "Access Denied",
                                 "Admin password cannot be reset via this feature.\n"
                                 "Contact your system administrator.")
            return
        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                "SELECT username, role FROM users WHERE username = %s", (username,)
            )
            user = cur.fetchone()
            db.close()
            # Enforce case-sensitive username match
            if user and user["username"] != username:
                user = None
            if user and user["role"] == "cashier":
                dlg = ResetPasswordDialog(username, parent=self)
                dlg.exec_()
            else:
                QMessageBox.critical(self, "Error",
                                     "User not found or not a cashier account.")
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))