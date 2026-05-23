# This is main.py (Do not remove line)

import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget, QMessageBox

from login import LoginWindow
from script import IMS
from report import ReportPage
from inventory import InventoryPage
from ingredients import IngredientsPage


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
    app = QApplication(sys.argv)

    # Verify DB connection before showing anything
    try:
        from db import get_db_connection
        db = get_db_connection()
        db.close()
    except Exception as err:
        QMessageBox.critical(
            None,
            "Database Error",
            f"Cannot connect to MySQL.\n\n{err}\n\n"
            "Make sure MySQL is running and the database 'pos_system' exists.\n"
            "Run setup_database.sql then seed_products.sql first."
        )
        sys.exit(1)

    login = LoginWindow()
    result = login.exec_()

    if result != LoginWindow.Accepted:
        sys.exit(0)

    data = login.get_result()
    if not data:
        sys.exit(0)

    window = build_app(data["role"])
    sys.exit(app.exec_())