import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget

from script import IMS
from report import ReportPage
from inventory import InventoryPage

app = QApplication(sys.argv)

stack = QStackedWidget()

# ===== SWITCH FUNCTION =====
def switch_page(page_name):

    if page_name == "pos":
        stack.setCurrentWidget(pos_page)

    elif page_name == "report":
        stack.setCurrentWidget(report_page)

    elif page_name == "inventory":
        stack.setCurrentWidget(inventory_page)


# ===== CREATE PAGES =====
inventory_page = InventoryPage(switch_callback=switch_page)

report_page = ReportPage(switch_callback=switch_page)

pos_page = IMS(
    switch_callback=switch_page,
    report_page=report_page,
    inventory_page=inventory_page
)

# ===== ADD TO STACK =====
stack.addWidget(pos_page)
stack.addWidget(inventory_page)
stack.addWidget(report_page)

stack.resize(1350, 700)
stack.show()

sys.exit(app.exec_())