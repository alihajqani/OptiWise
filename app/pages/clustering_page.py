# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QTableView, QMessageBox, QGroupBox, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import pandas as pd

from ..logic.clustering_analysis import run_clustering_pipeline

# ===== CORE UI FOR CLUSTERING PAGE =====
class ClusteringPage(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None  # To store the loaded dataframe
        self.feature_checkboxes = []
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        title_label = QLabel("ماژول خوشه‌بندی (Clustering)")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(title_label)

        # --- Step 1: File Selection ---
        file_group_box = QGroupBox("مرحله ۱: انتخاب فایل داده")
        file_layout = QHBoxLayout()
        self.download_button = QPushButton("دانلود قالب اکسل")
        self.upload_button = QPushButton("انتخاب فایل اکسل")
        self.file_path_label = QLabel("هیچ فایلی انتخاب نشده است.")
        file_layout.addWidget(self.upload_button)
        file_layout.addWidget(self.file_path_label, stretch=1)
        file_layout.addWidget(self.download_button)
        file_group_box.setLayout(file_layout)
        main_layout.addWidget(file_group_box)

        # --- Step 2: Feature Selection ---
        self.feature_group_box = QGroupBox("مرحله ۲: انتخاب شاخص‌ها برای تحلیل")
        feature_main_layout = QVBoxLayout()
        
        # ScrollArea to handle many features
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.checkbox_layout = QVBoxLayout(scroll_widget)
        self.checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(scroll_widget)
        
        feature_main_layout.addWidget(scroll_area, stretch=1)
        
        self.run_button = QPushButton("مرحله ۳: اجرای تحلیل خوشه‌بندی")
        feature_main_layout.addWidget(self.run_button)
        self.feature_group_box.setLayout(feature_main_layout)
        main_layout.addWidget(self.feature_group_box)
        self.feature_group_box.setEnabled(False) # Disabled by default

        # --- Step 3: Results ---
        results_group_box = QGroupBox("نتایج تحلیل")
        results_layout = QVBoxLayout()
        results_layout.setSpacing(10)
        self.summary_label = QLabel("برای مشاهده نتایج، تحلیل را اجرا کنید.")
        self.summary_label.setObjectName("SubtitleLabel")
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.results_table = QTableView()
        results_layout.addWidget(self.summary_label)
        results_layout.addWidget(self.results_table)
        results_group_box.setLayout(results_layout)
        main_layout.addWidget(results_group_box, stretch=1)

        # --- Connections ---
        self.upload_button.clicked.connect(self.load_file_and_show_features)
        self.run_button.clicked.connect(self.run_analysis)
        self.download_button.clicked.connect(self.download_template)

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
        # Clear previous checkboxes
        for checkbox in self.feature_checkboxes:
            self.checkbox_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.feature_checkboxes.clear()
        
        # Get only numeric columns as potential features
        numeric_columns = self.df.select_dtypes(include=['number']).columns
        
        # Assume first column is always ID and not a feature
        all_columns = self.df.columns[1:] 

        for col in all_columns:
            checkbox = QCheckBox(col)
            # Pre-select if the column is numeric
            if col in numeric_columns:
                checkbox.setChecked(True)
            self.checkbox_layout.addWidget(checkbox)
            self.feature_checkboxes.append(checkbox)

    def run_analysis(self):
        selected_features = [cb.text() for cb in self.feature_checkboxes if cb.isChecked()]
        
        if len(selected_features) < 2:
            QMessageBox.warning(self, "شاخص ناکافی", "لطفاً حداقل دو شاخص را برای تحلیل انتخاب کنید.")
            return

        try:
            self.summary_label.setText("در حال تحلیل داده‌ها، لطفاً صبر کنید...")
            QApplication.processEvents()
            
            # The first column is always assumed to be the DMU identifier
            dmu_column = self.df.columns[0]
            
            # Pass the full dataframe and the list of selected features to the backend
            results = run_clustering_pipeline(self.df, dmu_column, selected_features)

            self.display_results(results)
        except Exception as e:
            QMessageBox.critical(self, "خطا در تحلیل", f"یک خطای پیش‌بینی نشده رخ داد:\n{e}")
            self.summary_label.setText("تحلیل با خطا مواجه شد.")

    def display_results(self, results):
        summary_text = (
            f"تحلیل با موفقیت انجام شد! "
            f"بهترین الگوریتم: <b>{results['algorithm']}</b> | "
            f"تعداد بهینه خوشه‌ها: <b>{results['best_k']}</b> | "
            f"امتیاز سیلوئت: <b>{results['best_score']:.2f}</b>"
        )
        self.summary_label.setText(summary_text)

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["واحد تصمیم‌گیرنده (DMU)", "شماره خوشه"])
        for dmu, label in zip(results['dmu_names'], results['labels']):
            dmu_item = QStandardItem(str(dmu))
            cluster_item = QStandardItem(str(label))
            dmu_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            cluster_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            dmu_item.setFlags(dmu_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            cluster_item.setFlags(cluster_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            model.appendRow([dmu_item, cluster_item])
        self.results_table.setModel(model)
        self.results_table.resizeColumnsToContents()

    def download_template(self):
        # ... (This method remains the same)
        template_data = {
            'DMU_Name': ['واحد_الف', 'واحد_ب', 'واحد_ج'], 'شاخص_۱': [10, 12, 15], 'شاخص_۲': [100, 110, 105],
        }
        df = pd.DataFrame(template_data)
        save_path, _ = QFileDialog.getSaveFileName(self, "ذخیره قالب اکسل", "clustering_template.xlsx", "Excel Files (*.xlsx)")
        if save_path:
            try:
                df.to_excel(save_path, index=False)
                QMessageBox.information(self, "موفقیت", f"قالب با موفقیت در مسیر زیر ذخیره شد:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل:\n{e}")