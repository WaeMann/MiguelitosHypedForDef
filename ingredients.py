# This is the ingredients.py (Do not remove line)

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QFrame, QHeaderView, QMessageBox,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QIcon, QIntValidator, QColor, QMouseEvent
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QIntValidator, QColor

from db import get_db_connection


def drop_shadow(widget, blur=25, x=3, y=3, alpha=150):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setXOffset(x)
    fx.setYOffset(y)
    fx.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(fx)
    return fx


NAV_BTN_STYLE = """
QPushButton {
    background-color: #E8D28C;
    color: #222222;
    font-size: 15px;
    border-radius: 8px;
    font-weight: bold;
    border: none;
    padding: 4px 14px;
}
QPushButton:hover { background-color: #D9BE70; }
"""

BLUE_BTN_STYLE = """
QPushButton {
    background-color: #34699A;
    color: white;
    font-size: 14px;
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: bold;
    border: none;
}
QPushButton:hover { background-color: #2a567a; }
"""

GREEN_BTN_STYLE = """
QPushButton {
    background-color: #1e7f3f;
    color: white;
    font-size: 14px;
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: bold;
    border: none;
}
QPushButton:hover { background-color: #166330; }
"""

RED_BTN_STYLE = """
QPushButton {
    background-color: #c0392b;
    color: white;
    font-size: 14px;
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: bold;
    border: none;
}
QPushButton:hover { background-color: #a93226; }
"""

INPUT_STYLE = """
QLineEdit {
    background-color: #fafaf7;
    border: 2px solid #d6d2c4;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    color: #2c3e50;
}
QLineEdit:focus {
    border: 2px solid #34699A;
    background-color: white;
}
"""

TABLE_STYLE = """
QTableWidget {
    background-color: white;
    border: none;
    border-radius: 10px;
    gridline-color: #ede9dc;
    alternate-background-color: #f7f5f0;
    font-size: 14px;
    color: #2c3e50;
    selection-background-color: #d4e6f7;
    selection-color: #2c3e50;
}
QHeaderView::section {
    background-color: #E8D28C;
    color: #2b2b2b;
    font-weight: bold;
    font-size: 14px;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #d6c870;
}
QScrollBar:vertical {
    background: #EFE9D1;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #c8b87a;
    border-radius: 4px;
}
"""

class DragScrollTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.setVerticalScrollMode(QTableWidget.ScrollPerPixel)

        self._dragging = False
        self._last_pos = None

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._last_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self._last_pos:
            delta = event.pos() - self._last_pos

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )

            self._last_pos = event.pos()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self._last_pos = None
        self.setCursor(Qt.ArrowCursor)

        super().mouseReleaseEvent(event)


