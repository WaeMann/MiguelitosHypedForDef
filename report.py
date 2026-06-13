import sys
import re

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QGridLayout, QGraphicsDropShadowEffect,
    QSizePolicy, QScrollArea, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QFormLayout, QComboBox, QMessageBox,
    QCheckBox, QAbstractItemView,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QColor, QFont
from datetime import date

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from db import get_db_connection, hash_password


# ── Colour palette ──────────────────────────────────────────────────────────
GOLD     = "#E8D28C"
GOLD_D   = "#D9BE70"
GOLD_DD  = "#C9A850"
BLUE     = "#34699A"
BLUE_D   = "#2a567a"
GREEN    = "#1e7f3f"
GREEN_D  = "#166330"
RED      = "#c0392b"
RED_D    = "#8e1f16"
BG       = "#DED6B2"
SUBBG    = "#EDE7CC"
BG_L     = "#EFE9D1"
CREAM    = "#FFF8E7"
BORDER   = "#c8b87a"
WHITE    = "#FFFFFF"
DARK     = "#2b2b2b"
MID      = "#555555"
GRAY     = "#888888"
PANEL_BD = "#ede9dc"

# ── Shared style strings ────────────────────────────────────────────────────
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

TABLE_STYLE = """
QTableWidget {
    background: white;
    border: none;
    gridline-color: #ede9dc;
    font-size: 13px;
    color: #2b2b2b;
    outline: none;
}
QTableWidget::item          { padding: 5px 10px; border: none; }
QTableWidget::item:selected { background: #E8D28C; color: #222222; }
QHeaderView::section {
    background: #DED6B2;
    color: #333;
    font-weight: bold;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #c8b87a;
    font-size: 12px;
}
QScrollBar:vertical {
    background: #EFE9D1; width: 8px; border-radius: 4px; margin: 2px;
}
QScrollBar::handle:vertical {
    background: #c8b87a; border-radius: 4px; min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #EFE9D1; height: 8px; border-radius: 4px; margin: 2px;
}
QScrollBar::handle:horizontal {
    background: #c8b87a; border-radius: 4px; min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
"""

FIELD_STYLE = """
QLineEdit {
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    background: white;
    color: #333;
}
QLineEdit:focus { border: 1.5px solid #E8D28C; }
"""

COMBO_STYLE = """
QComboBox {
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    background: white;
    color: #333;
    min-height: 36px;
}
QComboBox:focus { border: 1.5px solid #E8D28C; }
QComboBox QAbstractItemView {
    background: white;
    selection-background-color: #E8D28C;
    selection-color: #222;
    border: 1px solid #ccc;
}
"""

DIALOG_BASE = f"QDialog {{ background-color: {CREAM}; }}"

CHART_COLORS = [
    "#E8D28C", "#34699A", "#c0392b", "#1e7f3f",
    "#e67e22", "#8e44ad", "#16a085", "#2c3e50",
]


# ── Generic helpers ──────────────────────────────────────────────────────────
def drop_shadow(widget, blur=25, x=3, y=3, alpha=150):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setXOffset(x)
    fx.setYOffset(y)
    fx.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(fx)
    return fx


def make_panel(bg=WHITE, radius=14):
    p = QFrame()
    p.setStyleSheet(f"QFrame {{ background-color: {bg}; border-radius: {radius}px; }}")
    return p


