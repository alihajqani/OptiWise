from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem
from .styles import load_stylesheet
from .pages.welcome_page import WelcomePage
from .pages.clustering_page import ClusteringPage
from .pages.efficiency_page import EfficiencyPage

class MainWindow(QMainWindow):
    def __init__(self, version):
        super().__init__()
        self.version = version
        self.setWindowTitle(f"OptiWise - Decision Support System v{self.version}")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(load_stylesheet())
        self.latest_clustering_data = None

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
        self.welcome_page = WelcomePage()
        self.add_page(self.welcome_page, "صفحه اصلی")

        self.clustering_page = ClusteringPage()
        self.clustering_page.analysis_completed.connect(self.update_clustering_data)
        self.add_page(self.clustering_page, "تحلیل خوشه‌بندی")

        self.efficiency_page = EfficiencyPage()
        self.add_page(self.efficiency_page, "محاسبه بهره‌وری")
        
        self.nav_list.setCurrentRow(0)

    def add_page(self, widget, name):
        self.stacked_widget.addWidget(widget)
        self.nav_list.addItem(QListWidgetItem(name))
    
    def change_page(self, current_item):
        if current_item:
            index = self.nav_list.row(current_item)
            self.stacked_widget.setCurrentIndex(index)
            if self.stacked_widget.widget(index) == self.efficiency_page:
                self.efficiency_page.update_with_clustering_data(self.latest_clustering_data)
    
    def update_clustering_data(self, data):
        self.latest_clustering_data = data
        if self.stacked_widget.currentWidget() == self.efficiency_page:
            self.efficiency_page.update_with_clustering_data(self.latest_clustering_data)