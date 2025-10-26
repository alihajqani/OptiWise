# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from .logic.license_validator import LicenseValidator

from .styles import load_stylesheet
from .pages.welcome_page import WelcomePage
from .pages.clustering_page import ClusteringPage
from .pages.efficiency_page import EfficiencyPage
from .pages.ranking_page import RankingPage
from .pages.hr_efficiency_page import HrEfficiencyPage
from .pages.help_page import HelpPage


# ===== UI & APPLICATION LOGIC =====
class MainWindow(QMainWindow):
    def __init__(self, version):
        super().__init__()
        self.version = version
        self.setWindowTitle(f"OptiWise - Decision Support System v{self.version}")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(load_stylesheet())
        
        try:
            self.setWindowIcon(QIcon("assets/icon.png"))
        except Exception:
            print("Warning: Could not load application icon from 'assets/icon.png'")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(200)
        main_layout.addWidget(self.nav_list)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.setup_pages()
        self.nav_list.currentItemChanged.connect(self.change_page)
        
        self.check_license()

    def check_license(self):
        validator = LicenseValidator()
        is_expired, message = validator.check_status()
        
        if is_expired:
            self._enter_expired_mode(message)

    def _enter_expired_mode(self, message: str):
        self.welcome_page.show_expiration_message(message)
        self.nav_list.setCurrentRow(0)
        self.stacked_widget.setCurrentIndex(0)
        
        for i in range(1, self.nav_list.count()):
            item = self.nav_list.item(i)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            item.setToolTip("این نسخه منقضی شده است")

    def setup_pages(self):
        # --- MODIFIED: Pass version to WelcomePage ---
        self.welcome_page = WelcomePage(self.version)
        self.add_page(self.welcome_page, "صفحه اصلی")

        self.clustering_page = ClusteringPage()
        self.efficiency_page = EfficiencyPage()
        self.ranking_page = RankingPage()
        self.hr_efficiency_page = HrEfficiencyPage()
        self.help_page = HelpPage()
        
        self.clustering_page.analysis_completed.connect(self.efficiency_page.update_with_clustering_data)

        self.add_page(self.clustering_page, "تحلیل خوشه‌بندی")
        self.add_page(self.efficiency_page, "محاسبه بهره‌وری واحد")
        self.add_page(self.ranking_page, "رتبه‌بندی واحدها")
        self.add_page(self.hr_efficiency_page, "بهره‌وری نیروی انسانی")
        self.add_page(self.help_page, "راهنمای نرم‌افزار")

        self.nav_list.setCurrentRow(0)
        
    def add_page(self, widget, name):
        self.stacked_widget.addWidget(widget)
        item = QListWidgetItem(name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.nav_list.addItem(item)

    def change_page(self, current_item):
        if current_item:
            index = self.nav_list.row(current_item)
            self.stacked_widget.setCurrentIndex(index)