# ===== SECTION BEING MODIFIED: app/pages/resource_allocation_page.py =====
# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableView, 
    QGroupBox, QTabWidget, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel
import pandas as pd
from .utils import create_numeric_item, create_text_item, save_table_to_excel

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

        title_label = QLabel("تخصیص بهینه منابع (بودجه و تجهیزات)")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(title_label)
        
        # --- Tab widget for different resource types ---
        self.tab_widget = QTabWidget()
        self.tab_widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        self.budget_tab = QWidget()
        self.equipment_tab = QWidget()
        self.hr_tab = QWidget() # Kept for completeness if needed, but focus is on others
        
        # We setup tabs but we will only populate them based on incoming HR Efficiency data
        self.budget_table = self._setup_tab(self.budget_tab, "تخصیص بودجه")
        self.equipment_table = self._setup_tab(self.equipment_tab, "تخصیص تجهیزات")
        self.hr_table = self._setup_tab(self.hr_tab, "تحلیل نیروی انسانی")
        
        self.tab_widget.addTab(self.budget_tab, "بودجه")
        self.tab_widget.addTab(self.equipment_tab, "تجهیزات")
        self.tab_widget.addTab(self.hr_tab, "نیروی انسانی")
        
        main_layout.addWidget(self.tab_widget)
        
        self._show_initial_message()

    def _setup_tab(self, tab, group_box_title):
        layout = QVBoxLayout(tab)
        group_box = QGroupBox(group_box_title)
        group_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Export Button
        btn_layout = QHBoxLayout()
        btn_layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        export_btn = QPushButton("خروجی اکسل")
        export_btn.setObjectName("ExportButton")
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        
        table_layout = QVBoxLayout()
        table_layout.addLayout(btn_layout)
        
        table_view = QTableView()
        table_view.setSortingEnabled(True)
        table_layout.addWidget(table_view)
        group_box.setLayout(table_layout)
        layout.addWidget(group_box)
        
        export_btn.clicked.connect(lambda: save_table_to_excel(self, table_view, f"resource_allocation.xlsx"))
        
        return table_view
    
    def _show_initial_message(self):
        msg = "برای مشاهده نتایج، لطفاً ابتدا یک تحلیل در صفحه 'بهره‌وری نیروی انسانی' اجرا کنید."
        for table in [self.hr_table, self.budget_table, self.equipment_table]:
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["پیام سیستم"])
            model.appendRow([create_text_item(msg)])
            table.setModel(model)
            table.resizeColumnsToContents()
            table.setColumnWidth(0, 600)

    def update_data(self, data):
        """Public slot to receive data from the HR efficiency page."""
        self.full_data = data
        self.display_all_tables()

    def display_all_tables(self):
        if not self.full_data:
            self._show_initial_message()
            return
        
        # Note: data comes from HR Efficiency page now.
        # HR Page emits: {'input_df': df, 'results_list': [...]} or similar
        # We need to adapt based on what HR page actually sends.
        # Looking at hr_efficiency_page code (which I will modify to emit correct structure),
        # let's assume it sends the merged dataframe or source/results.
        
        self._display_single_table(
            table=self.budget_table,
            resource_keywords=['بودجه', 'هزینه', 'ریال', 'budget', 'cost'],
            resource_name="بودجه"
        )
        self._display_single_table(
            table=self.equipment_table,
            resource_keywords=['تجهیزات', 'ترانس', 'شبکه', 'ظرفیت', 'equipment'],
            resource_name="تجهیزات"
        )
        self._display_single_table(
            table=self.hr_table,
            resource_keywords=['پرسنل', 'نیروی انسانی', 'کارکنان', 'نفر', 'personnel'],
            resource_name="نیروی انسانی"
        )

    def _display_single_table(self, table, resource_keywords, resource_name):
        # We expect 'original_df' and 'results_df' in full_data
        if 'original_df' not in self.full_data or 'results_df' not in self.full_data:
             # Fallback if structure matches old efficiency page for compatibility
             if 'input_df' in self.full_data:
                 input_df = self.full_data['input_df']
                 # results_df logic might be different for HR vs Unit DEA
                 # But let's try to be generic
                 results_df = self.full_data.get('results_df', pd.DataFrame())
             else:
                 return
        else:
            input_df = self.full_data['original_df']
            results_df = self.full_data['results_df']

        # Find relevant columns in input_df
        relevant_inputs = [col for col in input_df.columns if any(kw in col for kw in resource_keywords)]
        
        if not relevant_inputs:
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(["پیام"])
            model.appendRow([create_text_item(f"هیچ شاخص مرتبط با '{resource_name}' در داده‌های ورودی یافت نشد.")])
            table.setModel(model)
            table.resizeColumnsToContents()
            return

        # Merge and Display
        # Assuming results_df has 'dmu' and 'score' (or 'efficiency')
        dmu_col_name = input_df.columns[0]
        
        # Prepare display dataframe
        model = QStandardItemModel()
        
        # Headers: DMU, Score, [Resource Current, Resource Target, Gap]
        headers = ["DMU", "بهره‌وری"]
        for col in relevant_inputs:
            headers.extend([f"{col} (موجود)", f"{col} (پیشنهادی)", "کمبود یا مازاد"]) # Changed "Slack" to Persian
        model.setHorizontalHeaderLabels(headers)
        
        # Merge score into input_df for easier row iteration
        # We need to map dmu names correctly
        if 'dmu' in results_df.columns:
            score_map = dict(zip(results_df['dmu'], results_df['score']))
        else:
            score_map = {}
            
        for idx, row in input_df.iterrows():
            dmu_val = row[dmu_col_name]
            score = score_map.get(dmu_val, 0)
            
            row_items = [
                create_text_item(dmu_val),
                create_numeric_item(score, precision=2)
            ]
            
            for col in relevant_inputs:
                current_val = row[col]
                try:
                    current_val = float(current_val)
                except:
                    current_val = 0
                    
                # Simple Allocation Logic: Target = Current * Score
                # (This is a simplification for visualization since real Slack comes from Solver)
                # If we want real slacks, we need them from the HR DEA result.
                # HR DEA (BCC) usually returns Theta (Score). 
                # Target input = Theta * Input - Slack. 
                # If we don't have explicit slacks from HR solver, we approximate: Target ~ Score * Input
                
                target_val = current_val * score
                gap = current_val - target_val # "Slack" or "Surplus"
                
                row_items.extend([
                    create_numeric_item(current_val, 0),
                    create_numeric_item(target_val, 0),
                    create_numeric_item(gap, 0)
                ])
            
            model.appendRow(row_items)
            
        table.setModel(model)
        table.resizeColumnsToContents()