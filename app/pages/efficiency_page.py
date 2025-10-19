# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTableView,
    QMessageBox, QGroupBox, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import traceback

from ..logic.dea_analysis import run_dea_analysis

# ===== HELPER FUNCTION FOR NORMALIZATION =====
def normalize_dmu_name(name):
    if not isinstance(name, str): name = str(name)
    name = name.replace("ي", "ی").replace("ك", "ک")
    return "".join(name.split())

# ===== CORE UI FOR EFFICIENCY PAGE =====
class EfficiencyPage(QWidget):
    def __init__(self):
        super().__init__()
        self.clustering_data = None
        self.dea_df = None
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25); main_layout.setSpacing(15)
        title_label = QLabel("فاز دوم: محاسبه بهره‌وری (DEA)"); title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight); main_layout.addWidget(title_label)
        
        # --- Simplified Top Controls ---
        upload_group = QGroupBox("مرحله ۱: بارگذاری فایل داده بهره‌وری")
        upload_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        upload_layout = QHBoxLayout()
        self.upload_button = QPushButton("انتخاب فایل اکسل")
        self.file_path_label = QLabel("هنوز فایلی انتخاب نشده")
        upload_layout.addWidget(self.upload_button)
        upload_layout.addWidget(self.file_path_label, 1)
        upload_group.setLayout(upload_layout)
        main_layout.addWidget(upload_group)

        middle_splitter = QSplitter(Qt.Orientation.Horizontal)
        io_selection_group = QGroupBox("مرحله ۲: انتخاب شاخص‌های ورودی و خروجی")
        io_selection_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        io_layout = QHBoxLayout(); self.inputs_list = QListWidget(); self.outputs_list = QListWidget()
        self.inputs_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.outputs_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        inputs_group = QGroupBox("ورودی‌ها"); inputs_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        inputs_layout = QVBoxLayout(); inputs_layout.addWidget(self.inputs_list); inputs_group.setLayout(inputs_layout)
        outputs_group = QGroupBox("خروجی‌ها"); outputs_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        outputs_layout = QVBoxLayout(); outputs_layout.addWidget(self.outputs_list); outputs_group.setLayout(outputs_layout)
        io_layout.addWidget(inputs_group, 1); io_layout.addWidget(outputs_group, 1)
        io_selection_group.setLayout(io_layout); middle_splitter.addWidget(io_selection_group)
        
        run_group = QGroupBox("مرحله ۳: اجرا"); run_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        run_layout = QVBoxLayout(); self.run_button = QPushButton("محاسبه بهره‌وری")
        self.run_button.setEnabled(False); run_layout.addWidget(self.run_button); run_group.setLayout(run_layout)
        middle_splitter.addWidget(run_group); middle_splitter.setSizes([400, 100]); main_layout.addWidget(middle_splitter)

        results_group = QGroupBox("نتایج تحلیل بهره‌وری (SBM ورودی-محور)"); results_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        results_layout = QVBoxLayout(); self.results_table = QTableView()
        results_layout.addWidget(self.results_table); results_group.setLayout(results_layout)
        main_layout.addWidget(results_group, 1)
        
        self.upload_button.clicked.connect(self.load_dea_data); self.run_button.clicked.connect(self.run_analysis)

    def update_with_clustering_data(self, clustering_data):
        """Simply stores the clustering data if it's available. Does not enable/disable UI."""
        self.clustering_data = clustering_data

    def run_analysis(self):
        if self.dea_df is None:
            QMessageBox.warning(self, "داده ناقص", "لطفاً ابتدا فایل داده بهره‌وری را بارگذاری کنید."); return

        selected_inputs = [item.text() for item in self.inputs_list.selectedItems()]
        selected_outputs = [item.text() for item in self.outputs_list.selectedItems()]
        if not selected_inputs or not selected_outputs:
            QMessageBox.warning(self, "شاخص انتخاب نشده", "لطفاً شاخص‌های ورودی و خروجی را انتخاب کنید."); return

        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            
            # --- CRITICAL CHANGE: DEA is now run on the ENTIRE dataframe ---
            dmu_column_dea = self.dea_df.columns[0]
            results = run_dea_analysis(self.dea_df, dmu_column_dea, selected_inputs, selected_outputs)
            
            self.display_results(results, selected_inputs)

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "خطا در تحلیل", f"یک خطای پیش‌بینی نشده رخ داد:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()

    def display_results(self, results, selected_inputs):
        # Convert results to a DataFrame for easy merging
        results_df = pd.DataFrame(results)

        # --- NEW LOGIC: Conditionally merge with clustering data ---
        if self.clustering_data and 'clusters_df' in self.clustering_data:
            clusters_df = self.clustering_data['clusters_df']
            
            # Normalize names in both dataframes for a reliable merge
            results_df['norm_dmu'] = results_df['dmu'].apply(normalize_dmu_name)
            clusters_df['norm_dmu'] = clusters_df['DMU'].apply(normalize_dmu_name)

            # Perform a left merge to add cluster info to the results
            final_df = pd.merge(results_df, clusters_df[['norm_dmu', 'cluster']], on='norm_dmu', how='left')
            final_df.drop(columns=['norm_dmu'], inplace=True)
            final_df['cluster'] = final_df['cluster'].fillna('-').astype(int, errors='ignore')
        else:
            # If no clustering data, just add an empty 'cluster' column
            final_df = results_df
            final_df['cluster'] = '-'
        
        model = QStandardItemModel()
        headers = ["خوشه", "DMU", "امتیاز بهره‌وری"] + [f"اسلک {inp}" for inp in selected_inputs] + ["مجموعه مرجع"]
        model.setHorizontalHeaderLabels(headers)

        # Sort by cluster, then by efficiency
        final_df = final_df.sort_values(by=['cluster', 'efficiency'])

        for _, row in final_df.iterrows():
            row_items = [
                QStandardItem(str(row['cluster'])),
                QStandardItem(str(row['dmu'])),
                QStandardItem(f"{row.get('efficiency', 0):.4f}")
            ]
            for inp in selected_inputs:
                row_items.append(QStandardItem(f"{row['slacks'].get(inp, 0):.2f}"))
            row_items.append(QStandardItem(row['peers']))
            
            for item in row_items:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            model.appendRow(row_items)
        
        self.results_table.setModel(model)
        self.results_table.resizeColumnsToContents()

    def load_dea_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل داده بهره‌وری", "", "Excel Files (*.xlsx *.xls)")
        if not file_path: return
        try: self.dea_df = pd.read_excel(file_path); self.file_path_label.setText(file_path.split('/')[-1]); self.populate_io_lists(); self.run_button.setEnabled(True)
        except Exception as e: QMessageBox.critical(self, "خطا در خواندن فایل", f"فایل اکسل قابل پردازش نیست:\n{e}"); self.run_button.setEnabled(False)

    def populate_io_lists(self):
        self.inputs_list.clear(); self.outputs_list.clear()
        if self.dea_df is None: return
        for col in self.dea_df.columns[1:]:
            self.inputs_list.addItem(QListWidgetItem(col)); self.outputs_list.addItem(QListWidgetItem(col))