# This is the script.py (Do not remove line)

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QFrame, QGraphicsDropShadowEffect,
    QPushButton, QScrollArea, QGridLayout, QVBoxLayout, QHBoxLayout,
    QComboBox, QSizePolicy, QMessageBox, QDialog, QLineEdit,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap, QIntValidator, QFont

from db import get_db_connection

try:
    from report import ReportPage
except ImportError:
    ReportPage = None

# Exit code that main.py watches for — triggers "go back to login"
LOGOUT_CODE = 42


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
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
    font-size: 13px;
    border-radius: 10px;
    padding: 4px 10px;
}
QPushButton:hover { background-color: #2a567a; }
"""

COMBO_STYLE = """
QComboBox {
    background-color: #34699A;
    color: white;
    font-size: 13px;
    border-radius: 10px;
    padding-left: 8px;
    min-height: 32px;
}
QComboBox:hover { background-color: #2a567a; }
QComboBox QAbstractItemView {
    background-color: white;
    selection-background-color: #34699A;
    selection-color: white;
}
"""


# ---------------------------------------------------------------------------
# Custom widgets
# ---------------------------------------------------------------------------
class ClickableRow(QFrame):
    clicked = pyqtSignal(object)

    def mousePressEvent(self, event):
        self.clicked.emit(self)
        super().mousePressEvent(event)


class DragScrollArea(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self._dragging = False
        self._start_pos = None
        self._start_v = self._start_h = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._start_pos = event.pos()
            self._start_v = self.verticalScrollBar().value()
            self._start_h = self.horizontalScrollBar().value()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self._start_pos:
            delta = event.pos() - self._start_pos
            self.verticalScrollBar().setValue(self._start_v - delta.y())
            self.horizontalScrollBar().setValue(self._start_h - delta.x())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)


# ---------------------------------------------------------------------------
# Payment dialog  (cash tendered + change calculator + receipt summary)
# ---------------------------------------------------------------------------
class PaymentDialog(QDialog):
    """Shows order summary, accepts cash, calculates change."""

    FIELD_STYLE = """
    QLineEdit {
        border: 2px solid #ccc;
        border-radius: 10px;
        padding: 8px 14px;
        font-size: 22px;
        font-weight: bold;
        background: white;
        color: #2b2b2b;
    }
    QLineEdit:focus { border: 2px solid #FFD700; }
    """

    def __init__(self, order_rows, total, parent=None):
        super().__init__(parent)
        self.order_rows = order_rows
        self.order_total = total
        self.payment_confirmed = False

        self.setWindowTitle("Payment")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.resize(500, 700)  # initial size
        self.setMinimumSize(440, 670)
        self.setStyleSheet("""
            QDialog { background-color: #FFF8E7; }
            QLabel  { color: #333; }
        """)
        self._build()
        self._center()

    # ── build UI ─────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet("background-color: #E8D28C; border-radius: 0px;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)
        htitle = QLabel("💳  Complete Payment")
        htitle.setFont(QFont("Segoe UI", 14, QFont.Bold))
        htitle.setStyleSheet("color: #2b2b2b; background: transparent;")
        hl.addWidget(htitle)
        hl.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #2b2b2b;
                border: none; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: rgba(0,0,0,0.12); border-radius: 6px; }
        """)
        close_btn.clicked.connect(self.reject)
        hl.addWidget(close_btn)
        root.addWidget(header)

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(24, 16, 24, 16)
        bl.setSpacing(10)
        root.addWidget(body)
        root.setStretchFactor(body, 1)

        # ── Order summary ─────────────────────────────────────────────────────
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame { background-color: white; border-radius: 10px;
                     border: 1px solid #ede9dc; }
        """)
        sf_layout = QVBoxLayout(summary_frame)
        sf_layout.setContentsMargins(12, 10, 12, 10)
        sf_layout.setSpacing(4)

        sh = QLabel("ORDER SUMMARY")
        sh.setStyleSheet(
            "font-size: 10px; font-weight: bold; color: #aaa; "
            "letter-spacing: 2px; background: transparent;"
        )
        sf_layout.addWidget(sh)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(110)
        scroll.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        sc = QWidget()
        sc.setStyleSheet("background: transparent;")
        scl = QVBoxLayout(sc)
        scl.setContentsMargins(0, 0, 0, 0)
        scl.setSpacing(2)

        for row in self.order_rows:
            item_lbl = QLabel(
                f"  {row['name']}  ×{row['qty']}  ({row['size']})  "
                f"<b>₱{row['price']:,}</b>"
            )
            item_lbl.setTextFormat(Qt.RichText)
            item_lbl.setStyleSheet("font-size: 13px; color: #2c3e50; background: transparent;")
            scl.addWidget(item_lbl)

        scl.addStretch()
        scroll.setWidget(sc)
        sf_layout.addWidget(scroll)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #ede9dc; border: none;")
        sf_layout.addWidget(sep)

        total_row = QHBoxLayout()
        total_lbl = QLabel("TOTAL")
        total_lbl.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #555; background: transparent;"
        )
        self._total_val = QLabel(f"₱{self.order_total:,}")
        self._total_val.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2b2b2b; background: transparent;"
        )
        self._total_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_row.addWidget(total_lbl)
        total_row.addWidget(self._total_val)
        sf_layout.addLayout(total_row)
        bl.addWidget(summary_frame)

        # ── Cash tendered ─────────────────────────────────────────────────────
        # ── Payment Area (2-column layout) ────────────────────────────────
        payment_row = QHBoxLayout()
        payment_row.setSpacing(16)

        # LEFT SIDE
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        cash_lbl = QLabel("CASH TENDERED")
        cash_lbl.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #888; letter-spacing: 1px;"
        )
        left_panel.addWidget(cash_lbl)

        self.cash_input = QLineEdit()
        self.cash_input.setPlaceholderText("Enter amount…")
        self.cash_input.setValidator(QIntValidator(0, 9_999_999, self))
        self.cash_input.setStyleSheet(self.FIELD_STYLE)
        self.cash_input.setFixedHeight(52)
        self.cash_input.textChanged.connect(self._update_change)
        left_panel.addWidget(self.cash_input)

        # Change display
        change_frame = QFrame()
        change_frame.setStyleSheet("""
            QFrame {
                background-color: #f0faf4;
                border-radius: 10px;
                border: 1px solid #b2dfcc;
            }
        """)
        change_frame.setFixedHeight(64)

        cf_layout = QHBoxLayout(change_frame)
        cf_layout.setContentsMargins(16, 0, 16, 0)

        change_title = QLabel("CHANGE")
        change_title.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #777;"
        )

        self.change_val = QLabel("₱—")
        self.change_val.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.change_val.setStyleSheet("color: #1e7f3f; background: transparent;")
        self.change_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        cf_layout.addWidget(change_title)
        cf_layout.addWidget(self.change_val)

        left_panel.addWidget(change_frame)
        left_panel.addStretch()

        payment_row.addLayout(left_panel, 2)

        # RIGHT SIDE (NUMPAD)
        numpad = QFrame()
        grid = QGridLayout(numpad)
        grid.setSpacing(8)

        buttons = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2),
            ("C", 3, 0), ("0", 3, 1), ("⌫", 3, 2),
        ]

        for text, row, col in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(80, 65)

            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid #d9d9d9;
                    border-radius: 8px;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                }
                QPushButton:pressed {
                    background-color: #e8e8e8;
                }
            """)

            if text == "C":
                btn.clicked.connect(self._clear_cash)
            elif text == "⌫":
                btn.clicked.connect(self._backspace_cash)
            else:
                btn.clicked.connect(
                    lambda checked=False, digit=text: self._append_digit(digit)
                )

            grid.addWidget(btn, row, col)

        payment_row.addWidget(numpad, 0)

        bl.addLayout(payment_row)

        # ── Confirm button ────────────────────────────────────────────────────
        self.confirm_btn = QPushButton("✔  CONFIRM PAYMENT")
        self.confirm_btn.setMinimumHeight(50)
        self.confirm_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e7f3f; color: white;
                border: none; border-radius: 12px;
                font-weight: bold; font-size: 14px;
            }
            QPushButton:hover   { background-color: #166330; }
            QPushButton:pressed { background-color: #0e4a22; }
            QPushButton:disabled {
                background-color: #ccc; color: #888;
            }
        """)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self._confirm)
        bl.addWidget(self.confirm_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #888;
                border: 1px solid #ccc; border-radius: 10px;
                font-size: 13px;
            }
            QPushButton:hover { background: #f5f5f5; }
        """)
        cancel_btn.clicked.connect(self.reject)
        bl.addWidget(cancel_btn)

    # ── slots ─────────────────────────────────────────────────────────────────

    def _update_change(self):
        try:
            cash = int(self.cash_input.text() or 0)
        except ValueError:
            cash = 0

        change = cash - self.order_total
        if cash == 0:
            self.change_val.setText("₱—")
            self.change_val.setStyleSheet("color: #1e7f3f; background: transparent;")
            self.confirm_btn.setEnabled(False)
        elif change >= 0:
            self.change_val.setText(f"₱{change:,}")
            self.change_val.setStyleSheet("color: #1e7f3f; background: transparent;")
            # Also update parent frame color
            self.change_val.parent().setStyleSheet("""
                QFrame { background-color: #f0faf4; border-radius: 10px;
                         border: 1px solid #b2dfcc; }
            """)
            self.confirm_btn.setEnabled(True)
        else:
            self.change_val.setText(f"–₱{abs(change):,}")
            self.change_val.setStyleSheet("color: #c0392b; background: transparent;")
            self.change_val.parent().setStyleSheet("""
                QFrame { background-color: #fdf0f0; border-radius: 10px;
                         border: 1px solid #e8b4b4; }
            """)
            self.confirm_btn.setEnabled(False)

    def _confirm(self):
        try:
            cash = int(self.cash_input.text() or 0)
        except ValueError:
            cash = 0
        if cash < self.order_total:
            QMessageBox.warning(self, "Insufficient Cash",
                                "Cash tendered must be ≥ the order total.")
            return
        self.cash_paid = cash
        self.change_given = cash - self.order_total
        self.payment_confirmed = True
        self.accept()

    def _center(self):
        if self.parent():
            pg = self.parent().window().geometry()
            self.move(
                pg.x() + (pg.width()  - self.width())  // 2,
                pg.y() + (pg.height() - self.height()) // 2,
            )

    def _append_digit(self, digit):
        self.cash_input.setText(self.cash_input.text() + digit)

    def _clear_cash(self):
        self.cash_input.clear()

    def _backspace_cash(self):
        self.cash_input.backspace()


# ---------------------------------------------------------------------------
# Receipt dialog
# ---------------------------------------------------------------------------
class ReceiptDialog(QDialog):
    """Displays a formatted receipt after a completed order."""

    STORE_NAME    = "MIGUELITO'S HYPE MANGO"
    STORE_TAGLINE = "Your favorite mango shake destination!"
    RECEIPT_WIDTH = 42   # characters wide for the monospace receipt

    def __init__(self, order_rows, total, cash_paid, change_given, order_id, parent=None):
        super().__init__(parent)
        self.order_rows   = order_rows
        self.total        = total
        self.cash_paid    = cash_paid
        self.change_given = change_given
        self.order_id     = order_id

        self.setWindowTitle(f"Receipt – Order #{order_id}")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.resize(480, 640)
        self.setMinimumSize(420, 500)
        self.setStyleSheet("QDialog { background-color: #FFFDF7; }")
        self._build()
        self._center()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ───────────────────────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet("background-color: #E8D28C;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)
        hl.setSpacing(10)

        title_lbl = QLabel("🧾  Order Receipt")
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_lbl.setStyleSheet("color: #2b2b2b; background: transparent;")
        hl.addWidget(title_lbl)
        hl.addStretch()

        print_btn = QPushButton("🖨  Print / Save")
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #34699A; color: white;
                border-radius: 8px; font-size: 12px;
                padding: 4px 14px;
            }
            QPushButton:hover { background-color: #2a567a; }
        """)
        print_btn.clicked.connect(self._print)
        hl.addWidget(print_btn)

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

        root.addWidget(header)

        # Amber accent line
        accent = QFrame()
        accent.setFixedHeight(3)
        accent.setStyleSheet("background-color: #D9A800; border: none;")
        root.addWidget(accent)

        # ── Scrollable receipt body ───────────────────────────────────────────
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
        root.addWidget(self._txt)

        # ── Footer buttons ────────────────────────────────────────────────────
        footer = QFrame()
        footer.setFixedHeight(56)
        footer.setStyleSheet("background-color: #F5EFDC; border-top: 1px solid #E0D6B0;")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(20, 0, 20, 0)
        fl.setSpacing(10)
        fl.addStretch()

        new_order_btn = QPushButton("New Order  →")
        new_order_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        new_order_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e7f3f; color: white;
                border-radius: 10px; font-size: 13px;
                padding: 6px 20px;
            }
            QPushButton:hover { background-color: #166330; }
        """)
        new_order_btn.clicked.connect(self.accept)
        fl.addWidget(new_order_btn)

        root.addWidget(footer)

        self._render()

    def _render(self):
        import datetime
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

        now = datetime.datetime.now().strftime("%Y-%m-%d  %I:%M %p")
        lines.append(two_col("Order #  :", str(self.order_id)))
        lines.append(two_col("Date     :", now))
        lines.append("")

        lines.append(divider())
        lines.append(f"{'ITEM':<24} {'QTY':>4} {'SIZE':>6}  {'TOTAL':>4}")
        lines.append(divider())

        for row in self.order_rows:
            name  = row["name"][:22]
            qty   = str(row["qty"])
            size  = row.get("size", "")
            price = f"₱{row['price']:,}"
            label = f"{name} ×{qty}"
            right = f"{size:>6}  {price:>6}"
            gap   = max(1, W - len(label) - len(right))
            lines.append(label + " " * gap + right)

        lines.append(divider())
        lines.append(two_col("TOTAL DUE", f"₱{self.total:,}"))
        lines.append(divider("═"))
        lines.append("")
        lines.append(two_col("Cash Tendered", f"₱{self.cash_paid:,}"))
        lines.append(two_col("Change", f"₱{self.change_given:,}"))
        lines.append("")
        lines.append(divider())
        lines.append(center("Thank you for visiting Miguelito's!"))
        lines.append(center('"Stay Hyped. Stay Mango."'))
        lines.append(divider())
        lines.append(center("*** Customer Copy ***"))
        lines.append("")

        self._txt.setPlainText("\n".join(lines))

    def _print(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self, "Print Receipt",
            f"Receipt for Order #{self.order_id} sent to printer.\n\n"
            "(Connect a receipt printer and configure it\n"
            "in the system settings to enable printing.)"
        )

    def _center(self):
        if self.parent():
            pg = self.parent().window().geometry()
            self.move(
                pg.x() + (pg.width()  - self.width())  // 2,
                pg.y() + (pg.height() - self.height()) // 2,
            )


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------
def load_products_from_db():
    """
    Returns:
        categories        : dict  { category_name: [product_dict, ...] }
        product_map       : dict  { product_name: product_dict }
        sizes             : list  of size_name strings
        size_mult         : dict  { size_name: float multiplier }

    Each product_dict now contains:
        'has_ingredients' : bool  – True if at least one ingredient is linked
        'stock'           : int   – computed from ingredients if linked,
                                    otherwise the raw DB stock value
    """
    categories = {}
    product_map = {}
    sizes = []
    size_mult = {}

    try:
        db = get_db_connection()
        cur = db.cursor(dictionary=True)

        cur.execute("""
            SELECT p.id, p.product_name, p.base_price, p.image_path, p.stock,
                   c.category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY c.category_name, p.product_name
        """)
        products = cur.fetchall()

        # Load all ingredient links once
        cur.execute("""
            SELECT pi.product_id, pi.amount_used, i.stock_left
            FROM product_ingredients pi
            JOIN ingredients i ON pi.ingredient_id = i.id
        """)
        ingredient_links = {}
        for lnk in cur.fetchall():
            ingredient_links.setdefault(lnk["product_id"], []).append(lnk)

        for row in products:
            pid = row["id"]
            links = ingredient_links.get(pid)

            if links:
                # Stock = how many full orders we can make given ingredient stock
                row["has_ingredients"] = True
                row["stock"] = min(
                    int(lnk["stock_left"] / lnk["amount_used"])
                    for lnk in links
                    if lnk["amount_used"] > 0
                )
            else:
                row["has_ingredients"] = False
                # stock stays as-is from the DB column

            cat = row["category_name"] or "Other"
            categories.setdefault(cat, [])
            categories[cat].append(row)
            product_map[row["product_name"]] = row

        cur.execute("SELECT size_name, multiplier FROM sizes ORDER BY multiplier")
        for row in cur.fetchall():
            sizes.append(row["size_name"])
            size_mult[row["size_name"]] = float(row["multiplier"])

        db.close()
    except Exception as err:
        print(f"[DB] Could not load products: {err}")

    if not sizes:
        sizes = ["12oz", "16oz"]
        size_mult = {"12oz": 1.0, "16oz": 1.3}

    return categories, product_map, sizes, size_mult


def save_order_to_db(order_rows, total):
    """Persist a completed order and deduct product + ingredient stock.
    Returns the new order_id, or None on failure."""
    try:
        db = get_db_connection()
        cur = db.cursor()

        cur.execute("INSERT INTO orders (total) VALUES (%s)", (total,))
        order_id = cur.lastrowid

        for row_data in order_rows:
            cur.execute("""
                INSERT INTO order_items
                    (order_id, product_id, product_name, quantity, size_name, item_price)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                order_id,
                row_data.get("product_id"),
                row_data["name"],
                row_data["qty"],
                row_data["size"],
                row_data["price"],
            ))

        for row_data in order_rows:
            if row_data.get("product_id"):
                cur.execute("""
                    UPDATE products
                    SET stock = GREATEST(0, stock - %s)
                    WHERE id = %s
                """, (row_data["qty"], row_data["product_id"]))

        for row_data in order_rows:
            if row_data.get("product_id"):
                cur.execute("""
                    SELECT ingredient_id, amount_used
                    FROM product_ingredients
                    WHERE product_id = %s
                """, (row_data["product_id"],))
                for link in cur.fetchall():
                    ingredient_id = link[0]
                    amount_used   = link[1]
                    cur.execute("""
                        UPDATE ingredients
                        SET stock_left = GREATEST(0, stock_left - %s)
                        WHERE id = %s
                    """, (float(amount_used) * row_data["qty"], ingredient_id))

        db.commit()
        db.close()
        return order_id
    except Exception as err:
        print(f"[DB] Could not save order: {err}")
        return None


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class IMS(QWidget):
    def __init__(self, switch_callback=None, report_page=None,
                 inventory_page=None, ingredients_page=None, role="cashier"):
        super().__init__()
        self.switch_callback = switch_callback
        self.report_page = report_page
        self.inventory_page = inventory_page
        self.ingredients_page = ingredients_page
        self.role = role

        self.section_grids = []
        self.menu_cards = []
        self.current_columns = 3

        self.selected_item = None
        self.order_total = 0
        self.selected_order_row = None

        self.db_categories, self.product_map, self.sizes, self.size_mult = \
            load_products_from_db()

        self.setWindowTitle("Inventory Management System")
        self.setStyleSheet("QWidget { background-color: #DED6B2; }")
        # Prevent this page's sizeHint from driving the parent window's size.
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── SIDEBAR ──────────────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(338)
        sidebar.setStyleSheet("background-color: #DED6B2;")
        root.addWidget(sidebar)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(27, 10, 11, 10)
        sidebar_layout.setSpacing(12)

        self.title_logo = QLabel()
        self.title_logo.setFixedHeight(110)
        self.title_logo.setAlignment(Qt.AlignCenter)
        self.title_logo.setStyleSheet("background: transparent;")
        self._set_pixmap(self.title_logo, "hypedmangologo.png", 300, 110)
        sidebar_layout.addWidget(self.title_logo)

        yellow_card = QFrame()
        yellow_card.setStyleSheet("background-color: #E8D28C; border-radius: 20px;")
        yellow_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        drop_shadow(yellow_card, blur=25, alpha=180)
        sidebar_layout.addWidget(yellow_card, stretch=1)

        yellow_layout = QVBoxLayout(yellow_card)
        yellow_layout.setContentsMargins(15, 15, 15, 15)
        yellow_layout.setSpacing(8)

        name_price_row = QHBoxLayout()
        self.yellow_text = QLabel("Item Name")
        self.yellow_text.setStyleSheet(
            "color: black; font-size: 15px; font-weight: bold; background: transparent;"
        )
        self.price_text = QLabel("₱0")
        self.price_text.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.price_text.setStyleSheet(
            "color: black; font-size: 15px; font-weight: bold; background: transparent;"
        )
        name_price_row.addWidget(self.yellow_text)
        name_price_row.addWidget(self.price_text)
        yellow_layout.addLayout(name_price_row)

        self.red_box = QFrame()
        self.red_box.setStyleSheet("background-color: #EFE9D1; border-radius: 12px;")
        self.red_box.setFixedHeight(150)
        self.red_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        red_inner = QVBoxLayout(self.red_box)
        red_inner.setContentsMargins(0, 0, 0, 0)
        self.red_image = QLabel()
        self.red_image.setAlignment(Qt.AlignCenter)
        self.red_image.setStyleSheet("background: transparent;")
        red_inner.addWidget(self.red_image)
        yellow_layout.addWidget(self.red_box)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(6)

        qty_col = QVBoxLayout()
        qty_col.setSpacing(2)
        qty_lbl = QLabel("QUANTITY")
        qty_lbl.setAlignment(Qt.AlignCenter)
        qty_lbl.setStyleSheet("color: black; font-size: 10px; background: transparent;")
        self.combo1 = QComboBox()
        self.combo1.addItems(["1", "2", "3", "4", "5"])
        self.combo1.setStyleSheet(COMBO_STYLE)
        qty_col.addWidget(qty_lbl)
        qty_col.addWidget(self.combo1)

        size_col = QVBoxLayout()
        size_col.setSpacing(2)
        size_lbl = QLabel("SIZE")
        size_lbl.setAlignment(Qt.AlignCenter)
        size_lbl.setStyleSheet("color: black; font-size: 10px; background: transparent;")
        self.combo2 = QComboBox()
        self.combo2.addItems(self.sizes)
        self.combo2.setStyleSheet(COMBO_STYLE)
        self.combo2.currentIndexChanged.connect(self.update_price_display)
        size_col.addWidget(size_lbl)
        size_col.addWidget(self.combo2)

        self.add_item_btn = QPushButton("ADD ITEM")
        self.add_item_btn.setStyleSheet(BLUE_BTN_STYLE)
        self.add_item_btn.setFixedHeight(40)
        self.add_item_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_item_btn.clicked.connect(self.button_clicked)

        controls_row.addLayout(qty_col)
        controls_row.addLayout(size_col)
        controls_row.addWidget(self.add_item_btn, alignment=Qt.AlignBottom)
        yellow_layout.addLayout(controls_row)

        self.order_scroll = DragScrollArea()
        self.order_scroll.setWidgetResizable(True)
        self.order_scroll.setStyleSheet("""
            QScrollArea { background-color: white; border: none; border-radius: 10px; }
            QScrollArea QWidget { background-color: white; }
            QScrollBar:vertical { background: #ddd; width: 8px; }
        """)
        self.order_content = QWidget()
        self.order_scroll.setWidget(self.order_content)
        self.order_layout = QVBoxLayout(self.order_content)
        self.order_layout.setContentsMargins(10, 10, 10, 10)
        self.order_layout.setSpacing(8)
        self.order_layout.setAlignment(Qt.AlignTop)
        self.order_content.setStyleSheet("background-color: white;")
        yellow_layout.addWidget(self.order_scroll, stretch=1)

        bottom_row = QHBoxLayout()
        self.total_label = QLabel("Total: ₱0")
        self.total_label.setStyleSheet(
            "color: black; font-size: 16px; font-weight: bold; background: transparent;"
        )
        self.complete_order_btn = QPushButton("COMPLETE ORDER")
        self.complete_order_btn.setStyleSheet(BLUE_BTN_STYLE)
        self.complete_order_btn.setFixedHeight(40)
        self.complete_order_btn.clicked.connect(self.complete_order)
        bottom_row.addWidget(self.total_label)
        bottom_row.addWidget(self.complete_order_btn)
        yellow_layout.addLayout(bottom_row)

        # ── MAIN AREA ─────────────────────────────────────────────────────────
        main_area = QWidget()
        main_area.setStyleSheet("background-color: #DED6B2;")
        root.addWidget(main_area, stretch=1)

        main_area_layout = QVBoxLayout(main_area)
        main_area_layout.setContentsMargins(0, 0, 0, 0)
        main_area_layout.setSpacing(0)

        # TOP BAR
        top_bar = QFrame()
        top_bar.setFixedHeight(80)
        top_bar.setStyleSheet("background-color: #DED6B2;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(24, 0, 125, 0)
        top_bar_layout.setSpacing(10)

        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(8)

        self.inventory_top_btn = QPushButton("📦 INVENTORY")
        self.inventory_top_btn.setFixedSize(170, 36)
        self.inventory_top_btn.setStyleSheet(NAV_BTN_STYLE)
        drop_shadow(self.inventory_top_btn, blur=18, alpha=100)

        self.report_top_btn = QPushButton("📋 REPORT")
        self.report_top_btn.setFixedSize(170, 36)
        self.report_top_btn.setStyleSheet(NAV_BTN_STYLE)
        drop_shadow(self.report_top_btn, blur=18, alpha=100)

        nav_layout.addWidget(self.inventory_top_btn)
        nav_layout.addWidget(self.report_top_btn)

        self.admin_btn = QPushButton("🚪 LOG OUT")
        self.admin_btn.setFixedSize(170, 36)
        self.admin_btn.setStyleSheet(NAV_BTN_STYLE)
        drop_shadow(self.admin_btn, blur=18, alpha=100)

        top_bar_layout.addStretch()
        top_bar_layout.addLayout(nav_layout)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.admin_btn)

        main_area_layout.addWidget(top_bar)

        # ── Wire nav buttons ──────────────────────────────────────────────────
        if self.switch_callback:
            self.report_top_btn.clicked.connect(
                lambda: self.switch_callback("report"))
            self.inventory_top_btn.clicked.connect(
                lambda: self.switch_callback("inventory"))

        self.admin_btn.clicked.connect(self.admin_clicked)

        # Cashiers don't need inventory / report access from POS screen
        if self.role != "admin":
            self.inventory_top_btn.hide()
            self.report_top_btn.hide()

        # MENU SCROLL AREA
        self.scroll_area = DragScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(0)   # allow it to compress when bottom_box is shown
        self.scroll_area.setStyleSheet("background-color: #EFE9D1; border: none;")
        self.scroll_content = QWidget()
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        menu_layout = QVBoxLayout(self.scroll_content)
        menu_layout.setContentsMargins(20, 20, 20, 20)
        menu_layout.setSpacing(30)
        menu_layout.setAlignment(Qt.AlignTop)

        if self.db_categories:
            for category_name, products in self.db_categories.items():
                menu_layout.addWidget(self._create_section(category_name, products))
        else:
            lbl = QLabel("No products found in database.\nPlease run seed_products.sql first.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 16px; color: #666;")
            menu_layout.addWidget(lbl)

        main_area_layout.addWidget(self.scroll_area, stretch=1)

        # CHANGE ORDER DETAILS BAR
        self.bottom_box = QFrame()
        self.bottom_box.setFixedHeight(100)
        self.bottom_box.setStyleSheet(
            "QFrame { background-color: #EFE9D1; border-radius: 10px; }"
        )

        bottom_box_layout = QHBoxLayout(self.bottom_box)
        bottom_box_layout.setContentsMargins(15, 8, 15, 8)
        bottom_box_layout.setSpacing(10)

        change_col = QVBoxLayout()
        change_col.setSpacing(3)
        self.change_label = QLabel("CHANGE ORDER DETAILS")
        self.change_label.setStyleSheet(
            "color: black; font-size: 13px; background: transparent;"
        )
        self.change_text = QLabel("ITEMS TO BE CHANGED:")
        self.change_text.setStyleSheet(
            "color: black; font-size: 13px; background: transparent;"
        )
        change_col.addWidget(self.change_label)
        change_col.addWidget(self.change_text)
        bottom_box_layout.addLayout(change_col, stretch=1)

        self.bottom_combo1 = QComboBox()
        self.bottom_combo1.addItems(["1", "2", "3", "4", "5"])
        self.bottom_combo1.setFixedWidth(100)
        self.bottom_combo1.setStyleSheet(COMBO_STYLE)

        self.bottom_combo2 = QComboBox()
        self.bottom_combo2.addItems(self.sizes)
        self.bottom_combo2.setFixedWidth(100)
        self.bottom_combo2.setStyleSheet(COMBO_STYLE)

        self.remove_btn = QPushButton("REMOVE ITEM")
        self.remove_btn.setStyleSheet(BLUE_BTN_STYLE)
        self.remove_btn.setFixedHeight(40)
        self.remove_btn.clicked.connect(self.remove_selected_order)

        self.apply_changes_btn = QPushButton("APPLY CHANGES")
        self.apply_changes_btn.setStyleSheet(BLUE_BTN_STYLE)
        self.apply_changes_btn.setFixedHeight(40)
        self.apply_changes_btn.clicked.connect(self.apply_changes)

        self.redd_box = QFrame()
        self.redd_box.setFixedSize(80, 80)
        self.redd_box.setStyleSheet("background-color: #DED6B2; border-radius: 10px;")
        redd_inner = QVBoxLayout(self.redd_box)
        redd_inner.setContentsMargins(0, 0, 0, 0)
        self.redd_box_image = QLabel()
        self.redd_box_image.setAlignment(Qt.AlignCenter)
        self.redd_box_image.setStyleSheet("background: transparent;")
        redd_inner.addWidget(self.redd_box_image)

        bottom_box_layout.addWidget(self.bottom_combo1, alignment=Qt.AlignVCenter)
        bottom_box_layout.addWidget(self.bottom_combo2, alignment=Qt.AlignVCenter)
        bottom_box_layout.addWidget(self.remove_btn)
        bottom_box_layout.addWidget(self.apply_changes_btn)
        bottom_box_layout.addWidget(self.redd_box)

        main_area_layout.addWidget(self.bottom_box)
        self.bottom_box.hide()

        self.scroll_area.viewport().installEventFilter(self)
        self.scroll_content.installEventFilter(self)
        self.installEventFilter(self)

    # -------------------------------------------------------------------------
    # Section builder
    # -------------------------------------------------------------------------
    def _create_section(self, title, products):
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(10)

        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: black;")
        layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setSpacing(15)
        cards = []

        for product in products:
            name = product["product_name"]
            image_path = product.get("image_path") or "images/default.png"
            stock = product.get("stock", 0)
            has_ingredients = product.get("has_ingredients", False)

            card = QFrame()
            card.setFixedSize(250, 150)

            if not has_ingredients:
                # No ingredients linked — card is locked/orange-tinted
                card.setStyleSheet("""
                    QFrame { background-color: #f0d080; border-radius: 15px;
                             border: 2px dashed #c8a020; }
                """)
            elif stock <= 0:
                card.setStyleSheet("""
                    QFrame { background-color: #cccccc; border-radius: 15px; }
                """)
            else:
                card.setStyleSheet("""
                    QFrame { background-color: #E8D28C; border-radius: 15px; }
                    QFrame:hover { background-color: #D9BE70; }
                """)

            drop_shadow(card, blur=25, alpha=150)

            # Only make clickable if ingredients are linked AND stock > 0
            if has_ingredients and stock > 0:
                card.mousePressEvent = lambda e, n=name: self.item_clicked(n)
            elif not has_ingredients:
                # Still make it clickable so the warning message fires
                card.mousePressEvent = lambda e, n=name: self.item_clicked(n)

            vbox = QVBoxLayout(card)
            vbox.setAlignment(Qt.AlignCenter)
            vbox.setSpacing(5)

            img = QLabel()
            img.setAlignment(Qt.AlignCenter)
            img.setStyleSheet("background: transparent;")
            px = QPixmap(image_path)
            if not px.isNull():
                img.setPixmap(px.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                img.setText("No Image")

            text = QLabel(name)
            text.setAlignment(Qt.AlignCenter)
            text.setStyleSheet("color: #2b2b2b; font-weight: bold;")

            if not has_ingredients:
                stock_lbl = QLabel("⚠ No ingredients linked")
                stock_lbl.setAlignment(Qt.AlignCenter)
                stock_lbl.setStyleSheet("color: #8b5c00; font-size: 10px; font-weight: bold;")
            else:
                stock_lbl = QLabel(f"Stock: {stock}")
                stock_lbl.setAlignment(Qt.AlignCenter)
                stock_lbl.setStyleSheet("color: #555; font-size: 11px;")

            vbox.addWidget(img)
            vbox.addWidget(text)
            vbox.addWidget(stock_lbl)

            cards.append(card)

        self.section_grids.append(grid)
        self.menu_cards.append(cards)

        for i, card in enumerate(cards):
            row, col = divmod(i, 3)
            grid.addWidget(card, row, col)

        layout.addLayout(grid)
        return section

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.width() < 800:
            columns = 1
        elif self.width() < 1200:
            columns = 2
        else:
            columns = 3

        if hasattr(self, "current_columns") and self.current_columns == columns:
            return
        self.current_columns = columns

        for grid, cards in zip(self.section_grids, self.menu_cards):
            while grid.count():
                grid.takeAt(0)
            for i, card in enumerate(cards):
                grid.addWidget(card, i // columns, i % columns)

    def _set_pixmap(self, label, path, w, h):
        px = QPixmap(path)
        if not px.isNull():
            label.setPixmap(px.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            label.setText("No Image")

    # -------------------------------------------------------------------------
    # Refresh menu cards from DB (called after each completed order)
    # -------------------------------------------------------------------------
    def refresh_products(self):
        """Reload products from DB and rebuild the menu card grid."""
        self.db_categories, self.product_map, self.sizes, self.size_mult = \
            load_products_from_db()
        self.section_grids = []
        self.menu_cards = []

        # Update size combo boxes with latest sizes
        self.combo2.blockSignals(True)
        self.combo2.clear()
        self.combo2.addItems(self.sizes)
        self.combo2.blockSignals(False)
        self.bottom_combo2.clear()
        self.bottom_combo2.addItems(self.sizes)

        # Replace scroll content widget
        new_content = QWidget()
        new_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        menu_layout = QVBoxLayout(new_content)
        menu_layout.setContentsMargins(20, 20, 20, 20)
        menu_layout.setSpacing(30)
        menu_layout.setAlignment(Qt.AlignTop)

        if self.db_categories:
            for category_name, products in self.db_categories.items():
                menu_layout.addWidget(self._create_section(category_name, products))
        else:
            lbl = QLabel("No products found in database.\nPlease run seed_products.sql first.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 16px; color: #666;")
            menu_layout.addWidget(lbl)

        old = self.scroll_area.takeWidget()
        self.scroll_content = new_content
        self.scroll_area.setWidget(new_content)
        if old:
            old.deleteLater()

    # -------------------------------------------------------------------------
    # Slots
    # -------------------------------------------------------------------------
    def item_clicked(self, name):
        product = self.product_map.get(name, {})

        # Block ordering if no ingredients are linked
        if not product.get("has_ingredients", False):
            QMessageBox.warning(
                self,
                "No Ingredients Linked",
                f"'{name}' cannot be ordered yet.\n\n"
                "Please link at least one ingredient to this product in\n"
                "Inventory → select product → ⚙ Manage.",
            )
            return

        self.bottom_box.hide()
        self.selected_item = name
        self.yellow_text.setText(name)
        self.update_price_display()
        image_path = product.get("image_path") or "images/default.png"
        self.set_menu_preview_image(image_path)

    def update_price_display(self):
        if not self.selected_item:
            return
        product = self.product_map.get(self.selected_item, {})
        base = float(product.get("base_price", 0))
        size = self.combo2.currentText()
        final = int(base * self.size_mult.get(size, 1.0))
        self.price_text.setText(f"₱{final}")

    def button_clicked(self):
        if not self.selected_item:
            return

        product = self.product_map.get(self.selected_item, {})
        qty = int(self.combo1.currentText())
        size = self.combo2.currentText()

        base = float(product.get("base_price", 0))
        unit_price = int(base * self.size_mult.get(size, 1.0))
        added_price = unit_price * qty

        # Check if item already exists in order
        for i in range(self.order_layout.count()):
            existing_row = self.order_layout.itemAt(i).widget()

            if (
                    existing_row
                    and hasattr(existing_row, "data")
                    and existing_row.data["name"] == self.selected_item
                    and existing_row.data["size"] == size
            ):
                # Update quantity
                existing_row.data["qty"] += qty

                # Recalculate row price
                existing_row.data["price"] = (
                        unit_price * existing_row.data["qty"]
                )

                # Update labels
                existing_row.qty_label.setText(
                    f"Q: {existing_row.data['qty']}"
                )
                existing_row.price_label.setText(
                    f"₱{existing_row.data['price']}"
                )

                # Update order total
                self.order_total += added_price
                self.total_label.setText(f"Total: ₱{self.order_total}")

                return

        # No existing row found → create a new one

        self.order_total += added_price
        self.total_label.setText(f"Total: ₱{self.order_total}")

        row = ClickableRow()
        row.clicked.connect(self.order_row_clicked)
        row.setStyleSheet("QFrame { background-color: #f5f5f5; border-radius: 6px; }")
        row.data = {
            "name": self.selected_item,
            "product_id": product.get("id"),
            "qty": qty,
            "size": size,
            "price": added_price,
            "image": product.get("image_path") or "images/default.png",
        }

        from PyQt5.QtWidgets import QGridLayout as _GL
        g = _GL(row)
        g.setContentsMargins(8, 4, 8, 4)

        row.name_label  = QLabel(self.selected_item)
        row.qty_label   = QLabel(f"Q: {qty}")
        row.size_label  = QLabel(f"S: {size}")
        row.price_label = QLabel(f"₱{added_price}")

        for w in [row.name_label, row.qty_label, row.size_label, row.price_label]:
            w.setStyleSheet("font-size: 13px; color: black;")

        g.addWidget(row.name_label,  0, 0)
        g.addWidget(row.qty_label,   0, 1)
        g.addWidget(row.size_label,  0, 2)
        g.addWidget(row.price_label, 0, 3)

        row.setFixedHeight(45)
        self.order_layout.addWidget(row)

    def order_row_clicked(self, row):
        self.bottom_box.show()
        self.selected_order_row = row

        for i in range(self.order_layout.count()):
            w = self.order_layout.itemAt(i).widget()
            if w:
                w.setStyleSheet("QFrame { background-color: #f5f5f5; border-radius: 6px; }")

        row.setStyleSheet("QFrame { background-color: #cce5ff; border-radius: 6px; }")
        self.change_text.setText(
            f"ITEMS TO BE CHANGED: {row.data['name']} | "
            f"Q: {row.data['qty']} | S: {row.data['size']} | ₱{row.data['price']}"
        )
        self.set_order_preview_image(row.data.get("image", "images/default.png"))

    def remove_selected_order(self):
        if not self.selected_order_row:
            return
        row = self.selected_order_row
        self.order_total = max(0, self.order_total - row.data["price"])
        self.total_label.setText(f"Total: ₱{self.order_total}")
        self.order_layout.removeWidget(row)
        row.deleteLater()
        self.selected_order_row = None
        self.change_text.setText("ITEMS TO BE CHANGED:")
        self.bottom_box.hide()

    def apply_changes(self):
        if not self.selected_order_row:
            return
        row = self.selected_order_row
        new_qty  = int(self.bottom_combo1.currentText())
        new_size = self.bottom_combo2.currentText()
        product  = self.product_map.get(row.data["name"], {})
        base     = float(product.get("base_price", 0))
        new_price = int(base * self.size_mult.get(new_size, 1.0)) * new_qty

        self.order_total = max(0, self.order_total - row.data["price"] + new_price)
        self.total_label.setText(f"Total: ₱{self.order_total}")

        row.data.update(qty=new_qty, size=new_size, price=new_price)
        row.qty_label.setText(f"Q: {new_qty}")
        row.size_label.setText(f"S: {new_size}")
        row.price_label.setText(f"₱{new_price}")
        self.change_text.setText(
            f"ITEMS TO BE CHANGED: {row.data['name']} | "
            f"Q: {new_qty} | S: {new_size} | ₱{new_price}"
        )

    def complete_order(self):
        if self.order_total == 0:
            QMessageBox.warning(self, "Empty Order",
                                "Please add items before completing an order.")
            return

        # Collect rows first (needed for payment dialog summary)
        order_rows = []
        report_items = []
        for i in range(self.order_layout.count()):
            w = self.order_layout.itemAt(i).widget()
            if w and hasattr(w, "data"):
                order_rows.append(w.data)
                report_items.append((w.data["name"], w.data["price"]))

        # ── Payment dialog (cash + change calculator) ─────────────────────────
        dlg = PaymentDialog(order_rows, self.order_total, parent=self)
        dlg.exec_()
        if not dlg.payment_confirmed:
            return  # cashier cancelled — keep the order open

        cash_paid    = getattr(dlg, "cash_paid",    self.order_total)
        change_given = getattr(dlg, "change_given", 0)

        # ── Save to DB ────────────────────────────────────────────────────────
        order_id = save_order_to_db(order_rows, self.order_total)

        # ── Show receipt ──────────────────────────────────────────────────────
        receipt = ReceiptDialog(
            order_rows, self.order_total,
            cash_paid, change_given,
            order_id or "—",
            parent=self,
        )
        receipt.exec_()

        # ── Notify report page ─────────────────────────────────────────────────
        if self.report_page:
            self.report_page.reload_from_db_and_refresh()

        # ── Refresh inventory page so stock numbers update live ────────────────
        if self.inventory_page:
            self.inventory_page.load_from_db()

        # ── Refresh ingredients page so stock counts update live ───────────────
        if self.ingredients_page:
            self.ingredients_page.load_from_db()

        # ── Clear order list ──────────────────────────────────────────────────
        for i in reversed(range(self.order_layout.count())):
            item = self.order_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        self.order_total = 0
        self.total_label.setText("Total: ₱0")
        self.selected_item = None
        self.selected_order_row = None
        self.yellow_text.setText("Item Name")
        self.price_text.setText("₱0")
        self.red_image.clear()
        self.bottom_box.hide()

        # ── Refresh menu cards so stock counts update ─────────────────────────
        self.refresh_products()

    def set_menu_preview_image(self, path):
        px = QPixmap(path)
        if px.isNull():
            self.red_image.setText("No Image")
            return
        self.red_image.setText("")
        self.red_image.setPixmap(
            px.scaled(self.red_box.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def set_order_preview_image(self, path):
        px = QPixmap(path)
        if px.isNull():
            self.redd_box_image.setText("No Image")
            return
        self.redd_box_image.setText("")
        self.redd_box_image.setPixmap(
            px.scaled(self.redd_box.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def admin_clicked(self):
        reply = QMessageBox.question(
            self, "Log Out",
            "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            QApplication.exit(LOGOUT_CODE)

    def eventFilter(self, obj, event):
        if event.type() == event.MouseButtonPress:
            widget = QApplication.widgetAt(event.globalPos())
            if widget and not self.order_scroll.isAncestorOf(widget):
                self.bottom_box.hide()
        return super().eventFilter(obj, event)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IMS()
    window.show()
    sys.exit(app.exec_())