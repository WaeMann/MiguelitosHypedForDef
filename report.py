import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QGridLayout, QGraphicsDropShadowEffect,
    QSizePolicy, QScrollArea, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QLineEdit, QComboBox,
    QCheckBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QColor
from datetime import date

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from db import get_db_connection, hash_password


# ─────────────────────────────────────────────────────────────────────────────
# STYLE CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

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

ADMIN_BTN_STYLE = """
QPushButton {
    background-color: #E8D28C;
    color: #2b2b2b;
    font-size: 13px;
    border-radius: 7px;
    font-weight: bold;
    border: none;
    padding: 5px 18px;
}
QPushButton:hover  { background-color: #D9BE70; }
QPushButton:pressed { background-color: #C9A850; }
"""

DANGER_BTN_STYLE = """
QPushButton {
    background-color: #c0392b;
    color: white;
    font-size: 12px;
    border-radius: 6px;
    font-weight: bold;
    border: none;
    padding: 6px 14px;
}
QPushButton:hover { background-color: #a93226; }
"""

BLUE_BTN_STYLE = """
QPushButton {
    background-color: #34699A;
    color: white;
    font-size: 12px;
    border-radius: 6px;
    font-weight: bold;
    border: none;
    padding: 6px 14px;
}
QPushButton:hover { background-color: #2a567a; }
"""

GREEN_BTN_STYLE = """
QPushButton {
    background-color: #1e7f3f;
    color: white;
    font-size: 12px;
    border-radius: 6px;
    font-weight: bold;
    border: none;
    padding: 6px 14px;
}
QPushButton:hover { background-color: #175f30; }
"""

AMBER_BTN_STYLE = """
QPushButton {
    background-color: #d97706;
    color: white;
    font-size: 12px;
    border-radius: 6px;
    font-weight: bold;
    border: none;
    padding: 6px 14px;
}
QPushButton:hover { background-color: #b45309; }
"""

CANCEL_BTN_STYLE = """
QPushButton {
    background-color: #d6d0bc;
    color: #444;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: bold;
    border: none;
}
QPushButton:hover { background-color: #c5bfa6; }
"""

TABLE_STYLE = """
QTableWidget {
    background-color: white;
    border: none;
    gridline-color: #ede9dc;
    font-size: 13px;
    outline: none;
}
QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #ede9dc;
    color: #2b2b2b;
}
QTableWidget::item:selected {
    background-color: #E8D28C;
    color: #2b2b2b;
}
QTableWidget { alternate-background-color: #fafaf7; }
QHeaderView::section {
    background-color: #2b2b2b;
    color: #E8D28C;
    font-weight: bold;
    font-size: 12px;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #3d3d3d;
}
"""

INPUT_STYLE = """
QLineEdit {
    border: 1px solid #c8b87a;
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 13px;
    background: white;
    color: #2b2b2b;
}
QLineEdit:focus { border: 2px solid #E8D28C; }
QComboBox {
    border: 1px solid #c8b87a;
    border-radius: 6px;
    padding: 5px 8px;
    background: white;
    font-size: 13px;
    color: #2b2b2b;
    min-height: 32px;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: white;
    selection-background-color: #E8D28C;
    selection-color: #2b2b2b;
}
QCheckBox { color: #555; font-size: 12px; background: transparent; }
"""

CHART_COLORS = [
    "#E8D28C", "#34699A", "#c0392b", "#1e7f3f",
    "#e67e22", "#8e44ad", "#16a085", "#2c3e50",
]


# ─────────────────────────────────────────────────────────────────────────────
# SHARED HELPERS
# ─────────────────────────────────────────────────────────────────────────────

class DragScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._drag_active = False
        self._start_pos = None
        self._start_scroll = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._start_pos = event.pos()
            self._start_scroll = (
                self.verticalScrollBar().value(),
                self.horizontalScrollBar().value(),
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active and self._start_pos:
            delta = event.pos() - self._start_pos
            self.verticalScrollBar().setValue(self._start_scroll[0] - delta.y())
            self.horizontalScrollBar().setValue(self._start_scroll[1] - delta.x())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        self._start_pos = None
        super().mouseReleaseEvent(event)


def drop_shadow(widget, blur=25, x=3, y=3, alpha=150):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setXOffset(x)
    fx.setYOffset(y)
    fx.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(fx)
    return fx


def _dialog_header(layout, title: str, subtitle: str = ""):
    """Dark/gold header bar used by all admin dialogs."""
    hdr = QFrame()
    hdr.setStyleSheet("background-color: #2b2b2b;")
    hdr.setFixedHeight(60)
    hl = QHBoxLayout(hdr)
    hl.setContentsMargins(22, 0, 22, 0)
    col = QVBoxLayout()
    col.setSpacing(2)
    t = QLabel(title)
    t.setStyleSheet(
        "font-size: 16px; font-weight: bold; color: #E8D28C; background: transparent;"
    )
    col.addWidget(t)
    if subtitle:
        s = QLabel(subtitle)
        s.setStyleSheet("font-size: 11px; color: #888; background: transparent;")
        col.addWidget(s)
    hl.addLayout(col)
    hl.addStretch()
    layout.addWidget(hdr)
    acc = QFrame()
    acc.setFixedHeight(3)
    acc.setStyleSheet("background-color: #E8D28C;")
    layout.addWidget(acc)


def _center_dialog(dlg):
    """Center a dialog on its parent or the primary screen."""
    dlg.adjustSize()
    if dlg.parent():
        pg = dlg.parent().frameGeometry()
        dlg.move(
            pg.x() + max(0, (pg.width()  - dlg.width())  // 2),
            pg.y() + max(0, (pg.height() - dlg.height()) // 2),
        )
    else:
        screen = QApplication.primaryScreen().availableGeometry()
        dlg.move(
            screen.x() + (screen.width()  - dlg.width())  // 2,
            screen.y() + (screen.height() - dlg.height()) // 2,
        )


def _form_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        "color: #555; font-size: 12px; font-weight: bold; background: transparent;"
    )
    return lbl


# ─────────────────────────────────────────────────────────────────────────────
# ORDER DETAIL DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class OrderDetailDialog(QDialog):
    def __init__(self, order_id: int, order_total: float,
                 order_date: str, parent=None):
        super().__init__(parent)
        self.order_id    = order_id
        self.order_total = order_total
        self.order_date  = order_date
        self.setWindowTitle(f"Order #{order_id} – Detail")
        self.setFixedSize(520, 540)
        self.setStyleSheet("QDialog { background-color: #EFE9D1; font-family: 'Segoe UI'; }")
        self._build()
        _center_dialog(self)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        _dialog_header(root, f"📋  Order #{self.order_id}",
                       subtitle=f"Date: {self.order_date}")

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(20, 16, 20, 16)
        bl.setSpacing(12)
        root.addWidget(body, stretch=1)

        # Items table
        tbl = QTableWidget()
        tbl.setStyleSheet(TABLE_STYLE)
        tbl.setColumnCount(4)
        tbl.setHorizontalHeaderLabels(["Item", "Size", "Qty", "Price"])
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tbl.setColumnWidth(1, 90)
        tbl.setColumnWidth(2, 55)
        tbl.setColumnWidth(3, 100)
        tbl.verticalHeader().setVisible(False)
        tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setAlternatingRowColors(True)
        tbl.setShowGrid(False)

        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                "SELECT product_name, size_name, quantity, item_price "
                "FROM order_items WHERE order_id = %s",
                (self.order_id,),
            )
            rows = cur.fetchall()
            db.close()
            tbl.setRowCount(len(rows))
            for r, row in enumerate(rows):
                tbl.setItem(r, 0, QTableWidgetItem(row["product_name"] or "—"))
                size_item = QTableWidgetItem(row["size_name"] or "—")
                size_item.setTextAlignment(Qt.AlignCenter)
                tbl.setItem(r, 1, size_item)
                qty_item = QTableWidgetItem(str(row["quantity"]))
                qty_item.setTextAlignment(Qt.AlignCenter)
                tbl.setItem(r, 2, qty_item)
                price_item = QTableWidgetItem(f"₱{float(row['item_price']):,.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tbl.setItem(r, 3, price_item)
        except Exception as err:
            tbl.setRowCount(1)
            tbl.setItem(0, 0, QTableWidgetItem(f"Error: {err}"))

        bl.addWidget(tbl)

        # Total card
        tot_f = QFrame()
        tot_f.setStyleSheet(
            "QFrame { background-color: white; border-radius: 10px; border: 1px solid #c8b87a; }"
        )
        tot_l = QHBoxLayout(tot_f)
        tot_l.setContentsMargins(18, 12, 18, 12)
        lbl = QLabel("ORDER TOTAL")
        lbl.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #888; "
            "letter-spacing: 1px; background: transparent; border: none;"
        )
        val = QLabel(f"₱{self.order_total:,.2f}")
        val.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #2b2b2b; "
            "background: transparent; border: none;"
        )
        tot_l.addWidget(lbl)
        tot_l.addStretch()
        tot_l.addWidget(val)
        bl.addWidget(tot_f)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(ADMIN_BTN_STYLE)
        close_btn.setFixedHeight(36)
        close_btn.clicked.connect(self.accept)
        bl.addWidget(close_btn, alignment=Qt.AlignRight)


