import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QFrame, QGraphicsDropShadowEffect,
    QPushButton, QScrollArea, QGridLayout, QVBoxLayout, QHBoxLayout,
    QComboBox, QSplitter, QSizePolicy, QMessageBox, QSpacerItem,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap

# ---------------------------------------------------------------------------
# Try importing ReportPage; gracefully skip if not present
# ---------------------------------------------------------------------------
try:
    from report import ReportPage
except ImportError:
    ReportPage = None

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
FLAVORS = {
    "Ice Creams": [
        "Vanilla Ice Cream",
        "Chocolate Ice Cream",
        "Strawberry Ice Cream",
        "Mango Ice Cream",
        "Hiyuki-Onna Cream",
    ],
    "Floats": [
        "Mint Chocolate Chip Float",
        "Rocky Road Float",
        "Cookies & Cream Float",
        "Chocolate Cola Float",
    ],
    "Shakes": [
        "Chocolate Shake",
        "Vanilla Shake",
        "Strawberry Shake",
        "Ube Shake",
    ],
}

FLAVOR_IMAGES = {
    "Vanilla Ice Cream":        "miguelitos_mangocheesecake.png",
    "Chocolate Ice Cream":      "miguelitos_mangosago.png",
    "Strawberry Ice Cream":     "images/strawberry.png",
    "Mango Ice Cream":          "miguelitos_hypedmango.png",
    "Hiyuki-Onna Cream":        "YuCream.jpg",
    "Mint Chocolate Chip Float":"miguelitos_mangojuice.png",
    "Rocky Road Float":         "chisapiano.jpg",
    "Cookies & Cream Float":    "miguelitos_mangoshake.png",
    "Chocolate Cola Float":     "miguelitos_nuttymango.png",
    "Chocolate Shake":          "miguelitos_mangosupreme.png",
    "Vanilla Shake":            "miguelitos_purpleyamango.png",
    "Strawberry Shake":         "miguelitos_ubemangocone.png",
    "Ube Shake":                "raidenwoofwoof.jpg",
}

FLAVOR_PRICES = {
    "Vanilla Ice Cream":        45,
    "Chocolate Ice Cream":      50,
    "Strawberry Ice Cream":     55,
    "Mango Ice Cream":          60,
    "Hiyuki-Onna Cream":        80,
    "Mint Chocolate Chip Float":70,
    "Rocky Road Float":         75,
    "Cookies & Cream Float":    75,
    "Chocolate Cola Float":     65,
    "Chocolate Shake":          60,
    "Vanilla Shake":            55,
    "Strawberry Shake":         65,
    "Ube Shake":                70,
}

