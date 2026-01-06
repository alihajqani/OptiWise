# ===== SECTION BEING MODIFIED: app/pages/utils.py =====
# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtGui import QStandardItem, QColor
from PyQt6.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QIcon

CLUSTER_COLORS = [
    "#E6F7FF", "#F6FFED", "#FFFBE6", "#FFF1F0", "#F9F0FF",
    "#E6FFFB", "#FCFFE6", "#FFF7E6", "#F0F5FF", "#FEFFE6"
]

def get_color_for_cluster(cluster_id):
    try:
        cluster_id = int(cluster_id)
        if cluster_id >= 1:
            return QColor(CLUSTER_COLORS[(cluster_id - 1) % len(CLUSTER_COLORS)])
    except (ValueError, TypeError):
        pass
    return None

def create_numeric_item(value, precision=2):
    item = QStandardItem()
    try:
        float_val = float(value)
        item.setData(float_val, Qt.ItemDataRole.UserRole)
        if precision == 0:
            item.setText(f"{int(float_val):,}")
        else:
            item.setText(f"{float_val:,.{precision}f}")
    except (ValueError, TypeError):
        item.setText(str(value))
    
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item

def create_text_item(text):
    item = QStandardItem(str(text))
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item

def save_table_to_excel(parent, table_view, default_name="results.xlsx"):
    """
    Exports the content of a QTableView (QStandardItemModel) to an Excel file.
    """
    model = table_view.model()
    if not model or model.rowCount() == 0:
        QMessageBox.warning(parent, "خطا", "جدولی برای ذخیره وجود ندارد.")
        return

    file_path, _ = QFileDialog.getSaveFileName(parent, "ذخیره فایل اکسل", default_name, "Excel Files (*.xlsx)")
    if not file_path:
        return

    try:
        # Extract headers
        headers = []
        for col in range(model.columnCount()):
            headers.append(model.headerData(col, Qt.Orientation.Horizontal))

        # Extract data
        data = []
        for row in range(model.rowCount()):
            row_data = []
            for col in range(model.columnCount()):
                index = model.index(row, col)
                # Prefer raw data (UserRole) for numbers, otherwise display text
                val = model.data(index, Qt.ItemDataRole.UserRole)
                if val is None:
                    val = model.data(index, Qt.ItemDataRole.DisplayRole)
                row_data.append(val)
            data.append(row_data)

        df = pd.DataFrame(data, columns=headers)
        df.to_excel(file_path, index=False)
        QMessageBox.information(parent, "موفقیت", f"فایل با موفقیت ذخیره شد:\n{file_path}")
    except Exception as e:
        QMessageBox.critical(parent, "خطا", f"خطا در ذخیره فایل اکسل:\n{e}")

# ===== BASE PAGE CLASS =====
class BasePage(QWidget):
    """
    A base class for all pages (except WelcomePage) to provide a consistent
    "Back to Home" button and a content layout.
    """
    back_to_home_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top bar for the back button
        top_bar_widget = QWidget()
        top_bar_widget.setFixedHeight(60)
        # --- MODIFICATION: Set object name for styling ---
        top_bar_widget.setObjectName("PageTopBar") 
        
        top_bar_layout = QHBoxLayout(top_bar_widget)
        top_bar_layout.setContentsMargins(20, 0, 20, 0)

        back_button = QPushButton("بازگشت به صفحه اصلی")
        back_button.setObjectName("BackButton")
        back_button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        # --- MODIFICATION: Use white icon for dark background ---
        back_button.setIcon(QIcon("assets/icons/W-home.png"))
        back_button.setIconSize(QSize(24, 24))
        back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        back_button.clicked.connect(self.back_to_home_requested.emit)

        top_bar_layout.addWidget(back_button)
        top_bar_layout.addStretch()

        main_layout.addWidget(top_bar_widget)

        # 2. Content area for child pages to populate
        content_container = QWidget()
        self.content_layout = QVBoxLayout(content_container)
        self.content_layout.setContentsMargins(25, 25, 25, 25)

        main_layout.addWidget(content_container)