class IngredientsPage(QWidget):
    def __init__(self, switch_callback=None):
        super().__init__()
        self.switch_callback = switch_callback
        self.setWindowTitle("Hyped Mangoes — Ingredients")
        self.showMaximized()
        self.selected_row = None
        self._row_ids = {}   # table row index → DB id

        self.setStyleSheet("QWidget { background-color: #DED6B2; font-family: 'Segoe UI'; }")
        self.initUI()
        self.load_from_db()

    def initUI(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── TOP BAR ──────────────────────────────────────────────────────────
        top_bar = QFrame()
        top_bar.setFixedHeight(80)
        top_bar.setStyleSheet("background-color: #DED6B2;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(24, 0, 24, 0)
        top_bar_layout.setSpacing(10)

        logo = QLabel()
        px = QPixmap("hypedmangologo.png")
        if not px.isNull():
            logo.setPixmap(px.scaled(160, 65, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo.setText("🥭 Hyped Mangoes")
            logo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2b2b2b;")

        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(8)

        for label, icon_path, page_key in [
            ("  TRANSACTIONS", "pos.png",       "pos"),
            ("  INVENTORY",    "inventory.png", "inventory"),
            ("  REPORT",       "reports.png",   "report"),
        ]:
            btn = QPushButton(label)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(18, 18))
            btn.setFixedSize(160, 36)
            btn.setStyleSheet(NAV_BTN_STYLE)
            _key = page_key
            btn.clicked.connect(lambda checked, k=_key: self.switch_callback(k) if self.switch_callback else None)
            drop_shadow(btn, blur=18, alpha=100)
            nav_layout.addWidget(btn)

        top_bar_layout.addWidget(logo)
        top_bar_layout.addStretch()
        top_bar_layout.addLayout(nav_layout)
        top_bar_layout.addStretch()
        root.addWidget(top_bar)

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #c8b87a;")
        root.addWidget(sep)

        # ── CONTENT AREA ─────────────────────────────────────────────────────
        content_area = QWidget()
        content_area.setStyleSheet("background-color: #EFE9D1;")
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(20)
        root.addWidget(content_area, stretch=1)

        # TABLE PANEL
        table_panel = QFrame()
        table_panel.setStyleSheet("QFrame { background-color: white; border-radius: 16px; }")
        drop_shadow(table_panel, blur=30, alpha=120)
        table_panel_layout = QVBoxLayout(table_panel)
        table_panel_layout.setContentsMargins(16, 16, 16, 16)
        table_panel_layout.setSpacing(12)

        panel_title = QLabel("🧂  Ingredients Stock")
        panel_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2b2b2b; background: transparent;"
        )
        table_panel_layout.addWidget(panel_title)

        self.table = DragScrollTable(0, 5)
        self.table.setHorizontalHeaderLabels(["#", "Ingredient Name", "Stock Left", "Unit", "Category"])
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.load_selected_row)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setFrameShape(QFrame.NoFrame)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setDefaultAlignment(Qt.AlignCenter)

        table_panel_layout.addWidget(self.table)
        content_layout.addWidget(table_panel, stretch=3)

        # FORM PANEL
        form_panel = QFrame()
        form_panel.setStyleSheet("QFrame { background-color: #E8D28C; border-radius: 16px; }")
        form_panel.setFixedWidth(280)
        drop_shadow(form_panel, blur=30, alpha=140)
        form_panel_layout = QVBoxLayout(form_panel)
        form_panel_layout.setContentsMargins(20, 20, 20, 20)
        form_panel_layout.setSpacing(10)

        form_title = QLabel("Edit Ingredient")
        form_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2b2b2b; background: transparent;"
        )
        form_title.setAlignment(Qt.AlignCenter)
        form_panel_layout.addWidget(form_title)

        div = QFrame()
        div.setFixedHeight(2)
        div.setStyleSheet("background-color: #c8b87a; border-radius: 1px;")
        form_panel_layout.addWidget(div)
        form_panel_layout.addSpacing(4)

        def field_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(
                "font-size: 12px; font-weight: bold; color: #555; background: transparent;"
                " text-transform: uppercase; letter-spacing: 1px;"
            )
            return lbl

        self.name = QLineEdit()
        self.name.setPlaceholderText("e.g. Fresh Mangoes")
        self.name.setStyleSheet(INPUT_STYLE)

        self.stock = QLineEdit()
        self.stock.setPlaceholderText("e.g. 10")
        self.stock.setValidator(QIntValidator(0, 999999))
        self.stock.setStyleSheet(INPUT_STYLE)

        self.unit = QLineEdit()
        self.unit.setPlaceholderText("e.g. kg, pcs, cones")
        self.unit.setStyleSheet(INPUT_STYLE)

        self.category = QLineEdit()
        self.category.setPlaceholderText("e.g. Fruit")
        self.category.setStyleSheet(INPUT_STYLE)

        form_panel_layout.addWidget(field_label("Ingredient Name"))
        form_panel_layout.addWidget(self.name)
        form_panel_layout.addWidget(field_label("Stock Left"))
        form_panel_layout.addWidget(self.stock)
        form_panel_layout.addWidget(field_label("Unit"))
        form_panel_layout.addWidget(self.unit)
        form_panel_layout.addWidget(field_label("Category"))
        form_panel_layout.addWidget(self.category)
        form_panel_layout.addSpacing(10)

        add_btn = QPushButton("＋  ADD ITEM")
        add_btn.setStyleSheet(GREEN_BTN_STYLE)
        add_btn.setFixedHeight(42)
        add_btn.clicked.connect(self.add_item)
        drop_shadow(add_btn, blur=12, alpha=80)

        update_btn = QPushButton("✎  UPDATE")
        update_btn.setStyleSheet(BLUE_BTN_STYLE)
        update_btn.setFixedHeight(42)
        update_btn.clicked.connect(self.update_item)
        drop_shadow(update_btn, blur=12, alpha=80)

        delete_btn = QPushButton("✕  DELETE")
        delete_btn.setStyleSheet(RED_BTN_STYLE)
        delete_btn.setFixedHeight(42)
        delete_btn.clicked.connect(self.delete_item)
        drop_shadow(delete_btn, blur=12, alpha=80)

        form_panel_layout.addWidget(add_btn)
        form_panel_layout.addWidget(update_btn)
        form_panel_layout.addWidget(delete_btn)
        form_panel_layout.addStretch()

        content_layout.addWidget(form_panel)

    # ── DB FUNCTIONS ──────────────────────────────────────────────────────────

    def load_from_db(self):
        """Load all ingredients from DB into the table."""
        self.table.setRowCount(0)
        self._row_ids = {}
        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute("SELECT id, ingredient_name, stock_left, unit, category FROM ingredients ORDER BY category, ingredient_name")
            rows = cur.fetchall()
            db.close()
            for ingredient in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setRowHeight(row, 40)
                for col, val in enumerate([
                    str(row + 1),
                    ingredient["ingredient_name"],
                    str(ingredient["stock_left"]),
                    ingredient["unit"] or "",
                    ingredient["category"] or "",
                ]):
                    self.table.setItem(row, col, self._make_cell(val))
                self._row_ids[row] = ingredient["id"]
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not load ingredients:\n{err}")

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def _make_cell(self, text, align=Qt.AlignCenter):
        item = QTableWidgetItem(text)
        item.setTextAlignment(align)
        return item

    def update_numbers(self):
        new_ids = {}
        for row in range(self.table.rowCount()):
            self.table.setItem(row, 0, self._make_cell(str(row + 1)))
            if row in self._row_ids:
                new_ids[row] = self._row_ids[row]
        self._row_ids = new_ids

    def add_item(self):
        if not self.name.text() or not self.stock.text():
            QMessageBox.warning(self, "Missing Fields", "Please fill in Ingredient Name and Stock.")
            return
        try:
            db = get_db_connection()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO ingredients (ingredient_name, stock_left, unit, category) VALUES (%s, %s, %s, %s)",
                (self.name.text(), int(self.stock.text()), self.unit.text(), self.category.text())
            )
            new_id = cur.lastrowid
            db.commit()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not add ingredient:\n{err}")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 40)
        for col, val in enumerate(["", self.name.text(), self.stock.text(), self.unit.text(), self.category.text()]):
            self.table.setItem(row, col, self._make_cell(val))
        self._row_ids[row] = new_id
        self.update_numbers()
        self.clear_inputs()

    def load_selected_row(self, row, column):
        self.selected_row = row
        self.name.setText(self.table.item(row, 1).text())
        self.stock.setText(self.table.item(row, 2).text())
        self.unit.setText(self.table.item(row, 3).text())
        self.category.setText(self.table.item(row, 4).text())

    def update_item(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "No Selection", "Select a row first!")
            return
        product_id = self._row_ids.get(self.selected_row)
        if product_id:
            try:
                db = get_db_connection()
                cur = db.cursor()
                cur.execute(
                    "UPDATE ingredients SET ingredient_name=%s, stock_left=%s, unit=%s, category=%s WHERE id=%s",
                    (self.name.text(), int(self.stock.text() or 0), self.unit.text(), self.category.text(), product_id)
                )
                db.commit()
                db.close()
            except Exception as err:
                QMessageBox.critical(self, "DB Error", f"Could not update ingredient:\n{err}")
                return
        for col, val in enumerate(["", self.name.text(), self.stock.text(), self.unit.text(), self.category.text()]):
            self.table.setItem(self.selected_row, col, self._make_cell(val))
        self.update_numbers()
        self.clear_inputs()
        self.selected_row = None

    def delete_item(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "No Selection", "Select a row first!")
            return
        product_id = self._row_ids.get(self.selected_row)
        if product_id:
            reply = QMessageBox.question(
                self, "Confirm Delete", "Delete this ingredient from the database?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
            try:
                db = get_db_connection()
                cur = db.cursor()
                cur.execute("DELETE FROM ingredients WHERE id = %s", (product_id,))
                db.commit()
                db.close()
            except Exception as err:
                QMessageBox.critical(self, "DB Error", f"Could not delete ingredient:\n{err}")
                return
        self.table.removeRow(self.selected_row)
        if self.selected_row in self._row_ids:
            del self._row_ids[self.selected_row]
        self.selected_row = None
        self.update_numbers()
        self.clear_inputs()

    def clear_inputs(self):
        self.name.clear()
        self.stock.clear()
        self.unit.clear()
        self.category.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IngredientsPage()
    window.show()
    sys.exit(app.exec_())