# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem
from .styles import load_stylesheet
from .pages.welcome_page import WelcomePage
# Import the new clustering page
from .pages.clustering_page import ClusteringPage

# ===== CORE UI STRUCTURE =====
class MainWindow(QMainWindow):
    def __init__(self, version):
        super().__init__()
        self.version = version
        self.setWindowTitle(f"OptiWise - Decision Support System v{self.version}") # Updated name
        self.setGeometry(100, 100, 1100, 750)
        
        self.setStyleSheet(load_stylesheet())
        
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

    def setup_pages(self):
        """Creates pages and adds them to the navigation and stacked widget."""
        # Page 1: Welcome
        self.welcome_page = WelcomePage()
        self.add_page(self.welcome_page, "صفحه اصلی")

        # Page 2: Clustering (The new page)
        self.clustering_page = ClusteringPage()
        self.add_page(self.clustering_page, "تحلیل خوشه‌بندی")

        # --- Add other pages as placeholders ---
        # self.ranking_page = QWidget() # Placeholder
        # self.add_page(self.ranking_page, "رتبه‌بندی")
        
        self.nav_list.setCurrentRow(0)

    def add_page(self, widget, name, icon_path=None):
        """A helper function to add a page to both the nav and the stack."""
        self.stacked_widget.addWidget(widget)
        list_item = QListWidgetItem(name)
        # Icons can be added later
        self.nav_list.addItem(list_item)
    
    def change_page(self, current_item):
        """Slot to change the visible page in the QStackedWidget."""
        if current_item:
            index = self.nav_list.row(current_item)
            self.stacked_widget.setCurrentIndex(index)