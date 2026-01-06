# ===== SECTION BEING MODIFIED: app/pages/clustering_page.py =====
# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QTableView, QMessageBox, QGroupBox, QCheckBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QIcon
import pandas as pd
import traceback

from ..logic.clustering_analysis import get_all_clustering_results, run_single_clustering_model
from .utils import create_numeric_item, create_text_item, save_table_to_excel, BasePage

# ===== COLOR PALETTES =====
ALGORITHM_COLORS = {
    "K-Means": QColor("#E6F7FF"),
    "K-Medoids": QColor("#F6FFED"),
    "Ward": QColor("#FFF7E6"),
    "K-Median": QColor("#F0F5FF"),
}
CLUSTER_COLORS = [
    "#E6F7FF", "#F6FFED", "#FFFBE6", "#FFF1F0", "#F9F0FF",
    "#E6FFFB", "#FCFFE6", "#FFF0F6", "#F0F5FF", "#FEFFE6"
]

def get_color_for_item(item_name, color_map, color_list=None):
    if item_name in color_map:
        return color_map[item_name]
    if color_list:
        try:
            item_id = int(item_name)
            if item_id >= 1:
                return QColor(color_list[(item_id - 1) % len(color_list)])
        except (ValueError, TypeError):
            pass
    return None

# ===== UI & APPLICATION LOGIC =====
class ClusteringPage(BasePage):
    analysis_completed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.df = None
        self.feature_checkboxes = []
        self.selected_features = []
        self.is_fullscreen = False
        self.initUI()

    def initUI(self):
        self.content_layout.setSpacing(15)

        # --- Title ---
        # Force horizontal centering of the title label using stretches on both sides
        title_layout = QHBoxLayout()
        title_label = QLabel("ماژول تحلیل خوشه‌بندی (الگوریتم‌های K-Means, K-Medoids, Ward)")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_layout.addStretch(1)  # Add stretch on the left side
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)  # Add stretch on the right side
        
        self.content_layout.addLayout(title_layout)

        # --- Step 1: File Upload ---
        self.file_group_box = QGroupBox("مرحله ۱: انتخاب فایل داده")
        self.file_group_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        file_v_layout = QVBoxLayout()
        file_h_layout = QHBoxLayout()
        file_h_layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        
        self.upload_button = QPushButton("انتخاب فایل اکسل")
        self.download_button = QPushButton("دانلود قالب اکسل")
        self.file_path_label = QLabel("هیچ فایلی انتخاب نشده است.")
        self.file_path_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        file_h_layout.addWidget(self.upload_button)
        file_h_layout.addWidget(self.download_button)
        file_h_layout.addWidget(self.file_path_label, 1)
        file_v_layout.addLayout(file_h_layout)
        self.file_group_box.setLayout(file_v_layout)
        self.content_layout.addWidget(self.file_group_box)

        # --- Middle Section (Steps 2 & 3) ---
        self.middle_layout = QHBoxLayout()
        self.middle_layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        self.middle_layout.setSpacing(15)

        self.feature_group_box = QGroupBox("مرحله ۲ و ۳: انتخاب شاخص‌ها و اجرا")
        self.feature_group_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        feature_scroll_area = QScrollArea()
        feature_scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.checkbox_layout = QVBoxLayout(scroll_widget)
        self.checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        feature_scroll_area.setWidget(scroll_widget)
        
        feature_v_layout = QVBoxLayout()
        feature_v_layout.addWidget(feature_scroll_area)
        
        self.run_button = QPushButton("تحلیل خوشه‌بندی")
        feature_v_layout.addWidget(self.run_button)
        
        self.feature_group_box.setLayout(feature_v_layout)
        self.feature_group_box.setEnabled(False)
        self.middle_layout.addWidget(self.feature_group_box, stretch=1)

        # --- Step 4: Results ---
        self.comparison_group_box = QGroupBox("مرحله ۴: مقایسه نتایج (برای مشاهده جزئیات کلیک کنید)")
        self.comparison_group_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        comparison_layout = QVBoxLayout()
        
        self.results_table = QTableView()
        self.results_table.setSortingEnabled(True)
        comparison_layout.addWidget(self.results_table)
        self.comparison_group_box.setLayout(comparison_layout)
        self.middle_layout.addWidget(self.comparison_group_box, stretch=2)
        
        self.content_layout.addLayout(self.middle_layout, stretch=2)

        # --- Detailed Results (Bottom) ---
        self.dmu_group_box = QGroupBox("جزئیات خوشه‌بندی مدل انتخاب شده")
        self.dmu_group_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        dmu_layout = QVBoxLayout()
        
        # Control Buttons for Results
        res_ctrl_layout = QHBoxLayout()
        res_ctrl_layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        self.export_button = QPushButton("خروجی اکسل")
        self.export_button.setObjectName("ExportButton")
        self.fullscreen_button = QPushButton("نمایش تمام صفحه")
        res_ctrl_layout.addWidget(self.export_button)
        res_ctrl_layout.addWidget(self.fullscreen_button)
        res_ctrl_layout.addStretch()
        dmu_layout.addLayout(res_ctrl_layout)

        self.dmu_table = QTableView()
        self.dmu_table.setSortingEnabled(True)
        dmu_layout.addWidget(self.dmu_table)
        self.dmu_group_box.setLayout(dmu_layout)
        self.content_layout.addWidget(self.dmu_group_box, stretch=2)

        # --- Models & Connections ---
        self.results_table.setModel(QStandardItemModel())
        self.dmu_table.setModel(QStandardItemModel())
        self.upload_button.clicked.connect(self.load_file_and_show_features)
        self.run_button.clicked.connect(self.run_analysis)
        self.download_button.clicked.connect(self.download_template)
        self.results_table.selectionModel().selectionChanged.connect(self.on_result_selection_changed)
        self.export_button.clicked.connect(lambda: save_table_to_excel(self, self.dmu_table, "clustering_results.xlsx"))
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        
        # Toggle visibility of top widgets
        self.file_group_box.setVisible(not self.is_fullscreen)
        self.feature_group_box.setVisible(not self.is_fullscreen)
        self.comparison_group_box.setVisible(not self.is_fullscreen)
        
        if self.is_fullscreen:
            self.fullscreen_button.setText("خروج از تمام صفحه")
            self.dmu_group_box.setTitle("جزئیات خوشه‌بندی (تمام صفحه)")
        else:
            self.fullscreen_button.setText("نمایش تمام صفحه")
            self.dmu_group_box.setTitle("جزئیات خوشه‌بندی مدل انتخاب شده")

    def run_analysis(self):
        self.selected_features = [cb.text() for cb in self.feature_checkboxes if cb.isChecked()]
        if len(self.selected_features) < 2:
            QMessageBox.warning(self, "شاخص ناکافی", "لطفاً حداقل دو شاخص را برای تحلیل انتخاب کنید.")
            return
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            all_results = get_all_clustering_results(self.df, self.selected_features)
            if not all_results:
                QMessageBox.information(self, "نتیجه‌ای یافت نشد", "هیچ مدل خوشه‌بندی موفقی برای داده‌های فعلی اجرا نشد.")
                return
            self.display_comparison_results(all_results)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "خطا در تحلیل", f"یک خطای پیش‌بینی نشده رخ داد:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()

    def _calculate_combined_score(self, result_item, all_results):
        sil_scores = [res['silhouette'] for res in all_results]
        db_scores = [res['davies_bouldin'] for res in all_results]
        min_sil, max_sil = min(sil_scores), max(sil_scores)
        min_db, max_db = min(db_scores), max(db_scores)
        norm_sil = (result_item['silhouette'] - min_sil) / (max_sil - min_sil) if (max_sil - min_sil) > 0 else 0
        norm_db = (result_item['davies_bouldin'] - min_db) / (max_db - min_db) if (max_db - min_db) > 0 else 0
        inverted_norm_db = 1 - norm_db
        return norm_sil + inverted_norm_db

    def display_comparison_results(self, all_results):
        try:
            self.results_table.selectionModel().selectionChanged.disconnect(self.on_result_selection_changed)
        except TypeError: pass

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["الگوریتم", "تعداد خوشه (k)", "امتیاز سیلوئت", "شاخص دیویس-بولدین"])
        
        sorted_results = sorted(all_results, key=lambda x: self._calculate_combined_score(x, all_results), reverse=True)
        
        for result in sorted_results:
            alg_name = result['algorithm']
            row_color = get_color_for_item(alg_name, ALGORITHM_COLORS)
            
            row_items = [
                create_text_item(alg_name),
                create_numeric_item(result['k'], precision=0),
                create_numeric_item(result['silhouette'], precision=2),
                create_numeric_item(result['davies_bouldin'], precision=2)
            ]
            
            if row_color:
                for item in row_items:
                    item.setBackground(row_color)
            
            model.appendRow(row_items)
        
        self.results_table.setModel(model)
        self.results_table.resizeColumnsToContents()
        self.results_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.results_table.selectionModel().selectionChanged.connect(self.on_result_selection_changed)

        if model.rowCount() > 0:
            self.results_table.selectRow(0)
            best_model = sorted_results[0]
            dmu_column = self.df.columns[0]
            labels = run_single_clustering_model(self.df, self.selected_features, best_model['algorithm'], best_model['k'])
            final_clusters_df = pd.DataFrame({'DMU': self.df[dmu_column], 'cluster': [l + 1 for l in labels]})
            self.analysis_completed.emit({
                'dataframe': self.df,
                'selected_features': self.selected_features,
                'clusters_df': final_clusters_df,
                'all_results': all_results
            })

    def on_result_selection_changed(self, selected, deselected):
        if not selected.indexes() or self.df is None: return
        
        selected_row = selected.indexes()[0].row()
        model = self.results_table.model()
        algorithm_name = model.item(selected_row, 0).text()
        k_item = model.item(selected_row, 1)
        k = int(k_item.data(Qt.ItemDataRole.UserRole))

        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            dmu_column = self.df.columns[0]
            labels = run_single_clustering_model(self.df, self.selected_features, algorithm_name, k)
            
            results_df = pd.DataFrame({
                'dmu': self.df[dmu_column],
                'label': [l + 1 for l in labels]
            })
            results_df = results_df.sort_values(by='label')
            
            dmu_model = QStandardItemModel()
            dmu_model.setHorizontalHeaderLabels(["واحد تصمیم‌گیرنده (DMU)", "شماره خوشه"])
            
            for _, row_data in results_df.iterrows():
                cluster_id = row_data['label']
                row_color = get_color_for_item(str(cluster_id), {}, CLUSTER_COLORS)
                
                row_items = [
                    create_text_item(row_data['dmu']),
                    create_numeric_item(cluster_id, precision=0)
                ]
                
                if row_color:
                    for item in row_items:
                        item.setBackground(row_color)

                dmu_model.appendRow(row_items)
                
            self.dmu_table.setModel(dmu_model)
            self.dmu_table.resizeColumnsToContents()
            self.dmu_table.sortByColumn(1, Qt.SortOrder.AscendingOrder)
            
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "خطا", f"خطا در اجرای مدل انتخاب شده:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()

    def load_file_and_show_features(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل اکسل", "", "Excel Files (*.xlsx *.xls)")
        if not file_path: return
        try:
            self.df = pd.read_excel(file_path)
            self.file_path_label.setText(file_path.split('/')[-1])
            self.populate_feature_checkboxes()
            self.feature_group_box.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "خطا در خواندن فایل", f"فایل اکسل قابل پردازش نیست:\n{e}")
            self.feature_group_box.setEnabled(False)

    def populate_feature_checkboxes(self):
        for checkbox in self.feature_checkboxes:
            self.checkbox_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.feature_checkboxes.clear()
        numeric_columns = self.df.select_dtypes(include=['number']).columns
        all_columns = self.df.columns[1:]
        for col in all_columns:
            checkbox = QCheckBox(col)
            checkbox.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            if col in numeric_columns:
                checkbox.setChecked(True)
            self.checkbox_layout.addWidget(checkbox)
            self.feature_checkboxes.append(checkbox)

    def download_template(self):
        template_data = {'DMU_Name': ['واحد_الف', 'واحد_ب', 'واحد_ج'], 'شاخص_۱': [10, 12, 15], 'شاخص_۲': [100, 110, 105]}
        df = pd.DataFrame(template_data)
        save_path, _ = QFileDialog.getSaveFileName(self, "ذخیره قالب اکسل", "clustering_template.xlsx", "Excel Files (*.xlsx)")
        if save_path:
            try:
                df.to_excel(save_path, index=False)
                QMessageBox.information(self, "موفقیت", f"قالب با موفقیت در مسیر زیر ذخیره شد:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل:\n{e}")