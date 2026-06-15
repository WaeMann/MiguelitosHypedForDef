# This is the ingredients.py (Do not remove line)

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QFrame, QHeaderView, QMessageBox,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QIcon, QIntValidator, QColor, QMouseEvent
from PyQt5.QtCore import Qt, QSize, QEvent
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
        self.selected_row = None
        self._row_ids = {}   # table row index → DB id

        self.setStyleSheet("QWidget { background-color: #DED6B2; font-family: 'Segoe UI'; }")
        # Prevent this page's sizeHint from driving the parent window's size.
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
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
            ("🛒 TRANSACTIONS", "pos.png",       "pos"),
            ("📋 REPORT",       "reports.png",   "report"),
            ("📦 INVENTORY", "inventory.png", "inventory"),
        ]:
            btn = QPushButton(label)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(18, 18))
            btn.setFixedSize(170, 36)
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

        # ── TABLE SIDE (left) ─────────────────────────────────────────────────
        table_side = QWidget()
        table_side.setStyleSheet("background: transparent;")
        table_side.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table_side_layout = QVBoxLayout(table_side)
        table_side_layout.setContentsMargins(0, 0, 0, 0)
        table_side_layout.setSpacing(10)
        content_layout.addWidget(table_side, stretch=3)

        # TABLE PANEL
        table_panel = QFrame()
        table_panel.setStyleSheet("QFrame { background-color: white; border-radius: 16px; }")
        drop_shadow(table_panel, blur=30, alpha=120)
        table_panel.setMinimumHeight(0)   # allow panel to compress when action_bar/edit_form appear
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
        self.table.cellClicked.connect(self._on_row_clicked)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setFrameShape(QFrame.NoFrame)
        self.table.setMinimumHeight(0)   # let table compress; it scrolls internally

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setDefaultAlignment(Qt.AlignCenter)

        table_panel_layout.addWidget(self.table)
        table_side_layout.addWidget(table_panel, stretch=1)

        # ── HIDDEN ACTION BAR ─────────────────────────────────────────────────
        self.action_bar = QFrame()
        self.action_bar.setFixedHeight(80)
        self.action_bar.setStyleSheet("""
            QFrame { background-color: #DED6B2; border-radius: 12px; }
        """)
        drop_shadow(self.action_bar, blur=20, alpha=130)

        ab_layout = QHBoxLayout(self.action_bar)
        ab_layout.setContentsMargins(18, 0, 18, 0)
        ab_layout.setSpacing(14)

        self.action_info = QLabel("No item selected")
        self.action_info.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #2b2b2b; background: transparent;"
        )
        self.action_info.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        ab_layout.addWidget(self.action_info)

        self.edit_btn = QPushButton("✎  Edit")
        self.edit_btn.setFixedSize(110, 40)
        self.edit_btn.setStyleSheet(BLUE_BTN_STYLE)
        self.edit_btn.clicked.connect(self._toggle_edit_form)
        drop_shadow(self.edit_btn, blur=10, alpha=80)
        ab_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("✕  Delete")
        self.delete_btn.setFixedSize(110, 40)
        self.delete_btn.setStyleSheet(RED_BTN_STYLE)
        self.delete_btn.clicked.connect(self.delete_item)
        drop_shadow(self.delete_btn, blur=10, alpha=80)
        ab_layout.addWidget(self.delete_btn)

        table_side_layout.addWidget(self.action_bar)
        self.action_bar.hide()

        # ── HIDDEN INLINE EDIT FORM ───────────────────────────────────────────
        from PyQt5.QtGui import QFont
        self.edit_form = QFrame()
        self.edit_form.setStyleSheet("""
            QFrame { background-color: #E8D28C; border-radius: 12px; }
        """)
        drop_shadow(self.edit_form, blur=18, alpha=110)

        ef_layout = QVBoxLayout(self.edit_form)
        ef_layout.setContentsMargins(18, 14, 18, 14)
        ef_layout.setSpacing(10)

        ef_title = QLabel("Edit Ingredient")
        ef_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        ef_title.setStyleSheet("color: #2b2b2b; background: transparent;")
        ef_layout.addWidget(ef_title)

        ef_sep = QFrame()
        ef_sep.setFixedHeight(2)
        ef_sep.setStyleSheet("background-color: #c8b87a;")
        ef_layout.addWidget(ef_sep)

        def ef_col(label_text, widget):
            col = QVBoxLayout()
            col.setSpacing(4)
            lbl = QLabel(label_text)
            lbl.setStyleSheet(
                "font-size: 11px; font-weight: bold; color: #555; background: transparent;"
            )
            col.addWidget(lbl)
            col.addWidget(widget)
            return col

        self.ef_name = QLineEdit()
        self.ef_name.setPlaceholderText("Ingredient name")
        self.ef_name.setStyleSheet(INPUT_STYLE)
        self.ef_name.setFixedHeight(36)

        self.ef_stock = QLineEdit()
        self.ef_stock.setPlaceholderText("Stock")
        self.ef_stock.setValidator(QIntValidator(0, 999999))
        self.ef_stock.setStyleSheet(INPUT_STYLE)
        self.ef_stock.setFixedWidth(100)
        self.ef_stock.setFixedHeight(36)

        self.ef_unit = QLineEdit()
        self.ef_unit.setPlaceholderText("Unit")
        self.ef_unit.setStyleSheet(INPUT_STYLE)
        self.ef_unit.setFixedWidth(120)
        self.ef_unit.setFixedHeight(36)

        self.ef_category = QLineEdit()
        self.ef_category.setPlaceholderText("Category")
        self.ef_category.setStyleSheet(INPUT_STYLE)
        self.ef_category.setFixedWidth(150)
        self.ef_category.setFixedHeight(36)

        fields_row = QHBoxLayout()
        fields_row.setSpacing(12)
        fields_row.addLayout(ef_col("INGREDIENT NAME", self.ef_name), stretch=1)
        fields_row.addLayout(ef_col("STOCK LEFT",      self.ef_stock))
        fields_row.addLayout(ef_col("UNIT",            self.ef_unit))
        fields_row.addLayout(ef_col("CATEGORY",        self.ef_category))

        save_ef = QPushButton("✔  Save")
        save_ef.setFixedSize(120, 36)
        save_ef.setStyleSheet(GREEN_BTN_STYLE)
        save_ef.clicked.connect(self.update_item)
        drop_shadow(save_ef, blur=8, alpha=80)

        cancel_ef = QPushButton("Cancel")
        cancel_ef.setFixedSize(90, 36)
        cancel_ef.setStyleSheet(BLUE_BTN_STYLE)
        cancel_ef.clicked.connect(self.edit_form.hide)
        drop_shadow(cancel_ef, blur=8, alpha=80)

        btn_row = QHBoxLayout()
        btn_row.addLayout(fields_row, stretch=1)
        btn_row.addSpacing(10)
        btn_row.addWidget(save_ef,   alignment=Qt.AlignBottom)
        btn_row.addWidget(cancel_ef, alignment=Qt.AlignBottom)

        ef_layout.addLayout(btn_row)

        table_side_layout.addWidget(self.edit_form)
        self.edit_form.hide()

        # ── FORM PANEL (right side — Add Item only) ───────────────────────────
        form_panel = QFrame()
        form_panel.setStyleSheet("QFrame { background-color: #E8D28C; border-radius: 16px; }")
        form_panel.setFixedWidth(280)
        drop_shadow(form_panel, blur=30, alpha=140)
        form_panel_layout = QVBoxLayout(form_panel)
        form_panel_layout.setContentsMargins(20, 20, 20, 20)
        form_panel_layout.setSpacing(10)

        form_title = QLabel("Add Ingredient")
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

        form_panel_layout.addWidget(add_btn)
        form_panel_layout.addStretch()

        content_layout.addWidget(form_panel)

        # event filter — hide action bar / edit form when clicking outside
        self.table.viewport().installEventFilter(self)
        self.installEventFilter(self)

    # ── auto-refresh on page show ─────────────────────────────────────────────

    def showEvent(self, event):
        """Reload from DB every time this page becomes visible."""
        super().showEvent(event)
        self.action_bar.hide()
        self.edit_form.hide()
        self.selected_row = None
        self.load_from_db()

    # ── event filter ──────────────────────────────────────────────────────────

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            from PyQt5.QtWidgets import QApplication as _App
            w = _App.widgetAt(event.globalPos())
            in_bar   = self.action_bar.isAncestorOf(w)  if w else False
            in_form  = self.edit_form.isAncestorOf(w)   if w else False
            in_table = (self.table.viewport() is w or self.table.isAncestorOf(w)) if w else False
            if not (in_bar or in_form or in_table):
                self.action_bar.hide()
                self.edit_form.hide()
                self.table.clearSelection()
                self.selected_row = None
        return super().eventFilter(obj, event)

    # ── row click → show action bar ───────────────────────────────────────────

    def _on_row_clicked(self, row, column):
        self.selected_row = row
        name  = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
        stock = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
        self.action_info.setText(f"Selected:  {name}   |   Stock: {stock}")
        self.action_bar.show()

        # Pre-fill edit form fields but keep the form hidden until Edit is pressed
        self.ef_name.setText(name)
        self.ef_stock.setText(stock)
        self.ef_unit.setText(    self.table.item(row, 3).text() if self.table.item(row, 3) else "")
        self.ef_category.setText(self.table.item(row, 4).text() if self.table.item(row, 4) else "")

    # ── toggle edit form ──────────────────────────────────────────────────────

    def _toggle_edit_form(self):
        if self.edit_form.isVisible():
            self.edit_form.hide()
        else:
            self.edit_form.show()

    # ── DB FUNCTIONS ──────────────────────────────────────────────────────────

    def load_from_db(self):
        """Load all ingredients from DB into the table."""
        self.table.setRowCount(0)
        self._row_ids = {}
        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                "SELECT id, ingredient_name, stock_left, unit, category "
                "FROM ingredients ORDER BY category, ingredient_name"
            )
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
                    ingredient["unit"]     or "",
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
                "INSERT INTO ingredients (ingredient_name, stock_left, unit, category) "
                "VALUES (%s, %s, %s, %s)",
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
        for col, val in enumerate(["", self.name.text(), self.stock.text(),
                                   self.unit.text(), self.category.text()]):
            self.table.setItem(row, col, self._make_cell(val))
        self._row_ids[row] = new_id
        self.update_numbers()
        self.clear_inputs()

    # kept for any external callers
    def load_selected_row(self, row, column):
        self._on_row_clicked(row, column)

    def update_item(self):
        """Save edits from the inline edit form."""
        if self.selected_row is None:
            QMessageBox.warning(self, "No Selection", "Select a row first!")
            return
        name  = self.ef_name.text().strip()
        stock = self.ef_stock.text().strip()
        if not name or not stock:
            QMessageBox.warning(self, "Missing Fields",
                                "Please fill in Ingredient Name and Stock.")
            return
        ingredient_id = self._row_ids.get(self.selected_row)
        if ingredient_id:
            try:
                db = get_db_connection()
                cur = db.cursor()
                cur.execute(
                    "UPDATE ingredients SET ingredient_name=%s, stock_left=%s, "
                    "unit=%s, category=%s WHERE id=%s",
                    (name, int(stock), self.ef_unit.text(),
                     self.ef_category.text(), ingredient_id)
                )
                db.commit()
                db.close()
            except Exception as err:
                QMessageBox.critical(self, "DB Error", f"Could not update ingredient:\n{err}")
                return

        for col, val in enumerate(["", name, stock,
                                   self.ef_unit.text(), self.ef_category.text()]):
            self.table.setItem(self.selected_row, col, self._make_cell(val))
        self.update_numbers()
        self.action_info.setText(f"Selected:  {name}   |   Stock: {stock}")
        self.edit_form.hide()

    def delete_item(self):
        if self.selected_row is None:
            return
        ingredient_id = self._row_ids.get(self.selected_row)
        name = (self.table.item(self.selected_row, 1).text()
                if self.table.item(self.selected_row, 1) else "this item")
        if QMessageBox.question(
            self, "Confirm Delete", f"Delete '{name}' from the database?",
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
        if ingredient_id:
            try:
                db = get_db_connection()
                cur = db.cursor()
                cur.execute("DELETE FROM ingredients WHERE id = %s", (ingredient_id,))
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
        self.action_bar.hide()
        self.edit_form.hide()

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