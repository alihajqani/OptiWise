# ===== SECTION BEING MODIFIED: app/pages/ranking_page.py =====
#===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTableView,
    QMessageBox, QGroupBox, QListWidget, QListWidgetItem, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import traceback

from ..logic.dea_analysis import run_ranking_dea
# --- MODIFIED: Import BasePage ---
from .utils import create_numeric_item, create_text_item, save_table_to_excel, BasePage

#===== UI & APPLICATION LOGIC =====
# --- MODIFIED: Inherit from BasePage ---
class RankingPage(BasePage):
    def __init__(self):
        super().__init__()
        self.df = None
        self.is_fullscreen = False
        self.initUI()
        
    def initUI(self):
        # --- MODIFIED: Use self.content_layout provided by BasePage ---
        self.content_layout.setSpacing(15)
        
        title_label = QLabel("ماژول رتبه‌بندی (مدل Super Efficiency)")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.content_layout.addWidget(title_label)

        # --- Step 1 ---
        self.upload_group = QGroupBox("مرحله ۱: بارگذاری فایل داده")
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
        
        # Run
        self.run_group = QGroupBox("مرحله ۳: اجرا")
        self.run_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        run_layout = QVBoxLayout()
        self.run_button = QPushButton("محاسبه رتبه‌بندی")
        self.run_button.setEnabled(False)
        run_layout.addWidget(self.run_button)
        self.run_group.setLayout(run_layout)
        
        self.middle_splitter.addWidget(self.run_group)
        self.middle_splitter.setSizes([400, 100])
        self.content_layout.addWidget(self.middle_splitter)

        # --- Step 4: Results ---
        self.results_group = QGroupBox("نتایج رتبه‌بندی")
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
        self.results_table.setSortingEnabled(True)
        results_layout.addWidget(self.results_table)
        self.results_group.setLayout(results_layout)
        self.content_layout.addWidget(self.results_group, 1)
        
        # Connections
        self.upload_button.clicked.connect(self.load_data)
        self.download_button.clicked.connect(self.download_template)
        self.run_button.clicked.connect(self.run_analysis)
        self.inputs_select_all_cb.stateChanged.connect(self.toggle_select_all_inputs)
        self.outputs_select_all_cb.stateChanged.connect(self.toggle_select_all_outputs)
        self.inputs_list.itemSelectionChanged.connect(self.update_inputs_checkbox_state)
        self.outputs_list.itemSelectionChanged.connect(self.update_outputs_checkbox_state)
        self.export_button.clicked.connect(lambda: save_table_to_excel(self, self.results_table, "ranking_results.xlsx"))
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
        template_data = {'DMU': ['A', 'B'], 'Input1': [10, 20], 'Output1': [100, 200]}
        df = pd.DataFrame(template_data)
        save_path, _ = QFileDialog.getSaveFileName(self, "ذخیره قالب اکسل", "ranking_template.xlsx", "Excel Files (*.xlsx)")
        if save_path:
            df.to_excel(save_path, index=False)
            QMessageBox.information(self, "موفقیت", "قالب ذخیره شد.")

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

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل داده", "", "Excel Files (*.xlsx *.xls)")
        if not file_path: return
        try:
            self.df = pd.read_excel(file_path)
            self.file_path_label.setText(file_path.split('/')[-1])
            self.populate_io_lists(); self.run_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "خطا در خواندن فایل", f"فایل اکسل قابل پردازش نیست:\n{e}")

    def populate_io_lists(self):
        self.inputs_list.clear(); self.outputs_list.clear()
        if self.df is None: return
        for col in self.df.columns[1:]:
            self.inputs_list.addItem(QListWidgetItem(col))
            self.outputs_list.addItem(QListWidgetItem(col))
        self.update_inputs_checkbox_state()
        self.update_outputs_checkbox_state()

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
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["رتبه", "واحد تصمیم‌گیرنده (DMU)", "امتیاز ابرکارایی"])

        sorted_results = sorted(results, key=lambda x: x.get('score', 0) or 0, reverse=True)

        for i, res in enumerate(sorted_results):
            row = [
                create_numeric_item(i + 1, precision=0),
                create_text_item(res['dmu']),
                create_numeric_item(res.get('score', 0), precision=2)
            ]
            model.appendRow(row)
        
        self.results_table.setModel(model)
        self.results_table.resizeColumnsToContents()
        self.results_table.sortByColumn(0, Qt.SortOrder.AscendingOrder)