# ─────────────────────────────────────────────────────────────────────────────
# ORDERS DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class OrdersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Order History")
        self.resize(820, 560)
        self.setMinimumSize(680, 440)
        self.setStyleSheet("QDialog { background-color: #EFE9D1; font-family: 'Segoe UI'; }")
        self._build()
        _center_dialog(self)
        self._load()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        _dialog_header(root, "📋  Order History",
                       subtitle="Double-click a row to view its full breakdown")

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(16, 12, 16, 12)
        bl.setSpacing(10)
        root.addWidget(body, stretch=1)

        # Toolbar
        tb = QHBoxLayout()
        self._count_lbl = QLabel("Loading…")
        self._count_lbl.setStyleSheet(
            "color: #888; font-size: 12px; background: transparent;"
        )
        tb.addWidget(self._count_lbl)
        tb.addStretch()
        refresh_btn = QPushButton("🔄  Refresh")
        refresh_btn.setStyleSheet(ADMIN_BTN_STYLE)
        refresh_btn.setFixedHeight(34)
        refresh_btn.clicked.connect(self._load)
        tb.addWidget(refresh_btn)
        bl.addLayout(tb)

        # Table
        self._table = QTableWidget()
        self._table.setStyleSheet(TABLE_STYLE)
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(
            ["Order ID", "Date / Time", "# Items", "Total"]
        )
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.setColumnWidth(0, 90)
        self._table.setColumnWidth(2, 80)
        self._table.setColumnWidth(3, 130)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.doubleClicked.connect(self._view_detail)
        bl.addWidget(self._table)

        hint = QLabel("Double-click any row to view the full order breakdown.")
        hint.setStyleSheet("color: #bbb; font-size: 11px; background: transparent;")
        hint.setAlignment(Qt.AlignCenter)
        bl.addWidget(hint)

    def _load(self):
        self._table.setRowCount(0)
        self._count_lbl.setText("Loading…")
        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute("""
                SELECT o.id, o.total, o.created_at,
                       COALESCE(COUNT(oi.id), 0) AS item_count
                FROM orders o
                LEFT JOIN order_items oi ON oi.order_id = o.id
                GROUP BY o.id
                ORDER BY o.id DESC
                LIMIT 500
            """)
            rows = cur.fetchall()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))
            self._count_lbl.setText("Error loading data.")
            return

        self._table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            id_item = QTableWidgetItem(str(row["id"]))
            id_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(r, 0, id_item)

            self._table.setItem(r, 1, QTableWidgetItem(str(row["created_at"])))

            cnt_item = QTableWidgetItem(str(row["item_count"] or 0))
            cnt_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(r, 2, cnt_item)

            total_item = QTableWidgetItem(f"₱{float(row['total']):,.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._table.setItem(r, 3, total_item)

        self._count_lbl.setText(f"{len(rows)} record(s)")

    def _view_detail(self, index):
        r = index.row()
        order_id  = int(self._table.item(r, 0).text())
        order_date = self._table.item(r, 1).text()
        total_str  = self._table.item(r, 3).text().replace("₱", "").replace(",", "")
        try:
            total = float(total_str)
        except ValueError:
            total = 0.0
        dlg = OrderDetailDialog(order_id, total, order_date, parent=self)
        dlg.exec_()


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class SummaryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sales Summary")
        self.setFixedSize(520, 510)
        self.setStyleSheet("QDialog { background-color: #EFE9D1; font-family: 'Segoe UI'; }")
        self._build()
        _center_dialog(self)
        self._load()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        _dialog_header(root, "📊  Sales Summary",
                       subtitle="Today's performance at a glance")

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(24, 20, 24, 20)
        bl.setSpacing(14)
        root.addWidget(body, stretch=1)

        # ── TODAY section ─────────────────────────────────────────────────
        sec1 = QLabel("TODAY'S STATS")
        sec1.setStyleSheet(
            "font-size: 10px; font-weight: bold; color: #888; "
            "letter-spacing: 2px; background: transparent;"
        )
        bl.addWidget(sec1)

        today_configs = [
            ("Total Orders Today", "#34699A", "_lbl_today_orders"),
            ("Revenue Today",      "#1e7f3f", "_lbl_today_rev"),
            ("Average Order Value","#e67e22", "_lbl_today_avg"),
        ]
        for label, color, attr in today_configs:
            card = self._stat_card(label, color, "—", attr)
            bl.addWidget(card)

        # Divider
        div = QFrame()
        div.setFixedHeight(2)
        div.setStyleSheet("background-color: #c8b87a; border: none;")
        bl.addWidget(div)

        # ── ALL-TIME section ──────────────────────────────────────────────
        sec2 = QLabel("ALL-TIME TOTALS")
        sec2.setStyleSheet(
            "font-size: 10px; font-weight: bold; color: #888; "
            "letter-spacing: 2px; background: transparent;"
        )
        bl.addWidget(sec2)

        all_row = QHBoxLayout()
        all_row.setSpacing(12)
        for label, color, attr in [
            ("Total Orders",  "#2b2b2b", "_lbl_all_orders"),
            ("Total Revenue", "#E8D28C", "_lbl_all_rev"),
        ]:
            card = self._stat_card(label, color, "—", attr, horizontal=False)
            all_row.addWidget(card)
        bl.addLayout(all_row)

        bl.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ref = QPushButton("🔄  Refresh")
        ref.setStyleSheet(BLUE_BTN_STYLE)
        ref.setFixedHeight(36)
        ref.clicked.connect(self._load)
        btn_row.addWidget(ref)
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(ADMIN_BTN_STYLE)
        close_btn.setFixedHeight(36)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        bl.addLayout(btn_row)

    def _stat_card(self, label: str, color: str, initial: str,
                   attr: str, horizontal: bool = True) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: white; border-radius: 10px; "
            "border: 1px solid #ede9dc; }"
        )
        drop_shadow(card, blur=12, alpha=50)

        if horizontal:
            cl = QHBoxLayout(card)
            cl.setContentsMargins(14, 10, 14, 10)
            accent = QFrame()
            accent.setFixedWidth(5)
            accent.setStyleSheet(
                f"background-color: {color}; border-radius: 3px; border: none;"
            )
            cl.addWidget(accent)
            info = QVBoxLayout()
            info.setSpacing(2)
            lbl = QLabel(label)
            lbl.setStyleSheet(
                "font-size: 11px; color: #888; background: transparent; border: none;"
            )
            val = QLabel(initial)
            val.setStyleSheet(
                f"font-size: 22px; font-weight: bold; color: {color}; "
                "background: transparent; border: none;"
            )
            info.addWidget(lbl)
            info.addWidget(val)
            cl.addLayout(info)
            cl.addStretch()
        else:
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            lbl = QLabel(label)
            lbl.setStyleSheet(
                "font-size: 11px; color: #888; background: transparent; border: none;"
            )
            val = QLabel(initial)
            val.setStyleSheet(
                f"font-size: 20px; font-weight: bold; color: {color}; "
                "background: transparent; border: none;"
            )
            cl.addWidget(lbl)
            cl.addWidget(val)

        setattr(self, attr, val)
        return card

    def _load(self):
        today_orders, today_rev, today_avg = 0, 0.0, 0.0
        all_orders,   all_rev              = 0, 0.0
        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)
            today_str = date.today().isoformat()

            cur.execute(
                "SELECT COUNT(*) AS cnt, COALESCE(SUM(total), 0) AS rev "
                "FROM orders WHERE DATE(created_at) = %s",
                (today_str,),
            )
            row = cur.fetchone()
            today_orders = row["cnt"] or 0
            today_rev    = float(row["rev"] or 0)
            today_avg    = today_rev / today_orders if today_orders else 0.0

            cur.execute(
                "SELECT COUNT(*) AS cnt, COALESCE(SUM(total), 0) AS rev FROM orders"
            )
            row = cur.fetchone()
            all_orders = row["cnt"] or 0
            all_rev    = float(row["rev"] or 0)
            db.close()
        except Exception as err:
            QMessageBox.warning(self, "Database Error", str(err))

        self._lbl_today_orders.setText(str(today_orders))
        self._lbl_today_rev.setText(f"₱{today_rev:,.2f}")
        self._lbl_today_avg.setText(f"₱{today_avg:,.2f}")
        self._lbl_all_orders.setText(str(all_orders))
        self._lbl_all_rev.setText(f"₱{all_rev:,.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# ADD USER DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.created = False
        self.setWindowTitle("Add New User")
        self.setFixedSize(420, 380)
        self.setStyleSheet("QDialog { background-color: #EFE9D1; font-family: 'Segoe UI'; }")
        self._build()
        _center_dialog(self)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        _dialog_header(root, "➕  Add New User")

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(28, 20, 28, 20)
        bl.setSpacing(10)
        root.addWidget(body, stretch=1)

        # Form grid
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnStretch(1, 1)

        self._uname_edit = QLineEdit()
        self._uname_edit.setPlaceholderText("at least 3 characters")
        self._uname_edit.setStyleSheet(INPUT_STYLE)
        self._uname_edit.setFixedHeight(36)

        self._pwd_edit = QLineEdit()
        self._pwd_edit.setPlaceholderText("password")
        self._pwd_edit.setEchoMode(QLineEdit.Password)
        self._pwd_edit.setStyleSheet(INPUT_STYLE)
        self._pwd_edit.setFixedHeight(36)

        self._role_combo = QComboBox()
        self._role_combo.addItems(["cashier", "admin"])
        self._role_combo.setStyleSheet(INPUT_STYLE)

        for row_idx, (lbl_text, widget) in enumerate([
            ("Username:",  self._uname_edit),
            ("Password:",  self._pwd_edit),
            ("Role:",      self._role_combo),
        ]):
            grid.addWidget(_form_label(lbl_text), row_idx, 0, Qt.AlignVCenter)
            grid.addWidget(widget, row_idx, 1)

        bl.addLayout(grid)

        show_cb = QCheckBox("Show password")
        show_cb.setStyleSheet(INPUT_STYLE)
        show_cb.toggled.connect(
            lambda on: self._pwd_edit.setEchoMode(
                QLineEdit.Normal if on else QLineEdit.Password
            )
        )
        bl.addWidget(show_cb)

        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(
            "color: #c0392b; font-size: 12px; background: transparent;"
        )
        self._status_lbl.setWordWrap(True)
        bl.addWidget(self._status_lbl)
        bl.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancel")
        cancel.setStyleSheet(CANCEL_BTN_STYLE)
        cancel.setFixedHeight(36)
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)
        create = QPushButton("➕  Create User")
        create.setStyleSheet(GREEN_BTN_STYLE)
        create.setFixedHeight(36)
        create.clicked.connect(self._create)
        btn_row.addWidget(create)
        bl.addLayout(btn_row)

    def _create(self):
        uname = self._uname_edit.text().strip()
        pwd   = self._pwd_edit.text()
        role  = self._role_combo.currentText()

        if len(uname) < 3:
            self._status_lbl.setText("⚠  Username must be at least 3 characters.")
            return
        if not pwd:
            self._status_lbl.setText("⚠  Password is required.")
            return

        try:
            db  = get_db_connection()
            cur = db.cursor(buffered=True)
            cur.execute("SELECT id FROM users WHERE username = %s", (uname,))
            if cur.fetchone():
                self._status_lbl.setText(f"⚠  Username '{uname}' is already taken.")
                db.close()
                return
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (uname, hash_password(pwd), role),
            )
            db.commit()
            db.close()
            self.created = True
            QMessageBox.information(
                self, "User Created",
                f"Account '{uname}' ({role}) was created successfully.",
            )
            self.accept()
        except Exception as err:
            self._status_lbl.setText(f"⚠  DB Error: {err}")


