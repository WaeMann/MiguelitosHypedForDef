# This is main.py (Do not remove line)

import sys
print("main: import sys done", flush=True)

sys.stdout.flush()
sys.stderr.flush()

LOGOUT_CODE = 42  # exit code that signals "go back to login"


def switch_page_factory(stack, pages):
    def switch(page_name):
        if page_name in pages:
            stack.setCurrentWidget(pages[page_name])
    return switch


def build_app(role):
    stack = QStackedWidget()
    pages = {}
    switch = switch_page_factory(stack, pages)

    pages["report"]      = ReportPage(switch_callback=switch)
    pages["inventory"]   = InventoryPage(switch_callback=switch)
    pages["ingredients"] = IngredientsPage(switch_callback=switch)
    pages["pos"]         = IMS(
        switch_callback=switch,
        report_page=pages["report"],
        inventory_page=pages["inventory"],
        role=role,
    )

    for p in pages.values():
        stack.addWidget(p)

    if role == "admin":
        stack.setCurrentWidget(pages["report"])
    else:
        stack.setCurrentWidget(pages["pos"])

    stack.showMaximized()
    return stack


if __name__ == "__main__":
    # Verify DB connection before importing the full GUI modules.
    try:
        from db import get_db_connection
        print("main: testing DB connection before importing Qt modules", flush=True)
        db = get_db_connection()
        db.close()
        print("main: DB connection OK", flush=True)
    except Exception as err:
        print(f"main: DB connection failed: {err}", flush=True)
        sys.exit(1)

    print("main: importing PyQt5.QtWidgets after DB check", flush=True)
    from PyQt5.QtWidgets import QApplication, QStackedWidget, QMessageBox

    print("main: importing app modules after DB check", flush=True)
    from login import LoginWindow
    from script import IMS
    from report import ReportPage
    from inventory import InventoryPage
    from ingredients import IngredientsPage

    print("main: starting QApplication", flush=True)
    app = QApplication(sys.argv)
    print("main: QApplication created", flush=True)

    # ── Login → App → Logout loop ────────────────────────────────────────────
    while True:
        print("main: creating LoginWindow", flush=True)
        login = LoginWindow()
        print("main: calling login.exec_()", flush=True)
        result = login.exec_()
        print(f"main: login.exec_ returned {result}", flush=True)

        if result != LoginWindow.Accepted:
            print("main: login canceled or closed", flush=True)
            break

        data = login.get_result()
        print(f"main: login result data={data}", flush=True)
        if not data:
            print("main: no login data", flush=True)
            break

        print("main: building main window", flush=True)
        window = build_app(data["role"])
        print("main: starting event loop", flush=True)
        exit_code = app.exec_()
        print(f"main: event loop exited with code {exit_code}", flush=True)

        # Close & clean up the window before potentially looping
        window.close()

        if exit_code != LOGOUT_CODE:
            # Normal close (user hit X), not a logout request
            break
        # else: loop back to show login again

    sys.exit(0)