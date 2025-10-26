# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTableView,
    QMessageBox, QGroupBox, QListWidget, QListWidgetItem, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import traceback
from ..logic.dea_analysis import run_hr_dea_analysis


# ===== UTILITY FUNCTIONS =====
def create_numeric_item(value, precision=2):
    """Creates a QStandardItem that sorts numerically."""
    item = QStandardItem()
    try:
        float_val = float(value)
        item.setData(float_val, Qt.ItemDataRole.UserRole)
        item.setText(f"{float_val:.{precision}f}")
    except (ValueError, TypeError):
        item.setText(str(value))
    
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
class HrEfficiencyPage(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        title_label = QLabel("ماژول محاسبه بهره‌وری نیروی انسانی (مدل BCC)")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(title_label)

        upload_group = QGroupBox("مرحله ۱: بارگذاری فایل داده پرسنل")
        upload_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        upload_layout = QHBoxLayout()
        self.upload_button = QPushButton("انتخاب فایل اکسل")
        self.file_path_label = QLabel("هنوز فایلی انتخاب نشده")
        upload_layout.addWidget(self.upload_button)
        upload_layout.addWidget(self.file_path_label, 1)
        upload_group.setLayout(upload_layout)
        main_layout.addWidget(upload_group)

        middle_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        io_selection_group = QGroupBox("مرحله ۲: انتخاب شاخص‌های ورودی و خروجی")
        io_selection_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        io_main_layout = QHBoxLayout()
        
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
        
        io_selection_group.setLayout(io_main_layout)
        middle_splitter.addWidget(io_selection_group)
        
        run_group = QGroupBox("مرحله ۳: اجرا")
        run_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        run_layout = QVBoxLayout()
        self.run_button = QPushButton("محاسبه بهره‌وری پرسنل")
        self.run_button.setEnabled(False)
        run_layout.addWidget(self.run_button)
        run_group.setLayout(run_layout)
        middle_splitter.addWidget(run_group)
        middle_splitter.setSizes([400, 100])
        main_layout.addWidget(middle_splitter)

        results_group = QGroupBox("نتایج بهره‌وری نیروی انسانی")
        results_group.setAlignment(Qt.AlignmentFlag.AlignRight)
        results_layout = QVBoxLayout()
        self.results_table = QTableView()
        self.results_table.setSortingEnabled(True)
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group, 1)
        
        self.upload_button.clicked.connect(self.load_data)
        self.run_button.clicked.connect(self.run_analysis)
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

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل داده پرسنل", "", "Excel Files (*.xlsx *.xls)")
        if not file_path: return
        try:
            self.df = pd.read_excel(file_path)
            self.file_path_label.setText(file_path.split('/')[-1])
            self.populate_io_lists()
            self.run_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "خطا در خواندن فایل", f"فایل اکسل قابل پردازش نیست:\n{e}")
            self.run_button.setEnabled(False)

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
            results_list = run_hr_dea_analysis(self.df, dmu_column, selected_inputs, selected_outputs)
            
            # Pass the original dataframe along with the results
            self.display_results(results_list, self.df)
            
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "خطا در تحلیل", f"یک خطای پیش‌بینی نشده رخ داد:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()

    def display_results(self, results_list, original_df):
        results_df = pd.DataFrame(results_list)
        
        # Merge results with original dataframe to get extra columns
        # The first column of original_df is the key (dmu name)
        dmu_col_name = original_df.columns[0]
        merged_df = pd.merge(original_df, results_df, left_on=dmu_col_name, right_on='dmu', how='left')
        
        # Initial sort before displaying
        merged_df = merged_df.sort_values(by='score', ascending=False)

        model = QStandardItemModel()
        
        # --- Dynamically find optional columns ---
        # Define possible names for optional columns
        code_col_options = ['کد پرسنلی', 'کدپرسنلی', 'personnel_code', 'code']
        name_col_options = ['نام و نام خانوادگی', 'نام', 'name', 'fullname']
        
        # Find the actual column names present in the dataframe
        code_col = next((col for col in code_col_options if col in merged_df.columns), None)
        name_col = next((col for col in name_col_options if col in merged_df.columns), None)
        
        # --- Build headers dynamically ---
        headers = []
        if code_col: headers.append("کد پرسنلی")
        if name_col: headers.append("نام و نام خانوادگی")
        headers.extend(["DMU (از فایل)", "امتیاز بهره‌وری (BCC)"])
        model.setHorizontalHeaderLabels(headers)

        for _, row in merged_df.iterrows():
            row_items = []
            if code_col: row_items.append(create_text_item(row.get(code_col, '')))
            if name_col: row_items.append(create_text_item(row.get(name_col, '')))
            row_items.extend([
                create_text_item(row['dmu']),
                create_numeric_item(row.get('score', 0), precision=2)
            ])
            model.appendRow(row_items)
        
        self.results_table.setModel(model)
        self.results_table.resizeColumnsToContents()