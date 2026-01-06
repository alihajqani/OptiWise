# ===== SECTION BEING MODIFIED: app/pages/forecast_page.py =====
# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTableView,
    QMessageBox, QGroupBox, QListWidget, QListWidgetItem, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor
import pandas as pd
import traceback
# --- MODIFIED: Import BasePage ---
from .utils import create_numeric_item, create_text_item, save_table_to_excel, BasePage
from ..logic.forecasting_logic import run_forecast

# ===== UI & APPLICATION LOGIC =====
# --- MODIFIED: Inherit from BasePage ---
class ForecastPage(BasePage):
    def __init__(self):
        super().__init__()
        self.df = None
        self.is_fullscreen = False
        self.initUI()

    def initUI(self):
        # --- MODIFIED: Use self.content_layout provided by BasePage ---
        self.content_layout.setSpacing(15)

        title_label = QLabel("پیش‌بینی تعداد نیروی انسانی مورد نیاز (مدل سری زمانی)"); 
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content_layout.addWidget(title_label)

        # --- Step 1 ---
        self.upload_group = QGroupBox("مرحله ۱: بارگذاری فایل داده‌های تاریخی (۵ سال گذشته)")
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
        self.content_layout.addWidget(self.upload_group)

        # --- Step 2 & 3 ---
        self.middle_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.middle_splitter.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.selection_group = QGroupBox("مرحله ۲: انتخاب شاخص‌ها برای پیش‌بینی")
        self.selection_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        selection_layout = QVBoxLayout()
        self.select_all_cb = QCheckBox("انتخاب همه")
        self.indicators_list = QListWidget()
        self.indicators_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        selection_layout.addWidget(self.select_all_cb)
        selection_layout.addWidget(self.indicators_list)
        self.selection_group.setLayout(selection_layout)
        self.middle_splitter.addWidget(self.selection_group)

        self.run_group = QGroupBox("مرحله ۳: اجرا")
        self.run_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        run_layout = QVBoxLayout()
        self.run_button = QPushButton("پیش‌بینی نیروی انسانی")
        self.run_button.setEnabled(False)
        run_layout.addWidget(self.run_button)
        self.run_group.setLayout(run_layout)
        
        self.middle_splitter.addWidget(self.run_group)
        self.middle_splitter.setSizes([400, 100])
        self.content_layout.addWidget(self.middle_splitter)

        # --- Step 4 ---
        self.results_group = QGroupBox("نتایج پیش‌بینی (سری زمانی)")
        self.results_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        results_layout = QVBoxLayout()
        
        # Controls
        res_ctrl_layout = QHBoxLayout()
        res_ctrl_layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        self.export_button = QPushButton("خروجی اکسل")
        self.export_button.setObjectName("ExportButton")
        self.fullscreen_button = QPushButton("نمایش تمام صفحه")
        res_ctrl_layout.addWidget(self.export_button)
        res_ctrl_layout.addWidget(self.fullscreen_button)
        res_ctrl_layout.addStretch()
        results_layout.addLayout(res_ctrl_layout)

        self.results_table = QTableView()
        self.results_table.setSortingEnabled(False) 
        results_layout.addWidget(self.results_table)
        self.results_group.setLayout(results_layout)
        self.content_layout.addWidget(self.results_group, 1)

        self.upload_button.clicked.connect(self.load_data)
        self.download_button.clicked.connect(self.download_template)
        self.run_button.clicked.connect(self.run_analysis)
        self.select_all_cb.stateChanged.connect(
            lambda state: self.indicators_list.selectAll() if state == Qt.CheckState.Checked.value else self.indicators_list.clearSelection()
        )
        self.export_button.clicked.connect(lambda: save_table_to_excel(self, self.results_table, "forecast_results.xlsx"))
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
        template_data = {'سال': [1398, 1399, 1400, 1401, 1402], 'شاخص_۱': [100, 110, 120, 125, 135]}
        df = pd.DataFrame(template_data)
        save_path, _ = QFileDialog.getSaveFileName(self, "ذخیره قالب اکسل", "forecast_template.xlsx", "Excel Files (*.xlsx)")
        if save_path:
            df.to_excel(save_path, index=False)
            QMessageBox.information(self, "موفقیت", "قالب ذخیره شد.")

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل داده تاریخی", "", "Excel Files (*.xlsx *.xls)")
        if not file_path: return
        try:
            self.df = pd.read_excel(file_path)
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
        
        first_result = next(iter(results.values()))
        historical_years = [str(h['سال']) for h in first_result['historical']]
        next_year = str(int(historical_years[-1]) + 1)
        
        headers = ["نام شاخص"] + historical_years + [f"پیش‌بینی {next_year}"]
        model.setHorizontalHeaderLabels(headers)

        forecast_color = QColor("#E6F7FF")

        for indicator_name, data in results.items():
            row_items = [create_text_item(indicator_name)]
            
            for h_data in data['historical']:
                row_items.append(create_numeric_item(h_data[indicator_name], 0))
            
            forecast_item = create_numeric_item(data['forecast'], 0)
            forecast_item.setBackground(forecast_color)
            forecast_item.setToolTip(f"مقدار پیش‌بینی شده برای سال {next_year}")
            row_items.append(forecast_item)
            
            model.appendRow(row_items)
        
        self.results_table.setModel(model)
        self.results_table.resizeColumnsToContents()