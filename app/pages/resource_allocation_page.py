# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableView, 
    QGroupBox, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel
import pandas as pd
# --- Import helper functions from the central utils file ---
from .utils import create_numeric_item, create_text_item

# ===== UI & APPLICATION LOGIC =====
class ResourceAllocationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.full_data = None
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        title_label = QLabel("تخصیص بهینه منابع")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(title_label)
        
        # --- Tab widget for different resource types ---
        self.tab_widget = QTabWidget()
        self.tab_widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        self.hr_tab = QWidget()
        self.budget_tab = QWidget()
        self.equipment_tab = QWidget()
        
        self.hr_table = self._setup_tab(self.hr_tab, "تخصیص نیروی انسانی")
        self.budget_table = self._setup_tab(self.budget_tab, "تخصیص بودجه")
        self.equipment_table = self._setup_tab(self.equipment_tab, "تخصیص تجهیزات")
        
        self.tab_widget.addTab(self.hr_tab, "نیروی انسانی")
        self.tab_widget.addTab(self.budget_tab, "بودجه")
        self.tab_widget.addTab(self.equipment_tab, "تجهیزات")
        
        main_layout.addWidget(self.tab_widget)
        
        self._show_initial_message()

    def _setup_tab(self, tab, group_box_title):
        layout = QVBoxLayout(tab)
        group_box = QGroupBox(group_box_title)
        group_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        table_layout = QVBoxLayout()
        table_view = QTableView()
        table_view.setSortingEnabled(True)
        table_layout.addWidget(table_view)
        group_box.setLayout(table_layout)
        layout.addWidget(group_box)
        return table_view
    
    def _show_initial_message(self):
        for table in [self.hr_table, self.budget_table, self.equipment_table]:
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["پیام"])
            model.appendRow([create_text_item("برای مشاهده نتایج، لطفاً ابتدا یک تحلیل در صفحه 'محاسبه بهره‌وری واحد' اجرا کنید.")])
            table.setModel(model)
            table.resizeColumnsToContents()

    def update_data(self, data):
        """Public slot to receive data from the efficiency page."""
        self.full_data = data
        self.display_all_tables()

    def display_all_tables(self):
        if not self.full_data:
            self._show_initial_message()
            return
            
        self._display_single_table(
            table=self.hr_table,
            resource_keywords=['پرسنل', 'نیروی انسانی', 'کارکنان', 'نفر'],
            resource_name="نیروی انسانی"
        )
        self._display_single_table(
            table=self.budget_table,
            resource_keywords=['بودجه', 'هزینه', 'ریال'],
            resource_name="بودجه"
        )
        self._display_single_table(
            table=self.equipment_table,
            resource_keywords=['تجهیزات', 'ترانس', 'شبکه', 'ظرفیت'],
            resource_name="تجهیزات"
        )

    def _display_single_table(self, table, resource_keywords, resource_name):
        input_df = self.full_data['input_df']
        results_df = self.full_data['results_df']
        
        relevant_inputs = [col for col in input_df.columns if any(kw in col for kw in resource_keywords)]
        
        if not relevant_inputs:
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["پیام"])
            model.appendRow([create_text_item(f"هیچ شاخص ورودی مرتبط با '{resource_name}' در تحلیل بهره‌وری انتخاب نشده است.")])
            table.setModel(model)
            table.resizeColumnsToContents()
            return

        dmu_col_name = input_df.columns[0]
        results_df_renamed = results_df.rename(columns={'dmu': dmu_col_name})
        
        display_df = pd.merge(input_df[[dmu_col_name] + relevant_inputs], results_df_renamed, on=dmu_col_name, how='left')
        
        model = QStandardItemModel()
        headers = ["DMU", "بهره‌وری"]
        for col in relevant_inputs:
            headers.extend([f"{col} (موجود)", f"{col} (مورد نیاز)", f"{col} (مازاد)"])
        model.setHorizontalHeaderLabels(headers)
        
        display_df = display_df.sort_values(by='efficiency', ascending=False)

        for _, row in display_df.iterrows():
            row_items = [
                create_text_item(row[dmu_col_name]),
                create_numeric_item(row.get('efficiency', 0.0), precision=2)
            ]
            for col in relevant_inputs:
                current_val = row.get(col, 0)
                slacks_dict = row.get('slacks', {})
                slack_val = slacks_dict.get(col, 0) if isinstance(slacks_dict, dict) else 0
                required_val = current_val - slack_val
                
                row_items.extend([
                    create_numeric_item(current_val, 0),
                    create_numeric_item(required_val, 0),
                    create_numeric_item(slack_val, 0)
                ])
            
            model.appendRow(row_items)
            
        table.setModel(model)
        table.resizeColumnsToContents()