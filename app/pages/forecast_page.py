# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTableView,
    QMessageBox, QGroupBox, QListWidget, QListWidgetItem, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor
import pandas as pd
import traceback
from .utils import create_numeric_item, create_text_item
from ..logic.forecasting_logic import run_forecast

# ===== UI & APPLICATION LOGIC =====
class ForecastPage(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25); main_layout.setSpacing(15)

        title_label = QLabel("پیش‌بینی تعداد نیروی انسانی مورد نیاز"); title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight); main_layout.addWidget(title_label)

        upload_group = QGroupBox("مرحله ۱: بارگذاری فایل داده‌های تاریخی (۵ سال گذشته)")
        upload_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        upload_layout = QHBoxLayout()
        self.upload_button = QPushButton("انتخاب فایل اکسل")
        self.file_path_label = QLabel("هنوز فایلی انتخاب نشده")
        upload_layout.addWidget(self.upload_button)
        upload_layout.addWidget(self.file_path_label, 1)
        upload_group.setLayout(upload_layout)
        main_layout.addWidget(upload_group)

        middle_splitter = QSplitter(Qt.Orientation.Horizontal)

        selection_group = QGroupBox("مرحله ۲: انتخاب شاخص‌ها برای پیش‌بینی")
        selection_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        selection_layout = QVBoxLayout()
        self.select_all_cb = QCheckBox("انتخاب همه")
        self.indicators_list = QListWidget()
        self.indicators_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        selection_layout.addWidget(self.select_all_cb)
        selection_layout.addWidget(self.indicators_list)
        selection_group.setLayout(selection_layout)
        middle_splitter.addWidget(selection_group)

        run_group = QGroupBox("مرحله ۳: اجرا")
        run_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        run_layout = QVBoxLayout()
        self.run_button = QPushButton("اجرای پیش‌بینی")
        self.run_button.setEnabled(False)
        run_layout.addWidget(self.run_button)
        run_group.setLayout(run_layout)
        middle_splitter.addWidget(run_group)
        middle_splitter.setSizes([400, 100])
        main_layout.addWidget(middle_splitter)

        results_group = QGroupBox("نتایج پیش‌بینی (رگرسیون خطی)")
        results_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        results_layout = QVBoxLayout()
        self.results_table = QTableView()
        self.results_table.setSortingEnabled(False) # Sorting is not meaningful here
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group, 1)

        self.upload_button.clicked.connect(self.load_data)
        self.run_button.clicked.connect(self.run_analysis)
        self.select_all_cb.stateChanged.connect(
            lambda state: self.indicators_list.selectAll() if state == Qt.CheckState.Checked.value else self.indicators_list.clearSelection()
        )

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل داده تاریخی", "", "Excel Files (*.xlsx *.xls)")
        if not file_path: return
        try:
            self.df = pd.read_excel(file_path)
            # Basic validation
            if 'سال' not in self.df.columns:
                raise ValueError("فایل اکسل باید شامل ستونی با نام 'سال' باشد.")
            self.file_path_label.setText(file_path.split('/')[-1])
            self.populate_indicators_list()
            self.run_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "خطا در خواندن فایل", f"فایل اکسل قابل پردازش نیست:\n{e}")
            self.run_button.setEnabled(False)
    
    def populate_indicators_list(self):
        self.indicators_list.clear()
        if self.df is None: return
        # Add all columns except 'سال' to the list
        for col in self.df.columns:
            if col != 'سال':
                self.indicators_list.addItem(QListWidgetItem(col))

    def run_analysis(self):
        if self.df is None:
            QMessageBox.warning(self, "داده ناقص", "لطفاً ابتدا فایل داده را بارگذاری کنید.")
            return
        
        selected_indicators = [item.text() for item in self.indicators_list.selectedItems()]
        if not selected_indicators:
            QMessageBox.warning(self, "شاخص انتخاب نشده", "لطفاً حداقل یک شاخص را برای پیش‌بینی انتخاب کنید.")
            return

        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            results = run_forecast(self.df, selected_indicators)
            self.display_results(results)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "خطا در تحلیل", f"یک خطای پیش‌بینی نشده رخ داد:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()

    def display_results(self, results):
        if not results:
            self.results_table.setModel(QStandardItemModel())
            return
            
        model = QStandardItemModel()
        
        # --- Dynamically build headers ---
        first_result = next(iter(results.values()))
        historical_years = [str(h['سال']) for h in first_result['historical']]
        next_year = str(int(historical_years[-1]) + 1)
        
        headers = ["نام شاخص"] + historical_years + [f"پیش‌بینی {next_year}"]
        model.setHorizontalHeaderLabels(headers)

        forecast_color = QColor("#E6F7FF") # Light Blue for highlight

        for indicator_name, data in results.items():
            row_items = [create_text_item(indicator_name)]
            
            # Add historical values
            for h_data in data['historical']:
                row_items.append(create_numeric_item(h_data[indicator_name], 0))
            
            # Add forecasted value and highlight it
            forecast_item = create_numeric_item(data['forecast'], 0)
            forecast_item.setBackground(forecast_color)
            forecast_item.setToolTip(f"مقدار پیش‌بینی شده برای سال {next_year}")
            row_items.append(forecast_item)
            
            model.appendRow(row_items)
        
        self.results_table.setModel(model)
        self.results_table.resizeColumnsToContents()