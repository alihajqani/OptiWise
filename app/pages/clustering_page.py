# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QTableView, QMessageBox, QGroupBox, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import traceback

from ..logic.clustering_analysis import get_all_clustering_results, run_single_clustering_model


# ===== UTILITY FUNCTIONS =====
def create_numeric_item(value, precision=4):
    """Creates a QStandardItem that sorts numerically."""
    item = QStandardItem()
    item.setData(float(value), Qt.ItemDataRole.UserRole)
    item.setText(f"{value:.{precision}f}")
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item

def create_text_item(text):
    """Creates a standard, non-editable text QStandardItem."""
    item = QStandardItem(str(text))
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return item


# ===== UI & APPLICATION LOGIC =====
class ClusteringPage(QWidget):
    analysis_completed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.df = None
        self.feature_checkboxes = []
        self.selected_features = []
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25); main_layout.setSpacing(15)

        title_label = QLabel("ماژول خوشه‌بندی (Clustering)"); title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight); main_layout.addWidget(title_label)

        file_group_box = QGroupBox("مرحله ۱: انتخاب فایل داده")
        file_group_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        file_v_layout = QVBoxLayout(); file_h_layout = QHBoxLayout()
        self.upload_button = QPushButton("انتخاب فایل اکسل")
        self.file_path_label = QLabel("هیچ فایلی انتخاب نشده است.")
        self.file_path_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        file_h_layout.addWidget(self.upload_button); file_h_layout.addWidget(self.file_path_label, stretch=1)
        self.download_button = QPushButton("دانلود قالب اکسل")
        file_v_layout.addLayout(file_h_layout); file_v_layout.addWidget(self.download_button)
        file_group_box.setLayout(file_v_layout); main_layout.addWidget(file_group_box)

        middle_layout = QHBoxLayout(); middle_layout.setSpacing(15)

        self.feature_group_box = QGroupBox("مرحله ۲ و ۳: انتخاب شاخص‌ها و اجرا")
        self.feature_group_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        feature_scroll_area = QScrollArea(); feature_scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.checkbox_layout = QVBoxLayout(scroll_widget)
        self.checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        feature_scroll_area.setWidget(scroll_widget); feature_v_layout = QVBoxLayout()
        feature_v_layout.addWidget(feature_scroll_area)
        self.run_button = QPushButton("اجرای تمام تحلیل‌ها")
        feature_v_layout.addWidget(self.run_button); self.feature_group_box.setLayout(feature_v_layout)
        self.feature_group_box.setEnabled(False); middle_layout.addWidget(self.feature_group_box, stretch=1)

        comparison_group_box = QGroupBox("مرحله ۴: مقایسه نتایج (برای مشاهده جزئیات کلیک کنید)")
        comparison_group_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        comparison_layout = QVBoxLayout()
        self.results_table = QTableView()
        # --- SORTING ENABLED ---
        self.results_table.setSortingEnabled(True)
        comparison_layout.addWidget(self.results_table)
        comparison_group_box.setLayout(comparison_layout)
        middle_layout.addWidget(comparison_group_box, stretch=3)
        main_layout.addLayout(middle_layout, stretch=1)

        dmu_group_box = QGroupBox("جزئیات خوشه‌بندی مدل انتخاب شده")
        dmu_group_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        dmu_layout = QVBoxLayout()
        self.dmu_table = QTableView()
        # --- SORTING ENABLED ---
        self.dmu_table.setSortingEnabled(True)
        dmu_layout.addWidget(self.dmu_table)
        dmu_group_box.setLayout(dmu_layout)
        main_layout.addWidget(dmu_group_box, stretch=1)

        self.results_table.setModel(QStandardItemModel()); self.dmu_table.setModel(QStandardItemModel())
        self.upload_button.clicked.connect(self.load_file_and_show_features)
        self.run_button.clicked.connect(self.run_analysis)
        self.download_button.clicked.connect(self.download_template)
        self.results_table.selectionModel().selectionChanged.connect(self.on_result_selection_changed)

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
        except TypeError:
            pass

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["الگوریتم", "تعداد خوشه (k)", "امتیاز سیلوئت", "شاخص دیویس-بولدین"])
        
        sorted_results = sorted(all_results, key=lambda x: self._calculate_combined_score(x, all_results), reverse=True)
        
        for result in sorted_results:
            row = [
                create_text_item(result['algorithm']),
                create_numeric_item(result['k'], precision=0),
                create_numeric_item(result['silhouette'], precision=2),
                create_numeric_item(result['davies_bouldin'], precision=2)
            ]
            model.appendRow(row)
        
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
            final_clusters_df = pd.DataFrame({'DMU': self.df[dmu_column], 'cluster': labels})
            self.analysis_completed.emit({
                'dataframe': self.df,
                'selected_features': self.selected_features,
                'clusters_df': final_clusters_df,
                'all_results': all_results
            })

    def on_result_selection_changed(self, selected, deselected):
        if not selected.indexes() or self.df is None:
            return
        selected_row = selected.indexes()[0].row()
        model = self.results_table.model()
        algorithm_name = model.item(selected_row, 0).text()
        k_item = model.item(selected_row, 1)
        k = int(k_item.data(Qt.ItemDataRole.UserRole))

        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            dmu_column = self.df.columns[0]
            labels = run_single_clustering_model(self.df, self.selected_features, algorithm_name, k)
            dmu_model = QStandardItemModel()
            dmu_model.setHorizontalHeaderLabels(["واحد تصمیم‌گیرنده (DMU)", "شماره خوشه"])
            
            for dmu, label in zip(self.df[dmu_column], labels):
                row = [
                    create_text_item(dmu),
                    create_numeric_item(label, precision=0)
                ]
                dmu_model.appendRow(row)
                
            self.dmu_table.setModel(dmu_model)
            self.dmu_table.resizeColumnsToContents()
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