def styled_btn(text, bg, hover, fg="white", font_size=11, min_w=0):
    b = QPushButton(text)
    b.setCursor(Qt.PointingHandCursor)
    b.setFont(QFont("Segoe UI", font_size, QFont.Bold))
    mw = f"min-width: {min_w}px;" if min_w else ""
    b.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg}; color: {fg};
            border: none; border-radius: 8px;
            padding: 7px 18px; {mw}
        }}
        QPushButton:hover  {{ background-color: {hover}; }}
        QPushButton:pressed {{ background-color: {hover}; }}
    """)
    return b


def dialog_header(title_text, bg=GOLD, fg=DARK):
    hdr = QFrame()
    hdr.setFixedHeight(58)
    hdr.setStyleSheet(f"QFrame {{ background-color: {bg}; border-radius: 0px; }}")
    hl = QHBoxLayout(hdr)
    hl.setContentsMargins(22, 0, 22, 0)
    lbl = QLabel(title_text)
    lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
    lbl.setStyleSheet(f"color: {fg}; background: transparent;")
    hl.addWidget(lbl)
    return hdr


def validate_username(u):
    if len(u) < 3:
        return False, "Username must be at least 3 characters."
    if len(u) > 32:
        return False, "Username must be at most 32 characters."
    if not re.match(r"^[A-Za-z0-9_]+$", u):
        return False, "Only letters, numbers and underscores allowed."
    return True, "OK"


def validate_password(p):
    if len(p) < 6:
        return False, "Password must be at least 6 characters."
    return True, "OK"


def center_on_parent(dialog):
    if dialog.parent():
        pg = dialog.parent().geometry()
        dialog.move(
            pg.x() + (pg.width()  - dialog.width())  // 2,
            pg.y() + (pg.height() - dialog.height()) // 2,
        )


# ════════════════════════════════════════════════════════════════════════════
#  ORDER DETAIL DIALOG
# ════════════════════════════════════════════════════════════════════════════
class OrderDetailDialog(QDialog):
    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        self.order_id = order_id
        self.setWindowTitle(f"Order #{order_id} — Details")
        self.resize(500, 520)
        self.setMinimumSize(440, 400)
        self.setStyleSheet(DIALOG_BASE)
        self._build()
        center_on_parent(self)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(dialog_header(f"📋  Order #{self.order_id} — Details", BLUE, WHITE))

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(20, 16, 20, 16)
        bl.setSpacing(12)

        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute("SELECT * FROM orders WHERE id = %s", (self.order_id,))
            order = cur.fetchone()
            cur.execute(
                "SELECT product_name, quantity, size_name, item_price "
                "FROM order_items WHERE order_id = %s",
                (self.order_id,)
            )
            items = cur.fetchall()
            db.close()

            # Meta card
            meta = QFrame()
            meta.setStyleSheet(
                f"QFrame {{ background: white; border-radius: 10px; border: 1px solid {PANEL_BD}; }}"
            )
            mcl = QVBoxLayout(meta)
            mcl.setContentsMargins(16, 12, 16, 12)
            mcl.setSpacing(6)
            if order:
                for k_text, v_text in [
                    ("Order ID",    f"#{order['id']}"),
                    ("Date / Time", str(order.get("created_at", "—"))),
                    ("Total",       f"₱{float(order.get('total', 0)):,.2f}"),
                ]:
                    row_l = QHBoxLayout()
                    k_lbl = QLabel(f"{k_text}:")
                    k_lbl.setStyleSheet(
                        f"font-size: 12px; color: {GRAY}; background: transparent; min-width: 95px;"
                    )
                    v_lbl = QLabel(v_text)
                    v_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
                    v_lbl.setStyleSheet(f"color: {DARK}; background: transparent;")
                    row_l.addWidget(k_lbl)
                    row_l.addWidget(v_lbl)
                    row_l.addStretch()
                    mcl.addLayout(row_l)
            bl.addWidget(meta)

            items_hdr = QLabel("ORDER ITEMS")
            items_hdr.setStyleSheet(
                f"font-size: 10px; font-weight: bold; color: {GRAY}; "
                "letter-spacing: 2px; background: transparent;"
            )
            bl.addWidget(items_hdr)

            tbl = QTableWidget(len(items), 4)
            tbl.setHorizontalHeaderLabels(["Product", "Size", "Qty", "Price"])
            tbl.setStyleSheet(TABLE_STYLE)
            tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
            tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
            tbl.verticalHeader().setVisible(False)
            tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            for i in (1, 2, 3):
                tbl.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

            for r, itm in enumerate(items):
                tbl.setItem(r, 0, QTableWidgetItem(itm.get("product_name", "—")))
                s = QTableWidgetItem(itm.get("size_name") or "—")
                s.setTextAlignment(Qt.AlignCenter)
                tbl.setItem(r, 1, s)
                q = QTableWidgetItem(str(itm.get("quantity", 0)))
                q.setTextAlignment(Qt.AlignCenter)
                tbl.setItem(r, 2, q)
                p = QTableWidgetItem(f"₱{float(itm.get('item_price', 0)):,.2f}")
                p.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tbl.setItem(r, 3, p)
            bl.addWidget(tbl, stretch=1)

        except Exception as err:
            err_lbl = QLabel(f"Error loading order details:\n{err}")
            err_lbl.setStyleSheet(f"color: {RED}; font-size: 13px; background: transparent;")
            err_lbl.setWordWrap(True)
            bl.addWidget(err_lbl)

        bl.addStretch()
        close_btn = styled_btn("✖  Close", GOLD, GOLD_D, DARK)
        close_btn.setFixedWidth(110)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(close_btn)
        bl.addLayout(row)
        close_btn.clicked.connect(self.accept)
        root.addWidget(body, stretch=1)


# ════════════════════════════════════════════════════════════════════════════
#  ORDERS DIALOG
# ════════════════════════════════════════════════════════════════════════════
class OrdersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("All Orders")
        self.resize(840, 580)
        self.setMinimumSize(680, 460)
        self.setStyleSheet(DIALOG_BASE)
        self._build()
        self._load()
        center_on_parent(self)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(dialog_header("📋  All Orders", BLUE, WHITE))

        # Toolbar
        bar = QFrame()
        bar.setStyleSheet(f"QFrame {{ background: {CREAM}; border: none; }}")
        bar.setFixedHeight(50)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(16, 8, 16, 8)
        bl.setSpacing(8)
        ref_btn = styled_btn("🔄  Refresh", GOLD, GOLD_D, DARK, 10)
        ref_btn.clicked.connect(self._load)
        view_btn = styled_btn("🔍  View Details", BLUE, BLUE_D, font_size=10)
        view_btn.clicked.connect(self._view_detail)
        for b in (ref_btn, view_btn):
            bl.addWidget(b)
        bl.addStretch()
        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet(
            f"font-size: 12px; color: {GRAY}; background: transparent;"
        )
        bl.addWidget(self._count_lbl)
        root.addWidget(bar)

        # Body
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bvl = QVBoxLayout(body)
        bvl.setContentsMargins(16, 8, 16, 16)
        bvl.setSpacing(8)

        self._tbl = QTableWidget(0, 4)
        self._tbl.setHorizontalHeaderLabels(["Order ID", "Date / Time", "# Items", "Total"])
        self._tbl.setStyleSheet(TABLE_STYLE)
        self._tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tbl.setAlternatingRowColors(True)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._tbl.doubleClicked.connect(self._view_detail)
        bvl.addWidget(self._tbl)

        hint = QLabel("💡  Double-click any row to view full order details")
        hint.setStyleSheet(f"font-size: 11px; color: {GRAY}; background: transparent;")
        hint.setAlignment(Qt.AlignCenter)
        bvl.addWidget(hint)

        close_btn = styled_btn("✖  Close", GOLD, GOLD_D, DARK)
        close_btn.setFixedWidth(110)
        close_btn.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(close_btn)
        bvl.addLayout(row)
        root.addWidget(body, stretch=1)

    def _load(self):
        self._tbl.setRowCount(0)
        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute("""
                SELECT o.id, o.total, o.created_at,
                       COUNT(oi.id) AS item_count
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                GROUP BY o.id
                ORDER BY o.created_at DESC
                LIMIT 500
            """)
            rows = cur.fetchall()
            db.close()

            self._tbl.setRowCount(len(rows))
            for r, row in enumerate(rows):
                id_item = QTableWidgetItem(f"#{row['id']}")
                id_item.setTextAlignment(Qt.AlignCenter)
                id_item.setData(Qt.UserRole, row["id"])
                self._tbl.setItem(r, 0, id_item)
                self._tbl.setItem(r, 1, QTableWidgetItem(str(row["created_at"])))
                cnt = QTableWidgetItem(str(row["item_count"] or 0))
                cnt.setTextAlignment(Qt.AlignCenter)
                self._tbl.setItem(r, 2, cnt)
                total = QTableWidgetItem(f"₱{float(row['total'] or 0):,.2f}")
                total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self._tbl.setItem(r, 3, total)

            self._count_lbl.setText(f"{len(rows)} order(s) loaded")
        except Exception as err:
            QMessageBox.critical(self, "Database Error", f"Could not load orders:\n{err}")

    def _view_detail(self):
        row = self._tbl.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Please select an order first.")
            return
        id_item = self._tbl.item(row, 0)
        if not id_item:
            return
        OrderDetailDialog(id_item.data(Qt.UserRole), self).exec_()


# ════════════════════════════════════════════════════════════════════════════
#  SALES SUMMARY DIALOG
# ════════════════════════════════════════════════════════════════════════════
class SummaryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sales Summary")
        self.setFixedSize(560, 570)
        self.setStyleSheet(DIALOG_BASE)
        self._build()
        center_on_parent(self)

    # ── helpers ──────────────────────────────────────────────────────────────
    def _stat_card(self, val_lbl, label_text, color):
        card = make_panel()
        drop_shadow(card, blur=18, alpha=70)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)
        stripe = QFrame()
        stripe.setFixedHeight(4)
        stripe.setStyleSheet(f"background: {color}; border-radius: 2px;")
        cl.addWidget(stripe)
        inner = QVBoxLayout()
        inner.setContentsMargins(14, 10, 14, 10)
        inner.setSpacing(2)
        lbl_w = QLabel(label_text)
        lbl_w.setStyleSheet(f"font-size: 11px; color: {GRAY}; background: transparent;")
        val_lbl.setFont(QFont("Segoe UI", 17, QFont.Bold))
        val_lbl.setStyleSheet(f"color: {color}; background: transparent;")
        inner.addWidget(lbl_w)
        inner.addWidget(val_lbl)
        cl.addLayout(inner)
        return card

    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"font-size: 10px; font-weight: bold; color: {GRAY}; "
            "letter-spacing: 2px; background: transparent;"
        )
        return lbl

    # ── build ─────────────────────────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(dialog_header("📊  Sales Summary", GREEN, WHITE))

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(24, 18, 24, 18)
        bl.setSpacing(12)

        # ── today cards ──────────────────────────────────────────────────────
        bl.addWidget(self._section_label("TODAY'S SALES"))
        today_row = QHBoxLayout()
        today_row.setSpacing(10)
        self._t_orders = QLabel("—")
        self._t_rev    = QLabel("—")
        self._t_avg    = QLabel("—")
        for val_lbl, label, color in [
            (self._t_orders, "Orders",    BLUE),
            (self._t_rev,    "Revenue",   GREEN),
            (self._t_avg,    "Avg Order", GOLD_DD),
        ]:
            today_row.addWidget(self._stat_card(val_lbl, label, color))
        bl.addLayout(today_row)

        # ── all-time cards ───────────────────────────────────────────────────
        bl.addWidget(self._section_label("ALL-TIME SALES"))
        all_row = QHBoxLayout()
        all_row.setSpacing(10)
        self._a_orders = QLabel("—")
        self._a_rev    = QLabel("—")
        self._a_avg    = QLabel("—")
        for val_lbl, label, color in [
            (self._a_orders, "Orders",    BLUE),
            (self._a_rev,    "Revenue",   GREEN),
            (self._a_avg,    "Avg Order", GOLD_DD),
        ]:
            all_row.addWidget(self._stat_card(val_lbl, label, color))
        bl.addLayout(all_row)

        # ── top-5 panel ──────────────────────────────────────────────────────
        bl.addWidget(self._section_label("TOP 5 ITEMS  (ALL-TIME)"))
        self._top_frame = QFrame()
        self._top_frame.setStyleSheet(
            f"QFrame {{ background: white; border-radius: 10px; "
            f"border: 1px solid {PANEL_BD}; }}"
        )
        self._top_layout = QVBoxLayout(self._top_frame)
        self._top_layout.setContentsMargins(14, 10, 14, 10)
        self._top_layout.setSpacing(5)
        bl.addWidget(self._top_frame, stretch=1)

        # ── buttons ──────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        ref_btn   = styled_btn("🔄  Refresh", GOLD,  GOLD_D,  DARK, min_w=110)
        close_btn = styled_btn("✖  Close",    BLUE,  BLUE_D,       min_w=110)
        ref_btn.clicked.connect(self._load)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(ref_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        bl.addLayout(btn_row)

        root.addWidget(body, stretch=1)
        self._load()

    # ── data ─────────────────────────────────────────────────────────────────
    def _load(self):
        today_str = date.today().isoformat()
        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)

            # Today
            cur.execute(
                "SELECT COUNT(*) AS cnt, COALESCE(SUM(total), 0) AS rev "
                "FROM orders WHERE DATE(created_at) = %s",
                (today_str,)
            )
            row = cur.fetchone()
            tc = row["cnt"] or 0
            tr = float(row["rev"] or 0)
            self._t_orders.setText(str(tc))
            self._t_rev.setText(f"₱{tr:,.2f}")
            self._t_avg.setText(f"₱{tr / tc:,.2f}" if tc else "₱0.00")

            # All-time
            cur.execute(
                "SELECT COUNT(*) AS cnt, COALESCE(SUM(total), 0) AS rev FROM orders"
            )
            row = cur.fetchone()
            ac = row["cnt"] or 0
            ar = float(row["rev"] or 0)
            self._a_orders.setText(str(ac))
            self._a_rev.setText(f"₱{ar:,.2f}")
            self._a_avg.setText(f"₱{ar / ac:,.2f}" if ac else "₱0.00")

            # Top 5
            cur.execute("""
                SELECT product_name, SUM(item_price) AS total
                FROM order_items
                GROUP BY product_name
                ORDER BY total DESC
                LIMIT 5
            """)
            top = cur.fetchall()
            db.close()

            # Rebuild top-items list in-place
            while self._top_layout.count():
                w = self._top_layout.takeAt(0).widget()
                if w:
                    w.deleteLater()

            if not top:
                empty = QLabel("No sales data yet.")
                empty.setStyleSheet(
                    f"font-size: 13px; color: {GRAY}; background: transparent;"
                )
                empty.setAlignment(Qt.AlignCenter)
                self._top_layout.addWidget(empty)
            else:
                max_val = float(top[0]["total"] or 1)
                for i, itm in enumerate(top):
                    val = float(itm["total"] or 0)
                    row_w = QFrame()
                    row_w.setStyleSheet("QFrame { background: transparent; border: none; }")
                    row_l = QHBoxLayout(row_w)
                    row_l.setContentsMargins(0, 2, 0, 2)
                    row_l.setSpacing(8)

                    dot = QLabel("●")
                    dot.setStyleSheet(
                        f"color: {CHART_COLORS[i % len(CHART_COLORS)]}; "
                        "font-size: 16px; background: transparent;"
                    )
                    dot.setFixedWidth(20)

                    name_lbl = QLabel(itm["product_name"])
                    name_lbl.setStyleSheet(
                        f"font-size: 13px; color: {DARK}; background: transparent;"
                    )
                    name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

                    val_lbl = QLabel(f"₱{val:,.2f}")
                    val_lbl.setStyleSheet(
                        f"font-size: 13px; font-weight: bold; "
                        f"color: {DARK}; background: transparent;"
                    )
                    val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                    pct_lbl = QLabel(f"{val / max_val * 100:.0f}%")
                    pct_lbl.setStyleSheet(
                        f"font-size: 12px; color: {GRAY}; "
                        "background: transparent; min-width: 42px;"
                    )
                    pct_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                    for w in (dot, name_lbl, val_lbl, pct_lbl):
                        row_l.addWidget(w)
                    self._top_layout.addWidget(row_w)

        except Exception as err:
            for lbl in (self._t_orders, self._t_rev, self._t_avg,
                        self._a_orders, self._a_rev, self._a_avg):
                lbl.setText("—")
            print(f"[SummaryDialog] DB error: {err}")


# ════════════════════════════════════════════════════════════════════════════
#  ADD USER DIALOG
# ════════════════════════════════════════════════════════════════════════════
class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New User")
        self.setFixedSize(400, 420)
        self.setStyleSheet(DIALOG_BASE)
        self._build()
        center_on_parent(self)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(dialog_header("➕  Add New User", GREEN, WHITE))

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(30, 18, 30, 18)
        bl.setSpacing(8)

        def field(label, widget):
            lbl = QLabel(label)
            lbl.setStyleSheet(
                f"font-size: 12px; font-weight: bold; color: {MID}; background: transparent;"
            )
            bl.addWidget(lbl)
            bl.addWidget(widget)

        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("e.g.  juan_mango")
        self.user_edit.setStyleSheet(FIELD_STYLE)
        self.user_edit.setFixedHeight(38)
        field("Username", self.user_edit)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["cashier", "admin"])
        self.role_combo.setStyleSheet(COMBO_STYLE)
        field("Role", self.role_combo)

        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("min. 6 characters")
        self.pass_edit.setEchoMode(QLineEdit.Password)
        self.pass_edit.setStyleSheet(FIELD_STYLE)
        self.pass_edit.setFixedHeight(38)
        field("Password", self.pass_edit)

        self.confirm_edit = QLineEdit()
        self.confirm_edit.setPlaceholderText("confirm password")
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit.setStyleSheet(FIELD_STYLE)
        self.confirm_edit.setFixedHeight(38)
        field("Confirm Password", self.confirm_edit)

        show_cb = QCheckBox("Show Password")
        show_cb.setStyleSheet(f"font-size: 12px; color: {MID}; background: transparent;")
        show_cb.toggled.connect(self._toggle_pw)
        bl.addWidget(show_cb)

        self._status = QLabel("")
        self._status.setStyleSheet(
            f"color: {RED}; font-size: 12px; background: transparent;"
        )
        self._status.setWordWrap(True)
        bl.addWidget(self._status)

        bl.addStretch()
        btn_row = QHBoxLayout()
        cancel_btn = styled_btn("Cancel",          GOLD,  GOLD_D,  DARK)
        create_btn = styled_btn("➕  Create User",  GREEN, GREEN_D)
        cancel_btn.clicked.connect(self.reject)
        create_btn.clicked.connect(self._create)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(create_btn)
        bl.addLayout(btn_row)

        root.addWidget(body, stretch=1)
        self.user_edit.setFocus()

    def _toggle_pw(self, on):
        m = QLineEdit.Normal if on else QLineEdit.Password
        self.pass_edit.setEchoMode(m)
        self.confirm_edit.setEchoMode(m)

    def _create(self):
        u    = self.user_edit.text().strip()
        p    = self.pass_edit.text()
        cp   = self.confirm_edit.text()
        role = self.role_combo.currentText()

        ok, msg = validate_username(u)
        if not ok:
            self._status.setText(f"✖  {msg}"); return

        ok, msg = validate_password(p)
        if not ok:
            self._status.setText(f"✖  {msg}"); return

        if p != cp:
            self._status.setText("✖  Passwords do not match."); return

        try:
            db = get_db_connection()
            cur = db.cursor(buffered=True)
            cur.execute("SELECT id FROM users WHERE username = %s", (u,))
            if cur.fetchone():
                self._status.setText(f"✖  Username '{u}' already exists.")
                db.close(); return
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (u, hash_password(p), role),
            )
            db.commit()
            db.close()
            QMessageBox.information(
                self, "✅  User Created",
                f"Account '{u}'  ({role})  created successfully!"
            )
            self.accept()
        except Exception as err:
            self._status.setText(f"✖  {err}")


# ════════════════════════════════════════════════════════════════════════════
#  EDIT USER DIALOG
# ════════════════════════════════════════════════════════════════════════════
class EditUserDialog(QDialog):
    def __init__(self, user_row, parent=None):
        super().__init__(parent)
        self.user_row = user_row
        self.setWindowTitle(f"Edit — {user_row['username']}")
        self.setFixedSize(400, 410)
        self.setStyleSheet(DIALOG_BASE)
        self._build()
        center_on_parent(self)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(dialog_header(f"✏️  Edit: {self.user_row['username']}", GOLD, DARK))

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(30, 18, 30, 18)
        bl.setSpacing(8)

        def field(label, widget):
            lbl = QLabel(label)
            lbl.setStyleSheet(
                f"font-size: 12px; font-weight: bold; color: {MID}; background: transparent;"
            )
            bl.addWidget(lbl)
            bl.addWidget(widget)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["cashier", "admin"])
        self.role_combo.setCurrentText(self.user_row.get("role", "cashier"))
        self.role_combo.setStyleSheet(COMBO_STYLE)
        field("Role", self.role_combo)

        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("leave blank to keep current password")
        self.pass_edit.setEchoMode(QLineEdit.Password)
        self.pass_edit.setStyleSheet(FIELD_STYLE)
        self.pass_edit.setFixedHeight(38)
        field("New Password  (optional)", self.pass_edit)

        self.confirm_edit = QLineEdit()
        self.confirm_edit.setPlaceholderText("confirm new password")
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit.setStyleSheet(FIELD_STYLE)
        self.confirm_edit.setFixedHeight(38)
        field("Confirm Password", self.confirm_edit)

        show_cb = QCheckBox("Show Password")
        show_cb.setStyleSheet(f"font-size: 12px; color: {MID}; background: transparent;")
        show_cb.toggled.connect(self._toggle_pw)
        bl.addWidget(show_cb)

        self._status = QLabel("")
        self._status.setStyleSheet(
            f"color: {RED}; font-size: 12px; background: transparent;"
        )
        self._status.setWordWrap(True)
        bl.addWidget(self._status)

        bl.addStretch()
        btn_row = QHBoxLayout()
        cancel_btn = styled_btn("Cancel",           GOLD,  GOLD_D,  DARK)
        save_btn   = styled_btn("💾  Save Changes",  GREEN, GREEN_D)
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        bl.addLayout(btn_row)

        root.addWidget(body, stretch=1)

    def _toggle_pw(self, on):
        m = QLineEdit.Normal if on else QLineEdit.Password
        self.pass_edit.setEchoMode(m)
        self.confirm_edit.setEchoMode(m)

    def _save(self):
        new_role = self.role_combo.currentText()
        new_pass = self.pass_edit.text()
        confirm  = self.confirm_edit.text()

        if new_pass:
            ok, msg = validate_password(new_pass)
            if not ok:
                self._status.setText(f"✖  {msg}"); return
            if new_pass != confirm:
                self._status.setText("✖  Passwords do not match."); return

        try:
            db = get_db_connection()
            cur = db.cursor()
            if new_pass:
                cur.execute(
                    "UPDATE users SET role=%s, password_hash=%s WHERE id=%s",
                    (new_role, hash_password(new_pass), self.user_row["id"])
                )
            else:
                cur.execute(
                    "UPDATE users SET role=%s WHERE id=%s",
                    (new_role, self.user_row["id"])
                )
            db.commit()
            db.close()
            QMessageBox.information(self, "✅  Saved", "User updated successfully!")
            self.accept()
        except Exception as err:
            self._status.setText(f"✖  {err}")


# ════════════════════════════════════════════════════════════════════════════
#  USER MANAGEMENT DIALOG
# ════════════════════════════════════════════════════════════════════════════
class UsersDialog(QDialog):
    def __init__(self, current_username="admin", parent=None):
        super().__init__(parent)
        self.current_username = current_username
        self.setWindowTitle("User Management")
        self.resize(780, 540)
        self.setMinimumSize(640, 440)
        self.setStyleSheet(DIALOG_BASE)
        self._build()
        self._load()
        center_on_parent(self)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(dialog_header("👤  User Management", GOLD, DARK))

        # Toolbar
        bar = QFrame()
        bar.setStyleSheet(f"QFrame {{ background: {CREAM}; border: none; }}")
        bar.setFixedHeight(52)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(16, 8, 16, 8)
        bl.setSpacing(8)

        add_btn  = styled_btn("➕  Add User",        GREEN, GREEN_D, font_size=10)
        edit_btn = styled_btn("✏️  Edit Selected",   BLUE,  BLUE_D,  font_size=10)
        del_btn  = styled_btn("🗑  Delete Selected", RED,   RED_D,   font_size=10)
        ref_btn  = styled_btn("🔄  Refresh",          GOLD,  GOLD_D,  DARK, 10)

        add_btn.clicked.connect(self._add_user)
        edit_btn.clicked.connect(self._edit_user)
        del_btn.clicked.connect(self._delete_user)
        ref_btn.clicked.connect(self._load)

        for b in (add_btn, edit_btn, del_btn, ref_btn):
            bl.addWidget(b)
        bl.addStretch()

        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet(
            f"font-size: 12px; color: {GRAY}; background: transparent;"
        )
        bl.addWidget(self._count_lbl)
        root.addWidget(bar)

        # Table
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bvl = QVBoxLayout(body)
        bvl.setContentsMargins(16, 8, 16, 16)
        bvl.setSpacing(8)

        self._tbl = QTableWidget(0, 4)
        self._tbl.setHorizontalHeaderLabels(["ID", "Username", "Role", "Created At"])
        self._tbl.setStyleSheet(TABLE_STYLE)
        self._tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tbl.setAlternatingRowColors(True)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._tbl.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._tbl.doubleClicked.connect(self._edit_user)
        bvl.addWidget(self._tbl)

        hint = QLabel("💡  Double-click a row to edit  •  The last admin account cannot be deleted")
        hint.setStyleSheet(f"font-size: 11px; color: {GRAY}; background: transparent;")
        hint.setAlignment(Qt.AlignCenter)
        bvl.addWidget(hint)

        close_btn = styled_btn("✖  Close", GOLD, GOLD_D, DARK)
        close_btn.setFixedWidth(110)
        close_btn.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(close_btn)
        bvl.addLayout(row)

        root.addWidget(body, stretch=1)

    def _load(self):
        self._tbl.setRowCount(0)
        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute("SELECT * FROM users ORDER BY id")
            rows = cur.fetchall()
            db.close()

            self._tbl.setRowCount(len(rows))
            for r, row in enumerate(rows):
                id_item = QTableWidgetItem(str(row["id"]))
                id_item.setTextAlignment(Qt.AlignCenter)
                id_item.setData(Qt.UserRole, dict(row))
                self._tbl.setItem(r, 0, id_item)

                uname_item = QTableWidgetItem(row["username"])
                if row["username"] == self.current_username:
                    uname_item.setFont(QFont("Segoe UI", 12, QFont.Bold))
                    uname_item.setForeground(QColor(BLUE))
                self._tbl.setItem(r, 1, uname_item)

                role_item = QTableWidgetItem(row["role"].capitalize())
                role_item.setTextAlignment(Qt.AlignCenter)
                if row["role"] == "admin":
                    role_item.setForeground(QColor(RED))
                    role_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
                self._tbl.setItem(r, 2, role_item)

                self._tbl.setItem(r, 3, QTableWidgetItem(str(row.get("created_at", "—"))))

            self._count_lbl.setText(f"{len(rows)} user(s)")
        except Exception as err:
            QMessageBox.critical(self, "Database Error", f"Could not load users:\n{err}")

    def _get_selected_user(self):
        row = self._tbl.currentRow()
        if row < 0:
            return None
        id_item = self._tbl.item(row, 0)
        return id_item.data(Qt.UserRole) if id_item else None

    def _count_admins(self):
        try:
            db = get_db_connection()
            cur = db.cursor()
            cur.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
            cnt = cur.fetchone()[0]
            db.close()
            return cnt
        except Exception:
            return 99

    def _add_user(self):
        if AddUserDialog(self).exec_() == QDialog.Accepted:
            self._load()

    def _edit_user(self):
        user = self._get_selected_user()
        if not user:
            QMessageBox.information(self, "No Selection", "Please select a user to edit.")
            return
        if EditUserDialog(user, self).exec_() == QDialog.Accepted:
            self._load()

    def _delete_user(self):
        user = self._get_selected_user()
        if not user:
            QMessageBox.information(self, "No Selection", "Please select a user to delete.")
            return

        uname = user["username"]
        if uname == self.current_username:
            QMessageBox.warning(self, "Cannot Delete",
                                "You cannot delete your own account while logged in.")
            return

        if user["role"] == "admin" and self._count_admins() <= 1:
            QMessageBox.warning(self, "Cannot Delete",
                                "Cannot delete the last admin account.\n"
                                "Promote another user to admin first.")
            return

        reply = QMessageBox.question(
            self, "⚠  Confirm Deletion",
            f"Permanently delete user  '{uname}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            db = get_db_connection()
            cur = db.cursor()
            cur.execute("DELETE FROM users WHERE id = %s", (user["id"],))
            db.commit()
            db.close()
            self._load()
            QMessageBox.information(self, "Deleted", f"User '{uname}' has been deleted.")
        except Exception as err:
            QMessageBox.critical(self, "Database Error", f"Could not delete user:\n{err}")


# ════════════════════════════════════════════════════════════════════════════
#  DRAG SCROLL AREA  (unchanged)
# ════════════════════════════════════════════════════════════════════════════
class DragScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._drag_active  = False
        self._start_pos    = None
        self._start_scroll = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active  = True
            self._start_pos    = event.pos()
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
        self._start_pos   = None
        super().mouseReleaseEvent(event)


# ════════════════════════════════════════════════════════════════════════════
#  REPORT PAGE
# ════════════════════════════════════════════════════════════════════════════
class ReportPage(QWidget):
    def __init__(self, switch_callback=None, role="cashier", username=""):
        super().__init__()
        self.switch_callback = switch_callback
        self.role            = role
        self.username        = username
        self.sales_data      = {}
        self.daily_sales     = {}

        self.setWindowTitle("Hyped Mangoes — Reports")
        self.setStyleSheet("QWidget { background-color: #DED6B2; font-family: 'Segoe UI'; }")

        self._build_ui()
        self._load_from_db()
        self.refresh_report()

    # ── DB load ──────────────────────────────────────────────────────────────
    def _load_from_db(self):
        """Load all past orders from DB to pre-populate charts."""
        try:
            db = get_db_connection()
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

    # ── UI build ─────────────────────────────────────────────────────────────
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
                lambda checked, k=_k: self.switch_callback(k) if self.switch_callback else None
            )
            drop_shadow(btn, blur=18, alpha=100)
            nav_layout.addWidget(btn)

        tbl.addWidget(logo)
        tbl.addStretch()
        tbl.addLayout(nav_layout)
        tbl.addStretch()
        root.addWidget(top_bar)

        # ── GOLD SEPARATOR ───────────────────────────────────────────────────
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #c8b87a;")
        root.addWidget(sep)

        # ── ADMIN SUB-BAR  (admin only) ──────────────────────────────────────
        if self.role == "admin":
            admin_bar = QFrame()
            admin_bar.setFixedHeight(56)
            admin_bar.setStyleSheet(f"""
                QFrame {{
                    background-color: {SUBBG};
                    border-bottom: 1px solid {BORDER};
                }}
            """)
            abl = QHBoxLayout(admin_bar)
            abl.setContentsMargins(22, 0, 22, 0)
            abl.setSpacing(12)

            # "ADMIN" tag
            tag = QLabel("⚙  ADMIN")
            tag.setStyleSheet(
                f"font-size: 10px; font-weight: bold; color: {GRAY}; "
                "letter-spacing: 2px; background: transparent;"
            )
            abl.addWidget(tag)

            # Vertical divider
            vdiv = QFrame()
            vdiv.setFrameShape(QFrame.VLine)
            vdiv.setFixedHeight(28)
            vdiv.setStyleSheet(f"background: {BORDER}; border: none; max-width: 1px;")
            abl.addWidget(vdiv)

            # Action buttons
            btn_specs = [
                ("📋  Orders",   BLUE,  BLUE_D,  self._open_orders),
                ("📊  Summary",  GREEN, GREEN_D, self._open_summary),
                ("👤  Users",    RED,   RED_D,   self._open_users),
            ]
            for label, bg, hover, callback in btn_specs:
                b = QPushButton(label)
                b.setCursor(Qt.PointingHandCursor)
                b.setFont(QFont("Segoe UI", 11, QFont.Bold))
                b.setFixedHeight(36)
                b.setMinimumWidth(120)
                b.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {bg};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 0 18px;
                    }}
                    QPushButton:hover  {{ background-color: {hover}; }}
                    QPushButton:pressed {{ background-color: {hover}; }}
                """)
                b.clicked.connect(callback)
                drop_shadow(b, blur=12, alpha=70)
                abl.addWidget(b)

            abl.addStretch()

            # User badge (right side)
            if self.username:
                badge = QLabel(f"  👤 {self.username}  ·  Admin  ")
                badge.setStyleSheet(f"""
                    font-size: 11px; font-weight: bold;
                    color: {DARK};
                    background: {GOLD};
                    border-radius: 10px;
                    padding: 4px 12px;
                """)
                abl.addWidget(badge)

            root.addWidget(admin_bar)

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
            "font-size: 11px; font-weight: bold; color: #888; letter-spacing: 2px; background: transparent;"
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

    # ── Panel factory ─────────────────────────────────────────────────────────
    def _make_panel(self):
        panel = QFrame()
        panel.setStyleSheet("QFrame { background-color: white; border-radius: 14px; }")
        return panel

    # ── Admin button handlers ─────────────────────────────────────────────────
    def _open_orders(self):
        OrdersDialog(self).exec_()

    def _open_summary(self):
        SummaryDialog(self).exec_()

    def _open_users(self):
        UsersDialog(current_username=self.username, parent=self).exec_()

    # ── Data updates (called by IMS on complete_order) ────────────────────────
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

    # ── Tracker ───────────────────────────────────────────────────────────────
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
                "QFrame { background-color: #fafaf7; border-radius: 8px; border: 1px solid #ede9dc; }"
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
            name_lbl.setStyleSheet("font-size: 13px; color: #2c3e50; background: transparent;")
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

    # ── Charts ────────────────────────────────────────────────────────────────
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
                f"₱{val:,.0f}", ha="center", va="bottom",
                fontsize=9, color="#2b2b2b", fontweight="bold",
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
    window = ReportPage(role="admin", username="admin")
    window.show()
    sys.exit(app.exec_())