# ─────────────────────────────────────────────────────────────────────────────
# RESET PASSWORD DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class ResetPasswordDialog(QDialog):
    def __init__(self, user_id: int, username: str, parent=None):
        super().__init__(parent)
        self.user_id  = user_id
        self.username = username
        self.setWindowTitle("Reset Password")
        self.setFixedSize(420, 320)
        self.setStyleSheet("QDialog { background-color: #EFE9D1; font-family: 'Segoe UI'; }")
        self._build()
        _center_dialog(self)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        _dialog_header(root, "🔑  Reset Password",
                       subtitle=f"Account: {self.username}")

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(28, 20, 28, 20)
        bl.setSpacing(10)
        root.addWidget(body, stretch=1)

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnStretch(1, 1)

        self._new_pwd = QLineEdit()
        self._new_pwd.setPlaceholderText("new password")
        self._new_pwd.setEchoMode(QLineEdit.Password)
        self._new_pwd.setStyleSheet(INPUT_STYLE)
        self._new_pwd.setFixedHeight(36)

        self._re_pwd = QLineEdit()
        self._re_pwd.setPlaceholderText("confirm new password")
        self._re_pwd.setEchoMode(QLineEdit.Password)
        self._re_pwd.setStyleSheet(INPUT_STYLE)
        self._re_pwd.setFixedHeight(36)

        for row_idx, (lbl_text, widget) in enumerate([
            ("New Password:", self._new_pwd),
            ("Confirm:",      self._re_pwd),
        ]):
            grid.addWidget(_form_label(lbl_text), row_idx, 0, Qt.AlignVCenter)
            grid.addWidget(widget, row_idx, 1)

        bl.addLayout(grid)

        show_cb = QCheckBox("Show password")
        show_cb.setStyleSheet(INPUT_STYLE)
        show_cb.toggled.connect(self._toggle_pw)
        bl.addWidget(show_cb)

        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(
            "color: #c0392b; font-size: 12px; background: transparent;"
        )
        self._status_lbl.setWordWrap(True)
        bl.addWidget(self._status_lbl)
        bl.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancel")
        cancel.setStyleSheet(CANCEL_BTN_STYLE)
        cancel.setFixedHeight(36)
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)
        confirm = QPushButton("✓  Update Password")
        confirm.setStyleSheet(GREEN_BTN_STYLE)
        confirm.setFixedHeight(36)
        confirm.clicked.connect(self._confirm)
        btn_row.addWidget(confirm)
        bl.addLayout(btn_row)

    def _toggle_pw(self, on: bool):
        mode = QLineEdit.Normal if on else QLineEdit.Password
        self._new_pwd.setEchoMode(mode)
        self._re_pwd.setEchoMode(mode)

    def _confirm(self):
        p1 = self._new_pwd.text()
        p2 = self._re_pwd.text()
        if not p1:
            self._status_lbl.setText("⚠  Please enter a new password.")
            return
        if p1 != p2:
            self._status_lbl.setText("⚠  Passwords do not match.")
            return
        try:
            db  = get_db_connection()
            cur = db.cursor()
            cur.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (hash_password(p1), self.user_id),
            )
            db.commit()
            db.close()
            QMessageBox.information(
                self, "Password Updated",
                f"Password for '{self.username}' was updated successfully.",
            )
            self.accept()
        except Exception as err:
            self._status_lbl.setText(f"⚠  DB Error: {err}")


