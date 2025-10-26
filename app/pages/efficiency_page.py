#===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTableView,
    QMessageBox, QGroupBox, QComboBox, QListWidget, QListWidgetItem, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor
import pandas as pd
import traceback

from ..logic.dea_analysis import run_dea_analysis
from ..logic.clustering_analysis import run_single_clustering_model


#===== UTILITY FUNCTIONS =====

# --- COLOR PALETTE for cluster highlighting ---
CLUSTER_COLORS = [
    "#E6F7FF",  # Light Blue
    "#F6FFED",  # Light Green
    "#FFFBE6",  # Light Yellow
    "#FFF1F0",  # Light Red/Pink
    "#F9F0FF",  # Light Purple
    "#E6FFFB",  # Light Cyan
    "#FCFFE6",  # Light Lime
    "#FFF7E6"   # Light Orange
]

def get_color_for_cluster(cluster_id):
    """Returns a consistent color for a given cluster ID."""
    try:
        cluster_id = int(cluster_id)
        if cluster_id >= 0:
            return QColor(CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)])
    except (ValueError, TypeError):
        pass # Handle cases where cluster_id is not a valid number (e.g., '-')
    return None # No color

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


#===== UI & APPLICATION LOGIC =====
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
        title_label = QLabel("ماژول محاسبه بهره‌وری (DEA)"); title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight); main_layout.addWidget(title_label)
        top_controls_layout = QHBoxLayout()
        upload_group = QGroupBox("مرحله ۱: بارگذاری فایل داده بهره‌وری"); upload_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        upload_layout = QHBoxLayout(); self.upload_button = QPushButton("انتخاب فایل اکسل")
        self.file_path_label = QLabel("هنوز فایلی انتخاب نشده"); upload_layout.addWidget(self.upload_button)
        upload_layout.addWidget(self.file_path_label, 1); upload_group.setLayout(upload_layout)
        top_controls_layout.addWidget(upload_group, 1); main_layout.addLayout(top_controls_layout)
        middle_splitter = QSplitter(Qt.Orientation.Horizontal)
        io_selection_group = QGroupBox("مرحله ۲: انتخاب شاخص‌های ورودی و خروجی"); io_selection_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # --- Create main layout for I/O selection ---
        io_main_layout = QHBoxLayout()
        
        # --- Input Section ---
        inputs_main_v_layout = QVBoxLayout()
        inputs_group = QGroupBox("ورودی‌ها"); inputs_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        inputs_layout = QVBoxLayout()
        self.inputs_select_all_cb = QCheckBox("همه")
        self.inputs_list = QListWidget()
        self.inputs_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        inputs_layout.addWidget(self.inputs_select_all_cb)
        inputs_layout.addWidget(self.inputs_list)
        inputs_group.setLayout(inputs_layout)
        inputs_main_v_layout.addWidget(inputs_group)
        
        # --- Output Section ---
        outputs_main_v_layout = QVBoxLayout()
        outputs_group = QGroupBox("خروجی‌ها"); outputs_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        outputs_layout = QVBoxLayout()
        self.outputs_select_all_cb = QCheckBox("همه")
        self.outputs_list = QListWidget()
        self.outputs_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        outputs_layout.addWidget(self.outputs_select_all_cb)
        outputs_layout.addWidget(self.outputs_list)
        outputs_group.setLayout(outputs_layout)
        outputs_main_v_layout.addWidget(outputs_group)
        
        io_main_layout.addLayout(inputs_main_v_layout, 1)
        io_main_layout.addLayout(outputs_main_v_layout, 1)
        
        io_selection_group.setLayout(io_main_layout)
        middle_splitter.addWidget(io_selection_group)
        
        run_group = QGroupBox("مرحله ۳: اجرا"); run_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        run_layout = QVBoxLayout(); self.run_button = QPushButton("محاسبه بهره‌وری"); self.run_button.setEnabled(False)
        run_layout.addWidget(self.run_button); run_group.setLayout(run_layout)
        middle_splitter.addWidget(run_group); middle_splitter.setSizes([400, 100]); main_layout.addWidget(middle_splitter)
        results_group = QGroupBox("نتایج تحلیل بهره‌وری (SBM ورودی-محور)"); results_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        results_layout = QVBoxLayout()
        self.cluster_filter_combo = QComboBox(); self.cluster_filter_combo.setEnabled(False)
        results_layout.addWidget(self.cluster_filter_combo)
        self.results_table = QTableView()
        self.results_table.setSortingEnabled(True)
        results_layout.addWidget(self.results_table); results_group.setLayout(results_layout)
        main_layout.addWidget(results_group, 1)
        
        # --- Connections ---
        self.upload_button.clicked.connect(self.load_dea_data)
        self.run_button.clicked.connect(self.run_analysis)
        self.cluster_filter_combo.currentIndexChanged.connect(self.filter_display)
        self.inputs_select_all_cb.stateChanged.connect(self.toggle_select_all_inputs)
        self.outputs_select_all_cb.stateChanged.connect(self.toggle_select_all_outputs)
        self.inputs_list.itemSelectionChanged.connect(self.update_inputs_checkbox_state)
        self.outputs_list.itemSelectionChanged.connect(self.update_outputs_checkbox_state)

    def toggle_select_all_inputs(self, state):
        self.inputs_list.itemSelectionChanged.disconnect(self.update_inputs_checkbox_state)
        if Qt.CheckState(state) == Qt.CheckState.Checked:
            self.inputs_list.selectAll()
        else:
            self.inputs_list.clearSelection()
        self.inputs_list.itemSelectionChanged.connect(self.update_inputs_checkbox_state)

    def toggle_select_all_outputs(self, state):
        self.outputs_list.itemSelectionChanged.disconnect(self.update_outputs_checkbox_state)
        if Qt.CheckState(state) == Qt.CheckState.Checked:
            self.outputs_list.selectAll()
        else:
            self.outputs_list.clearSelection()
        self.outputs_list.itemSelectionChanged.connect(self.update_outputs_checkbox_state)

    def update_inputs_checkbox_state(self):
        self.inputs_select_all_cb.stateChanged.disconnect(self.toggle_select_all_inputs)
        if self.inputs_list.count() > 0 and len(self.inputs_list.selectedItems()) == self.inputs_list.count():
            self.inputs_select_all_cb.setCheckState(Qt.CheckState.Checked)
        elif len(self.inputs_list.selectedItems()) == 0:
            self.inputs_select_all_cb.setCheckState(Qt.CheckState.Unchecked)
        else:
            self.inputs_select_all_cb.setCheckState(Qt.CheckState.PartiallyChecked)
        self.inputs_select_all_cb.stateChanged.connect(self.toggle_select_all_inputs)

    def update_outputs_checkbox_state(self):
        self.outputs_select_all_cb.stateChanged.disconnect(self.toggle_select_all_outputs)
        if self.outputs_list.count() > 0 and len(self.outputs_list.selectedItems()) == self.outputs_list.count():
            self.outputs_select_all_cb.setCheckState(Qt.CheckState.Checked)
        elif len(self.outputs_list.selectedItems()) == 0:
            self.outputs_select_all_cb.setCheckState(Qt.CheckState.Unchecked)
        else:
            self.outputs_select_all_cb.setCheckState(Qt.CheckState.PartiallyChecked)
        self.outputs_select_all_cb.stateChanged.connect(self.toggle_select_all_outputs)
        
    def update_with_clustering_data(self, clustering_data):
        self.clustering_data = clustering_data
        self.cluster_filter_combo.clear()
        
        if clustering_data and 'all_results' in clustering_data:
            self.cluster_filter_combo.setEnabled(True)
            self.cluster_filter_combo.addItem("نمایش همه (بدون گروه‌بندی)", userData=None)
            
            best_model_info = sorted(clustering_data['all_results'], key=lambda x: self._calculate_combined_score(x, clustering_data['all_results']), reverse=True)[0]
            
            best_text = f"⭐ بهترین مدل: {best_model_info['algorithm']} (k={best_model_info['k']})"
            self.cluster_filter_combo.addItem(best_text, userData=best_model_info)
            
            sorted_models = sorted(clustering_data['all_results'], key=lambda x: (x['algorithm'], x['k']))
            for model_info in sorted_models:
                if model_info != best_model_info:
                    text = f"{model_info['algorithm']} (k={model_info['k']})"
                    self.cluster_filter_combo.addItem(text, userData=model_info)
        else:
            self.cluster_filter_combo.setPlaceholderText("خوشه‌بندی انجام نشده")
            self.cluster_filter_combo.setEnabled(False)
            
        if self.full_dea_results_df is not None:
            self.display_results()
            
    def _calculate_combined_score(self, result_item, all_results):
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
            labels = [l + 1 for l in labels]
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

        final_df['sort_cluster'] = pd.to_numeric(final_df['cluster'], errors='coerce').fillna(float('inf'))
        final_df = final_df.sort_values(by=['sort_cluster', 'efficiency'])

        for _, row in final_df.iterrows():
            cluster_val = row['cluster']
            row_color = get_color_for_cluster(cluster_val)

            row_items = [
                create_numeric_item(cluster_val, precision=0),
                create_text_item(row['dmu']),
                create_numeric_item(row.get('efficiency', 0), precision=2)
            ]
            for inp in self.selected_inputs:
                row_items.append(create_numeric_item(row['slacks'].get(inp, 0)))
            row_items.append(create_text_item(row['peers']))
            
            # --- Apply background color to all items in the row ---
            if row_color:
                for item in row_items:
                    item.setBackground(row_color)
            
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
        
        self.update_inputs_checkbox_state()
        self.update_outputs_checkbox_state()