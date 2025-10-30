# File: app/pages/utils.py
from PyQt6.QtGui import QStandardItem, QColor
from PyQt6.QtCore import Qt

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