# ===== SECTION BEING MODIFIED: main_window.py =====
# ===== IMPORTS & DEPENDENCIES =====
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QStackedWidget, 
                             QVBoxLayout, QToolButton, QButtonGroup, QSizePolicy, QSpacerItem)
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


# ===== UI & APPLICATION LOGIC =====
class MainWindow(QMainWindow):
    def __init__(self, version):
        super().__init__()
        self.version = version
        self.setWindowTitle(f"OptiWise - Decision Support System v{self.version}")
        self.setGeometry(100, 100, 1200, 850)
        self.setStyleSheet(load_stylesheet())
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft) # Force RTL
        
        try:
            self.setWindowIcon(QIcon("assets/app_icon.png"))
        except Exception:
            print("Warning: Could not load application icon from 'assets/app_icon.png'")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.nav_bar = QWidget()
        self.nav_bar.setObjectName("NavBar")
        self.nav_bar.setFixedWidth(240) # Slightly wider for bold text
        self.nav_layout = QVBoxLayout(self.nav_bar)
        self.nav_layout.setContentsMargins(5, 20, 5, 20)
        self.nav_layout.setSpacing(8)
        main_layout.addWidget(self.nav_bar)
        
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.setup_pages()
        
        # Add spacer to push buttons to fill space or distribute them
        # To distribute 8 items across full height, we use spacers or stretch
        # Here we add a final spacer to ensure they don't bunch up if height is large, 
        # but we set button policy to expanding in add_page.
        self.nav_layout.addStretch() 
        
        self.button_group.idClicked.connect(self.stacked_widget.setCurrentIndex)
        
        self.check_license()

    def check_license(self):
        validator = LicenseValidator()
        is_expired, message = validator.check_status()
        if is_expired:
            self._enter_expired_mode(message)

    def _enter_expired_mode(self, message: str):
        self.welcome_page.show_expiration_message(message)
        self.stacked_widget.setCurrentIndex(0)
        self.button_group.button(0).setChecked(True)
        buttons = self.button_group.buttons()
        for i, button in enumerate(buttons):
            if i > 0:
                button.setEnabled(False)
                button.setToolTip("این نسخه منقضی شده است")
                
    def setup_pages(self):
        self.welcome_page = WelcomePage(self.version)
        self.clustering_page = ClusteringPage()
        self.efficiency_page = EfficiencyPage()
        self.ranking_page = RankingPage()
        self.hr_efficiency_page = HrEfficiencyPage()
        self.resource_allocation_page = ResourceAllocationPage()
        self.forecast_page = ForecastPage()
        self.help_page = HelpPage()
        
        # Connections
        # Clustering -> Efficiency (Unit)
        self.clustering_page.analysis_completed.connect(self.efficiency_page.update_with_clustering_data)
        
        # CHANGED: Resource Allocation now depends on HR Efficiency as per client request
        self.hr_efficiency_page.analysis_completed.connect(self.resource_allocation_page.update_data)

        # Adding Pages with Updated Names
        self.add_page(self.welcome_page, "صفحه اصلی", "assets/icons/home.png")
        self.add_page(self.clustering_page, "تحلیل خوشه‌بندی", "assets/icons/cluster.png")
        self.add_page(self.efficiency_page, "محاسبه بهره‌وری واحدی", "assets/icons/efficiency.png")
        self.add_page(self.resource_allocation_page, "تخصیص بهینه منابع", "assets/icons/resource.png")
        self.add_page(self.ranking_page, "رتبه‌بندی", "assets/icons/ranking.png")
        self.add_page(self.hr_efficiency_page, "بهره‌وری نیروی انسانی", "assets/icons/users.png")
        self.add_page(self.forecast_page, "پیش‌بینی نیروی انسانی", "assets/icons/forecast.png")
        self.add_page(self.help_page, "راهنما", "assets/icons/help.png")

        if self.button_group.buttons():
            self.button_group.button(0).setChecked(True)
            self.stacked_widget.setCurrentIndex(0)

    def add_page(self, widget: QWidget, name: str, icon_path: str):
        page_index = self.stacked_widget.count()
        self.stacked_widget.addWidget(widget)

        button = QToolButton()
        button.setText(name)
        
        icon = QIcon()
        
        try:
            dir_name, file_name = os.path.split(icon_path)
            white_file_name = f"W-{file_name}" 
            white_icon_path = os.path.join(dir_name, white_file_name)
            
            # Load icon (Logic remains the same)
            if os.path.exists(white_icon_path):
                icon.addFile(white_icon_path, state=QIcon.State.Off)
                icon.addFile(icon_path, state=QIcon.State.On)
            else:
                icon.addFile(icon_path, state=QIcon.State.Off)
                icon.addFile(icon_path, state=QIcon.State.On)

        except Exception as e:
            print(f"Error creating multi-state icon: {e}")
            icon.addFile(icon_path, state=QIcon.State.Off)
            icon.addFile(icon_path, state=QIcon.State.On)

        button.setIcon(icon)
        button.setIconSize(QSize(36, 36)) # Slightly larger icons
        button.setCheckable(True)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        button.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Make buttons expand to fill vertical space evenly
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        button.setMinimumHeight(60) # Minimum height to look like a key/tile

        self.nav_layout.addWidget(button)
        self.button_group.addButton(button, page_index)        