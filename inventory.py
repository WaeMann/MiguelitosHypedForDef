import sys
import subprocess
import mysql.connector
from script import FLAVORS, FLAVOR_PRICES, FLAVOR_IMAGES, SIZE_MULTIPLIER
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QFrame, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QIntValidator


class InventoryPage(QWidget):
    def __init__(self, switch_callback=None):
        super().__init__()
        self.switch_callback = switch_callback


        self.setWindowTitle("Hyped Mangoes Inventory")
        self.showMaximized()

        self.selected_row = None

        self.setStyleSheet(""" 
        QWidget {
            background-color: #DED6B2;
            font-family: "Segoe UI";
            font-size: 16px;
            color: #2c3e50;
        }

        QLabel {
            font-size: 16px;
            font-weight: 600;
        }

        QFrame {
            background-color: #DED6B2;
            border-radius: 14px;
            padding: 15px;
        }

        QPushButton {
            background-color: #f39c12;
            padding: 12px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
        }

        QPushButton:hover {
            background-color: #ffffff;
        }

        QPushButton#addBtn {
            background-color: #1e7f3f;
            color: white;
            font-weight: 700;
        }

        QPushButton#updateBtn {
            background-color: #f39c12;
            color: white;
        }
        
          QPushButton#logoutBtn:hover {
            background-color: #ffffff;
        }
        QPushButton#deleteBtn {
            background-color: #e74c3c;
            color: white;
        }

        QPushButton#logoutBtn {
            background-color: #f39c12;
            color: #2c3e50;
        }

        QLineEdit {
            padding: 10px;
            border-radius: 8px;
            border: 2px solid #dcdcdc;
            background: #fafafa;
        }

        QLineEdit:focus {
            border: 2px solid #1e7f3f;
        }

        QTableWidget {
            background-color: white;
            border-radius: 10px;
            gridline-color: #e0e0e0;
            alternate-background-color: #f7f5f0;
        }

        QHeaderView::section {
            background-color: #f0ede6;
            color: #333333;
            font-weight: bold;
            padding: 10px;
            border: none;
            border-bottom: 2px solid #d6d2c4;
        }
        """)

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # = TOP BAR =
        top_layout = QHBoxLayout()

        logo = QLabel()
        pixmap = QPixmap("hypedmangologo.png")
        logo.setPixmap(pixmap.scaled(180, 80, Qt.KeepAspectRatio))

        nav_layout = QHBoxLayout()
        buttons = [
            ("PoS", "pos.png"),
            ("Reports", "reports.png")
        ]

        for name, icon in buttons:
            btn = QPushButton(name)
            btn.setIcon(QIcon(icon))
            btn.setIconSize(QSize(20, 20))

            if name.lower() == "pos":
                btn.clicked.connect(lambda: self.switch_callback("pos") if self.switch_callback else None)

            elif name.lower() == "reports":
                btn.clicked.connect(lambda: self.switch_callback("report") if self.switch_callback else None)

            nav_layout.addWidget(btn)

            btn.setIcon(QIcon(icon))
            btn.setIconSize(QSize(20, 20))

        logout_btn = QPushButton("Log-Out")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.setIcon(QIcon("logout.png"))

        top_layout.addWidget(logo)
        top_layout.addStretch()
        top_layout.addLayout(nav_layout)
        top_layout.addStretch()
        top_layout.addWidget(logout_btn)

        # TABLE
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["#", "Product Name", "Quantity Left", "Available Sizes", "Flavors"]
        )

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.cellClicked.connect(self.load_selected_row)

        # HEADER SETTINGS
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignCenter)

        self.table.verticalHeader().setVisible(False)

        table_frame = QFrame()
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.table)
        table_frame.setLayout(table_layout)

        # FORM 
        form_frame = QFrame()
        form_layout = QVBoxLayout()

        self.name = QLineEdit()
        self.quantity = QLineEdit()
        self.expiry = QLineEdit()
        self.type = QLineEdit()

        self.quantity.setValidator(QIntValidator(0, 999999))

        form_layout.addWidget(QLabel("Product Name"))
        form_layout.addWidget(self.name)

        form_layout.addWidget(QLabel("Quantity Left"))
        form_layout.addWidget(self.quantity)

        form_layout.addWidget(QLabel("Available Sizes"))
        form_layout.addWidget(self.expiry)

        form_layout.addWidget(QLabel("Flavors"))
        form_layout.addWidget(self.type)

        # BUTTONS
        add_btn = QPushButton("ADD")
        add_btn.setObjectName("addBtn")
        add_btn.setIcon(QIcon("add.png"))
        add_btn.clicked.connect(self.add_item)

        update_btn = QPushButton("UPDATE")
        update_btn.setObjectName("updateBtn")
        update_btn.setIcon(QIcon("edit.png"))
        update_btn.clicked.connect(self.update_item)

        delete_btn = QPushButton("DELETE")
        delete_btn.setObjectName("deleteBtn")
        delete_btn.setIcon(QIcon("delete.png"))
        delete_btn.clicked.connect(self.delete_item)

        form_layout.addSpacing(15)
        form_layout.addWidget(add_btn)
        form_layout.addWidget(update_btn)
        form_layout.addWidget(delete_btn)

        form_frame.setLayout(form_layout)

        # LAYOUT
        content_layout = QHBoxLayout()
        content_layout.addWidget(table_frame, 3)
        content_layout.addWidget(form_frame, 1)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

        self.load_flavor_inventory()

    # FUNCTIONS

    def update_numbers(self):
        for row in range(self.table.rowCount()):
            item = QTableWidgetItem(str(row + 1))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item)

    def add_item(self):
        if not self.name.text() or not self.quantity.text():
            return

        row = self.table.rowCount()
        self.table.insertRow(row)

        values = [
            "",
            self.name.text(),
            self.quantity.text(),
            self.expiry.text(),
            self.type.text()
        ]

        for col, value in enumerate(values):
            self.table.setItem(row, col, QTableWidgetItem(value))

        self.update_numbers()
        self.clear_inputs()

    def load_selected_row(self, row, column):
        self.selected_row = row

        self.name.setText(self.table.item(row, 1).text())
        self.quantity.setText(self.table.item(row, 2).text())
        self.expiry.setText(self.table.item(row, 3).text())
        self.type.setText(self.table.item(row, 4).text())

    def update_item(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "Warning", "Select a row first!")
            return

        values = [
            "",
            self.name.text(),
            self.quantity.text(),
            self.expiry.text(),
            self.type.text()
        ]

        for col, value in enumerate(values):
            self.table.setItem(self.selected_row, col, QTableWidgetItem(value))

        self.update_numbers()
        self.clear_inputs()

    def delete_item(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "Warning", "Select a row first!")
            return

        self.table.removeRow(self.selected_row)
        self.selected_row = None

        self.update_numbers()
        self.clear_inputs()

    def clear_inputs(self):
        self.name.clear()
        self.quantity.clear()
        self.expiry.clear()
        self.type.clear()

    def reduce_stock(self, sold_items):
        """
        sold_items format:
        [(name, quantity_sold), ...]
        """

        for name, qty_sold in sold_items:
            for row in range(self.table.rowCount()):
                item_name = self.table.item(row, 1).text()

                if item_name.strip().lower() == name.strip().lower():
                    current_qty = int(self.table.item(row, 2).text())
                    new_qty = max(0, current_qty - qty_sold)

                    self.table.setItem(row, 2, QTableWidgetItem(str(new_qty)))
                    break

    def load_flavor_inventory(self):
        self.table.setRowCount(0)

        row_index = 0

        for category, items in FLAVORS.items():
            for item in items:
                self.table.insertRow(row_index)

                name = item
                qty = "0"  # default stock
                sizes = ", ".join(SIZE_MULTIPLIER.keys())
                price = f"₱{FLAVOR_PRICES.get(item, 0)}"
                flavor = category

                values = [
                    str(row_index + 1),
                    name,
                    qty,
                    sizes,
                    flavor
                ]

                for col, value in enumerate(values):
                    cell = QTableWidgetItem(value)
                    cell.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_index, col, cell)

                row_index += 1
