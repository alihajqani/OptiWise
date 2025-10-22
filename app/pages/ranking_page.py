from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTableView,
    QMessageBox, QGroupBox, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import traceback

from ..logic.dea_analysis import run_ranking_dea


class RankingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25); main_layout.setSpacing(15)
        title_label = QLabel("فاز سوم: رتبه‌بندی واحدها (Super-Efficiency)"); title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight); main_layout.addWidget(title_label)

        upload_group = QGroupBox("مرحله ۱: بارگذاری فایل داده"); upload_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        upload_layout = QHBoxLayout(); self.upload_button = QPushButton("انتخاب فایل اکسل")
        self.file_path_label = QLabel("هنوز فایلی انتخاب نشده"); upload_layout.addWidget(self.upload_button)
        upload_layout.addWidget(self.file_path_label, 1); upload_group.setLayout(upload_layout)
        main_layout.addWidget(upload_group)

        middle_splitter = QSplitter(Qt.Orientation.Horizontal)
        io_selection_group = QGroupBox("مرحله ۲: انتخاب شاخص‌های ورودی و خروجی"); io_selection_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        io_layout = QHBoxLayout(); self.inputs_list = QListWidget(); self.outputs_list = QListWidget()
        self.inputs_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection); self.outputs_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        inputs_group = QGroupBox("ورودی‌ها"); inputs_group.setAlignment(Qt.AlignmentFlag.AlignRight); inputs_layout = QVBoxLayout(); inputs_layout.addWidget(self.inputs_list); inputs_group.setLayout(inputs_layout)
        outputs_group = QGroupBox("خروجی‌ها"); outputs_group.setAlignment(Qt.AlignmentFlag.AlignRight); outputs_layout = QVBoxLayout(); outputs_layout.addWidget(self.outputs_list); outputs_group.setLayout(outputs_layout)
        io_layout.addWidget(inputs_group, 1); io_layout.addWidget(outputs_group, 1)
        io_selection_group.setLayout(io_layout); middle_splitter.addWidget(io_selection_group)
        
        run_group = QGroupBox("مرحله ۳: اجرا"); run_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        run_layout = QVBoxLayout(); self.run_button = QPushButton("محاسبه رتبه‌بندی")
        self.run_button.setEnabled(False); run_layout.addWidget(self.run_button); run_group.setLayout(run_layout)
        middle_splitter.addWidget(run_group); middle_splitter.setSizes([400, 100]); main_layout.addWidget(middle_splitter)

        results_group = QGroupBox("نتایج رتبه‌بندی"); results_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        results_layout = QVBoxLayout(); self.results_table = QTableView()
        results_layout.addWidget(self.results_table); results_group.setLayout(results_layout)
        main_layout.addWidget(results_group, 1)
        
        self.upload_button.clicked.connect(self.load_data); self.run_button.clicked.connect(self.run_analysis)

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل داده", "", "Excel Files (*.xlsx *.xls)")
        if not file_path:
            return
        try:
            self.df = pd.read_excel(file_path)
            self.file_path_label.setText(file_path.split('/')[-1])
            self.populate_io_lists(); self.run_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "خطا در خواندن فایل", f"فایل اکسل قابل پردازش نیست:\n{e}")

    def populate_io_lists(self):
        self.inputs_list.clear(); self.outputs_list.clear()
        if self.df is None:
            return
        for col in self.df.columns[1:]:
            self.inputs_list.addItem(QListWidgetItem(col))
            self.outputs_list.addItem(QListWidgetItem(col))

    def run_analysis(self):
        if self.df is None:
            QMessageBox.warning(self, "داده ناقص", "لطفاً ابتدا فایل داده را بارگذاری کنید.")
            return
        selected_inputs = [item.text() for item in self.inputs_list.selectedItems()]
        selected_outputs = [item.text() for item in self.outputs_list.selectedItems()]
        if not selected_inputs or not selected_outputs:
            QMessageBox.warning(self, "شاخص انتخاب نشده", "لطفاً شاخص‌های ورودی و خروجی را انتخاب کنید.")
            return

        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            dmu_column = self.df.columns[0]
            results = run_ranking_dea(self.df, dmu_column, selected_inputs, selected_outputs)
            self.display_results(results)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "خطا در تحلیل", f"یک خطای پیش‌بینی نشده رخ داد:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()

    def display_results(self, results):
        # Sort by score in descending order to get the rank
        sorted_results = sorted(results, key=lambda x: x.get('score', 0) or 0, reverse=True)
        
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["رتبه", "واحد تصمیم‌گیرنده (DMU)", "امتیاز ابرکارایی"])

        for i, res in enumerate(sorted_results):
            rank_item = QStandardItem(str(i + 1))
            dmu_item = QStandardItem(str(res['dmu']))
            score_item = QStandardItem(f"{res.get('score', 0):.4f}")
            
            for item in [rank_item, dmu_item, score_item]:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            model.appendRow([rank_item, dmu_item, score_item])
        
        self.results_table.setModel(model)
        self.results_table.resizeColumnsToContents()