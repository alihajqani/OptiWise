# ===== IMPORTS & DEPENDENCIES =====
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# ===== CONFIGURATION & CONSTANTS =====
__version__ = "0.1.0"

# ===== CORE BUSINESS LOGIC & UI =====
class WelcomeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"My PyQt App v{__version__}")
        self.resize(400, 200)
        
        welcome_label = QLabel("Welcome to the Application!", self)
        welcome_label.setFont(QFont("Arial", 16))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout = QVBoxLayout()
        layout.addWidget(welcome_label)
        
        self.setLayout(layout)

# ===== INITIALIZATION & STARTUP =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = WelcomeApp()
    main_window.show()
    sys.exit(app.exec())