# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTableView,
    QMessageBox, QGroupBox, QComboBox, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import traceback

from ..logic.dea_analysis import run_dea_analysis
from ..logic.clustering_analysis import run_single_clustering_model


# ===== UTILITY FUNCTIONS =====
def create_numeric_item(value, precision=2):
    """Creates a QStandardItem that sorts numerically."""
    item = QStandardItem()
    try:
        float_val = float(value)
        item.setData(float_val, Qt.ItemDataRole.UserRole)
        item.setText(f"{float_val:.{precision}f}")
    except (ValueError, TypeError):
        item.setText(str(value)) # Fallback for non-numeric
    
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item

def create_text_item(text):
    """Creates a standard, non-editable text QStandardItem."""
    item = QStandardItem(str(text))
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item


def normalize_dmu_name(name):
    if not isinstance(name, str):
        name = str(name)
    name = name.replace("ي", "ی").replace("ك", "ک")
    return "".join(name.split())


# ===== UI & APPLICATION LOGIC =====
class EfficiencyPage(QWidget):
    def __init__(self):
        super().__init__()
        self.clustering_data = None
        self.dea_df = None
        self.full_dea_results_df = None
        self.selected_inputs = []
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25); main_layout.setSpacing(15)
        title_label = QLabel("فاز دوم: محاسبه بهره‌وری (DEA)"); title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight); main_layout.addWidget(title_label)
        top_controls_layout = QHBoxLayout()
        upload_group = QGroupBox("مرحله ۱: بارگذاری فایل داده بهره‌وری"); upload_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        upload_layout = QHBoxLayout(); self.upload_button = QPushButton("انتخاب فایل اکسل")
        self.file_path_label = QLabel("هنوز فایلی انتخاب نشده"); upload_layout.addWidget(self.upload_button)
        upload_layout.addWidget(self.file_path_label, 1); upload_group.setLayout(upload_layout)
        top_controls_layout.addWidget(upload_group, 1); main_layout.addLayout(top_controls_layout)
        middle_splitter = QSplitter(Qt.Orientation.Horizontal)
        io_selection_group = QGroupBox("مرحله ۲: انتخاب شاخص‌های ورودی و خروجی"); io_selection_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        io_layout = QHBoxLayout(); self.inputs_list = QListWidget(); self.outputs_list = QListWidget()
        self.inputs_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection); self.outputs_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        inputs_group = QGroupBox("ورودی‌ها"); inputs_group.setAlignment(Qt.AlignmentFlag.AlignRight); inputs_layout = QVBoxLayout(); inputs_layout.addWidget(self.inputs_list); inputs_group.setLayout(inputs_layout)
        outputs_group = QGroupBox("خروجی‌ها"); outputs_group.setAlignment(Qt.AlignmentFlag.AlignRight); outputs_layout = QVBoxLayout(); outputs_layout.addWidget(self.outputs_list); outputs_group.setLayout(outputs_layout)
        io_layout.addWidget(inputs_group, 1); io_layout.addWidget(outputs_group, 1)
        io_selection_group.setLayout(io_layout); middle_splitter.addWidget(io_selection_group)
        run_group = QGroupBox("مرحله ۳: اجرا"); run_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        run_layout = QVBoxLayout(); self.run_button = QPushButton("محاسبه بهره‌وری"); self.run_button.setEnabled(False)
        run_layout.addWidget(self.run_button); run_group.setLayout(run_layout)
        middle_splitter.addWidget(run_group); middle_splitter.setSizes([400, 100]); main_layout.addWidget(middle_splitter)
        results_group = QGroupBox("نتایج تحلیل بهره‌وری (SBM ورودی-محور)"); results_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        results_layout = QVBoxLayout()
        self.cluster_filter_combo = QComboBox(); self.cluster_filter_combo.setEnabled(False)
        results_layout.addWidget(self.cluster_filter_combo)
        self.results_table = QTableView()
        # --- SORTING ENABLED ---
        self.results_table.setSortingEnabled(True)
        results_layout.addWidget(self.results_table); results_group.setLayout(results_layout)
        main_layout.addWidget(results_group, 1)
        self.upload_button.clicked.connect(self.load_dea_data); self.run_button.clicked.connect(self.run_analysis)
        self.cluster_filter_combo.currentIndexChanged.connect(self.filter_display)

    def update_with_clustering_data(self, clustering_data):
        self.clustering_data = clustering_data
        self.cluster_filter_combo.clear()
        
        if clustering_data and 'all_results' in clustering_data:
            self.cluster_filter_combo.setEnabled(True)
            self.cluster_filter_combo.addItem("نمایش همه (بدون گروه‌بندی)", userData=None)
            
            # Use the combined score to find the best model for default selection
            best_model_info = sorted(clustering_data['all_results'], key=lambda x: self._calculate_combined_score(x, clustering_data['all_results']), reverse=True)[0]
            
            # Add the best model first
            best_text = f"⭐ بهترین مدل: {best_model_info['algorithm']} (k={best_model_info['k']})"
            self.cluster_filter_combo.addItem(best_text, userData=best_model_info)
            
            # Add other models
            sorted_models = sorted(clustering_data['all_results'], key=lambda x: (x['algorithm'], x['k']))
            for model_info in sorted_models:
                if model_info != best_model_info: # Avoid duplicating the best model
                    text = f"{model_info['algorithm']} (k={model_info['k']})"
                    self.cluster_filter_combo.addItem(text, userData=model_info)
        else:
            self.cluster_filter_combo.setPlaceholderText("خوشه‌بندی انجام نشده")
            self.cluster_filter_combo.setEnabled(False)
            
        if self.full_dea_results_df is not None:
            self.display_results()
            
    def _calculate_combined_score(self, result_item, all_results):
        # Helper to find best model for dropdown
        sil_scores = [res['silhouette'] for res in all_results]
        db_scores = [res['davies_bouldin'] for res in all_results]
        min_sil, max_sil = min(sil_scores), max(sil_scores)
        min_db, max_db = min(db_scores), max(db_scores)
        norm_sil = (result_item['silhouette'] - min_sil) / (max_sil - min_sil) if (max_sil - min_sil) > 0 else 0
        norm_db = (result_item['davies_bouldin'] - min_db) / (max_db - min_db) if (max_db - min_db) > 0 else 0
        return norm_sil + (1 - norm_db)

    def run_analysis(self):
        if self.dea_df is None:
            QMessageBox.warning(self, "داده ناقص", "لطفاً فایل داده بهره‌وری را بارگذاری کنید.")
            return
        self.selected_inputs = [item.text() for item in self.inputs_list.selectedItems()]
        selected_outputs = [item.text() for item in self.outputs_list.selectedItems()]
        if not self.selected_inputs or not selected_outputs:
            QMessageBox.warning(self, "شاخص انتخاب نشده", "لطفاً شاخص‌های ورودی و خروجی را انتخاب کنید.")
            return

        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            dmu_column_dea = self.dea_df.columns[0]
            results = run_dea_analysis(self.dea_df, dmu_column_dea, self.selected_inputs, selected_outputs)
            self.full_dea_results_df = pd.DataFrame(results)
            self.display_results()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "خطا در تحلیل", f"یک خطای پیش‌بینی نشده رخ داد:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()

    def display_results(self):
        if self.full_dea_results_df is None: return
        
        final_df = self.full_dea_results_df.copy()
        selected_model_info = self.cluster_filter_combo.currentData()
        
        if selected_model_info and self.clustering_data and 'dataframe' in self.clustering_data:
            clustering_df_original = self.clustering_data['dataframe']
            selected_features = self.clustering_data['selected_features']
            algorithm = selected_model_info['algorithm']
            k = selected_model_info['k']
            
            labels = run_single_clustering_model(clustering_df_original, selected_features, algorithm, k)
            clusters_df = pd.DataFrame({'DMU': clustering_df_original.iloc[:, 0], 'cluster': labels})

            final_df['norm_dmu'] = final_df['dmu'].apply(normalize_dmu_name)
            clusters_df['norm_dmu'] = clusters_df['DMU'].apply(normalize_dmu_name)
            final_df = pd.merge(final_df, clusters_df[['norm_dmu', 'cluster']], on='norm_dmu', how='left')
            final_df.drop(columns=['norm_dmu'], inplace=True)
            final_df['cluster'] = final_df['cluster'].fillna('-')
        else:
            final_df['cluster'] = '-'

        model = QStandardItemModel()
        headers = ["خوشه", "DMU", "امتیاز بهره‌وری"] + [f"اسلک {inp}" for inp in self.selected_inputs] + ["مجموعه مرجع"]
        model.setHorizontalHeaderLabels(headers)

        # Sort dataframe before display, table will use this as initial order
        final_df['sort_cluster'] = pd.to_numeric(final_df['cluster'], errors='coerce').fillna(float('inf'))
        final_df = final_df.sort_values(by=['sort_cluster', 'efficiency'])

        for _, row in final_df.iterrows():
            row_items = [
                create_numeric_item(row['cluster'], precision=0),
                create_text_item(row['dmu']),
                create_numeric_item(row.get('efficiency', 0), precision=2)
            ]
            for inp in self.selected_inputs:
                row_items.append(create_numeric_item(row['slacks'].get(inp, 0)))
            row_items.append(create_text_item(row['peers']))
            
            model.appendRow(row_items)
        
        self.results_table.setModel(model)
        self.results_table.resizeColumnsToContents()

    def filter_display(self):
        self.display_results()

    def load_dea_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل داده بهره‌وری", "", "Excel Files (*.xlsx *.xls)")
        if not file_path: return
        try:
            self.dea_df = pd.read_excel(file_path)
            self.file_path_label.setText(file_path.split('/')[-1])
            self.populate_io_lists()
            self.run_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "خطا در خواندن فایل", f"فایل اکسل قابل پردازش نیست:\n{e}")
            self.run_button.setEnabled(False)

    def populate_io_lists(self):
        self.inputs_list.clear(); self.outputs_list.clear()
        if self.dea_df is None: return
        for col in self.dea_df.columns[1:]:
            self.inputs_list.addItem(QListWidgetItem(col)); self.outputs_list.addItem(QListWidgetItem(col))