# ===== SECTION BEING MODIFIED: app/pages/efficiency_page.py =====
# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTableView,
    QMessageBox, QGroupBox, QComboBox, QListWidget, QListWidgetItem, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import traceback

from ..logic.dea_analysis import run_dea_analysis
from ..logic.clustering_analysis import run_single_clustering_model
# --- MODIFIED: Import BasePage and other necessary utilities ---
from .utils import create_numeric_item, create_text_item, get_color_for_cluster, save_table_to_excel, BasePage

# ===== UI & APPLICATION LOGIC =====
# --- MODIFIED: Inherit from BasePage instead of QWidget ---
class EfficiencyPage(BasePage):
    analysis_completed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.clustering_data = None
        self.dea_df = None
        self.full_dea_results_df = None
        self.selected_inputs = []
        self.selected_outputs = []
        self.is_fullscreen = False
        self.initUI()

    def initUI(self):
        self.content_layout.setSpacing(15)
        # Force horizontal centering of the title label using stretches on both sides
        title_layout = QHBoxLayout()
        
        title_label = QLabel("ماژول محاسبه بهره‌وری واحدی (مدل SBM)")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_layout.addStretch(1)  # Add stretch on the left side
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)  # Add stretch on the right side
        
        self.content_layout.addLayout(title_layout)
        
        # --- Step 1: Upload ---
        self.top_controls_layout = QHBoxLayout()
        self.top_controls_layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        
        self.upload_group = QGroupBox("مرحله ۱: بارگذاری فایل داده بهره‌وری")
        self.upload_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        upload_layout = QHBoxLayout()
        upload_layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        
        self.upload_button = QPushButton("انتخاب فایل اکسل")
        self.download_button = QPushButton("دانلود قالب اکسل")
        self.file_path_label = QLabel("هنوز فایلی انتخاب نشده")
        
        upload_layout.addWidget(self.upload_button)
        upload_layout.addWidget(self.download_button)
        upload_layout.addWidget(self.file_path_label, 1)
        self.upload_group.setLayout(upload_layout)
        self.top_controls_layout.addWidget(self.upload_group, 1)
        self.content_layout.addLayout(self.top_controls_layout)
        
        # --- Step 2 & 3: Splitter ---
        self.middle_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.middle_splitter.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # IO Selection
        self.io_selection_group = QGroupBox("مرحله ۲: انتخاب شاخص‌های ورودی و خروجی")
        self.io_selection_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        io_main_layout = QHBoxLayout()
        io_main_layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        
        inputs_group = QGroupBox("ورودی‌ها")
        inputs_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        inputs_layout = QVBoxLayout()
        self.inputs_select_all_cb = QCheckBox("همه")
        self.inputs_list = QListWidget()
        self.inputs_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        inputs_layout.addWidget(self.inputs_select_all_cb)
        inputs_layout.addWidget(self.inputs_list)
        inputs_group.setLayout(inputs_layout)
        
        outputs_group = QGroupBox("خروجی‌ها")
        outputs_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        outputs_layout = QVBoxLayout()
        self.outputs_select_all_cb = QCheckBox("همه")
        self.outputs_list = QListWidget()
        self.outputs_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        outputs_layout.addWidget(self.outputs_select_all_cb)
        outputs_layout.addWidget(self.outputs_list)
        outputs_group.setLayout(outputs_layout)
        
        io_main_layout.addWidget(inputs_group, 1)
        io_main_layout.addWidget(outputs_group, 1)
        self.io_selection_group.setLayout(io_main_layout)
        self.middle_splitter.addWidget(self.io_selection_group)
        
        # Run Button
        self.run_group = QGroupBox("مرحله ۳: اجرا")
        self.run_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        run_layout = QVBoxLayout()
        self.run_button = QPushButton("محاسبه بهره‌وری واحدی")
        self.run_button.setEnabled(False)
        run_layout.addWidget(self.run_button)
        self.run_group.setLayout(run_layout)
        
        self.middle_splitter.addWidget(self.run_group)
        self.middle_splitter.setSizes([400, 100])
        self.content_layout.addWidget(self.middle_splitter)
        
        # --- Step 4: Results ---
        self.results_group = QGroupBox("نتایج تحلیل بهره‌وری (SBM ورودی-محور)")
        self.results_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        results_layout = QVBoxLayout()
        
        # Controls for Results
        res_ctrl_layout = QHBoxLayout()
        res_ctrl_layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        self.cluster_filter_combo = QComboBox()
        self.cluster_filter_combo.setEnabled(False)
        self.export_button = QPushButton("خروجی اکسل")
        self.export_button.setObjectName("ExportButton")
        self.fullscreen_button = QPushButton("نمایش تمام صفحه")
        
        res_ctrl_layout.addWidget(QLabel("فیلتر خوشه:"))
        res_ctrl_layout.addWidget(self.cluster_filter_combo)
        res_ctrl_layout.addWidget(self.export_button)
        res_ctrl_layout.addWidget(self.fullscreen_button)
        res_ctrl_layout.addStretch()
        results_layout.addLayout(res_ctrl_layout)

        self.results_table = QTableView()
        self.results_table.setSortingEnabled(True)
        results_layout.addWidget(self.results_table)
        self.results_group.setLayout(results_layout)
        self.content_layout.addWidget(self.results_group, 1)
        
        # Connections
        self.upload_button.clicked.connect(self.load_dea_data)
        self.download_button.clicked.connect(self.download_template)
        self.run_button.clicked.connect(self.run_analysis)
        self.cluster_filter_combo.currentIndexChanged.connect(self.filter_display)
        self.inputs_select_all_cb.stateChanged.connect(self.toggle_select_all_inputs)
        self.outputs_select_all_cb.stateChanged.connect(self.toggle_select_all_outputs)
        self.inputs_list.itemSelectionChanged.connect(self.update_inputs_checkbox_state)
        self.outputs_list.itemSelectionChanged.connect(self.update_outputs_checkbox_state)
        self.export_button.clicked.connect(lambda: save_table_to_excel(self, self.results_table, "efficiency_results.xlsx"))
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.upload_group.setVisible(not self.is_fullscreen)
        self.middle_splitter.setVisible(not self.is_fullscreen)
        
        if self.is_fullscreen:
            self.fullscreen_button.setText("خروج از تمام صفحه")
        else:
            self.fullscreen_button.setText("نمایش تمام صفحه")

    def download_template(self):
        template_data = {'DMU': ['واحد_۱', 'واحد_۲'], 'ورودی_۱': [10, 20], 'ورودی_۲': [5, 8], 'خروجی_۱': [100, 150]}
        df = pd.DataFrame(template_data)
        save_path, _ = QFileDialog.getSaveFileName(self, "ذخیره قالب اکسل", "efficiency_template.xlsx", "Excel Files (*.xlsx)")
        if save_path:
            try:
                df.to_excel(save_path, index=False)
                QMessageBox.information(self, "موفقیت", f"قالب ذخیره شد:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا:\n{e}")

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
        self.selected_outputs = [item.text() for item in self.outputs_list.selectedItems()]
        if not self.selected_inputs or not self.selected_outputs:
            QMessageBox.warning(self, "شاخص انتخاب نشده", "لطفاً شاخص‌های ورودی و خروجی را انتخاب کنید.")
            return

        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            dmu_column_dea = self.dea_df.columns[0]
            results = run_dea_analysis(self.dea_df, dmu_column_dea, self.selected_inputs, self.selected_outputs)
            self.full_dea_results_df = pd.DataFrame(results)
            
            final_df, cluster_info_df = self.display_results()
            
            if final_df is not None:
                self.analysis_completed.emit({
                    "input_df": self.dea_df,
                    "results_df": self.full_dea_results_df,
                    "cluster_info": cluster_info_df
                })
            
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "خطا در تحلیل", f"یک خطای پیش‌بینی نشده رخ داد:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()

    def display_results(self):
        if self.full_dea_results_df is None: 
            return None, pd.DataFrame()
        
        final_df = self.full_dea_results_df.copy()
        selected_model_info = self.cluster_filter_combo.currentData()
        
        cluster_info_df = pd.DataFrame()

        def normalize_dmu_name(name):
            if not isinstance(name, str): name = str(name)
            name = name.replace("ي", "ی").replace("ك", "ک")
            return "".join(name.split())

        if selected_model_info and self.clustering_data and 'dataframe' in self.clustering_data:
            clustering_df_original = self.clustering_data['dataframe']
            clustering_dmu_col = clustering_df_original.columns[0]
            
            labels = run_single_clustering_model(
                clustering_df_original, 
                self.clustering_data['selected_features'], 
                selected_model_info['algorithm'], 
                selected_model_info['k']
            )
            labels = [l + 1 for l in labels]
            
            cluster_info_df = pd.DataFrame({
                clustering_dmu_col: clustering_df_original.iloc[:, 0],
                'cluster': labels
            })
            
            dea_dmu_col = 'dmu'
            final_df['norm_dmu'] = final_df[dea_dmu_col].apply(normalize_dmu_name)
            cluster_info_df['norm_dmu'] = cluster_info_df[clustering_dmu_col].apply(normalize_dmu_name)
            
            final_df = pd.merge(final_df, cluster_info_df[['norm_dmu', 'cluster']], on='norm_dmu', how='left')
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
            
            if row_color:
                for item in row_items:
                    item.setBackground(row_color)
            
            model.appendRow(row_items)
        
        self.results_table.setModel(model)
        self.results_table.resizeColumnsToContents()
        
        return final_df, cluster_info_df

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