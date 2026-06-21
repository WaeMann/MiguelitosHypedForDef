# This is the ingredients.py (Do not remove line)

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QFrame, QHeaderView, QMessageBox,
    QGraphicsDropShadowEffect, QSizePolicy, QDateEdit
)
from PyQt5.QtGui import QPixmap, QIcon, QIntValidator, QColor, QMouseEvent
from PyQt5.QtCore import Qt, QSize, QEvent, QTimer, QDate
import datetime as _dt
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


class ClockWidget(QWidget):
    """Live time + date label for the top bar (upper-right)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        from PyQt5.QtGui import QFont
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(1)
        self.time_lbl = QLabel()
        self.time_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.time_lbl.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.time_lbl.setStyleSheet("color: #2b2b2b; background: transparent;")
        self.date_lbl = QLabel()
        self.date_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.date_lbl.setFont(QFont("Segoe UI", 9))
        self.date_lbl.setStyleSheet("color: #555555; background: transparent;")
        layout.addWidget(self.time_lbl)
        layout.addWidget(self.date_lbl)
        self._tick()

    def _tick(self):
        now = _dt.datetime.now()
        self.time_lbl.setText(now.strftime("%I:%M:%S %p"))
        self.date_lbl.setText(now.strftime("%A, %b %d, %Y"))
        ms_until_next = 1000 - (now.microsecond // 1000)
        QTimer.singleShot(ms_until_next, self._tick)


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
QLineEdit, QDateEdit {
    background-color: #fafaf7;
    border: 2px solid #d6d2c4;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    color: #2c3e50;
}
QLineEdit:focus, QDateEdit:focus {
    border: 2px solid #34699A;
    background-color: white;
}
QDateEdit::drop-down {
    border: none;
    width: 24px;
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

        self.on_change = None

        self.setStyleSheet("QWidget { background-color: #DED6B2; font-family: 'Segoe UI'; }")

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
            logo.setPixmap(px.scaled(200, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
        clock_widget = ClockWidget()
        top_bar_layout.addWidget(clock_widget)
        top_bar_layout.addSpacing(12)
        self.admin_btn = QPushButton("🚪 LOG OUT")
        self.admin_btn.setFixedSize(130, 36)
        self.admin_btn.setStyleSheet(NAV_BTN_STYLE)
        drop_shadow(self.admin_btn, blur=18, alpha=100)
        self.admin_btn.clicked.connect(self.admin_clicked)
        top_bar_layout.addWidget(self.admin_btn)
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

        self.table = DragScrollTable(0, 6)
        self.table.setHorizontalHeaderLabels(["#", "Ingredient Name", "Stock Left", "Unit", "Category", "Expiry Date (yyyy-mm-dd)"])
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

        self.ef_expiry = QDateEdit()
        self.ef_expiry.setCalendarPopup(True)
        self.ef_expiry.setDisplayFormat("yyyy-MM-dd")
        self.ef_expiry.setDate(QDate.currentDate())
        self.ef_expiry.setStyleSheet(INPUT_STYLE)
        self.ef_expiry.setFixedWidth(130)
        self.ef_expiry.setFixedHeight(36)

        fields_row = QHBoxLayout()
        fields_row.setSpacing(12)
        fields_row.addLayout(ef_col("INGREDIENT NAME", self.ef_name), stretch=1)
        fields_row.addLayout(ef_col("STOCK LEFT",      self.ef_stock))
        fields_row.addLayout(ef_col("UNIT",            self.ef_unit))
        fields_row.addLayout(ef_col("CATEGORY",        self.ef_category))
        fields_row.addLayout(ef_col("EXPIRY DATE",     self.ef_expiry))

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

        self.expiry_date = QDateEdit()
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setDisplayFormat("yyyy-MM-dd")
        self.expiry_date.setDate(QDate.currentDate())
        self.expiry_date.setStyleSheet(INPUT_STYLE)

        form_panel_layout.addWidget(field_label("Ingredient Name"))
        form_panel_layout.addWidget(self.name)
        form_panel_layout.addWidget(field_label("Stock Left"))
        form_panel_layout.addWidget(self.stock)
        form_panel_layout.addWidget(field_label("Unit"))
        form_panel_layout.addWidget(self.unit)
        form_panel_layout.addWidget(field_label("Category"))
        form_panel_layout.addWidget(self.category)
        form_panel_layout.addWidget(field_label("Expiry Date"))
        form_panel_layout.addWidget(self.expiry_date)
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

    def admin_clicked(self):
        reply = QMessageBox.question(
            self, "Log Out",
            "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            QApplication.exit(42)

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

        # Pre-fill expiry date from the table; default to today if blank
        exp_text = self.table.item(row, 5).text() if self.table.item(row, 5) else ""
        if exp_text:
            self.ef_expiry.setDate(QDate.fromString(exp_text, "yyyy-MM-dd"))
        else:
            self.ef_expiry.setDate(QDate.currentDate())

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
        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                "SELECT id, ingredient_name, stock_left, unit, category, expiry_date "
                "FROM ingredients ORDER BY category, ingredient_name"
            )
            rows = cur.fetchall()
            db.close()
            for ingredient in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setRowHeight(row, 40)
                exp_date = str(ingredient["expiry_date"]) if ingredient["expiry_date"] else ""
                for col, val in enumerate([
                    str(row + 1),
                    ingredient["ingredient_name"],
                    str(ingredient["stock_left"]),
                    ingredient["unit"]     or "",
                    ingredient["category"] or "",
                    exp_date,
                ]):
                    self.table.setItem(row, col, self._make_cell(val))
                # Store the DB id on the row itself rather than in a
                # separate row-index → id dict. A dict keyed by row index
                # silently goes stale the moment rows shift (e.g. after a
                # delete), which was causing edits/deletes to target the
                # wrong ingredient.
                self.table.item(row, 0).setData(Qt.UserRole, ingredient["id"])
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not load ingredients:\n{err}")

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def _make_cell(self, text, align=Qt.AlignCenter):
        item = QTableWidgetItem(text)
        item.setTextAlignment(align)
        return item

    def update_numbers(self):
        for row in range(self.table.rowCount()):
            ingredient_id = self._row_ingredient_id(row)
            cell = self._make_cell(str(row + 1))
            cell.setData(Qt.UserRole, ingredient_id)
            self.table.setItem(row, 0, cell)

    def _row_ingredient_id(self, row):
        """Read the DB id stored on a row, instead of trusting a row-index dict."""
        if row is None:
            return None
        item = self.table.item(row, 0)
        return item.data(Qt.UserRole) if item else None

    def _find_row_by_id(self, ingredient_id):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.data(Qt.UserRole) == ingredient_id:
                return row
        return None

    def _select_row(self, row):
        self.table.selectRow(row)
        self._on_row_clicked(row, 0)

    def add_item(self):
        if not self.name.text() or not self.stock.text():
            QMessageBox.warning(self, "Missing Fields", "Please fill in Ingredient Name and Stock.")
            return
        expiry_val = self.expiry_date.date().toString("yyyy-MM-dd")
        try:
            db = get_db_connection()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO ingredients (ingredient_name, stock_left, unit, category, expiry_date) "
                "VALUES (%s, %s, %s, %s, %s)",
                (self.name.text(), int(self.stock.text()), self.unit.text(), self.category.text(), expiry_val)
            )
            new_id = cur.lastrowid
            db.commit()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not add ingredient:\n{err}")
            return

        self.clear_inputs()
        # Reload from DB so row order/numbering stay correct and the
        # inventory + POS windows (which depend on ingredient stock) sync up.
        self.load_from_db()
        row = self._find_row_by_id(new_id)
        if row is not None:
            self._select_row(row)
        if self.on_change:
            self.on_change()

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
        ingredient_id = self._row_ingredient_id(self.selected_row)
        if ingredient_id is None:
            QMessageBox.warning(self, "No Selection", "Select a row first!")
            return
        expiry_val = self.ef_expiry.date().toString("yyyy-MM-dd")
        try:
            db = get_db_connection()
            cur = db.cursor()
            cur.execute(
                "UPDATE ingredients SET ingredient_name=%s, stock_left=%s, "
                "unit=%s, category=%s, expiry_date=%s WHERE id=%s",
                (name, int(stock), self.ef_unit.text(),
                 self.ef_category.text(), expiry_val, ingredient_id)
            )
            db.commit()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not update ingredient:\n{err}")
            return

        self.edit_form.hide()
        # Reload from DB, then re-select the same ingredient (rows can
        # shift since the table re-sorts by category/name) instead of
        # hand-patching cells, which left the action bar showing stale info.
        self.load_from_db()
        row = self._find_row_by_id(ingredient_id)
        if row is not None:
            self._select_row(row)
        if self.on_change:
            self.on_change()

    def delete_item(self):
        if self.selected_row is None:
            return
        ingredient_id = self._row_ingredient_id(self.selected_row)
        name = (self.table.item(self.selected_row, 1).text()
                if self.table.item(self.selected_row, 1) else "this item")
        if ingredient_id is None:
            QMessageBox.warning(self, "No Selection", "Select a row first!")
            return
        if QMessageBox.question(
            self, "Confirm Delete",
            f"Delete '{name}' from the database?\n\n"
            "This will also remove it from any menu items it's linked to.",
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
        try:
            db = get_db_connection()
            cur = db.cursor()
            cur.execute("DELETE FROM ingredients WHERE id = %s", (ingredient_id,))
            db.commit()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not delete ingredient:\n{err}")
            return
        self.selected_row = None
        self.action_bar.hide()
        self.edit_form.hide()
        # Reload from DB instead of manually removing the row and shifting
        # the id-tracking dict — that manual shift was the root cause of
        # edits/deletes silently targeting the wrong ingredient afterward.
        self.load_from_db()
        if self.on_change:
            self.on_change()

    def clear_inputs(self):
        self.name.clear()
        self.stock.clear()
        self.unit.clear()
        self.category.clear()
        self.expiry_date.setDate(QDate.currentDate())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IngredientsPage()
    window.show()
    sys.exit(app.exec_())