# ─────────────────────────────────────────────────────────────────────────────
# USERS DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class UsersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Users")
        self.resize(780, 520)
        self.setMinimumSize(680, 420)
        self.setStyleSheet("QDialog { background-color: #EFE9D1; font-family: 'Segoe UI'; }")
        self._build()
        _center_dialog(self)
        self._load()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        _dialog_header(root, "👤  Manage Users",
                       subtitle="Add, reset passwords, change roles, or delete accounts")

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(16, 12, 16, 12)
        bl.setSpacing(10)
        root.addWidget(body, stretch=1)

        # Toolbar
        tb = QHBoxLayout()
        tb.setSpacing(8)

        add_btn = QPushButton("➕  Add User")
        add_btn.setStyleSheet(GREEN_BTN_STYLE)
        add_btn.setFixedHeight(34)
        add_btn.clicked.connect(self._add_user)
        tb.addWidget(add_btn)

        self._reset_btn = QPushButton("🔑  Reset Password")
        self._reset_btn.setStyleSheet(BLUE_BTN_STYLE)
        self._reset_btn.setFixedHeight(34)
        self._reset_btn.clicked.connect(self._reset_password)
        tb.addWidget(self._reset_btn)

        self._role_btn = QPushButton("⚙  Change Role")
        self._role_btn.setStyleSheet(AMBER_BTN_STYLE)
        self._role_btn.setFixedHeight(34)
        self._role_btn.clicked.connect(self._change_role)
        tb.addWidget(self._role_btn)

        self._del_btn = QPushButton("🗑  Delete User")
        self._del_btn.setStyleSheet(DANGER_BTN_STYLE)
        self._del_btn.setFixedHeight(34)
        self._del_btn.clicked.connect(self._delete_user)
        tb.addWidget(self._del_btn)

        tb.addStretch()

        refresh_btn = QPushButton("🔄  Refresh")
        refresh_btn.setStyleSheet(ADMIN_BTN_STYLE)
        refresh_btn.setFixedHeight(34)
        refresh_btn.clicked.connect(self._load)
        tb.addWidget(refresh_btn)

        bl.addLayout(tb)

        # Table
        self._table = QTableWidget()
        self._table.setStyleSheet(TABLE_STYLE)
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(
            ["ID", "Username", "Role", "Created"]
        )
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._table.setColumnWidth(0, 55)
        self._table.setColumnWidth(2, 90)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        bl.addWidget(self._table)

        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(
            "color: #888; font-size: 11px; background: transparent;"
        )
        bl.addWidget(self._status_lbl)

    def _load(self):
        self._table.setRowCount(0)
        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                "SELECT id, username, role, created_at FROM users ORDER BY id"
            )
            rows = cur.fetchall()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))
            return

        self._table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            id_item = QTableWidgetItem(str(row["id"]))
            id_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(r, 0, id_item)

            self._table.setItem(r, 1, QTableWidgetItem(row["username"]))

            role_text = row["role"].title()
            role_item = QTableWidgetItem(role_text)
            role_item.setTextAlignment(Qt.AlignCenter)
            role_item.setForeground(
                QColor("#e67e22") if row["role"] == "admin" else QColor("#34699A")
            )
            self._table.setItem(r, 2, role_item)

            created = str(row["created_at"]) if row["created_at"] else "—"
            self._table.setItem(r, 3, QTableWidgetItem(created))

        self._status_lbl.setText(f"{len(rows)} user(s)  —  Select a row to act on it")

    def _selected(self):
        """Return (uid, username, role) for the selected row, or None on no selection."""
        row = self._table.currentRow()
        if row < 0 or not self._table.item(row, 0):
            QMessageBox.information(self, "No Selection", "Please select a user first.")
            return None
        uid   = int(self._table.item(row, 0).text())
        uname = self._table.item(row, 1).text()
        role  = self._table.item(row, 2).text().lower()
        return uid, uname, role

    def _count_admins(self) -> int:
        try:
            db  = get_db_connection()
            cur = db.cursor()
            cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            count = cur.fetchone()[0]
            db.close()
            return count
        except Exception:
            return 2   # safe fallback — assume more than one

    def _add_user(self):
        dlg = AddUserDialog(parent=self)
        dlg.exec_()
        if dlg.created:
            self._load()

    def _reset_password(self):
        sel = self._selected()
        if sel is None:
            return
        uid, uname, _ = sel
        dlg = ResetPasswordDialog(uid, uname, parent=self)
        dlg.exec_()

    def _change_role(self):
        sel = self._selected()
        if sel is None:
            return
        uid, uname, current_role = sel
        new_role = "admin" if current_role == "cashier" else "cashier"

        if current_role == "admin" and self._count_admins() <= 1:
            QMessageBox.warning(
                self, "Cannot Change Role",
                "Cannot demote the last admin account.\n"
                "Promote another user to admin first.",
            )
            return

        reply = QMessageBox.question(
            self, "Change Role",
            f"Change '{uname}' from {current_role} → {new_role}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            db  = get_db_connection()
            cur = db.cursor()
            cur.execute(
                "UPDATE users SET role = %s WHERE id = %s", (new_role, uid)
            )
            db.commit()
            db.close()
            QMessageBox.information(
                self, "Role Updated",
                f"'{uname}' is now a {new_role}.",
            )
            self._load()
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))

    def _delete_user(self):
        sel = self._selected()
        if sel is None:
            return
        uid, uname, role = sel

        if role == "admin" and self._count_admins() <= 1:
            QMessageBox.warning(
                self, "Cannot Delete",
                "Cannot delete the last admin account.",
            )
            return

        reply = QMessageBox.question(
            self, "⚠  Confirm Deletion",
            f"Permanently delete user '{uname}'?\n\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            db  = get_db_connection()
            cur = db.cursor()
            cur.execute("DELETE FROM users WHERE id = %s", (uid,))
            db.commit()
            db.close()
            QMessageBox.information(self, "Deleted", f"User '{uname}' has been deleted.")
            self._load()
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))


