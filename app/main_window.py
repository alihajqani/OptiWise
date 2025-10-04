# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem
from .styles import load_stylesheet
from .pages.welcome_page import WelcomePage
# Import other pages here as you create them
# from .pages.clustering_page import ClusteringPage
# from .pages.ranking_page import RankingPage

# ===== CORE UI STRUCTURE =====
class MainWindow(QMainWindow):
    def __init__(self, version):
        super().__init__()
        self.version = version
        self.setWindowTitle(f"Decision Support System v{self.version}")
        self.setGeometry(100, 100, 1000, 700) # x, y, width, height
        
        # Apply the custom stylesheet
        self.setStyleSheet(load_stylesheet())
        
        # --- Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Navigation Panel (Left Side) ---
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(200)
        main_layout.addWidget(self.nav_list)

        # --- Content Panel (Right Side) ---
        # QStackedWidget is like a deck of cards, we show one page at a time
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # --- Setup Pages ---
        self.setup_pages()

        # --- Connect Signals ---
        self.nav_list.currentItemChanged.connect(self.change_page)

    def setup_pages(self):
        """Creates pages and adds them to the navigation and stacked widget."""
        # Page 1: Welcome
        self.welcome_page = WelcomePage()
        self.add_page(self.welcome_page, "صفحه اصلی", "home_icon.png") # Icons can be added later

        # Add placeholders for other pages based on your document
        # self.clustering_page = ClusteringPage()
        # self.add_page(self.clustering_page, "خوشه‌بندی", "cluster_icon.png")
        
        # self.ranking_page = RankingPage()
        # self.add_page(self.ranking_page, "رتبه‌بندی", "rank_icon.png")
        
        # Select the first item by default
        self.nav_list.setCurrentRow(0)

    def add_page(self, widget, name, icon_path=None):
        """A helper function to add a page to both the nav and the stack."""
        self.stacked_widget.addWidget(widget)
        list_item = QListWidgetItem(name)
        # if icon_path:
        #     list_item.setIcon(QIcon(icon_path))
        self.nav_list.addItem(list_item)
    
    def change_page(self, current_item):
        """Slot to change the visible page in the QStackedWidget."""
        index = self.nav_list.row(current_item)
        self.stacked_widget.setCurrentIndex(index)