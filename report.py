import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt
from datetime import date
import matplotlib
matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ReportPage(QWidget):
    def __init__(self, switch_callback=None):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #DED6B2;
            }
        """)

        # ===== CALLBACK =====
        self.switch_callback = switch_callback

        # ===== DYNAMIC DATA =====
        self.sales_data = {}

        self.daily_sales = {}

        # ===== MAIN LAYOUT =====
        main_layout = QHBoxLayout(self)

        # ================= LEFT SIDEBAR =================
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #0f4c81; color: white;")

        side_layout = QVBoxLayout(sidebar)

        title = QLabel("MIGUELITOS")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: gold;")
        title.setAlignment(Qt.AlignCenter)

        btn_home = QPushButton("HOME")
        btn_inventory = QPushButton("INVENTORY")

        for btn in [btn_home, btn_inventory]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f5c542;
                    border-radius: 15px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e0b030;
                }
            """)

        btn_home.clicked.connect(lambda: self.switch_callback("pos"))
        btn_inventory.clicked.connect(lambda: self.switch_callback("inventory"))

        side_layout.addWidget(title)
        side_layout.addSpacing(30)
        side_layout.addWidget(btn_home)
        side_layout.addWidget(btn_inventory)
        side_layout.addStretch()

        # ================= MAIN CONTENT =================
        content = QFrame()
        content_layout = QVBoxLayout(content)

        grid = QGridLayout()

        # ================= PIE CHART =================
        pie_frame = QFrame()
        pie_layout = QVBoxLayout(pie_frame)

        pie_title = QLabel("Sales Breakdown by Item")
        pie_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.pie_canvas = FigureCanvas(Figure(figsize=(4, 3)))
        pie_layout.addWidget(pie_title)
        pie_layout.addWidget(self.pie_canvas)

        # ================= SALES TRACKER =================
        tracker_frame = QFrame()
        tracker_frame.setStyleSheet("background: white; border-radius: 10px;")

        self.tracker_layout = QVBoxLayout(tracker_frame)

        # ================= BAR GRAPH =================
        bar_frame = QFrame()
        bar_layout = QVBoxLayout(bar_frame)

        bar_title = QLabel("Daily Sales")
        bar_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.bar_canvas = FigureCanvas(Figure(figsize=(5, 3)))

        bar_layout.addWidget(bar_title)
        bar_layout.addWidget(self.bar_canvas)

        # ================= GRID =================
        grid.addWidget(pie_frame, 0, 0)
        grid.addWidget(tracker_frame, 0, 1)
        grid.addWidget(bar_frame, 1, 0, 1, 2)

        content_layout.addLayout(grid)

        # ================= ADD TO MAIN =================
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

        # ===== INITIAL DRAW =====
        self.refresh_report()

    # ================= UPDATE FROM POS =================
    def update_sales(self, items, total):
        if not items:
            return

        for item_name, value in items:
            self.sales_data[item_name] = self.sales_data.get(item_name, 0) + value

        # Add to today's sales (simple: last index)
        today = date.today().isoformat()

        self.daily_sales[today] = self.daily_sales.get(today, 0) + total

        self.refresh_report()

    # ================= REFRESH EVERYTHING =================
    def refresh_report(self):
        self.plot_pie()
        self.plot_bar()
        self.update_tracker()

    # ================= UPDATE TRACKER =================
    def update_tracker(self):
        # Clear old
        for i in reversed(range(self.tracker_layout.count())):
            item = self.tracker_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        total_sales = sum(self.sales_data.values())

        total_label = QLabel(f"Total Sales:\n₱{total_sales:.2f}")
        total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f4c81;")
        self.tracker_layout.addWidget(total_label)

        if total_sales == 0:
            self.tracker_layout.addWidget(QLabel("No Sales Yet"))
            return

        for item, value in self.sales_data.items():
            percent = (value / total_sales) * 100
            row = QLabel(f"{item}   ₱{value:.2f}   {percent:.0f}%")
            self.tracker_layout.addWidget(row)

    # ================= PIE CHART =================
    def plot_pie(self):
        self.pie_canvas.figure.clear()
        ax = self.pie_canvas.figure.add_subplot(111)

        if not self.sales_data:
            ax.text(0.5, 0.5, "No Sales Yet", ha='center', va='center')
            self.pie_canvas.draw()
            return

        labels = list(self.sales_data.keys())
        values = list(self.sales_data.values())

        ax.pie(values, labels=labels, autopct='%1.0f%%')
        self.pie_canvas.draw()

    # ================= BAR GRAPH =================
    def plot_bar(self):
        self.bar_canvas.figure.clear()
        ax = self.bar_canvas.figure.add_subplot(111)

        if not self.daily_sales:
            ax.text(0.5, 0.5, "No Sales Yet", ha='center', va='center')
            self.bar_canvas.draw()
            return

        dates = sorted(self.daily_sales.keys())
        values = [self.daily_sales[d] for d in dates]

        # 🔥 FIX: use numeric positions instead of strings
        x_pos = list(range(len(dates)))

        ax.bar(x_pos, values, width=0.5)  # adjust bar width here

        ax.set_xticks(x_pos)
        ax.set_xticklabels(dates, rotation=45, ha='right')

        ax.set_ylabel("Sales (₱)")
        ax.set_title("Daily Sales")

        self.bar_canvas.draw()

        # ================= MAIN ENTRY POINT =================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ReportPage()
    window.show()

    sys.exit(app.exec_())