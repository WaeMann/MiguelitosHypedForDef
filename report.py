# This is the report.py (Do not remove line)

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QGridLayout, QGraphicsDropShadowEffect,
    QSizePolicy, QScrollArea, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QLineEdit, QComboBox,
    QCheckBox, QAbstractItemView, QTextEdit, QDateEdit, QFileDialog,
    QButtonGroup, QTabWidget
)
from PyQt5.QtCore import Qt, QSize, QDate, QDateTime, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QColor, QFont
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from datetime import date, timedelta, datetime
import datetime as _dt

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import time as _time

from db import (
    get_db_connection, gen_salt, hash_password_pbkdf2,
    audit as db_audit,
)


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

class ClockWidget(QWidget):
    """Live time + date label for the top bar (upper-right)."""
    def __init__(self, parent=None):
        super().__init__(parent)
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


def _dialog_header(layout, title: str, subtitle: str = "", close_cb=None):
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
    if close_cb is not None:
        x_btn = QPushButton("✕")
        x_btn.setFixedSize(28, 28)
        x_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #E8D28C;
                border: none; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: rgba(255,255,255,0.15); border-radius: 6px; }
        """)
        x_btn.clicked.connect(close_cb)
        hl.addWidget(x_btn)
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
# RECEIPT DIALOG  (replaces OrderDetailDialog)
# ─────────────────────────────────────────────────────────────────────────────

STORE_INFO = {
    "name":    "MIGUELITO'S",
    "branch":  "Ayala Malls Marikina Branch",
    "address": "Liwasang Kalayaan, Marikina, 1800 Metro Manila",
    "tel":     "(02) 8-MANGO-01",
    "tin":     "123-456-789-000",
}

class ReceiptDialog(QDialog):
    """Receipt viewer for a past order — styled to match the checkout receipt
    in script.py (same header/footer copy, column layout, peso formatting,
    and discount breakdown) so cashiers see a consistent receipt everywhere."""

    STORE_NAME    = "MIGUELITO'S HYPE MANGO"
    STORE_TAGLINE = "Your favorite mango shake destination!"
    RECEIPT_WIDTH = 42   # characters wide for the monospace receipt

    def __init__(self, order_id: int, order_total: float,
                 order_date: str, parent=None):
        super().__init__(parent)
        self.order_id    = order_id
        self.order_total = order_total
        self.order_date  = order_date
        self._drag_pos   = None   # for frameless window dragging
        self._hdr        = None   # set in _build, used to restrict drag zone

        self.setWindowTitle(f"Receipt – Order #{order_id}")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(480, 640)
        self.setStyleSheet("QDialog { background-color: #FFFDF7; }")
        self._build()
        _center_dialog(self)

    # ── Drag-to-move (header bar only) ──────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._hdr:
            # Only start drag when the press is inside the header frame
            if self._hdr.geometry().contains(event.pos()):
                self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar (amber, matching the checkout receipt) ────────────────
        hdr = QFrame()
        hdr.setFixedHeight(56)
        hdr.setStyleSheet("background-color: #E8D28C; cursor: move;")
        self._hdr = hdr   # keep reference for drag-zone check
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(20, 0, 20, 0)
        hl.setSpacing(10)
        title_lbl = QLabel("🧾  Order Receipt")
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_lbl.setStyleSheet("color: #2b2b2b; background: transparent;")
        hl.addWidget(title_lbl)
        hl.addStretch()
        close_btn_hdr = QPushButton("✕")
        close_btn_hdr.setFixedSize(28, 28)
        close_btn_hdr.setStyleSheet("""
            QPushButton {
                background: transparent; color: #2b2b2b;
                border: none; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: rgba(0,0,0,0.12); border-radius: 6px; }
        """)
        close_btn_hdr.clicked.connect(self.reject)
        hl.addWidget(close_btn_hdr)
        root.addWidget(hdr)

        # Amber accent line
        accent = QFrame()
        accent.setFixedHeight(3)
        accent.setStyleSheet("background-color: #D9A800; border: none;")
        root.addWidget(accent)

        # ── Scrollable receipt body ─────────────────────────────────────────
        from PyQt5.QtWidgets import QTextEdit
        self._txt = QTextEdit()
        self._txt.setReadOnly(True)
        self._txt.setFont(QFont("Courier New", 11))
        self._txt.setStyleSheet("""
            QTextEdit {
                background-color: #FFFDF7;
                color: #1a1a1a;
                border: none;
                padding: 12px 20px;
            }
        """)
        root.addWidget(self._txt, stretch=1)

        self._render_receipt()

        # ── Footer buttons ──────────────────────────────────────────────────
        foot = QFrame()
        foot.setFixedHeight(56)
        foot.setStyleSheet("background-color: #F5EFDC; border-top: 1px solid #E0D6B0;")
        fl = QHBoxLayout(foot)
        fl.setContentsMargins(20, 0, 20, 0)
        fl.setSpacing(10)

        print_btn = QPushButton("🖨  Print / Save")
        print_btn.setStyleSheet(BLUE_BTN_STYLE)
        print_btn.setFixedHeight(34)
        print_btn.clicked.connect(self._on_print)
        fl.addWidget(print_btn)

        fl.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(ADMIN_BTN_STYLE)
        close_btn.setFixedHeight(34)
        close_btn.clicked.connect(self.accept)
        fl.addWidget(close_btn)

        root.addWidget(foot)

    def _render_receipt(self):
        """Build the monospace receipt text and push it into the QTextEdit.
        Mirrors script.py's ReceiptDialog._render exactly: same header/footer
        copy, same column layout, same whole-peso formatting, and the same
        SUBTOTAL / discount / TOTAL DUE breakdown when a discount applied."""
        W = self.RECEIPT_WIDTH

        def center(text):
            return text.center(W)

        def divider(ch="─"):
            return ch * W

        def two_col(left, right):
            gap = max(1, W - len(left) - len(right))
            return left + " " * gap + right

        lines = []
        lines.append(divider("═"))
        lines.append(center(self.STORE_NAME))
        lines.append(center(self.STORE_TAGLINE))
        lines.append(divider("═"))
        lines.append("")

        lines.append(two_col("Order #  :", str(self.order_id)))
        lines.append(two_col("Date     :", str(self.order_date)))
        lines.append("")

        lines.append(divider())
        lines.append(f"{'ITEM':<24} {'QTY':>4} {'SIZE':>6}  {'TOTAL':>4}")
        lines.append(divider())

        items = []
        discount_amount = 0
        cash_paid = None
        change_given = None
        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                "SELECT discount_amount, cash_paid, change_given "
                "FROM orders WHERE id = %s",
                (self.order_id,),
            )
            order_row = cur.fetchone()
            if order_row:
                discount_amount = int(round(float(order_row.get("discount_amount") or 0)))
                if order_row.get("cash_paid") is not None:
                    cash_paid = int(round(float(order_row["cash_paid"])))
                if order_row.get("change_given") is not None:
                    change_given = int(round(float(order_row["change_given"])))

            cur.execute(
                "SELECT product_name, size_name, quantity, item_price "
                "FROM order_items WHERE order_id = %s",
                (self.order_id,),
            )
            items = cur.fetchall()
            db.close()
        except Exception as err:
            lines.append(f"  Error loading items: {err}")

        for itm in items:
            name  = (itm["product_name"] or "—")[:22]
            size  = itm["size_name"] or ""
            qty   = itm["quantity"]
            price = f"₱{int(round(float(itm['item_price']))):,}"
            label = f"{name} ×{qty}"
            right = f"{size:>6}  {price:>6}"
            gap   = max(1, W - len(label) - len(right))
            lines.append(label + " " * gap + right)

        lines.append(divider())

        total_int = int(round(float(self.order_total)))
        if discount_amount:
            subtotal = total_int + discount_amount
            lines.append(two_col("SUBTOTAL", f"₱{subtotal:,}"))
            lines.append(two_col("PWD/Senior Discount (20%)", f"–₱{discount_amount:,}"))
        lines.append(two_col("TOTAL DUE", f"₱{total_int:,}"))
        lines.append(divider("═"))
        lines.append("")

        if cash_paid is not None or change_given is not None:
            if cash_paid is not None:
                lines.append(two_col("Cash Tendered", f"₱{cash_paid:,}"))
            if change_given is not None:
                lines.append(two_col("Change", f"₱{change_given:,}"))
            lines.append("")

        lines.append(divider())
        lines.append(center("Thank you for visiting Miguelito's!"))
        lines.append(center('"Stay Hyped. Stay Mango."'))
        lines.append(divider())
        lines.append(center("*** Customer Copy ***"))
        lines.append("")

        self._txt.setPlainText("\n".join(lines))

    def _on_print(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self, "Print Receipt",
            f"Receipt for Order #{self.order_id} sent to printer.\n\n"
            "(Connect a receipt printer and configure it\n"
            "in system settings to enable printing.)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# ORDERS DIALOG  (enhanced with period filters, date range, export)
# ─────────────────────────────────────────────────────────────────────────────

class OrdersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_rows = []  # cache loaded rows for export
        self.setWindowTitle("Order History")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.resize(900, 620)
        self.setMinimumSize(720, 480)
        self.setStyleSheet("QDialog { background-color: #EFE9D1; font-family: 'Segoe UI'; }")
        self._build()
        _center_dialog(self)
        self._load()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        _dialog_header(root, "📋  Order History",
                       subtitle="View, filter and export orders by period",
                       close_cb=self.reject)

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(16, 12, 16, 12)
        bl.setSpacing(10)
        root.addWidget(body, stretch=1)

        # ── Period filter row ─────────────────────────────────────────────────
        period_row = QHBoxLayout()
        period_row.setSpacing(6)

        period_lbl = QLabel("Filter:")
        period_lbl.setStyleSheet("color:#555; font-size:12px; font-weight:bold; background:transparent;")
        period_row.addWidget(period_lbl)

        self._period_btns = {}
        self._active_period = "all"

        PERIOD_BTN_BASE = """
            QPushButton {{
                background-color: {bg};
                color: {fg};
                font-size: 12px;
                border-radius: 6px;
                font-weight: bold;
                border: 1px solid #c8b87a;
                padding: 4px 12px;
            }}
            QPushButton:hover {{ background-color: #D9BE70; color: #222; }}
        """
        for key, label in [("all","All"), ("daily","Today"), ("weekly","This Week"), ("monthly","This Month"), ("custom","Custom…")]:
            is_active = key == "all"
            btn = QPushButton(label)
            btn.setFixedHeight(30)
            btn.setCheckable(True)
            btn.setChecked(is_active)
            btn.setStyleSheet(PERIOD_BTN_BASE.format(
                bg="#E8D28C" if is_active else "white",
                fg="#222" if is_active else "#555"
            ))
            btn.clicked.connect(lambda checked, k=key: self._set_period(k))
            self._period_btns[key] = btn
            period_row.addWidget(btn)

        period_row.addStretch()

        # Export buttons
        pdf_btn = QPushButton("📄 Save PDF")
        pdf_btn.setStyleSheet(BLUE_BTN_STYLE)
        pdf_btn.setFixedHeight(30)
        pdf_btn.clicked.connect(self._export_pdf)
        period_row.addWidget(pdf_btn)

        print_btn = QPushButton("🖨 Print")
        print_btn.setStyleSheet(GREEN_BTN_STYLE)
        print_btn.setFixedHeight(30)
        print_btn.clicked.connect(self._print_report)
        period_row.addWidget(print_btn)

        bl.addLayout(period_row)

        # ── Custom date range row (hidden by default) ─────────────────────────
        self._custom_row = QFrame()
        self._custom_row.setStyleSheet("QFrame { background: #f5f0e0; border-radius: 8px; border: 1px solid #c8b87a; }")
        self._custom_row.setFixedHeight(50)
        cr = QHBoxLayout(self._custom_row)
        cr.setContentsMargins(14, 0, 14, 0)
        cr.setSpacing(10)

        from_lbl = QLabel("From:")
        from_lbl.setStyleSheet("background:transparent; font-size:12px; color:#555;")
        self._from_date = QDateEdit()
        self._from_date.setCalendarPopup(True)
        self._from_date.setDate(QDate.currentDate().addDays(-6))
        self._from_date.setFixedHeight(30)
        self._from_date.setStyleSheet(INPUT_STYLE)
        self._from_date.setDisplayFormat("yyyy-MM-dd")

        to_lbl = QLabel("To:")
        to_lbl.setStyleSheet("background:transparent; font-size:12px; color:#555;")
        self._to_date = QDateEdit()
        self._to_date.setCalendarPopup(True)
        self._to_date.setDate(QDate.currentDate())
        self._to_date.setFixedHeight(30)
        self._to_date.setStyleSheet(INPUT_STYLE)
        self._to_date.setDisplayFormat("yyyy-MM-dd")

        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet(ADMIN_BTN_STYLE)
        apply_btn.setFixedHeight(30)
        apply_btn.clicked.connect(self._load)

        cr.addWidget(from_lbl)
        cr.addWidget(self._from_date)
        cr.addWidget(to_lbl)
        cr.addWidget(self._to_date)
        cr.addWidget(apply_btn)
        cr.addStretch()
        self._custom_row.setVisible(False)
        bl.addWidget(self._custom_row)

        # ── Toolbar (count, refresh) ──────────────────────────────────────────
        tb = QHBoxLayout()
        self._count_lbl = QLabel("Loading…")
        self._count_lbl.setStyleSheet("color:#888; font-size:12px; background:transparent;")
        tb.addWidget(self._count_lbl)
        tb.addStretch()

        self._total_lbl = QLabel("")
        self._total_lbl.setStyleSheet("color:#2b2b2b; font-size:13px; font-weight:bold; background:transparent;")
        tb.addWidget(self._total_lbl)

        refresh_btn = QPushButton("🔄  Refresh")
        refresh_btn.setStyleSheet(ADMIN_BTN_STYLE)
        refresh_btn.setFixedHeight(34)
        refresh_btn.clicked.connect(self._load)
        tb.addWidget(refresh_btn)
        bl.addLayout(tb)

        # ── Orders table ─────────────────────────────────────────────────────
        self._table = QTableWidget()
        self._table.setStyleSheet(TABLE_STYLE)
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Order ID", "Date / Time", "# Items", "Total"])
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

        hint = QLabel("Double-click any row to view its receipt.")
        hint.setStyleSheet("color:#bbb; font-size:11px; background:transparent;")
        hint.setAlignment(Qt.AlignCenter)
        bl.addWidget(hint)

    def _set_period(self, key: str):
        self._active_period = key
        PERIOD_BTN_BASE = """
            QPushButton {{
                background-color: {bg};
                color: {fg};
                font-size: 12px;
                border-radius: 6px;
                font-weight: bold;
                border: 1px solid #c8b87a;
                padding: 4px 12px;
            }}
            QPushButton:hover {{ background-color: #D9BE70; color: #222; }}
        """
        for k, btn in self._period_btns.items():
            is_active = (k == key)
            btn.setChecked(is_active)
            btn.setStyleSheet(PERIOD_BTN_BASE.format(
                bg="#E8D28C" if is_active else "white",
                fg="#222" if is_active else "#555"
            ))
        self._custom_row.setVisible(key == "custom")
        if key != "custom":
            self._load()

    def _get_date_range(self):
        """Return (start_str, end_str) for the active period, or None for all."""
        today = date.today()
        if self._active_period == "daily":
            return today.isoformat(), today.isoformat()
        elif self._active_period == "weekly":
            start = today - timedelta(days=today.weekday())
            return start.isoformat(), today.isoformat()
        elif self._active_period == "monthly":
            start = today.replace(day=1)
            return start.isoformat(), today.isoformat()
        elif self._active_period == "custom":
            f = self._from_date.date().toPyDate()
            t = self._to_date.date().toPyDate()
            return f.isoformat(), t.isoformat()
        return None, None  # all

    def _load(self):
        self._table.setRowCount(0)
        self._count_lbl.setText("Loading…")
        self._total_lbl.setText("")
        start_str, end_str = self._get_date_range()

        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)
            if start_str:
                cur.execute("""
                    SELECT o.id, o.total, o.created_at,
                           COALESCE(COUNT(oi.id), 0) AS item_count
                    FROM orders o
                    LEFT JOIN order_items oi ON oi.order_id = o.id
                    WHERE DATE(o.created_at) BETWEEN %s AND %s
                    GROUP BY o.id
                    ORDER BY o.id DESC
                """, (start_str, end_str))
            else:
                cur.execute("""
                    SELECT o.id, o.total, o.created_at,
                           COALESCE(COUNT(oi.id), 0) AS item_count
                    FROM orders o
                    LEFT JOIN order_items oi ON oi.order_id = o.id
                    GROUP BY o.id
                    ORDER BY o.id DESC
                    LIMIT 1000
                """)
            rows = cur.fetchall()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))
            self._count_lbl.setText("Error loading data.")
            return

        self._current_rows = rows
        grand_total = sum(float(r["total"]) for r in rows)
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

        period_label = {
            "all": "All time", "daily": "Today", "weekly": "This week",
            "monthly": "This month", "custom": "Custom range"
        }.get(self._active_period, "")
        self._count_lbl.setText(f"{len(rows)} record(s)  ·  {period_label}")
        if rows:
            self._total_lbl.setText(f"Total: ₱{grand_total:,.2f}")

    def _view_detail(self, index):
        r = index.row()
        order_id   = int(self._table.item(r, 0).text())
        order_date = self._table.item(r, 1).text()
        total_str  = self._table.item(r, 3).text().replace("₱", "").replace(",", "")
        try:
            total = float(total_str)
        except ValueError:
            total = 0.0
        dlg = ReceiptDialog(order_id, total, order_date, parent=self)
        dlg.exec_()

    # ── Export helpers ────────────────────────────────────────────────────────

    def _build_report_text(self) -> str:
        """Build a plain-text report string for printing/PDF."""
        rows = self._current_rows
        period_label = {
            "all": "All Time", "daily": "Today", "weekly": "This Week",
            "monthly": "This Month", "custom": "Custom Range"
        }.get(self._active_period, "")
        start_str, end_str = self._get_date_range()
        date_range_info = f"{start_str}  to  {end_str}" if start_str else "All records"

        grand_total = sum(float(r["total"]) for r in rows)
        lines = []
        lines.append("═" * 60)
        lines.append(f"  {STORE_INFO['name']}  —  {STORE_INFO['branch']}")
        lines.append(f"  {STORE_INFO['address']}")
        lines.append("═" * 60)
        lines.append(f"  ORDER HISTORY REPORT  ({period_label})")
        lines.append(f"  Period: {date_range_info}")
        lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("─" * 60)
        lines.append(f"  {'Order ID':<12} {'Date / Time':<25} {'Items':>5} {'Total':>12}")
        lines.append("─" * 60)
        for row in rows:
            oid  = str(row["id"])
            dt   = str(row["created_at"])[:19]
            cnt  = str(row["item_count"] or 0)
            tot  = f"₱{float(row['total']):>10,.2f}"
            lines.append(f"  {oid:<12} {dt:<25} {cnt:>5} {tot:>12}")
        lines.append("─" * 60)
        lines.append(f"  {'TOTAL ORDERS:':<38} {len(rows):>5}")
        lines.append(f"  {'GRAND TOTAL REVENUE:':<38} ₱{grand_total:>9,.2f}")
        lines.append("═" * 60)
        return "\n".join(lines)

    def _export_pdf(self):
        """Save a PDF copy of the current order report."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Report as PDF", f"orders_report_{date.today().isoformat()}.pdf",
            "PDF Files (*.pdf)"
        )
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
        self._do_print(printer)
        QMessageBox.information(self, "PDF Saved", f"Report saved to:\n{path}")

    def _print_report(self):
        """Send the current order report to the system printer."""
        printer = QPrinter(QPrinter.HighResolution)
        dlg = QPrintDialog(printer, self)
        if dlg.exec_() != QPrintDialog.Accepted:
            return
        self._do_print(printer)

    def _do_print(self, printer: QPrinter):
        from PyQt5.QtGui import QPainter, QFont, QFontMetrics
        painter = QPainter()
        if not painter.begin(printer):
            QMessageBox.critical(self, "Print Error", "Could not start printer.")
            return

        report_text = self._build_report_text()
        font = QFont("Courier New", 9)
        painter.setFont(font)
        # Bind the metrics to the printer device so line_height is measured
        # in the *printer's* DPI space, matching the coordinates drawText()
        # uses below. Using screen-bound metrics here was the root cause of
        # the exported PDF/printed report collapsing to the top of the page.
        fm = QFontMetrics(font, printer)
        line_height = fm.height() + 2
        page_rect = printer.pageRect()
        margin = max(40, printer.resolution() // 4)
        x = margin
        y = margin
        max_y = page_rect.height() - margin

        for line in report_text.split("\n"):
            if y + line_height > max_y:
                printer.newPage()
                y = margin
            painter.drawText(x, y + fm.ascent(), line)
            y += line_height

        painter.end()



# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY DIALOG
# ─────────────────────────────────────────────────────────────────────────────

class SummaryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sales Summary")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
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
                       subtitle="Today's performance at a glance",
                       close_cb=self.reject)

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
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(420, 380)
        self.setStyleSheet("QDialog { background-color: #EFE9D1; font-family: 'Segoe UI'; }")
        self._build()
        _center_dialog(self)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        _dialog_header(root, "➕  Add New User", close_cb=self.reject)

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
            salt  = gen_salt()
            phash = hash_password_pbkdf2(pwd, salt)
            cur.execute(
                "INSERT INTO users (username, password_hash, salt, role) "
                "VALUES (%s, %s, %s, %s)",
                (uname, phash, salt, role),
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
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(420, 320)
        self.setStyleSheet("QDialog { background-color: #EFE9D1; font-family: 'Segoe UI'; }")
        self._build()
        _center_dialog(self)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        _dialog_header(root, "🔑  Reset Password",
                       subtitle=f"Account: {self.username}",
                       close_cb=self.reject)

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
            salt  = gen_salt()
            phash = hash_password_pbkdf2(p1, salt)
            db    = get_db_connection()
            cur   = db.cursor()
            cur.execute(
                "UPDATE users SET password_hash=%s, salt=%s WHERE id=%s",
                (phash, salt, self.user_id),
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
    def __init__(self, current_username: str = "", parent=None):
        super().__init__(parent)
        self.current_username = current_username
        self.setWindowTitle("Manage Users")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.resize(880, 540)
        self.setMinimumSize(720, 440)
        self.setStyleSheet("QDialog { background-color: #EFE9D1; font-family: 'Segoe UI'; }")
        self._build()
        _center_dialog(self)
        self._load()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        _dialog_header(root, "👤  Manage Users",
                       subtitle="Add, reset passwords, change roles, or delete accounts",
                       close_cb=self.reject)

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

        self._unlock_btn = QPushButton("🔓  Unlock User")
        self._unlock_btn.setStyleSheet(AMBER_BTN_STYLE)
        self._unlock_btn.setFixedHeight(34)
        self._unlock_btn.clicked.connect(self._unlock_user)
        tb.addWidget(self._unlock_btn)

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
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["ID", "Username", "Role", "Created", "Fails", "Status"]
        )
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._table.setColumnWidth(0, 45)
        self._table.setColumnWidth(2, 80)
        self._table.setColumnWidth(4, 50)
        self._table.setColumnWidth(5, 100)
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
                "SELECT id, username, role, created_at, "
                "failed_attempts, locked_until FROM users ORDER BY id"
            )
            rows = cur.fetchall()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))
            return

        now_ts = int(_time.time())
        self._table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            id_item = QTableWidgetItem(str(row["id"]))
            id_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(r, 0, id_item)

            self._table.setItem(r, 1, QTableWidgetItem(row["username"]))

            role_item = QTableWidgetItem(row["role"].title())
            role_item.setTextAlignment(Qt.AlignCenter)
            role_item.setForeground(
                QColor("#e67e22") if row["role"] == "admin" else QColor("#34699A")
            )
            self._table.setItem(r, 2, role_item)

            created = str(row["created_at"]) if row["created_at"] else "—"
            self._table.setItem(r, 3, QTableWidgetItem(created))

            fails = int(row.get("failed_attempts") or 0)
            fail_item = QTableWidgetItem(str(fails))
            fail_item.setTextAlignment(Qt.AlignCenter)
            if fails > 0:
                fail_item.setForeground(QColor("#c0392b"))
            self._table.setItem(r, 4, fail_item)

            locked_until = int(row.get("locked_until") or 0)
            is_locked = locked_until > now_ts
            status_item = QTableWidgetItem("🔒 Locked" if is_locked else "✅ Active")
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(
                QColor("#c0392b") if is_locked else QColor("#1e7f3f")
            )
            self._table.setItem(r, 5, status_item)

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

    def _unlock_user(self):
        sel = self._selected()
        if sel is None:
            return
        uid, uname, _ = sel

        reply = QMessageBox.question(
            self, "Unlock User",
            f"Unlock account '{uname}' and reset failed attempts?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            db  = get_db_connection()
            cur = db.cursor()
            cur.execute(
                "UPDATE users SET failed_attempts = 0, locked_until = 0 "
                "WHERE id = %s",
                (uid,),
            )
            db.commit()
            db.close()
            QMessageBox.information(
                self, "Unlocked",
                f"Account '{uname}' has been unlocked successfully.",
            )
            self._load()
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))


