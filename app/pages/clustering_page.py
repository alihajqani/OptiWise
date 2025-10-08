# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QTableView, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import pandas as pd

from ..logic.clustering_analysis import run_clustering_pipeline

# ===== CORE UI FOR CLUSTERING PAGE =====
class ClusteringPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25) # Increased margins
        main_layout.setSpacing(20) # Increased spacing

        # --- Title ---
        title_label = QLabel("ماژول خوشه‌بندی (Clustering)")
        title_label.setObjectName("TitleLabel")
        # Align title text to the right
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(title_label)

        # --- File Operations GroupBox ---
        file_group_box = QGroupBox("مرحله ۱: ورود داده")
        file_layout = QHBoxLayout()
        
        self.download_button = QPushButton("دانلود قالب اکسل")
        self.upload_button = QPushButton("آپلود و اجرای تحلیل")
        
        file_layout.addWidget(self.download_button)
        file_layout.addWidget(self.upload_button)
        file_group_box.setLayout(file_layout)
        main_layout.addWidget(file_group_box)
        
        # --- Results GroupBox ---
        results_group_box = QGroupBox("مرحله ۲: مشاهده نتایج")
        results_layout = QVBoxLayout()
        results_layout.setSpacing(10)

        # Summary labels
        self.summary_label = QLabel("هنوز تحلیلی انجام نشده است.")
        self.summary_label.setObjectName("SubtitleLabel")
        # Align summary text to the right
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        results_layout.addWidget(self.summary_label)

        # Table for results
        self.results_table = QTableView()
        # The table's internal layout direction will be handled by the app's global setting
        results_layout.addWidget(self.results_table)
        results_group_box.setLayout(results_layout)
        main_layout.addWidget(results_group_box, stretch=1)

        # --- Connections ---
        self.upload_button.clicked.connect(self.run_analysis)
        self.download_button.clicked.connect(self.download_template)

    def run_analysis(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل اکسل", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path: return

        try:
            self.summary_label.setText("در حال تحلیل داده‌ها، لطفاً صبر کنید...")
            QApplication.processEvents()
            results = run_clustering_pipeline(file_path)
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

        for i, dmu_name in enumerate(results['dmu_names']):
            cluster_label = results['labels'][i]
            dmu_item = QStandardItem(str(dmu_name))
            cluster_item = QStandardItem(str(cluster_label))
            
            # Text alignment for individual cells can also be set if needed
            dmu_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            cluster_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            dmu_item.setFlags(dmu_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            cluster_item.setFlags(cluster_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            model.appendRow([dmu_item, cluster_item])
        
        self.results_table.setModel(model)
        self.results_table.resizeColumnsToContents()

    def download_template(self):
        template_data = {
            'DMU_Name': ['واحد_الف', 'واحد_ب', 'واحد_ج'],
            'شاخص_۱': [10, 12, 15],
            'شاخص_۲': [100, 110, 105],
        }
        df = pd.DataFrame(template_data)
        save_path, _ = QFileDialog.getSaveFileName(
            self, "ذخیره قالب اکسل", "clustering_template.xlsx", "Excel Files (*.xlsx)"
        )
        if save_path:
            try:
                df.to_excel(save_path, index=False)
                QMessageBox.information(self, "موفقیت", f"قالب با موفقیت در مسیر زیر ذخیره شد:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل:\n{e}")