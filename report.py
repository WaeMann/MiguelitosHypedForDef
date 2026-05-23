# This is the report.py (Do not remove line)

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QGridLayout, QGraphicsDropShadowEffect,
    QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QColor
from datetime import date

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ── Shared style helpers (mirrors script.py) ─────────────────────────────────

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

# Warm palette for matplotlib charts
CHART_COLORS = [
    "#E8D28C", "#34699A", "#c0392b", "#1e7f3f",
    "#e67e22", "#8e44ad", "#16a085", "#2c3e50",
]


class ReportPage(QWidget):
    def __init__(self, switch_callback=None):
        super().__init__()
        self.switch_callback = switch_callback
        self.sales_data = {}
        self.daily_sales = {}

        self.setWindowTitle("Hyped Mangoes — Reports")
        self.showMaximized()
        self.setStyleSheet("QWidget { background-color: #DED6B2; font-family: 'Segoe UI'; }")

        self._build_ui()
        self.refresh_report()

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
            ("  TRANSACTION",       "TRANSACTION.png",       "pos"),
            ("  INVENTORY", "inventory.png", "inventory"),
        ]:
            btn = QPushButton(label)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(18, 18))
            btn.setFixedSize(160, 36)
            btn.setStyleSheet(NAV_BTN_STYLE)
            _k = page_key
            btn.clicked.connect(lambda checked, k=_k: self.switch_callback(k) if self.switch_callback else None)
            drop_shadow(btn, blur=18, alpha=100)
            nav_layout.addWidget(btn)

        tbl.addWidget(logo)
        tbl.addStretch()
        tbl.addLayout(nav_layout)
        tbl.addStretch()
        root.addWidget(top_bar)

        # Thin separator
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #c8b87a;")
        root.addWidget(sep)

        # ── CONTENT ──────────────────────────────────────────────────────────
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #EFE9D1;
            }

            QScrollBar:vertical {
                background: #DED6B2;
                width: 10px;
                border-radius: 5px;
                margin: 4px;
            }

            QScrollBar::handle:vertical {
                background: #c8b87a;
                border-radius: 5px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #b59f5d;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
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

        # Equal column stretch
        content_grid.setColumnStretch(0, 1)
        content_grid.setColumnStretch(1, 1)

    # ── PANEL FACTORY ────────────────────────────────────────────────────────

    def _make_panel(self):
        panel = QFrame()
        panel.setStyleSheet("QFrame { background-color: white; border-radius: 14px; }")
        return panel

    # ── DATA UPDATES ─────────────────────────────────────────────────────────

    def update_sales(self, items, total):
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

    # ── CHARTS ───────────────────────────────────────────────────────────────

    def plot_pie(self):
        fig = self.pie_canvas.figure
        fig.clear()

        ax = fig.add_subplot(111)
        ax.set_facecolor("#FFFFFF")
        fig.patch.set_facecolor("#FFFFFF")

        if not self.sales_data:
            ax.text(
                0.5, 0.5,
                "No sales yet",
                ha="center",
                va="center",
                fontsize=13,
                color="#aaa"
            )
            ax.axis("off")
            self.pie_canvas.draw()
            return

        labels = list(self.sales_data.keys())
        values = list(self.sales_data.values())

        colors = [
            CHART_COLORS[i % len(CHART_COLORS)]
            for i in range(len(labels))
        ]

        wedges, texts, autotexts = ax.pie(
            values,
            labels=None,
            autopct="%1.0f%%",
            colors=colors,
            startangle=140,
            wedgeprops={
                "linewidth": 2,
                "edgecolor": "white"
            },
            pctdistance=0.75,
        )

        # IMPORTANT
        ax.axis("equal")

        for at in autotexts:
            at.set_fontsize(10)
            at.set_color("white")
            at.set_fontweight("bold")

        ax.legend(
            wedges,
            labels,
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=9,
            frameon=False,
        )

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

        dates = sorted(self.daily_sales.keys())
        values = [self.daily_sales[d] for d in dates]
        x_pos = list(range(len(dates)))

        bars = ax.bar(
            x_pos, values,
            width=0.5,
            color="#34699A",
            edgecolor="white",
            linewidth=1.5,
            zorder=3,
        )

        # Value labels on bars
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(values) * 0.02,
                f"₱{val:,.0f}",
                ha="center", va="bottom",
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


# ── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportPage()
    window.show()
    sys.exit(app.exec_())