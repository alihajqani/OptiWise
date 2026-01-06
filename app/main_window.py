# ===== SECTION BEING MODIFIED: app/main_window.py =====
# ===== IMPORTS & DEPENDENCIES =====
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QVBoxLayout)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

from .logic.license_validator import LicenseValidator
from .styles import load_stylesheet
from .pages.welcome_page import WelcomePage
from .pages.clustering_page import ClusteringPage
from .pages.efficiency_page import EfficiencyPage
from .pages.ranking_page import RankingPage
from .pages.hr_efficiency_page import HrEfficiencyPage
from .pages.resource_allocation_page import ResourceAllocationPage
from .pages.forecast_page import ForecastPage
from .pages.help_page import HelpPage
# --- NEW: Import BasePage to check instance type ---
from .pages.utils import BasePage


# ===== UI & APPLICATION LOGIC =====
class MainWindow(QMainWindow):
    def __init__(self, version):
        super().__init__()
        self.version = version
        self.setWindowTitle(f"OptiWise - Decision Support System v{self.version}")
        self.setGeometry(100, 100, 1280, 850)
        self.setStyleSheet(load_stylesheet())
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        try:
            self.setWindowIcon(QIcon("assets/app_icon.png"))
        except Exception:
            print("Warning: Could not load application icon from 'assets/app_icon.png'")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.pages_info = []
        self.setup_pages()
        
        if self.welcome_page:
            self.welcome_page.page_selected.connect(self.stacked_widget.setCurrentIndex)
        
        self.check_license()

    def go_to_home(self):
        """A simple slot to switch to the welcome page."""
        self.stacked_widget.setCurrentIndex(0)

    def check_license(self):
        validator = LicenseValidator()
        is_expired, message = validator.check_status()
        if is_expired:
            self._enter_expired_mode(message)

    def _enter_expired_mode(self, message: str):
        self.welcome_page.show_expiration_message(message)
        self.stacked_widget.setCurrentIndex(0)
                
    def setup_pages(self):
        page_definitions = [
            {"name": "صفحه اصلی", "icon": "assets/icons/home.png", "widget_class": None},
            {"name": "تحلیل خوشه‌بندی", "icon": "assets/icons/cluster.png", "widget_class": ClusteringPage},
            {"name": "محاسبه بهره‌وری واحدی", "icon": "assets/icons/efficiency.png", "widget_class": EfficiencyPage},
            {"name": "تخصیص بهینه منابع", "icon": "assets/icons/resource.png", "widget_class": ResourceAllocationPage},
            {"name": "رتبه‌بندی", "icon": "assets/icons/ranking.png", "widget_class": RankingPage},
            {"name": "بهره‌وری نیروی انسانی", "icon": "assets/icons/users.png", "widget_class": HrEfficiencyPage},
            {"name": "پیش‌بینی نیروی انسانی", "icon": "assets/icons/forecast.png", "widget_class": ForecastPage},
            {"name": "راهنما", "icon": "assets/icons/help.png", "widget_class": HelpPage}
        ]

        self.welcome_page = WelcomePage(self.version, page_definitions)
        self.stacked_widget.addWidget(self.welcome_page)

        clustering_page = None
        hr_efficiency_page = None
        
        for index, page_def in enumerate(page_definitions):
            if index == 0: continue
            
            widget = page_def["widget_class"]()
            self.stacked_widget.addWidget(widget)
            
            # --- NEW: Connect the back_to_home signal ---
            if isinstance(widget, BasePage):
                widget.back_to_home_requested.connect(self.go_to_home)

            # Signal connections for analysis logic
            if isinstance(widget, ClusteringPage):
                clustering_page = widget
            if isinstance(widget, HrEfficiencyPage):
                hr_efficiency_page = widget
            if isinstance(widget, EfficiencyPage) and clustering_page:
                clustering_page.analysis_completed.connect(widget.update_with_clustering_data)
            if isinstance(widget, ResourceAllocationPage) and hr_efficiency_page:
                hr_efficiency_page.analysis_completed.connect(widget.update_data)

        self.stacked_widget.setCurrentIndex(0)