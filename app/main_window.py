# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem
from .styles import load_stylesheet
from .pages.welcome_page import WelcomePage
from .pages.clustering_page import ClusteringPage
from .pages.efficiency_page import EfficiencyPage

# ===== CORE APPLICATION WINDOW =====
class MainWindow(QMainWindow):
    def __init__(self, version):
        super().__init__()
        self.version = version
        self.setWindowTitle(f"OptiWise - Decision Support System v{self.version}")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(load_stylesheet())
        
        # We don't need to store the state here anymore, we will pass it directly.
        
        # --- UI Setup ---
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

        # --- Initialize Pages and Connections ---
        self.setup_pages()
        self.nav_list.currentItemChanged.connect(self.change_page)
        
    def setup_pages(self):
        # Page 1: Welcome
        self.welcome_page = WelcomePage()
        self.add_page(self.welcome_page, "صفحه اصلی")

        # Page 2: Clustering
        self.clustering_page = ClusteringPage()
        
        # Page 3: Efficiency Calculation
        # Create the instance here so we can connect to it.
        self.efficiency_page = EfficiencyPage()

        # --- CRITICAL FIX: Connect the signal DIRECTLY to the efficiency page's slot ---
        # When clustering is done, it will directly tell the efficiency page to update.
        self.clustering_page.analysis_completed.connect(self.efficiency_page.update_with_clustering_data)
        
        # Add pages to the layout
        self.add_page(self.clustering_page, "تحلیل خوشه‌بندی")
        self.add_page(self.efficiency_page, "محاسبه بهره‌وری")
        
        self.nav_list.setCurrentRow(0)

    def add_page(self, widget, name):
        self.stacked_widget.addWidget(widget)
        self.nav_list.addItem(QListWidgetItem(name))
    
    def change_page(self, current_item):
        """This method now only handles changing the visible page."""
        if current_item:
            index = self.nav_list.row(current_item)
            self.stacked_widget.setCurrentIndex(index)