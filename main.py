# This is main.py (Do not remove line)

import sys
import os

# ── Fix for windowed PyInstaller exe (console=False) ──────────────────────────
# When there is no console window, Python sets sys.stdout and sys.stderr to
# None. Any print() or .flush() call then crashes instantly with:
#   AttributeError: 'NoneType' object has no attribute 'flush'
# Redirect them to devnull so the app starts silently instead of crashing.
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

# ── PyInstaller: set working directory to the _internal bundle folder ──────────
# When frozen, all data files (images, etc.) land in sys._MEIPASS.
# Setting CWD there makes every bare relative path — e.g. QPixmap("logo.png")
# or QPixmap("hypedmangologo.png") — resolve correctly without changing any
# other code. Has no effect when running from source.
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

LOGOUT_CODE = 42  # exit code that signals "go back to login"


def switch_page_factory(stack, pages):
    def switch(page_name):
        if page_name in pages:
            stack.setCurrentWidget(pages[page_name])
    return switch


def build_app(role, username="", splash=None):
    from PyQt5.QtCore import Qt
    if splash:
        splash.set_message("Loading menu and inventory...")
    stack = QStackedWidget()
    stack.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
    pages = {}
    switch = switch_page_factory(stack, pages)

    pages["report"]      = ReportPage(switch_callback=switch, role=role, username=username)
    pages["inventory"]   = InventoryPage(switch_callback=switch, role=role, username=username)
    pages["ingredients"] = IngredientsPage(switch_callback=switch, role=role, username=username)
    pages["pos"]         = IMS(
        switch_callback=switch,
        report_page=pages["report"],
        inventory_page=pages["inventory"],
        ingredients_page=pages["ingredients"],
        role=role,
        username=username,
    )

    # When inventory changes → refresh POS menu cards and ingredients combos.
    def _on_inventory_change():
        pages["pos"].refresh_products()

    pages["inventory"].on_change = _on_inventory_change

    # When ingredients change → refresh inventory stock calculations and POS.
    def _on_ingredients_change():
        pages["inventory"].load_from_db()
        pages["pos"].refresh_products()

    pages["ingredients"].on_change = _on_ingredients_change

    for p in pages.values():
        stack.addWidget(p)

    if role == "admin":
        stack.setCurrentWidget(pages["report"])
    else:
        stack.setCurrentWidget(pages["pos"])

    if splash:
        splash.set_message("Almost ready...")
    stack.showFullScreen()
    # Lock window to actual fullscreen size so that showing hidden panels
    # never causes the FramelessWindowHint window to resize beyond the screen.
    QApplication.processEvents()
    stack.setFixedSize(stack.width(), stack.height())
    return stack


if __name__ == "__main__":
    # Verify DB connection BEFORE importing any Qt modules. mysql-connector-python
    # and PyQt5 ship their own native networking/SSL DLLs -- if Qt is loaded
    # first and mysql-connector then touches the network, it can hard-crash
    # the process (access violation) on some Windows setups. Keep this order.
    try:
        from db import get_db_connection, end_session, audit
        db = get_db_connection()
        db.close()
    except Exception as err:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        _app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "Database Error",
            f"Cannot connect to the database.\n\n{err}\n\n"
            "Make sure MySQL is running and db.py settings are correct."
        )
        sys.exit(1)

    from PyQt5.QtWidgets import QApplication, QStackedWidget, QMessageBox

    app = QApplication(sys.argv)

    # ── Loading window #1: shown the moment the app's GUI spins up ──────────
    from splash import LoadingScreen
    splash = LoadingScreen("Starting up...")
    splash.show()
    splash.set_message("Loading application...")

    from login import LoginWindow
    from script import IMS
    from report import ReportPage
    from inventory import InventoryPage
    from ingredients import IngredientsPage

    splash.finish()

    # ── Login → App → Logout loop ────────────────────────────────────────────
    while True:
        login = LoginWindow()
        result = login.exec_()

        if result != LoginWindow.Accepted:
            break

        data = login.get_result()
        if not data:
            break

        # ── Loading window #2: shown right after a successful log-in ────────
        username = data.get("username", "")
        splash = LoadingScreen(f"Welcome, {username}!" if username else "Logging in...")
        splash.show()

        window = build_app(data["role"], username, splash=splash)
        splash.finish()

        exit_code = app.exec_()
        window.close()

        if exit_code != LOGOUT_CODE:
            break

        # ── Loading window #3: shown right after logging out ────────────────
        splash = LoadingScreen("Signing out...")
        splash.show()

        session_id = data.get("session_id")
        if session_id:
            try:
                sdb = get_db_connection()
                end_session(sdb, session_id, "manual")
                audit(sdb, data.get("uid"), data.get("username"),
                      "LOGOUT", f"Session {session_id}")
                sdb.commit()
                sdb.close()
            except Exception:
                pass

        splash.finish()

    sys.exit(0)