# ─────────────────────────────────────────────────────────────────────────────
# REPORT PAGE
# ─────────────────────────────────────────────────────────────────────────────

class ReportPage(QWidget):
    def __init__(self, switch_callback=None, role: str = "cashier"):
        super().__init__()
        self.switch_callback = switch_callback
        self.role        = role
        self.sales_data  = {}
        self.daily_sales = {}

        self.setWindowTitle("Hyped Mangoes — Reports")
        self.setStyleSheet("QWidget { background-color: #DED6B2; font-family: 'Segoe UI'; }")
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self._build_ui()
        self._load_from_db()
        self.refresh_report()

    # ── DB LOAD ──────────────────────────────────────────────────────────────

    def _load_from_db(self):
        """Load all past orders from DB to pre-populate charts."""
        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)

            cur.execute("""
                SELECT oi.product_name, SUM(oi.item_price) AS total
                FROM order_items oi
                GROUP BY oi.product_name
            """)
            for row in cur.fetchall():
                name = row["product_name"] or "Unknown"
                self.sales_data[name] = self.sales_data.get(name, 0) + float(row["total"])

            cur.execute("""
                SELECT DATE(created_at) AS day, SUM(total) AS day_total
                FROM orders
                GROUP BY DATE(created_at)
                ORDER BY day
            """)
            for row in cur.fetchall():
                day_str = str(row["day"])
                self.daily_sales[day_str] = (
                    self.daily_sales.get(day_str, 0) + float(row["day_total"])
                )

            db.close()
        except Exception as err:
            print(f"[Report] Could not load history from DB: {err}")

    # ── UI BUILD ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── TOP BAR ──────────────────────────────────────────────────────────
        top_bar = QFrame()
        top_bar.setFixedHeight(80)
        top_bar.setStyleSheet("background-color: #DED6B2;")
        tbl = QHBoxLayout(top_bar)
        tbl.setContentsMargins(24, 0, 24, 0)
        tbl.setSpacing(10)

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
            ("  TRANSACTIONS", "TRANSACTION.png", "pos"),
            ("  INVENTORY",    "inventory.png",   "inventory"),
        ]:
            btn = QPushButton(label)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(18, 18))
            btn.setFixedSize(160, 36)
            btn.setStyleSheet(NAV_BTN_STYLE)
            _k = page_key
            btn.clicked.connect(
                lambda checked, k=_k:
                    self.switch_callback(k) if self.switch_callback else None
            )
            drop_shadow(btn, blur=18, alpha=100)
            nav_layout.addWidget(btn)

        tbl.addWidget(logo)
        tbl.addStretch()
        tbl.addLayout(nav_layout)
        tbl.addStretch()
        root.addWidget(top_bar)

        # Gold separator under top bar
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #c8b87a;")
        root.addWidget(sep)

        # ── ADMIN BUTTON BAR ─────────────────────────────────────────────────
        self._build_admin_bar(root)

        # ── CONTENT SCROLL ───────────────────────────────────────────────────
        scroll_area = DragScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background-color: #EFE9D1; }
            QScrollBar:vertical {
                background: #DED6B2; width: 10px; border-radius: 5px; margin: 4px;
            }
            QScrollBar::handle:vertical {
                background: #c8b87a; border-radius: 5px; min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #b59f5d; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        content_area = QWidget()
        content_area.setStyleSheet("background-color: #EFE9D1;")
        content_grid = QGridLayout(content_area)
        content_grid.setContentsMargins(24, 20, 24, 20)
        content_grid.setSpacing(18)
        scroll_area.setWidget(content_area)
        root.addWidget(scroll_area, stretch=1)

        # ── TOTAL SALES CARD ─────────────────────────────────────────────────
        self.total_card = self._make_panel()
        self.total_card.setFixedHeight(120)
        drop_shadow(self.total_card, blur=25, alpha=110)
        total_inner = QHBoxLayout(self.total_card)
        total_inner.setContentsMargins(24, 16, 24, 16)

        left_col = QVBoxLayout()
        card_title = QLabel("TOTAL REVENUE")
        card_title.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #888; "
            "letter-spacing: 2px; background: transparent;"
        )
        self.total_value = QLabel("₱0.00")
        self.total_value.setStyleSheet(
            "font-size: 36px; font-weight: bold; color: #2b2b2b; background: transparent;"
        )
        left_col.addWidget(card_title)
        left_col.addWidget(self.total_value)
        total_inner.addLayout(left_col)
        total_inner.addStretch()

        icon_lbl = QLabel("₱")
        icon_lbl.setStyleSheet(
            "font-size: 52px; color: #E8D28C; font-weight: bold; background: transparent;"
        )
        total_inner.addWidget(icon_lbl)
        content_grid.addWidget(self.total_card, 0, 0, 1, 2)

        # ── PIE CHART PANEL ──────────────────────────────────────────────────
        pie_panel = self._make_panel()
        drop_shadow(pie_panel, blur=25, alpha=110)
        pie_layout = QVBoxLayout(pie_panel)
        pie_layout.setContentsMargins(16, 14, 16, 14)
        pie_layout.setSpacing(8)

        pie_title = QLabel("Sales Breakdown by Item")
        pie_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #2b2b2b; background: transparent;"
        )
        pie_layout.addWidget(pie_title)

        self.pie_canvas = FigureCanvas(Figure(figsize=(5, 4), facecolor="#FFFFFF"))
        self.pie_canvas.setMinimumHeight(320)
        self.pie_canvas.setStyleSheet("border-radius: 8px;")
        pie_layout.addWidget(self.pie_canvas)
        content_grid.addWidget(pie_panel, 1, 0)
        pie_panel.setMinimumHeight(420)

        # ── TRACKER PANEL ────────────────────────────────────────────────────
        tracker_panel = self._make_panel()
        drop_shadow(tracker_panel, blur=25, alpha=110)
        tracker_outer = QVBoxLayout(tracker_panel)
        tracker_outer.setContentsMargins(16, 14, 16, 14)
        tracker_outer.setSpacing(8)

        tracker_title = QLabel("Item Sales Breakdown")
        tracker_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #2b2b2b; background: transparent;"
        )
        tracker_outer.addWidget(tracker_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #EFE9D1; width: 7px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #c8b87a; border-radius: 3px; }
        """)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.tracker_layout = QVBoxLayout(scroll_content)
        self.tracker_layout.setContentsMargins(0, 0, 8, 0)
        self.tracker_layout.setSpacing(6)
        self.tracker_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(scroll_content)
        tracker_outer.addWidget(scroll, stretch=1)
        content_grid.addWidget(tracker_panel, 1, 1)

        # ── BAR CHART PANEL ──────────────────────────────────────────────────
        bar_panel = self._make_panel()
        bar_panel.setFixedHeight(280)
        drop_shadow(bar_panel, blur=25, alpha=110)
        bar_layout = QVBoxLayout(bar_panel)
        bar_layout.setContentsMargins(16, 14, 16, 14)
        bar_layout.setSpacing(8)

        bar_title = QLabel("Daily Sales")
        bar_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #2b2b2b; background: transparent;"
        )
        bar_layout.addWidget(bar_title)

        self.bar_canvas = FigureCanvas(Figure(figsize=(8, 2.4), facecolor="#FFFFFF"))
        self.bar_canvas.setStyleSheet("border-radius: 8px;")
        bar_layout.addWidget(self.bar_canvas)
        content_grid.addWidget(bar_panel, 2, 0, 1, 2)

        content_grid.setColumnStretch(0, 1)
        content_grid.setColumnStretch(1, 1)

    # ── ADMIN BAR ────────────────────────────────────────────────────────────

    def _build_admin_bar(self, root: QVBoxLayout):
        bar = QFrame()
        bar.setFixedHeight(52)
        bar.setStyleSheet("background-color: #2b2b2b;")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(20, 0, 20, 0)
        bl.setSpacing(10)

        # Always-visible buttons
        for label, slot in [
            ("📋  Orders",         self._open_orders),
            ("📊  Today's Summary", self._open_summary),
        ]:
            btn = QPushButton(label)
            btn.setFixedHeight(36)
            btn.setStyleSheet(ADMIN_BTN_STYLE)
            btn.setCursor(Qt.PointingHandCursor)
            drop_shadow(btn, blur=10, alpha=55)
            btn.clicked.connect(slot)
            bl.addWidget(btn)

        # Admin-only: Manage Users
        if self.role == "admin":
            usr_btn = QPushButton("👤  Manage Users")
            usr_btn.setFixedHeight(36)
            usr_btn.setStyleSheet(ADMIN_BTN_STYLE)
            usr_btn.setCursor(Qt.PointingHandCursor)
            drop_shadow(usr_btn, blur=10, alpha=55)
            usr_btn.clicked.connect(self._open_users)
            bl.addWidget(usr_btn)

        bl.addStretch()

        # Refresh stays on the right
        ref_btn = QPushButton("🔄  Refresh")
        ref_btn.setFixedHeight(36)
        ref_btn.setStyleSheet(ADMIN_BTN_STYLE)
        ref_btn.setCursor(Qt.PointingHandCursor)
        drop_shadow(ref_btn, blur=10, alpha=55)
        ref_btn.clicked.connect(self.refresh_report)
        bl.addWidget(ref_btn)

        root.addWidget(bar)

        # Thin gold accent under the admin bar
        acc = QFrame()
        acc.setFixedHeight(2)
        acc.setStyleSheet("background-color: #E8D28C;")
        root.addWidget(acc)

    # ── BUTTON HANDLERS ──────────────────────────────────────────────────────

    def _open_orders(self):
        dlg = OrdersDialog(parent=self)
        dlg.exec_()

    def _open_summary(self):
        dlg = SummaryDialog(parent=self)
        dlg.exec_()

    def _open_users(self):
        dlg = UsersDialog(parent=self)
        dlg.exec_()

    # ── PANEL FACTORY ────────────────────────────────────────────────────────

    def _make_panel(self):
        panel = QFrame()
        panel.setStyleSheet("QFrame { background-color: white; border-radius: 14px; }")
        return panel

    # ── DATA UPDATES (called by IMS on complete_order) ────────────────────────

    def update_sales(self, items, total):
        """items = list of (product_name, price). Called live from IMS."""
        if not items:
            return
        for item_name, value in items:
            self.sales_data[item_name] = self.sales_data.get(item_name, 0) + value
        today = date.today().isoformat()
        self.daily_sales[today] = self.daily_sales.get(today, 0) + total
        self.refresh_report()

    def refresh_report(self):
        self.plot_pie()
        self.plot_bar()
        self.update_tracker()

    # ── TRACKER ──────────────────────────────────────────────────────────────

    def update_tracker(self):
        for i in reversed(range(self.tracker_layout.count())):
            w = self.tracker_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        total_sales = sum(self.sales_data.values())
        self.total_value.setText(f"₱{total_sales:,.2f}")

        if total_sales == 0:
            empty = QLabel("No sales recorded yet.")
            empty.setStyleSheet("color: #aaa; font-size: 14px; background: transparent;")
            empty.setAlignment(Qt.AlignCenter)
            self.tracker_layout.addWidget(empty)
            return

        for i, (item, value) in enumerate(
            sorted(self.sales_data.items(), key=lambda x: -x[1])
        ):
            percent = (value / total_sales) * 100
            row = QFrame()
            row.setStyleSheet(
                "QFrame { background-color: #fafaf7; border-radius: 8px; "
                "border: 1px solid #ede9dc; }"
            )
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 8, 12, 8)

            color_dot = QLabel("●")
            dot_color = CHART_COLORS[i % len(CHART_COLORS)]
            color_dot.setStyleSheet(
                f"color: {dot_color}; font-size: 18px; background: transparent;"
            )
            color_dot.setFixedWidth(22)

            name_lbl = QLabel(item)
            name_lbl.setStyleSheet(
                "font-size: 13px; color: #2c3e50; background: transparent;"
            )
            name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            val_lbl = QLabel(f"₱{value:,.2f}")
            val_lbl.setStyleSheet(
                "font-size: 13px; font-weight: bold; color: #2b2b2b; background: transparent;"
            )

            pct_lbl = QLabel(f"{percent:.0f}%")
            pct_lbl.setStyleSheet(
                "font-size: 12px; color: #888; min-width: 38px; background: transparent;"
            )
            pct_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            row_layout.addWidget(color_dot)
            row_layout.addWidget(name_lbl)
            row_layout.addWidget(val_lbl)
            row_layout.addWidget(pct_lbl)
            self.tracker_layout.addWidget(row)

    # ── CHARTS ───────────────────────────────────────────────────────────────

    def plot_pie(self):
        fig = self.pie_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor("#FFFFFF")
        fig.patch.set_facecolor("#FFFFFF")

        if not self.sales_data:
            ax.text(0.5, 0.5, "No sales yet", ha="center", va="center",
                    fontsize=13, color="#aaa")
            ax.axis("off")
            self.pie_canvas.draw()
            return

        labels = list(self.sales_data.keys())
        values = list(self.sales_data.values())
        colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(labels))]

        wedges, texts, autotexts = ax.pie(
            values, labels=None, autopct="%1.0f%%", colors=colors,
            startangle=140, wedgeprops={"linewidth": 2, "edgecolor": "white"},
            pctdistance=0.75,
        )
        ax.axis("equal")
        for at in autotexts:
            at.set_fontsize(10)
            at.set_color("white")
            at.set_fontweight("bold")
        ax.legend(wedges, labels, loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9, frameon=False)
        fig.tight_layout()
        self.pie_canvas.draw()

    def plot_bar(self):
        fig = self.bar_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor("#fafaf7")
        fig.patch.set_facecolor("#FFFFFF")

        if not self.daily_sales:
            ax.text(0.5, 0.5, "No sales yet", ha="center", va="center",
                    fontsize=13, color="#aaa")
            ax.axis("off")
            self.bar_canvas.draw()
            return

        dates  = sorted(self.daily_sales.keys())
        values = [self.daily_sales[d] for d in dates]
        x_pos  = list(range(len(dates)))

        bars = ax.bar(x_pos, values, width=0.5, color="#34699A",
                      edgecolor="white", linewidth=1.5, zorder=3)
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(values) * 0.02,
                f"₱{val:,.0f}",
                ha="center", va="bottom", fontsize=9,
                color="#2b2b2b", fontweight="bold",
            )

        ax.set_xticks(x_pos)
        ax.set_xticklabels(dates, rotation=30, ha="right", fontsize=9)
        ax.set_ylabel("Sales (₱)", fontsize=10)
        ax.yaxis.set_tick_params(labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#ddd")
        ax.spines["bottom"].set_color("#ddd")
        ax.yaxis.grid(True, color="#ede9dc", linestyle="--", linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)
        fig.tight_layout()
        self.bar_canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportPage(role="admin")
    window.show()
    sys.exit(app.exec_())