SIZE_MULTIPLIER = {
    "12oz": 1.0,
    "16oz": 1.3,
}

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
# Main window
# ---------------------------------------------------------------------------
class IMS(QWidget):
    def __init__(self, switch_callback=None, report_page=None, inventory_page=None):
        super().__init__()
        self.switch_callback = switch_callback
        self.report_page = report_page
        self.inventory_page = inventory_page

        self.selected_item = None
        self.order_total = 0
        self.selected_order_row = None

        self.setWindowTitle("Inventory Management System")
        self.setMinimumSize(900, 600)
        self.resize(1350, 700)

        self.setStyleSheet("QWidget { background-color: #DED6B2; }")

        # ── Root horizontal layout: sidebar | main area ──────────────────────
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

        # Logo
        self.title_logo = QLabel()
        self.title_logo.setFixedHeight(110)
        self.title_logo.setAlignment(Qt.AlignCenter)
        self.title_logo.setStyleSheet("background: transparent;")
        self._set_pixmap(self.title_logo, "hypedmangologo.png", 300, 110)
        sidebar_layout.addWidget(self.title_logo)

        # Yellow card
        yellow_card = QFrame()
        yellow_card.setStyleSheet("background-color: #E8D28C; border-radius: 20px;")
        yellow_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        drop_shadow(yellow_card, blur=25, alpha=180)
        sidebar_layout.addWidget(yellow_card, stretch=1)

        yellow_layout = QVBoxLayout(yellow_card)
        yellow_layout.setContentsMargins(15, 15, 15, 15)
        yellow_layout.setSpacing(8)

        # Item name + price row
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

        # Preview image box
        self.red_box = QFrame()
        self.red_box.setStyleSheet("background-color: #EFE9D1; border-radius: 12px;")
        self.red_box.setMinimumHeight(120)
        self.red_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.red_box.setFixedHeight(150)

        red_inner = QVBoxLayout(self.red_box)
        red_inner.setContentsMargins(0, 0, 0, 0)
        self.red_image = QLabel()
        self.red_image.setAlignment(Qt.AlignCenter)
        self.red_image.setStyleSheet("background: transparent;")
        red_inner.addWidget(self.red_image)
        yellow_layout.addWidget(self.red_box)

        # Qty / Size / Add Item row
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
        self.combo2.addItems(["12oz", "16oz"])
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

        # Order scroll
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

        # Total + Complete Order row
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

        # ── TOP BAR ──────────────────────────────────────────────────────────
        top_bar = QFrame()
        top_bar.setFixedHeight(80)
        top_bar.setStyleSheet("background-color: #DED6B2;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(30, 0, 30, 0)
        top_bar_layout.setSpacing(10)

        self.inventory_top_btn = QPushButton("INVENTORY")
        self.inventory_top_btn.setFixedSize(140, 35)
        self.inventory_top_btn.setStyleSheet(NAV_BTN_STYLE)
        drop_shadow(self.inventory_top_btn, blur=20, alpha=120)

        self.report_top_btn = QPushButton("REPORT")
        self.report_top_btn.setFixedSize(140, 35)
        self.report_top_btn.setStyleSheet(NAV_BTN_STYLE)
        drop_shadow(self.report_top_btn, blur=20, alpha=120)

        self.admin_btn = QPushButton("LOG OUT")
        self.admin_btn.setFixedSize(150, 35)
        self.admin_btn.setStyleSheet(NAV_BTN_STYLE)
        drop_shadow(self.admin_btn, blur=20, alpha=120)

        top_bar_layout.addWidget(self.inventory_top_btn)
        top_bar_layout.addWidget(self.report_top_btn)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.admin_btn)
        main_area_layout.addWidget(top_bar)

        if self.switch_callback:
            self.report_top_btn.clicked.connect(lambda: self.switch_callback("report"))
            self.inventory_top_btn.clicked.connect(lambda: self.switch_callback("inventory"))
        self.admin_btn.clicked.connect(self.admin_clicked)

        # ── MENU SCROLL AREA ─────────────────────────────────────────────────
        self.scroll_area = DragScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #EFE9D1; border: none;")
        self.scroll_content = QWidget()
        self.scroll_area.setWidget(self.scroll_content)

        menu_layout = QVBoxLayout(self.scroll_content)
        menu_layout.setContentsMargins(20, 20, 20, 20)
        menu_layout.setSpacing(30)

        for title, items in FLAVORS.items():
            menu_layout.addWidget(self._create_section(title, items))

        main_area_layout.addWidget(self.scroll_area, stretch=1)

        # ── CHANGE ORDER DETAILS BAR ─────────────────────────────────────────
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
        self.bottom_combo2.addItems(["12oz", "16oz"])
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

        # Small preview image in bottom bar
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

        # Event filter to auto-hide bottom box on outside click
        self.scroll_area.viewport().installEventFilter(self)
        self.scroll_content.installEventFilter(self)
        self.installEventFilter(self)

    # -------------------------------------------------------------------------
    # Section builder
    # -------------------------------------------------------------------------
    def _create_section(self, title, items):
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(10)

        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: black;")
        layout.addWidget(lbl)

        grid = QGridLayout()
        grid.setSpacing(15)

        for i, name in enumerate(items):
            row, col = divmod(i, 3)

            card = QFrame()
            card.setFixedSize(250, 150)
            card.setStyleSheet("""
                QFrame { background-color: #E8D28C; border-radius: 15px; }
                QFrame:hover { background-color: #D9BE70; }
            """)
            drop_shadow(card, blur=25, alpha=150)
            card.mousePressEvent = lambda e, n=name: self.item_clicked(n)

            vbox = QVBoxLayout(card)
            vbox.setAlignment(Qt.AlignCenter)
            vbox.setSpacing(5)

            img = QLabel()
            img.setAlignment(Qt.AlignCenter)
            img.setStyleSheet("background: transparent;")
            path = FLAVOR_IMAGES.get(name, "images/default.png")
            px = QPixmap(path)
            if not px.isNull():
                img.setPixmap(px.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                img.setText("No Image")

            text = QLabel(name)
            text.setAlignment(Qt.AlignCenter)
            text.setStyleSheet("color: #2b2b2b; font-weight: bold;")

            vbox.addWidget(img)
            vbox.addWidget(text)
            grid.addWidget(card, row, col)

        layout.addLayout(grid)
        return section

    # -------------------------------------------------------------------------
    # Pixmap helper
    # -------------------------------------------------------------------------
    def _set_pixmap(self, label: QLabel, path: str, w: int, h: int):
        px = QPixmap(path)
        if not px.isNull():
            label.setPixmap(px.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            label.setText("No Image")

    # -------------------------------------------------------------------------
    # Slots
    # -------------------------------------------------------------------------
    def item_clicked(self, name):
        self.bottom_box.hide()
        self.selected_item = name
        self.yellow_text.setText(name)
        self.update_price_display()
        self.set_menu_preview_image(FLAVOR_IMAGES.get(name, "images/default.png"))

    def update_price_display(self):
        if not self.selected_item:
            return
        base = FLAVOR_PRICES.get(self.selected_item, 0)
        size = self.combo2.currentText()
        final = int(base * SIZE_MULTIPLIER.get(size, 1))
        self.price_text.setText(f"₱{final}")

    def button_clicked(self):
        if not self.selected_item:
            return
        qty = int(self.combo1.currentText())
        size = self.combo2.currentText()
        base = FLAVOR_PRICES.get(self.selected_item, 0)
        price = int(base * SIZE_MULTIPLIER.get(size, 1)) * qty

        self.order_total += price
        self.total_label.setText(f"Total: ₱{self.order_total}")

        row = ClickableRow()
        row.clicked.connect(self.order_row_clicked)
        row.setStyleSheet("QFrame { background-color: #f5f5f5; border-radius: 6px; }")
        row.data = {
            "name": self.selected_item,
            "qty": qty,
            "size": size,
            "price": price,
            "image": FLAVOR_IMAGES.get(self.selected_item, "images/default.png"),
        }

        g = QGridLayout(row)
        g.setContentsMargins(8, 4, 8, 4)

        row.name_label  = QLabel(self.selected_item)
        row.qty_label   = QLabel(f"Q: {qty}")
        row.size_label  = QLabel(f"S: {size}")
        row.price_label = QLabel(f"₱{price}")

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
        base     = FLAVOR_PRICES.get(row.data["name"], 0)
        new_price = int(base * SIZE_MULTIPLIER.get(new_size, 1)) * new_qty

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
        QMessageBox.information(self, "Order Complete", f"Total Price: ₱{self.order_total}")

        report_items = []
        inventory_items = []

        for i in range(self.order_layout.count()):
            w = self.order_layout.itemAt(i).widget()
            if w and hasattr(w, "data"):
                report_items.append((w.data["name"], w.data["price"]))
                inventory_items.append((w.data["name"], int(w.data["qty"])))

        if self.report_page:
            self.report_page.update_sales(report_items, self.order_total)
        if self.inventory_page:
            self.inventory_page.reduce_stock(inventory_items)

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
        import subprocess
        subprocess.Popen([sys.executable, "login.py"])
        self.close()
        QApplication.quit()

    def center(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.center() - self.rect().center())

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
    window.center()
    sys.exit(app.exec_())