# This is the inventory.py (Do not remove line)

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QFrame, QHeaderView, QMessageBox,
    QGraphicsDropShadowEffect, QSizePolicy, QFileDialog,
    QDialog, QScrollArea, QDoubleSpinBox, QComboBox,
)
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt, QSize, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QIntValidator, QColor, QFont

from db import get_db_connection


# ── helpers ───────────────────────────────────────────────────────────────────

def drop_shadow(widget, blur=25, x=3, y=3, alpha=150):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setXOffset(x)
    fx.setYOffset(y)
    fx.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(fx)
    return fx


def load_sizes_from_db():
    """Return a list of size_name strings from the sizes table."""
    sizes = []
    try:
        db = get_db_connection()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT size_name FROM sizes ORDER BY multiplier")
        sizes = [r["size_name"] for r in cur.fetchall()]
        db.close()
    except Exception as err:
        print(f"[DB] Could not load sizes: {err}")
    return sizes or ["12oz", "16oz"]


# ── styles ────────────────────────────────────────────────────────────────────

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

AMBER_BTN_STYLE = """
QPushButton {
    background-color: #b87c0e;
    color: white;
    font-size: 14px;
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: bold;
    border: none;
}
QPushButton:hover { background-color: #9a680b; }
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

COMBO_STYLE = """
QComboBox {
    background-color: #fafaf7;
    border: 2px solid #d6d2c4;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 13px;
    color: #2c3e50;
    min-height: 20px;
}
QComboBox:focus {
    border: 2px solid #34699A;
    background-color: white;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background: white;
    border: 1px solid #d6d2c4;
    border-radius: 6px;
    selection-background-color: #d4e6f7;
    selection-color: #2c3e50;
    font-size: 13px;
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

SPIN_STYLE = """
QDoubleSpinBox {
    background: white;
    border: 1px solid #d6d2c4;
    border-radius: 6px;
    padding: 4px 6px;
    font-size: 13px;
    color: #2c3e50;
}
QDoubleSpinBox:focus { border: 1px solid #34699A; }
"""

MANAGE_COMBO_STYLE = """
QComboBox {
    background-color: white;
    border: 2px solid #d6d2c4;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 13px;
    color: #2c3e50;
}
QComboBox:focus { border: 2px solid #34699A; }
QComboBox QAbstractItemView {
    background: white;
    selection-background-color: #d4e6f7;
    selection-color: #2c3e50;
}
"""


# ─────────────────────────────────────────────────────────────────────────────
#  Manage Ingredients Dialog
# ─────────────────────────────────────────────────────────────────────────────

class ManageIngredientsDialog(QDialog):
    def __init__(self, product_id: int, product_name: str, parent=None):
        super().__init__(parent)
        self.product_id   = product_id
        self.product_name = product_name

        self.setWindowTitle(f"Manage Ingredients — {product_name}")
        self.setMinimumSize(680, 540)
        self.setStyleSheet("QDialog { background-color: #EFE9D1; } QLabel { color: #2b2b2b; }")
        self._build()
        self._load_linked()
        self._center()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet("background-color: #DED6B2;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(22, 0, 22, 0)

        title = QLabel(f"📦  {self.product_name}")
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color: #2b2b2b; background: transparent;")
        hl.addWidget(title)
        hl.addStretch()

        sub = QLabel("Ingredient Links")
        sub.setStyleSheet("color: #888; font-size: 12px; background: transparent;")
        hl.addWidget(sub)
        root.addWidget(header)

        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #c8b87a;")
        root.addWidget(sep)

        body = QWidget()
        body.setStyleSheet("background-color: #EFE9D1;")
        bl = QHBoxLayout(body)
        bl.setContentsMargins(20, 16, 20, 16)
        bl.setSpacing(16)
        root.addWidget(body, stretch=1)

        left = QFrame()
        left.setStyleSheet("QFrame { background-color: white; border-radius: 14px; }")
        drop_shadow(left, blur=20, alpha=100)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(14, 14, 14, 14)
        ll.setSpacing(8)

        lhead = QLabel("Linked Ingredients")
        lhead.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lhead.setStyleSheet("color: #2b2b2b; background: transparent;")
        ll.addWidget(lhead)

        divl = QFrame()
        divl.setFixedHeight(1)
        divl.setStyleSheet("background-color: #ede9dc;")
        ll.addWidget(divl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #EFE9D1; width: 7px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #c8b87a; border-radius: 3px; }
        """)
        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 4, 0)
        self._list_layout.setSpacing(6)
        self._list_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self._list_widget)
        ll.addWidget(scroll, stretch=1)
        bl.addWidget(left, stretch=3)

        right = QFrame()
        right.setStyleSheet("QFrame { background-color: #E8D28C; border-radius: 14px; }")
        right.setFixedWidth(230)
        drop_shadow(right, blur=20, alpha=120)
        rl = QVBoxLayout(right)
        rl.setContentsMargins(16, 16, 16, 16)
        rl.setSpacing(10)

        rt = QLabel("Add Ingredient")
        rt.setFont(QFont("Segoe UI", 13, QFont.Bold))
        rt.setStyleSheet("color: #2b2b2b; background: transparent;")
        rt.setAlignment(Qt.AlignCenter)
        rl.addWidget(rt)

        divr = QFrame()
        divr.setFixedHeight(2)
        divr.setStyleSheet("background-color: #c8b87a;")
        rl.addWidget(divr)
        rl.addSpacing(4)

        def flbl(t):
            l = QLabel(t)
            l.setStyleSheet(
                "font-size: 11px; font-weight: bold; color: #555; background: transparent;"
            )
            return l

        rl.addWidget(flbl("INGREDIENT"))
        self._combo = QComboBox()
        self._combo.setStyleSheet(MANAGE_COMBO_STYLE)
        rl.addWidget(self._combo)

        rl.addWidget(flbl("AMOUNT USED (per order)"))
        self._spin = QDoubleSpinBox()
        self._spin.setRange(0.001, 99999)
        self._spin.setDecimals(3)
        self._spin.setValue(1.0)
        self._spin.setSingleStep(0.5)
        self._spin.setStyleSheet(SPIN_STYLE)
        rl.addWidget(self._spin)

        rl.addStretch()

        link_btn = QPushButton("＋  Link Ingredient")
        link_btn.setStyleSheet(GREEN_BTN_STYLE)
        link_btn.setFixedHeight(40)
        link_btn.clicked.connect(self._add_link)
        drop_shadow(link_btn, blur=10, alpha=80)
        rl.addWidget(link_btn)

        bl.addWidget(right)

        footer = QFrame()
        footer.setFixedHeight(60)
        footer.setStyleSheet("background-color: #DED6B2;")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(20, 0, 20, 0)
        fl.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedSize(110, 36)
        close_btn.setStyleSheet(BLUE_BTN_STYLE)
        close_btn.clicked.connect(self.accept)
        fl.addWidget(close_btn)
        root.addWidget(footer)

        self._fill_combo()

    def _fill_combo(self):
        self._combo.clear()
        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                "SELECT id, ingredient_name, unit FROM ingredients ORDER BY ingredient_name"
            )
            for r in cur.fetchall():
                label = f"{r['ingredient_name']}  ({r['unit'] or '—'})"
                self._combo.addItem(label, userData=r["id"])
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not load ingredients:\n{err}")

    def _load_linked(self):
        for i in reversed(range(self._list_layout.count())):
            w = self._list_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute("""
                SELECT pi.id AS link_id,
                       i.ingredient_name, i.unit,
                       pi.amount_used
                FROM product_ingredients pi
                JOIN ingredients i ON pi.ingredient_id = i.id
                WHERE pi.product_id = %s
                ORDER BY i.ingredient_name
            """, (self.product_id,))
            rows = cur.fetchall()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not load links:\n{err}")
            return

        if not rows:
            empty = QLabel("No ingredients linked yet.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                "color: #aaa; font-size: 13px; background: transparent; padding: 24px;"
            )
            self._list_layout.addWidget(empty)
            return

        for row in rows:
            self._make_row_card(row)

    def _make_row_card(self, row):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #fafaf7;
                border-radius: 8px;
                border: 1px solid #ede9dc;
            }
        """)
        cl = QHBoxLayout(card)
        cl.setContentsMargins(10, 6, 10, 6)
        cl.setSpacing(8)

        dot = QLabel("●")
        dot.setStyleSheet("color: #34699A; font-size: 16px; background: transparent;")
        dot.setFixedWidth(18)
        cl.addWidget(dot)

        name_lbl = QLabel(
            f"{row['ingredient_name']}"
            f"  <span style='color:#bbb; font-size:11px;'>({row['unit'] or '—'})</span>"
        )
        name_lbl.setTextFormat(Qt.RichText)
        name_lbl.setStyleSheet("font-size: 13px; color: #2c3e50; background: transparent;")
        name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        cl.addWidget(name_lbl)

        spin = QDoubleSpinBox()
        spin.setRange(0.001, 99999)
        spin.setDecimals(3)
        spin.setValue(float(row["amount_used"]))
        spin.setSingleStep(0.5)
        spin.setFixedWidth(95)
        spin.setStyleSheet(SPIN_STYLE)
        cl.addWidget(spin)

        save_btn = QPushButton("✔")
        save_btn.setFixedSize(30, 30)
        save_btn.setToolTip("Save amount")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e7f3f; color: white;
                border-radius: 6px; font-size: 13px; border: none;
            }
            QPushButton:hover { background-color: #166330; }
        """)
        _lid = row["link_id"]
        save_btn.clicked.connect(lambda _, lid=_lid, s=spin: self._save_amount(lid, s.value()))
        cl.addWidget(save_btn)

        rem_btn = QPushButton("✕")
        rem_btn.setFixedSize(30, 30)
        rem_btn.setToolTip("Remove link")
        rem_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b; color: white;
                border-radius: 6px; font-size: 13px; border: none;
            }
            QPushButton:hover { background-color: #a93226; }
        """)
        rem_btn.clicked.connect(lambda _, lid=_lid: self._remove_link(lid))
        cl.addWidget(rem_btn)

        self._list_layout.addWidget(card)

    def _add_link(self):
        idx = self._combo.currentIndex()
        if idx < 0:
            return
        ingredient_id = self._combo.itemData(idx)
        amount = self._spin.value()
        try:
            db = get_db_connection()
            cur = db.cursor()
            cur.execute("""
                INSERT INTO product_ingredients (product_id, ingredient_id, amount_used)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE amount_used = VALUES(amount_used)
            """, (self.product_id, ingredient_id, amount))
            db.commit()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not link ingredient:\n{err}")
            return
        self._load_linked()

    def _save_amount(self, link_id: int, value: float):
        try:
            db = get_db_connection()
            cur = db.cursor()
            cur.execute(
                "UPDATE product_ingredients SET amount_used = %s WHERE id = %s",
                (value, link_id)
            )
            db.commit()
            db.close()
            QMessageBox.information(self, "Saved", "Amount updated.")
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not update amount:\n{err}")

    def _remove_link(self, link_id: int):
        if QMessageBox.question(
            self, "Remove", "Remove this ingredient link?",
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
        try:
            db = get_db_connection()
            cur = db.cursor()
            cur.execute("DELETE FROM product_ingredients WHERE id = %s", (link_id,))
            db.commit()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not remove link:\n{err}")
            return
        self._load_linked()

    def _center(self):
        if self.parent():
            pg = self.parent().window().geometry()
            self.move(
                pg.x() + (pg.width()  - self.width())  // 2,
                pg.y() + (pg.height() - self.height()) // 2,
            )


# ─────────────────────────────────────────────────────────────────────────────
#  Inventory Page
# ─────────────────────────────────────────────────────────────────────────────

class InventoryPage(QWidget):
    def __init__(self, switch_callback=None):
        super().__init__()
        self.switch_callback = switch_callback
        self.setWindowTitle("Hyped Mangoes — Inventory")
        self.selected_row = None
        self._row_ids = {}

        # Callback wired by main.py to notify other pages when data changes.
        self.on_change = None

        # Load sizes once for use in both forms
        self._sizes = load_sizes_from_db()

        self.setStyleSheet("QWidget { background-color: #DED6B2; font-family: 'Segoe UI'; }")
        # Prevent this page's sizeHint from driving the parent window's size.
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.initUI()
        self.load_from_db()

    # ── UI ────────────────────────────────────────────────────────────────────

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

        pos_btn = QPushButton("TRANSACTIONS")
        pos_btn.setIcon(QIcon("pos.png"))
        pos_btn.setIconSize(QSize(18, 18))
        pos_btn.setFixedSize(160, 36)
        pos_btn.setStyleSheet(NAV_BTN_STYLE)
        pos_btn.clicked.connect(lambda: self.switch_callback("pos") if self.switch_callback else None)
        drop_shadow(pos_btn, blur=18, alpha=100)

        reports_btn = QPushButton("REPORT")
        reports_btn.setIcon(QIcon("report.png"))
        reports_btn.setIconSize(QSize(18, 18))
        reports_btn.setFixedSize(130, 36)
        reports_btn.setStyleSheet(NAV_BTN_STYLE)
        reports_btn.clicked.connect(lambda: self.switch_callback("report") if self.switch_callback else None)
        drop_shadow(reports_btn, blur=18, alpha=100)

        ingredients_btn = QPushButton("INGREDIENTS")
        ingredients_btn.setIcon(QIcon("ingredients.png"))
        ingredients_btn.setIconSize(QSize(18, 18))
        ingredients_btn.setFixedSize(150, 36)
        ingredients_btn.setStyleSheet(NAV_BTN_STYLE)
        ingredients_btn.clicked.connect(lambda: self.switch_callback("ingredients") if self.switch_callback else None)
        drop_shadow(ingredients_btn, blur=18, alpha=100)

        nav_layout.addWidget(pos_btn)
        nav_layout.addWidget(reports_btn)
        nav_layout.addWidget(ingredients_btn)

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

        # Table panel
        table_panel = QFrame()
        table_panel.setStyleSheet("QFrame { background-color: white; border-radius: 16px; }")
        drop_shadow(table_panel, blur=30, alpha=120)
        table_panel.setMinimumHeight(0)   # allow panel to compress when action_bar/edit_form appear
        table_panel_layout = QVBoxLayout(table_panel)
        table_panel_layout.setContentsMargins(16, 16, 16, 16)
        table_panel_layout.setSpacing(12)

        panel_title = QLabel("📦  Product Inventory")
        panel_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2b2b2b; background: transparent;"
        )
        table_panel_layout.addWidget(panel_title)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["#", "Product Name", "Price", "Qty Left", "Available Sizes", "Category", "Image Path"]
        )
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
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignCenter)
        self.table.setRowHeight(0, 40)

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
        self.edit_btn.clicked.connect(self._toggle_form)
        drop_shadow(self.edit_btn, blur=10, alpha=80)
        ab_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("✕  Delete")
        self.delete_btn.setFixedSize(110, 40)
        self.delete_btn.setStyleSheet(RED_BTN_STYLE)
        self.delete_btn.clicked.connect(self.delete_item)
        drop_shadow(self.delete_btn, blur=10, alpha=80)
        ab_layout.addWidget(self.delete_btn)

        self.manage_btn = QPushButton("⚙  Manage")
        self.manage_btn.setFixedSize(120, 40)
        self.manage_btn.setStyleSheet(AMBER_BTN_STYLE)
        self.manage_btn.clicked.connect(self._open_manage)
        drop_shadow(self.manage_btn, blur=10, alpha=80)
        ab_layout.addWidget(self.manage_btn)

        table_side_layout.addWidget(self.action_bar)
        self.action_bar.hide()

        # ── HIDDEN INLINE EDIT FORM ───────────────────────────────────────────
        self.edit_form = QFrame()
        self.edit_form.setStyleSheet("""
            QFrame { background-color: #E8D28C; border-radius: 12px; }
        """)
        drop_shadow(self.edit_form, blur=18, alpha=110)

        ef_layout = QVBoxLayout(self.edit_form)
        ef_layout.setContentsMargins(18, 14, 18, 14)
        ef_layout.setSpacing(10)

        ef_title = QLabel("Edit Product")
        ef_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        ef_title.setStyleSheet("color: #2b2b2b; background: transparent;")
        ef_layout.addWidget(ef_title)

        ef_sep = QFrame()
        ef_sep.setFixedHeight(2)
        ef_sep.setStyleSheet("background-color: #c8b87a;")
        ef_layout.addWidget(ef_sep)

        fields_row = QHBoxLayout()
        fields_row.setSpacing(12)

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
        self.ef_name.setPlaceholderText("Product name")
        self.ef_name.setStyleSheet(INPUT_STYLE)
        self.ef_name.setFixedHeight(36)

        self.ef_price = QLineEdit()
        self.ef_price.setPlaceholderText("Price")
        self.ef_price.setValidator(QIntValidator(0, 999999))
        self.ef_price.setStyleSheet(INPUT_STYLE)
        self.ef_price.setFixedWidth(90)
        self.ef_price.setFixedHeight(36)

        self.ef_qty = QLineEdit()
        self.ef_qty.setPlaceholderText("Qty")
        self.ef_qty.setValidator(QIntValidator(0, 999999))
        self.ef_qty.setStyleSheet(INPUT_STYLE)
        self.ef_qty.setFixedWidth(90)
        self.ef_qty.setFixedHeight(36)

        # ── Sizes dropdown (edit form) ────────────────────────────────────────
        self.ef_sizes = QComboBox()
        self.ef_sizes.addItems(self._sizes)
        self.ef_sizes.setStyleSheet(COMBO_STYLE)
        self.ef_sizes.setFixedWidth(130)
        self.ef_sizes.setFixedHeight(36)

        self.ef_category = QLineEdit()
        self.ef_category.setPlaceholderText("Category")
        self.ef_category.setStyleSheet(INPUT_STYLE)
        self.ef_category.setFixedWidth(140)
        self.ef_category.setFixedHeight(36)

        self.ef_image = QLineEdit()
        self.ef_image.setPlaceholderText("Image path")
        self.ef_image.setStyleSheet(INPUT_STYLE)
        self.ef_image.setFixedHeight(36)
        self.ef_image.textChanged.connect(self._update_image_preview)

        browse_ef = QPushButton("📁")
        browse_ef.setFixedSize(36, 36)
        browse_ef.setToolTip("Browse image")
        browse_ef.setStyleSheet(BLUE_BTN_STYLE)
        browse_ef.clicked.connect(self._browse_image_ef)

        img_col = QVBoxLayout()
        img_col.setSpacing(4)
        img_lbl = QLabel("IMAGE PATH")
        img_lbl.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #555; background: transparent;"
        )
        img_row2 = QHBoxLayout()
        img_row2.setSpacing(4)
        img_row2.addWidget(self.ef_image)
        img_row2.addWidget(browse_ef)
        img_col.addWidget(img_lbl)
        img_col.addLayout(img_row2)

        fields_row.addLayout(ef_col("PRODUCT NAME", self.ef_name), stretch=1)
        fields_row.addLayout(ef_col("PRICE", self.ef_price))
        fields_row.addLayout(ef_col("QTY", self.ef_qty))
        fields_row.addLayout(ef_col("SIZES",        self.ef_sizes))
        fields_row.addLayout(ef_col("CATEGORY",     self.ef_category))
        fields_row.addLayout(img_col, stretch=1)

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

        # ── FORM PANEL (right side — Add Item) ───────────────────────────────
        form_panel = QFrame()
        form_panel.setStyleSheet("QFrame { background-color: #E8D28C; border-radius: 16px; }")
        form_panel.setFixedWidth(280)
        drop_shadow(form_panel, blur=30, alpha=140)
        form_panel_layout = QVBoxLayout(form_panel)
        form_panel_layout.setContentsMargins(20, 20, 20, 20)
        form_panel_layout.setSpacing(10)

        form_title = QLabel("Add Item")
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

        self.name     = QLineEdit()
        self.name.setPlaceholderText("e.g. Mango Ice Cream")
        self.name.setStyleSheet(INPUT_STYLE)

        self.price = QLineEdit()
        self.price.setPlaceholderText("e.g. 99.00")
        self.price.setStyleSheet(INPUT_STYLE)
        self.price.setValidator(QDoubleValidator(0.0, 999999.0, 2))

        self.quantity = QLineEdit()
        self.quantity.setPlaceholderText("e.g. 50")
        self.quantity.setValidator(QIntValidator(0, 999999))
        self.quantity.setStyleSheet(INPUT_STYLE)

        # ── Sizes dropdown (add form) ─────────────────────────────────────────
        self.expiry = QComboBox()
        self.expiry.addItems(self._sizes)
        self.expiry.setStyleSheet(COMBO_STYLE)

        self.type = QLineEdit()
        self.type.setPlaceholderText("e.g. Desserts")
        self.type.setStyleSheet(INPUT_STYLE)

        self.image_path = QLineEdit()
        self.image_path.setPlaceholderText("e.g. images/product.png")
        self.image_path.setStyleSheet(INPUT_STYLE)
        self.image_path.textChanged.connect(self._update_add_preview)

        browse_btn = QPushButton("📁  Browse…")
        browse_btn.setStyleSheet(BLUE_BTN_STYLE)
        browse_btn.setFixedHeight(36)
        browse_btn.clicked.connect(self._browse_image)
        drop_shadow(browse_btn, blur=8, alpha=60)

        self.img_preview = QLabel()
        self.img_preview.setFixedSize(120, 90)
        self.img_preview.setAlignment(Qt.AlignCenter)
        self.img_preview.setStyleSheet(
            "background-color: white; border-radius: 8px;"
            " border: 1px solid #d6d2c4; color: #aaa; font-size: 11px;"
        )
        self.img_preview.setText("No Image")

        form_panel_layout.addWidget(field_label("Product Name"))
        form_panel_layout.addWidget(self.name)
        form_panel_layout.addWidget(field_label("Price"))
        form_panel_layout.addWidget(self.price)
        form_panel_layout.addWidget(field_label("Quantity Left"))
        form_panel_layout.addWidget(self.quantity)
        form_panel_layout.addWidget(field_label("Available Sizes"))
        form_panel_layout.addWidget(self.expiry)
        form_panel_layout.addWidget(field_label("Category"))
        form_panel_layout.addWidget(self.type)
        form_panel_layout.addWidget(field_label("Image Path / URL"))
        form_panel_layout.addWidget(self.image_path)
        form_panel_layout.addWidget(browse_btn)

        preview_row = QHBoxLayout()
        preview_row.addStretch()
        preview_row.addWidget(self.img_preview)
        preview_row.addStretch()
        form_panel_layout.addLayout(preview_row)
        form_panel_layout.addSpacing(6)

        add_btn = QPushButton("＋  ADD ITEM")
        add_btn.setStyleSheet(GREEN_BTN_STYLE)
        add_btn.setFixedHeight(42)
        add_btn.clicked.connect(self.add_item)
        drop_shadow(add_btn, blur=12, alpha=80)

        form_panel_layout.addWidget(add_btn)
        form_panel_layout.addStretch()
        content_layout.addWidget(form_panel)

        self.table.viewport().installEventFilter(self)
        self.installEventFilter(self)

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
        name = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
        self.ef_price.setText(
            self.table.item(row, 2).text() if self.table.item(row, 2) else "0"
        )
        qty  = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
        self.action_info.setText(f"Selected:  {name}   |   Qty: {qty}")
        self.action_bar.show()

        # Pre-fill edit form
        self.ef_name.setText(name)
        self.ef_qty.setText(qty)

        # Set the size combo to match the stored value if possible
        stored_size = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
        idx = self.ef_sizes.findText(stored_size)
        if idx >= 0:
            self.ef_sizes.setCurrentIndex(idx)
        else:
            self.ef_sizes.setCurrentIndex(0)

        self.ef_category.setText(self.table.item(row, 5).text() if self.table.item(row, 5) else "")
        img_item = self.table.item(row, 6)
        self.ef_image.setText(img_item.text() if img_item else "")

    # ── toggle edit form ──────────────────────────────────────────────────────

    def _toggle_form(self):
        if self.edit_form.isVisible():
            self.edit_form.hide()
        else:
            self.edit_form.show()

    # ── manage dialog ─────────────────────────────────────────────────────────

    def _open_manage(self):
        if self.selected_row is None:
            return
        item = self.table.item(self.selected_row, 0)
        product_id = item.data(Qt.UserRole) if item else None
        if not product_id:
            return
        name = self.table.item(self.selected_row, 1).text()
        dlg = ManageIngredientsDialog(product_id, name, parent=self)
        dlg.exec_()

    # ── image helpers (Add panel) ─────────────────────────────────────────────

    def _browse_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Product Image", "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif)"
        )
        if path:
            self.image_path.setText(path)

    def _update_add_preview(self, path):
        if not path.strip():
            self.img_preview.setPixmap(QPixmap())
            self.img_preview.setText("No Image")
            return
        px = QPixmap(path.strip())
        if not px.isNull():
            self.img_preview.setText("")
            self.img_preview.setPixmap(
                px.scaled(self.img_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.img_preview.setPixmap(QPixmap())
            self.img_preview.setText("Not found")

    def _update_image_preview(self, path):
        self._update_add_preview(path)

    # ── image helpers (Edit form) ─────────────────────────────────────────────

    def _browse_image_ef(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Product Image", "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif)"
        )
        if path:
            self.ef_image.setText(path)

    # ── DB helpers ────────────────────────────────────────────────────────────

    def load_from_db(self):
        self.table.setRowCount(0)
        self._row_ids = {}
        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute("""
                SELECT p.id, p.product_name, p.base_price, p.stock, p.image_path,
                       c.category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY c.category_name, p.product_name
            """)
            rows = cur.fetchall()

            # Pre-load ingredient links for all products in one query
            cur.execute("""
                SELECT pi.product_id, pi.amount_used, i.stock_left
                FROM product_ingredients pi
                JOIN ingredients i ON pi.ingredient_id = i.id
            """)
            ingredient_links = {}
            for link in cur.fetchall():
                ingredient_links.setdefault(link["product_id"], []).append(link)

            db.close()

            for product in rows:
                pid = product["id"]
                links = ingredient_links.get(pid)

                # Auto-calculate stock: minimum of (ingredient.stock_left / amount_used)
                # across all linked ingredients. If none linked, keep manual stock.
                if links:
                    computed = min(
                        int(lnk["stock_left"] / lnk["amount_used"])
                        for lnk in links
                        if lnk["amount_used"] > 0
                    )
                    display_stock = computed
                else:
                    display_stock = product["stock"]

                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setRowHeight(row, 40)
                for col, val in enumerate([
                    str(row + 1),
                    product["product_name"],
                    f"{product['base_price']:.2f}" if product["base_price"] is not None else "0.00",
                    str(display_stock),
                    ", ".join(self._sizes),
                    product["category_name"] or "",
                    product["image_path"] or "",
                ]):
                    self.table.setItem(row, col, self._make_cell(val))
                self.table.setItem(row, 0, self._make_cell(str(row + 1)))
                self.table.item(row, 0).setData(Qt.UserRole, pid)
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not load products:\n{err}")

    def _make_cell(self, text, align=Qt.AlignCenter):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(align)
        return item

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def add_item(self):
        if not self.name.text() or not self.quantity.text():
            QMessageBox.warning(self, "Missing Fields", "Please fill in Product Name and Quantity.")
            return
        selected_size = self.expiry.currentText()
        try:
            db = get_db_connection()
            cur = db.cursor()
            cat_name = self.type.text().strip() or "Other"
            cur.execute("SELECT id FROM categories WHERE category_name = %s", (cat_name,))
            cat = cur.fetchone()
            cat_id = cat[0] if cat else None
            if not cat_id:
                cur.execute("INSERT INTO categories (category_name) VALUES (%s)", (cat_name,))
                cat_id = cur.lastrowid
            price = float(self.price.text() or 0)

            cur.execute(
                "INSERT INTO products (category_id, product_name, base_price, stock, image_path)"
                " VALUES (%s,%s,%s,%s,%s)",
                (cat_id,
                 self.name.text(),
                 price,
                 int(self.quantity.text()),
                 self.image_path.text().strip() or None)
            )
            new_id = cur.lastrowid
            db.commit()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "DB Error", f"Could not add product:\n{err}")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 40)
        for col, val in enumerate([
            "",  # #
            self.name.text(),
            f"{price:.2f}",  # Price ✅
            self.quantity.text(),  # Qty Left ✅
            selected_size,  # Available Sizes ✅
            cat_name,  # Category ✅
            self.image_path.text().strip()
        ]):
            self.table.setItem(row, col, self._make_cell(val))
        self.table.setItem(row, 0, self._make_cell(str(row + 1)))
        self.table.item(row, 0).setData(Qt.UserRole, new_id)
        self.clear_inputs()
        # Reload table from DB so all windows stay in sync, then notify siblings.
        self.load_from_db()
        if self.on_change:
            self.on_change()

    def load_selected_row(self, row, column):
        self._on_row_clicked(row, column)

    def update_item(self):
        if self.selected_row is None:
            QMessageBox.warning(self, "No Selection", "Select a row first!")
            return
        name          = self.ef_name.text().strip()
        qty           = self.ef_qty.text().strip()
        selected_size = self.ef_sizes.currentText()
        if not name or not qty:
            QMessageBox.warning(self, "Missing Fields", "Please fill in Product Name and Quantity.")
            return
        item = self.table.item(self.selected_row, 0)
        product_id = item.data(Qt.UserRole) if item else None
        if product_id:
            try:
                db = get_db_connection()
                cur = db.cursor()
                cat_name = self.ef_category.text().strip() or "Other"
                cur.execute("SELECT id FROM categories WHERE category_name = %s", (cat_name,))
                cat = cur.fetchone()
                cat_id = cat[0] if cat else None
                if not cat_id:
                    cur.execute("INSERT INTO categories (category_name) VALUES (%s)", (cat_name,))
                    cat_id = cur.lastrowid
                cur.execute(
                    "UPDATE products SET product_name=%s, base_price=%s, stock=%s, category_id=%s, image_path=%s"
                    " WHERE id=%s",
                    (name,
                     float(self.ef_price.text() or 0),
                     int(qty),
                     cat_id,
                     self.ef_image.text().strip() or None,
                     product_id)
                )
                db.commit()
                db.close()
            except Exception as err:
                QMessageBox.critical(self, "DB Error", f"Could not update product:\n{err}")
                return
        for col, val in enumerate([
            "", name,
            self.ef_price.text(),
            qty,
            selected_size,
            self.ef_category.text(),
            self.ef_image.text().strip()
        ]):
            self.table.setItem(self.selected_row, col, self._make_cell(val))
        self.action_info.setText(f"Selected:  {name}   |   Qty: {qty}")
        self.edit_form.hide()
        # Reload table from DB so all windows stay in sync, then notify siblings.
        self.load_from_db()
        if self.on_change:
            self.on_change()

    def delete_item(self):
        if self.selected_row is None:
            return
        item = self.table.item(self.selected_row, 0)
        product_id = item.data(Qt.UserRole) if item else None
        if not item:
            return
        name = self.table.item(self.selected_row, 1).text() if self.table.item(self.selected_row, 1) else "this item"
        if QMessageBox.question(
            self, "Confirm Delete", f"Delete '{name}' from the database?",
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
        if product_id:
            try:
                db = get_db_connection()
                cur = db.cursor()
                # Nullify order_items references so the FK doesn't block deletion
                cur.execute(
                    "UPDATE order_items SET product_id = NULL WHERE product_id = %s",
                    (product_id,)
                )
                cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
                db.commit()
                db.close()
            except Exception as err:
                QMessageBox.critical(self, "DB Error", f"Could not delete product:\n{err}")
                return
        self.table.removeRow(self.selected_row)
        self.selected_row = None
        self.action_bar.hide()
        self.edit_form.hide()

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setText(str(row + 1))


    def clear_inputs(self):
        self.name.clear()
        self.price.clear()
        self.quantity.clear()
        self.expiry.setCurrentIndex(0)
        self.type.clear()
        self.image_path.clear()

    # ── called by IMS on complete_order ──────────────────────────────────────

    def reduce_stock(self, sold_items):
        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            for name, qty_sold in sold_items:
                cur.execute(
                    "UPDATE products SET stock = GREATEST(0, stock - %s) WHERE product_name = %s",
                    (qty_sold, name)
                )
                cur.execute("SELECT id FROM products WHERE product_name = %s", (name,))
                prod = cur.fetchone()
                if not prod:
                    continue
                cur.execute("""
                    SELECT ingredient_id, amount_used
                    FROM product_ingredients WHERE product_id = %s
                """, (prod["id"],))
                for link in cur.fetchall():
                    cur.execute("""
                        UPDATE ingredients
                        SET stock_left = GREATEST(0, stock_left - %s)
                        WHERE id = %s
                    """, (link["amount_used"] * qty_sold, link["ingredient_id"]))
            db.commit()
            db.close()
        except Exception as err:
            print(f"[DB] reduce_stock error: {err}")
        self.load_from_db()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryPage()
    window.show()
    sys.exit(app.exec_())