# ─────────────────────────────────────────────────────────────────────────────
# SECURITY DIALOG  (Login Log · Sessions · Audit Log)
# ─────────────────────────────────────────────────────────────────────────────

class SecurityDialog(QDialog):
    """Three-tab security panel: Login Log, Session History, and Audit Trail."""

    # Colour map used by the Audit Log tab
    _AUDIT_BG = {
        "LOGIN":         QColor("#D1FAE5"),
        "LOGOUT":        QColor("#EDE9FE"),
        "ORDER_PLACED":  QColor("#DBEAFE"),
        "USER_CREATED":  QColor("#CFFAFE"),
        "USER_EDITED":   QColor("#FEF9C3"),
        "USER_DELETED":  QColor("#FEE2E2"),
        "USER_UNLOCKED": QColor("#FEF3C7"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Security Logs")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.resize(1060, 640)
        self.setMinimumSize(860, 520)
        self.setStyleSheet(
            "QDialog { background-color: #EFE9D1; font-family: 'Segoe UI'; }"
        )
        self._build()
        _center_dialog(self)
        self._reload_login_log()
        self._reload_sessions()
        self._reload_audit()

    # ── LAYOUT ────────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        _dialog_header(
            root,
            "🔒  Security Logs",
            subtitle="Login activity · Session history · Audit trail",
            close_cb=self.reject,
        )

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane  { border: none; background: #EFE9D1; }
            QTabBar::tab {
                background: #2b2b2b;
                color: #E8D28C;
                font-weight: bold;
                font-size: 12px;
                padding: 9px 22px;
                border: none;
                min-width: 160px;
            }
            QTabBar::tab:selected          { background: #E8D28C; color: #2b2b2b; }
            QTabBar::tab:hover:!selected   { background: #3d3d3d; }
        """)

        # ── Tab 1: Login Log ─────────────────────────────────────────────────
        login_w = QWidget()
        login_w.setStyleSheet("background: #EFE9D1;")
        self._build_login_tab(login_w)
        tabs.addTab(login_w, "🔐  Login Log")

        # ── Tab 2: Sessions ──────────────────────────────────────────────────
        ses_w = QWidget()
        ses_w.setStyleSheet("background: #EFE9D1;")
        self._build_session_tab(ses_w)
        tabs.addTab(ses_w, "⏱  Sessions")

        # ── Tab 3: Audit Log ─────────────────────────────────────────────────
        aud_w = QWidget()
        aud_w.setStyleSheet("background: #EFE9D1;")
        self._build_audit_tab(aud_w)
        tabs.addTab(aud_w, "📜  Audit Log")

        root.addWidget(tabs, stretch=1)

    # ── SHARED HELPERS ────────────────────────────────────────────────────────

    @staticmethod
    def _filter_style(active: bool) -> str:
        if active:
            return (
                "QPushButton { background-color:#2b2b2b; color:#E8D28C; "
                "font-size:12px; border-radius:6px; font-weight:bold; "
                "border:none; padding:4px 14px; }"
            )
        return (
            "QPushButton { background-color:white; color:#555; "
            "font-size:12px; border-radius:6px; font-weight:bold; "
            "border:1px solid #c8b87a; padding:4px 14px; } "
            "QPushButton:hover { background-color:#E8D28C; color:#222; }"
        )

    @staticmethod
    def _std_table(parent_layout: QVBoxLayout, headers: list,
                   stretch_col: int, col_widths: dict) -> "QTableWidget":
        """Create a standardised read-only table and add it to parent_layout."""
        tbl = QTableWidget()
        tbl.setStyleSheet(TABLE_STYLE)
        tbl.setColumnCount(len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.horizontalHeader().setSectionResizeMode(stretch_col, QHeaderView.Stretch)
        for col, w in col_widths.items():
            tbl.setColumnWidth(col, w)
        tbl.verticalHeader().setVisible(False)
        tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        tbl.setAlternatingRowColors(True)
        tbl.setShowGrid(False)
        parent_layout.addWidget(tbl)
        return tbl

    @staticmethod
    def _toolbar(count_attr_holder, refresh_cb,
                 extra_left=None) -> tuple:
        """Build the standard refresh toolbar; return (layout, count_label)."""
        tb = QHBoxLayout()
        tb.setSpacing(8)
        if extra_left:
            for w in extra_left:
                tb.addWidget(w)
        count_lbl = QLabel("")
        count_lbl.setStyleSheet(
            "color:#888; font-size:12px; background:transparent;"
        )
        tb.addStretch()
        tb.addWidget(count_lbl)
        ref = QPushButton("🔄  Refresh")
        ref.setStyleSheet(ADMIN_BTN_STYLE)
        ref.setFixedHeight(34)
        ref.clicked.connect(refresh_cb)
        tb.addWidget(ref)
        return tb, count_lbl

    # ── LOGIN LOG TAB ─────────────────────────────────────────────────────────

    def _build_login_tab(self, parent: QWidget):
        lay = QVBoxLayout(parent)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(10)

        # ── Stats pills ──────────────────────────────────────────────────────
        stats_frame = QFrame()
        stats_frame.setStyleSheet("QFrame { background: transparent; }")
        sf_lay = QHBoxLayout(stats_frame)
        sf_lay.setContentsMargins(0, 0, 0, 0)
        sf_lay.setSpacing(12)

        stats_title = QLabel("Today's Login Activity")
        stats_title.setStyleSheet(
            "font-size:14px; font-weight:bold; color:#2b2b2b; background:transparent;"
        )
        sf_lay.addWidget(stats_title)

        self._log_stat_vals = {}
        for key, label, color in [
            ("total",   "Total Attempts", "#2b2b2b"),
            ("success", "✅ Successful",   "#1e7f3f"),
            ("failed",  "✖ Failed",        "#c0392b"),
        ]:
            pill = QFrame()
            pill.setStyleSheet(
                "QFrame { background:white; border-radius:8px; border:1px solid #ede9dc; }"
            )
            drop_shadow(pill, blur=10, alpha=40)
            pl = QVBoxLayout(pill)
            pl.setContentsMargins(14, 6, 14, 6)
            pl.setSpacing(0)
            lbl_w = QLabel(label)
            lbl_w.setStyleSheet(
                "font-size:11px; color:#888; background:transparent; border:none;"
            )
            val_w = QLabel("—")
            val_w.setStyleSheet(
                f"font-size:20px; font-weight:bold; color:{color}; "
                "background:transparent; border:none;"
            )
            pl.addWidget(lbl_w)
            pl.addWidget(val_w)
            self._log_stat_vals[key] = val_w
            sf_lay.addWidget(pill)

        sf_lay.addStretch()
        lay.addWidget(stats_frame)

        # ── Filter row + toolbar ─────────────────────────────────────────────
        filter_row = QHBoxLayout()
        filter_row.setSpacing(6)
        filter_lbl = QLabel("Filter:")
        filter_lbl.setStyleSheet(
            "color:#555; font-size:12px; font-weight:bold; background:transparent;"
        )
        filter_row.addWidget(filter_lbl)

        self._log_filter_grp = QButtonGroup(self)
        self._log_filter_grp.setExclusive(True)
        for label, val in [("All","all"),("✅ Success","success"),("✖ Failed","failed")]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setProperty("fval", val)
            is_first = val == "all"
            btn.setChecked(is_first)
            btn.setStyleSheet(self._filter_style(is_first))
            btn.clicked.connect(
                lambda _checked, b=btn: self._apply_log_filter(b)
            )
            self._log_filter_grp.addButton(btn)
            filter_row.addWidget(btn)

        filter_row.addStretch()
        self._log_count_lbl = QLabel("")
        self._log_count_lbl.setStyleSheet(
            "color:#888; font-size:12px; background:transparent;"
        )
        filter_row.addWidget(self._log_count_lbl)
        ref_log = QPushButton("🔄  Refresh")
        ref_log.setStyleSheet(ADMIN_BTN_STYLE)
        ref_log.setFixedHeight(34)
        ref_log.clicked.connect(self._reload_login_log)
        filter_row.addWidget(ref_log)
        lay.addLayout(filter_row)

        # ── Table ────────────────────────────────────────────────────────────
        self._log_table = self._std_table(
            lay,
            headers=["#","Username","Result","Reason / Info","Session ID","Timestamp"],
            stretch_col=3,
            col_widths={0:50, 1:110, 2:90, 4:190, 5:150},
        )

    def _apply_log_filter(self, clicked_btn: "QPushButton"):
        for btn in self._log_filter_grp.buttons():
            btn.setStyleSheet(self._filter_style(btn is clicked_btn))
        self._reload_login_log()

    def _active_log_filter(self) -> str:
        for btn in self._log_filter_grp.buttons():
            if btn.isChecked():
                return btn.property("fval")
        return "all"

    def _reload_login_log(self):
        # Refresh today's stats
        today_str = date.today().isoformat()
        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                """SELECT COUNT(*) AS total,
                          COALESCE(SUM(success), 0)           AS successes,
                          COUNT(*) - COALESCE(SUM(success),0) AS failures
                   FROM login_log
                   WHERE DATE(logged_at) = %s""",
                (today_str,),
            )
            row = cur.fetchone()
            db.close()
            if row:
                self._log_stat_vals["total"].setText(str(int(row["total"]   or 0)))
                self._log_stat_vals["success"].setText(str(int(row["successes"] or 0)))
                self._log_stat_vals["failed"].setText(str(int(row["failures"]  or 0)))
        except Exception as err:
            print(f"[Security/login-stats] {err}")

        # Reload table rows
        flt = self._active_log_filter()
        self._log_table.setRowCount(0)
        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM login_log ORDER BY id DESC LIMIT 500"
            )
            rows = cur.fetchall()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))
            return

        display = []
        for row in rows:
            success = bool(int(row.get("success", 0) or 0))
            if flt == "success" and not success:
                continue
            if flt == "failed" and success:
                continue
            display.append((row, success))

        self._log_table.setRowCount(len(display))
        for r, (row, success) in enumerate(display):
            result_txt = "✅ Success" if success else "✖ Failed"
            bg = QColor("#D1FAE5") if success else QColor("#FEE2E2")

            cells = [
                (str(row.get("id", "")),            Qt.AlignCenter),
                (str(row.get("username", "—")),     Qt.AlignLeft),
                (result_txt,                         Qt.AlignCenter),
                (str(row.get("reason", "") or "—"), Qt.AlignLeft),
                (str(row.get("session_id","") or "—"), Qt.AlignLeft),
                (str(row.get("logged_at","") or "—"),  Qt.AlignLeft),
            ]
            for c, (text, align) in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(align | Qt.AlignVCenter)
                item.setBackground(bg)
                self._log_table.setItem(r, c, item)

        self._log_count_lbl.setText(f"{len(display)} record(s)")

    # ── SESSION LOG TAB ───────────────────────────────────────────────────────

    def _build_session_tab(self, parent: QWidget):
        lay = QVBoxLayout(parent)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(10)

        # Toolbar
        tb = QHBoxLayout()
        tb.setSpacing(8)
        self._ses_count_lbl = QLabel("")
        self._ses_count_lbl.setStyleSheet(
            "color:#888; font-size:12px; background:transparent;"
        )
        tb.addWidget(self._ses_count_lbl)
        tb.addStretch()
        ref_ses = QPushButton("🔄  Refresh")
        ref_ses.setStyleSheet(ADMIN_BTN_STYLE)
        ref_ses.setFixedHeight(34)
        ref_ses.clicked.connect(self._reload_sessions)
        tb.addWidget(ref_ses)
        lay.addLayout(tb)

        # Table
        self._ses_table = self._std_table(
            lay,
            headers=["#","Username","Session ID","Login Time","Logout Time","Duration","Logout Type"],
            stretch_col=2,
            col_widths={0:50, 1:110, 3:150, 4:150, 5:90, 6:100},
        )

        hint = QLabel("Blue = active session  |  Amber = ended by timeout")
        hint.setStyleSheet("color:#bbb; font-size:11px; background:transparent;")
        hint.setAlignment(Qt.AlignCenter)
        lay.addWidget(hint)

    def _reload_sessions(self):
        self._ses_table.setRowCount(0)
        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM session_log ORDER BY id DESC LIMIT 200"
            )
            rows = cur.fetchall()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))
            return

        self._ses_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            dur_s  = row.get("duration_s")
            dur_t  = (
                f"{int(dur_s)//60}m {int(dur_s)%60}s"
                if dur_s is not None else "Active"
            )
            ltype = str(row.get("logout_type", "") or "—")

            is_active  = row.get("logout_at") is None
            is_timeout = (not is_active) and ltype == "timeout"

            if is_active:
                bg = QColor("#DBEAFE")   # blue — still logged in
            elif is_timeout:
                bg = QColor("#FEF3C7")   # amber — timed out
            else:
                bg = None

            cells = [
                (str(row.get("id", "")),                      Qt.AlignCenter),
                (str(row.get("username", "—")),               Qt.AlignLeft),
                (str(row.get("session_id", "—")),             Qt.AlignLeft),
                (str(row.get("login_at",  "—") or "—"),      Qt.AlignLeft),
                (str(row.get("logout_at", "—") or "—"),      Qt.AlignLeft),
                (dur_t,                                        Qt.AlignCenter),
                (ltype,                                        Qt.AlignCenter),
            ]
            for c, (text, align) in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(align | Qt.AlignVCenter)
                if bg:
                    item.setBackground(bg)
                self._ses_table.setItem(r, c, item)

        self._ses_count_lbl.setText(f"{len(rows)} record(s)")

    # ── AUDIT LOG TAB ─────────────────────────────────────────────────────────

    def _build_audit_tab(self, parent: QWidget):
        lay = QVBoxLayout(parent)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(10)

        # Filter bar
        fb = QHBoxLayout()
        fb.setSpacing(5)
        flbl = QLabel("Filter:")
        flbl.setStyleSheet(
            "color:#555; font-size:12px; font-weight:bold; background:transparent;"
        )
        fb.addWidget(flbl)

        self._aud_filter_grp = QButtonGroup(self)
        self._aud_filter_grp.setExclusive(True)
        for action in [
            "All","LOGIN","LOGOUT","ORDER_PLACED",
            "USER_CREATED","USER_EDITED","USER_DELETED","USER_UNLOCKED",
        ]:
            btn = QPushButton(action)
            btn.setCheckable(True)
            btn.setFixedHeight(28)
            btn.setProperty("fval", action)
            is_first = action == "All"
            btn.setChecked(is_first)
            btn.setStyleSheet(self._filter_style(is_first))
            btn.clicked.connect(
                lambda _checked, b=btn: self._apply_aud_filter(b)
            )
            self._aud_filter_grp.addButton(btn)
            fb.addWidget(btn)

        fb.addStretch()
        self._aud_count_lbl = QLabel("")
        self._aud_count_lbl.setStyleSheet(
            "color:#888; font-size:12px; background:transparent;"
        )
        fb.addWidget(self._aud_count_lbl)
        ref_aud = QPushButton("🔄  Refresh")
        ref_aud.setStyleSheet(ADMIN_BTN_STYLE)
        ref_aud.setFixedHeight(34)
        ref_aud.clicked.connect(self._reload_audit)
        fb.addWidget(ref_aud)
        lay.addLayout(fb)

        # Table
        self._aud_table = self._std_table(
            lay,
            headers=["#","User","Action","Details","Timestamp"],
            stretch_col=3,
            col_widths={0:50, 1:110, 2:150, 4:150},
        )

        hint = QLabel("Full immutable record of all significant system actions.")
        hint.setStyleSheet("color:#bbb; font-size:11px; background:transparent;")
        hint.setAlignment(Qt.AlignCenter)
        lay.addWidget(hint)

    def _apply_aud_filter(self, clicked_btn: "QPushButton"):
        for btn in self._aud_filter_grp.buttons():
            btn.setStyleSheet(self._filter_style(btn is clicked_btn))
        self._reload_audit()

    def _active_aud_filter(self) -> str:
        for btn in self._aud_filter_grp.buttons():
            if btn.isChecked():
                return btn.property("fval")
        return "All"

    def _reload_audit(self):
        flt = self._active_aud_filter()
        self._aud_table.setRowCount(0)
        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM audit_log ORDER BY id DESC LIMIT 500"
            )
            rows = cur.fetchall()
            db.close()
        except Exception as err:
            QMessageBox.critical(self, "Database Error", str(err))
            return

        display = [
            row for row in rows
            if flt == "All" or str(row.get("action","")) == flt
        ]

        self._aud_table.setRowCount(len(display))
        for r, row in enumerate(display):
            action = str(row.get("action","") or "")
            bg = self._AUDIT_BG.get(action)

            cells = [
                (str(row.get("id", "")),                       Qt.AlignCenter),
                (str(row.get("username", "—")),                Qt.AlignLeft),
                (action,                                        Qt.AlignCenter),
                (str(row.get("detail",   "") or "—"),          Qt.AlignLeft),
                (str(row.get("logged_at","") or "—"),          Qt.AlignLeft),
            ]
            for c, (text, align) in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(align | Qt.AlignVCenter)
                if bg:
                    item.setBackground(bg)
                self._aud_table.setItem(r, c, item)

        self._aud_count_lbl.setText(f"{len(display)} record(s)")


class UserInfoWidget(QWidget):
    """Shows logged-in username and role badge next to the clock."""
    def __init__(self, username: str, role: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        name_lbl = QLabel(username)
        name_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        name_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_lbl.setStyleSheet("color: #2b2b2b; background: transparent;")

        role_color = "#008000" if role == "admin" else "#34699A"
        role_lbl = QLabel(role.upper())
        role_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        role_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        role_lbl.setStyleSheet(
            f"color: white; background: {role_color}; border-radius: 4px;"
            " padding: 1px 6px; letter-spacing: 1px;"
        )

        layout.addWidget(name_lbl)
        layout.addWidget(role_lbl)


# ─────────────────────────────────────────────────────────────────────────────
# REPORT PAGE
# ─────────────────────────────────────────────────────────────────────────────

class ReportPage(QWidget):
    def __init__(self, switch_callback=None, role: str = "cashier", username: str = ""):
        super().__init__()
        self.switch_callback = switch_callback
        self.role        = role
        self.username    = username
        self.sales_data  = {}
        self.daily_sales = {}
        self._page_period = "all"   # "daily", "weekly", "monthly", "all"
        self._size_filter = "all"   # "all", "12oz", "16oz"

        self.setWindowTitle("Hyped Mangoes — Reports")
        self.setStyleSheet("QWidget { background-color: #DED6B2; font-family: 'Segoe UI'; }")
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self._build_ui()
        self._load_from_db()
        self.refresh_report()
        self._load_and_plot()

    # ── DB LOAD ──────────────────────────────────────────────────────────────

    def _load_from_db(self, start_date: str = None, end_date: str = None,
                       size_filter: str = None):
        """Load sales data from DB for the given date range (or all time),
        optionally restricted to a single size ("12oz"/"16oz"; None/"all" = both)."""
        try:
            db  = get_db_connection()
            cur = db.cursor(dictionary=True)

            item_query = """
                SELECT oi.product_name, SUM(oi.item_price) AS total
                FROM order_items oi
                JOIN orders o ON o.id = oi.order_id
                WHERE 1=1
            """
            item_params = []
            if start_date:
                item_query += " AND DATE(o.created_at) BETWEEN %s AND %s"
                item_params += [start_date, end_date]
            if size_filter and size_filter != "all":
                item_query += " AND oi.size_name = %s"
                item_params.append(size_filter)
            item_query += " GROUP BY oi.product_name"

            cur.execute(item_query, tuple(item_params))
            for row in cur.fetchall():
                name = row["product_name"] or "Unknown"
                self.sales_data[name] = self.sales_data.get(name, 0) + float(row["total"])

            if start_date:
                cur.execute("""
                    SELECT DATE(created_at) AS day, SUM(total) AS day_total
                    FROM orders
                    WHERE DATE(created_at) BETWEEN %s AND %s
                    GROUP BY DATE(created_at)
                    ORDER BY day
                """, (start_date, end_date))
            else:
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
            logo.setPixmap(px.scaled(200, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo.setText("🥭 Hyped Mangoes")
            logo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2b2b2b;")

        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(8)
        for label, icon_path, page_key in [
            ("🛒 TRANSACTIONS", "TRANSACTION.png", "pos"),
            ("📦 INVENTORY",    "inventory.png",   "inventory"),
            ("🧂 INGREDIENTS", "ingredient.png", "ingredients"),
        ]:
            btn = QPushButton(label)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(18, 18))
            btn.setFixedSize(170, 36)
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
        clock_widget = ClockWidget()
        tbl.addWidget(clock_widget)
        tbl.addSpacing(6)
        user_info = UserInfoWidget(self.username, self.role)
        tbl.addWidget(user_info)
        tbl.addSpacing(12)
        self._logout_btn = QPushButton("🚪 LOG OUT")
        self._logout_btn.setFixedSize(130, 36)
        self._logout_btn.setStyleSheet(NAV_BTN_STYLE)
        drop_shadow(self._logout_btn, blur=18, alpha=100)
        self._logout_btn.clicked.connect(self._admin_clicked)
        tbl.addWidget(self._logout_btn)
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

        # ── PERIOD FILTER BUTTONS ─────────────────────────────────────────────
        period_filter_panel = QFrame()
        period_filter_panel.setStyleSheet(
            "QFrame { background-color: #EFE9D1; border-radius: 0px; }"
        )
        period_filter_panel.setFixedHeight(48)
        pfl = QHBoxLayout(period_filter_panel)
        pfl.setContentsMargins(0, 6, 0, 6)
        pfl.setSpacing(8)

        filter_lbl = QLabel("View:")
        filter_lbl.setStyleSheet(
            "font-size: 12px; color: #555; font-weight: bold; background: transparent;"
        )
        pfl.addWidget(filter_lbl)

        PSTYLE_ACTIVE = """
            QPushButton {
                background-color: #2b2b2b; color: #E8D28C;
                font-size: 12px; border-radius: 6px; font-weight: bold;
                border: none; padding: 4px 16px;
            }
        """
        PSTYLE_INACTIVE = """
            QPushButton {
                background-color: #EFE9D1; color: #2b2b2b;
                font-size: 12px; border-radius: 6px; font-weight: bold;
                border: 1px solid #c8b87a; padding: 4px 16px;
            }
            QPushButton:hover { background-color: #E8D28C; }
        """
        self._page_period_btns = {}
        for period_key, period_label in [
            ("all",     "All Time"),
            ("daily",   "Today"),
            ("weekly",  "This Week"),
            ("monthly", "This Month"),
        ]:
            btn = QPushButton(period_label)
            btn.setFixedHeight(32)
            btn.setStyleSheet(PSTYLE_ACTIVE if period_key == "all" else PSTYLE_INACTIVE)
            btn.clicked.connect(lambda checked, k=period_key: self._set_page_period(k))
            self._page_period_btns[period_key] = btn
            pfl.addWidget(btn)

        pfl.addStretch()

        # ── SIZE FILTER BUTTONS (right side) ───────────────────────────────
        size_lbl = QLabel("Size:")
        size_lbl.setStyleSheet(
            "font-size: 12px; color: #555; font-weight: bold; background: transparent;"
        )
        pfl.addWidget(size_lbl)

        SSTYLE_ACTIVE = """
            QPushButton {
                background-color: #2b2b2b; color: #E8D28C;
                font-size: 12px; border-radius: 6px; font-weight: bold;
                border: none; padding: 4px 16px;
            }
        """
        SSTYLE_INACTIVE = """
            QPushButton {
                background-color: #EFE9D1; color: #2b2b2b;
                font-size: 12px; border-radius: 6px; font-weight: bold;
                border: 1px solid #c8b87a; padding: 4px 16px;
            }
            QPushButton:hover { background-color: #E8D28C; }
        """
        self._size_filter_btns = {}
        for size_key, size_label in [
            ("all",  "All Sizes"),
            ("12oz", "12oz"),
            ("16oz", "16oz"),
        ]:
            btn = QPushButton(size_label)
            btn.setFixedHeight(32)
            btn.setStyleSheet(SSTYLE_ACTIVE if size_key == "all" else SSTYLE_INACTIVE)
            btn.clicked.connect(lambda checked, k=size_key: self._set_size_filter(k))
            self._size_filter_btns[size_key] = btn
            pfl.addWidget(btn)

        content_grid.addWidget(period_filter_panel, 0, 0, 1, 2)

        # ── TOTAL SALES CARD ─────────────────────────────────────────────────
        self.total_card = self._make_panel()
        self.total_card.setFixedHeight(120)
        drop_shadow(self.total_card, blur=25, alpha=110)
        total_inner = QHBoxLayout(self.total_card)
        total_inner.setContentsMargins(24, 16, 24, 16)

        left_col = QVBoxLayout()
        self._period_title_lbl = QLabel("TOTAL REVENUE  (All Time)")
        self._period_title_lbl.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #888; "
            "letter-spacing: 2px; background: transparent;"
        )
        self.total_value = QLabel("₱0.00")
        self.total_value.setStyleSheet(
            "font-size: 36px; font-weight: bold; color: #2b2b2b; background: transparent;"
        )
        left_col.addWidget(self._period_title_lbl)
        left_col.addWidget(self.total_value)
        total_inner.addLayout(left_col)
        total_inner.addStretch()

        icon_lbl = QLabel("₱")
        icon_lbl.setStyleSheet(
            "font-size: 52px; color: #E8D28C; font-weight: bold; background: transparent;"
        )
        total_inner.addWidget(icon_lbl)
        content_grid.addWidget(self.total_card, 1, 0, 1, 2)

        # ── PIE CHART PANEL ──────────────────────────────────────────────────
        pie_panel = self._make_panel()
        drop_shadow(pie_panel, blur=25, alpha=110)
        pie_layout = QVBoxLayout(pie_panel)
        pie_layout.setContentsMargins(16, 14, 16, 14)
        pie_layout.setSpacing(8)

        self.pie_title_lbl = QLabel("Sales Breakdown by Item")
        self.pie_title_lbl.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #2b2b2b; background: transparent;"
        )
        pie_layout.addWidget(self.pie_title_lbl)

        self.pie_canvas = FigureCanvas(Figure(figsize=(5, 4), facecolor="#FFFFFF"))
        self.pie_canvas.setMinimumHeight(320)
        self.pie_canvas.setStyleSheet("border-radius: 8px;")
        pie_layout.addWidget(self.pie_canvas)
        content_grid.addWidget(pie_panel, 2, 0)
        pie_panel.setMinimumHeight(420)

        # ── TRACKER PANEL ────────────────────────────────────────────────────
        tracker_panel = self._make_panel()
        drop_shadow(tracker_panel, blur=25, alpha=110)
        tracker_outer = QVBoxLayout(tracker_panel)
        tracker_outer.setContentsMargins(16, 14, 16, 14)
        tracker_outer.setSpacing(8)

        self.tracker_title_lbl = QLabel("Item Sales Breakdown")
        self.tracker_title_lbl.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #2b2b2b; background: transparent;"
        )
        tracker_outer.addWidget(self.tracker_title_lbl)

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
        content_grid.addWidget(tracker_panel, 2, 1)

        content_grid.setColumnStretch(0, 1)
        content_grid.setColumnStretch(1, 1)

        # ── INCOME TRENDS SECTION ────────────────────────────────────────────
        trends_sep = QLabel("INCOME TRENDS")
        trends_sep.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #888; "
            "letter-spacing: 3px; background: transparent; padding: 8px 0 4px 0;"
        )
        content_grid.addWidget(trends_sep, 3, 0, 1, 2)
        self._trends_sep = trends_sep

        # Controls row
        it_controls_panel = self._make_panel()
        drop_shadow(it_controls_panel, blur=25, alpha=110)
        it_controls_panel.setFixedHeight(92)
        it_controls_layout = QHBoxLayout(it_controls_panel)
        it_controls_layout.setContentsMargins(18, 14, 18, 14)
        it_controls_layout.setSpacing(14)

        it_title = QLabel("INCOME TREND ANALYSIS")
        it_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2b2b2b; background: transparent;")
        it_controls_layout.addWidget(it_title)
        it_controls_layout.addStretch(1)

        self.range_combo = QComboBox()
        self.range_combo.addItems([
            "Last 7 days",
            "Last 30 days",
            "Last 90 days",
            "Custom (last 180 days)",
        ])
        self.range_combo.setFixedHeight(36)
        self.range_combo.setStyleSheet(
            "QComboBox { background-color: white; border: 2px solid #d6d2c4; border-radius: 10px; padding: 4px 10px; font-size: 13px; color: #2c3e50; }"
            "QComboBox:focus { border: 2px solid #34699A; }"
            "QComboBox QAbstractItemView { background-color: white; selection-background-color: #34699A; selection-color: white; }"
        )

        self.ma_combo = QComboBox()
        self.ma_combo.addItems([
            "No moving average",
            "3-day moving average",
            "7-day moving average",
        ])
        self.ma_combo.setFixedHeight(36)
        self.ma_combo.setStyleSheet(
            "QComboBox { background-color: white; border: 2px solid #d6d2c4; border-radius: 10px; padding: 4px 10px; font-size: 13px; color: #2c3e50; }"
            "QComboBox:focus { border: 2px solid #34699A; }"
            "QComboBox QAbstractItemView { background-color: white; selection-background-color: #34699A; selection-color: white; }"
        )

        range_lbl = QLabel("Range:")
        range_lbl.setStyleSheet("background: transparent;")
        ma_lbl = QLabel("MA:")
        ma_lbl.setStyleSheet("background: transparent;")
        it_controls_layout.addWidget(range_lbl)
        it_controls_layout.addWidget(self.range_combo)
        it_controls_layout.addWidget(ma_lbl)
        it_controls_layout.addWidget(self.ma_combo)

        content_grid.addWidget(it_controls_panel, 4, 0, 1, 2)
        self._it_controls_panel = it_controls_panel

        # Line chart panel
        line_panel = self._make_panel()
        drop_shadow(line_panel, blur=25, alpha=110)
        line_panel.setMinimumHeight(420)
        line_layout = QVBoxLayout(line_panel)
        line_layout.setContentsMargins(16, 14, 16, 14)
        line_layout.setSpacing(8)

        line_title_lbl = QLabel("Daily Income")
        line_title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #2b2b2b; background: transparent;")
        line_layout.addWidget(line_title_lbl)

        self.line_canvas = FigureCanvas(Figure(figsize=(9, 3.8), facecolor="#FFFFFF"))
        self.line_canvas.setStyleSheet("border-radius: 8px;")
        line_layout.addWidget(self.line_canvas)

        content_grid.addWidget(line_panel, 5, 0)
        self._line_panel = line_panel

        # Monthly bar chart panel
        monthly_panel = self._make_panel()
        drop_shadow(monthly_panel, blur=25, alpha=110)
        monthly_panel.setMinimumHeight(420)
        monthly_layout = QVBoxLayout(monthly_panel)
        monthly_layout.setContentsMargins(16, 14, 16, 14)
        monthly_layout.setSpacing(8)

        monthly_title_lbl = QLabel("Monthly Income (last 12 months)")
        monthly_title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #2b2b2b; background: transparent;")
        monthly_layout.addWidget(monthly_title_lbl)

        self.monthly_canvas = FigureCanvas(Figure(figsize=(6.7, 3.8), facecolor="#FFFFFF"))
        self.monthly_canvas.setStyleSheet("border-radius: 8px;")
        monthly_layout.addWidget(self.monthly_canvas)

        content_grid.addWidget(monthly_panel, 5, 1)
        self._monthly_panel = monthly_panel

        content_grid.setColumnStretch(0, 1)
        content_grid.setColumnStretch(1, 1)

        # ── Apply role-based restrictions ─────────────────────────────────────
        if self.role != "admin":
            self._trends_sep.hide()
            self._it_controls_panel.hide()
            self._line_panel.hide()
            self._monthly_panel.hide()
            # Also wire combo signals only if visible (avoid wasted work)
        else:
            self.range_combo.currentIndexChanged.connect(self._load_and_plot)
            self.ma_combo.currentIndexChanged.connect(self._load_and_plot)

    # ── ADMIN BAR ────────────────────────────────────────────────────────────

    def _admin_clicked(self):
        reply = QMessageBox.question(
            self, "Log Out",
            "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            QApplication.exit(42)

    def _build_admin_bar(self, root: QVBoxLayout):
        bar = QFrame()
        bar.setFixedHeight(52)
        bar.setStyleSheet("background-color: #2b2b2b;")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(20, 0, 20, 0)
        bl.setSpacing(10)

        # Always-visible buttons (left side)
        for label, slot in [
            ("📋  Orders", self._open_orders),
            ("📊  Today's Summary", self._open_summary),
        ]:
            btn = QPushButton(label)
            btn.setFixedHeight(36)
            btn.setStyleSheet(ADMIN_BTN_STYLE)
            btn.setCursor(Qt.PointingHandCursor)
            drop_shadow(btn, blur=10, alpha=55)
            btn.clicked.connect(slot)
            bl.addWidget(btn)

        bl.addStretch()

        # Admin-only: Manage Users + Security (right side)
        if self.role == "admin":
            usr_btn = QPushButton("👤  Manage Users")
            usr_btn.setFixedHeight(36)
            usr_btn.setStyleSheet(ADMIN_BTN_STYLE)
            usr_btn.setCursor(Qt.PointingHandCursor)
            drop_shadow(usr_btn, blur=10, alpha=55)
            usr_btn.clicked.connect(self._open_users)
            bl.addWidget(usr_btn)

            sec_btn = QPushButton("🔒  Security")
            sec_btn.setFixedHeight(36)
            sec_btn.setStyleSheet(ADMIN_BTN_STYLE)
            sec_btn.setCursor(Qt.PointingHandCursor)
            drop_shadow(sec_btn, blur=10, alpha=55)
            sec_btn.clicked.connect(self._open_security)
            bl.addWidget(sec_btn)

        ref_btn = QPushButton("🔄  Refresh")
        ref_btn.setFixedHeight(36)
        ref_btn.setStyleSheet(ADMIN_BTN_STYLE)
        ref_btn.setCursor(Qt.PointingHandCursor)
        drop_shadow(ref_btn, blur=10, alpha=55)
        ref_btn.clicked.connect(self.reload_from_db_and_refresh)
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

    def _open_security(self):
        dlg = SecurityDialog(parent=self)
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

    def _get_page_period_range(self):
        """Return (start_str, end_str) for the current page period, or (None, None) for all."""
        today = date.today()
        if self._page_period == "daily":
            return today.isoformat(), today.isoformat()
        elif self._page_period == "weekly":
            start = today - timedelta(days=today.weekday())
            return start.isoformat(), today.isoformat()
        elif self._page_period == "monthly":
            start = today.replace(day=1)
            return start.isoformat(), today.isoformat()
        return None, None  # all

    def _set_page_period(self, period: str):
        """Switch the whole-page period filter and reload."""
        self._page_period = period
        # Update period button styles
        PSTYLE_ACTIVE = """
            QPushButton {
                background-color: #2b2b2b; color: #E8D28C;
                font-size: 12px; border-radius: 6px; font-weight: bold;
                border: none; padding: 4px 16px;
            }
        """
        PSTYLE_INACTIVE = """
            QPushButton {
                background-color: #EFE9D1; color: #2b2b2b;
                font-size: 12px; border-radius: 6px; font-weight: bold;
                border: 1px solid #c8b87a; padding: 4px 16px;
            }
            QPushButton:hover { background-color: #E8D28C; }
        """
        for p, btn in self._page_period_btns.items():
            btn.setStyleSheet(PSTYLE_ACTIVE if p == period else PSTYLE_INACTIVE)
        self.reload_from_db_and_refresh()

    def _set_size_filter(self, size: str):
        """Switch the item-breakdown size filter (All Sizes / 12oz / 16oz) and reload."""
        self._size_filter = size
        SSTYLE_ACTIVE = """
            QPushButton {
                background-color: #2b2b2b; color: #E8D28C;
                font-size: 12px; border-radius: 6px; font-weight: bold;
                border: none; padding: 4px 16px;
            }
        """
        SSTYLE_INACTIVE = """
            QPushButton {
                background-color: #EFE9D1; color: #2b2b2b;
                font-size: 12px; border-radius: 6px; font-weight: bold;
                border: 1px solid #c8b87a; padding: 4px 16px;
            }
            QPushButton:hover { background-color: #E8D28C; }
        """
        for k, btn in self._size_filter_btns.items():
            btn.setStyleSheet(SSTYLE_ACTIVE if k == size else SSTYLE_INACTIVE)

        suffix = "" if size == "all" else f" — {size}"
        self.pie_title_lbl.setText(f"Sales Breakdown by Item{suffix}")
        self.tracker_title_lbl.setText(f"Item Sales Breakdown{suffix}")

        self.reload_from_db_and_refresh()

    def reload_from_db_and_refresh(self):
        """Reload all sales data fresh from DB using the current period, then re-render."""
        self.sales_data  = {}
        self.daily_sales = {}
        start_str, end_str = self._get_page_period_range()
        self._load_from_db(start_str, end_str, self._size_filter)
        self.refresh_report()
        self._load_and_plot()

    def refresh_report(self):
        self.plot_pie()
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

    # ── INCOME TRENDS METHODS ────────────────────────────────────────────────

    def _get_range_days(self):
        idx = self.range_combo.currentIndex()
        if idx == 0:
            return 7
        if idx == 1:
            return 30
        if idx == 2:
            return 90
        return 180

    def _get_ma_window(self):
        txt = self.ma_combo.currentText()
        if "3-day" in txt:
            return 3
        if "7-day" in txt:
            return 7
        return 0

    def _load_and_plot(self):
        days = self._get_range_days()
        ma_window = self._get_ma_window()

        end_day = date.today()
        start_day = end_day - timedelta(days=days - 1)

        daily = {}
        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                """
                SELECT DATE(created_at) AS day, COALESCE(SUM(total), 0) AS day_total
                FROM orders
                WHERE created_at >= %s AND created_at < %s
                GROUP BY DATE(created_at)
                ORDER BY day
                """,
                (start_day.isoformat(), (end_day + timedelta(days=1)).isoformat()),
            )
            for row in cur.fetchall():
                daily[str(row["day"])] = float(row["day_total"])
            db.close()
        except Exception as err:
            print(f"[IncomeTrends] DB load failed: {err}")

        dates = []
        values = []
        for i in range(days):
            d = (start_day + timedelta(days=i)).isoformat()
            dates.append(d)
            values.append(daily.get(d, 0.0))

        self._plot_line(dates, values, ma_window)
        self._plot_monthly()

    def _plot_line(self, dates, values, ma_window):
        fig = self.line_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor("#FFFFFF")
        fig.patch.set_facecolor("#FFFFFF")

        if not values or sum(values) == 0:
            ax.text(0.5, 0.5, "No income recorded yet", ha="center", va="center",
                    fontsize=13, color="#aaa")
            ax.axis("off")
            self.line_canvas.draw()
            return

        x = list(range(len(dates)))
        ax.plot(x, values, color="#34699A", linewidth=2.5, marker="o", markersize=3)
        ax.set_ylabel("Income (₱)")

        if ma_window and len(values) >= ma_window:
            ma = []
            for i in range(len(values)):
                start = max(0, i - ma_window + 1)
                window = values[start:i + 1]
                ma.append(sum(window) / len(window) if window else 0)
            ax.plot(x, ma, color="#b87c0e", linewidth=2.2, linestyle="--")

        step = max(1, len(dates) // 8)
        ticks = [i for i in range(len(dates)) if i % step == 0 or i == len(dates) - 1]
        ax.set_xticks(ticks)
        ax.set_xticklabels([dates[i] for i in ticks], rotation=30, ha="right", fontsize=8)

        ax.grid(True, axis="y", color="#ede9dc", linestyle="--", linewidth=0.8)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)

        fig.tight_layout()
        self.line_canvas.draw()

    def _plot_monthly(self):
        monthly = {}
        today = date.today()
        start_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        for _ in range(11):
            start_month = (start_month.replace(day=1) - timedelta(days=1)).replace(day=1)

        try:
            db = get_db_connection()
            cur = db.cursor(dictionary=True)
            cur.execute(
                """
                SELECT DATE_FORMAT(created_at, '%%Y-%%m') AS month_key,
                       COALESCE(SUM(total), 0) AS month_total
                FROM orders
                WHERE created_at >= %s
                GROUP BY DATE_FORMAT(created_at, '%%Y-%%m')
                ORDER BY month_key
                """,
                (start_month.isoformat(),),
            )
            for row in cur.fetchall():
                monthly[str(row["month_key"])] = float(row["month_total"])
            db.close()
        except Exception as err:
            print(f"[IncomeTrends] monthly DB load failed: {err}")

        labels = []
        vals = []
        y, m = start_month.year, start_month.month
        while (y, m) <= (today.year, today.month):
            key = f"{y:04d}-{m:02d}"
            labels.append(key)
            vals.append(monthly.get(key, 0.0))
            m += 1
            if m == 13:
                m = 1
                y += 1

        fig = self.monthly_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor("#FFFFFF")
        fig.patch.set_facecolor("#FFFFFF")

        if not vals or sum(vals) == 0:
            ax.text(0.5, 0.5, "No monthly income yet", ha="center", va="center",
                    fontsize=13, color="#aaa")
            ax.axis("off")
            self.monthly_canvas.draw()
            return

        x = list(range(len(labels)))
        ax.bar(x, vals, color="#34699A", edgecolor="white", linewidth=1.2)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
        ax.set_ylabel("Income (₱)")
        ax.grid(True, axis="y", color="#ede9dc", linestyle="--", linewidth=0.8)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)

        maxv = max(vals) if vals else 1
        for i, v in enumerate(vals):
            ax.text(i, v + maxv * 0.01, f"₱{v:,.0f}", ha="center", va="bottom",
                    fontsize=8, color="#2b2b2b", fontweight="bold")

        fig.tight_layout()
        self.monthly_canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportPage(role="admin")
    window.show()
    sys.exit(app.exec_())