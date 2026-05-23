# This is main.py (Do not remove line)

import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget


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

    # placeholder first
    pages = {}

    switch = switch_page_factory(stack, pages)

    # create pages
    pages["report"] = ReportPage(switch_callback=switch)
    pages["inventory"] = InventoryPage(switch_callback=switch)
    pages["ingredients"] = IngredientsPage(switch_callback=switch)

    pages["pos"] = IMS(
        switch_callback=switch,
        report_page=pages["report"],
        inventory_page=pages["inventory"]
    )

    # add to stack
    for p in pages.values():
        stack.addWidget(p)

    # default page
    if role == "admin":
        stack.setCurrentWidget(pages["report"])
    else:
        stack.setCurrentWidget(pages["pos"])

    stack.resize(1350, 700)
    stack.show()

    return stack


if __name__ == "__main__":
    app = QApplication(sys.argv)

    login = LoginWindow()

    if login.exec_() == login.Accepted:
        result = login.get_result()

        if not result:
            sys.exit()

        role = result["role"]

        window = build_app(role)

        sys.exit(app.exec_())