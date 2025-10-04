# ===== IMPORTS & DEPENDENCIES =====
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,       # We need QPushButton for the new button
    QMessageBox        # A simple dialog box for the 'About' message
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# ===== CONFIGURATION & CONSTANTS =====
# Bumping the version to 0.2.0 for the new feature release.
__version__ = "0.2.0"

# ===== CORE BUSINESS LOGIC & UI =====
class WelcomeApp(QWidget):
    """
    Main application window, now with an 'About' button.
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"My PyQt App v{__version__}")
        self.resize(400, 250) # Increased height a bit for the button

        # --- Create Widgets ---
        welcome_label = QLabel("Welcome to the Application!", self)
        welcome_label.setFont(QFont("Arial", 16))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create the new 'About' button
        self.about_button = QPushButton("About", self)
        self.about_button.setFont(QFont("Arial", 10))

        # --- Layout Management ---
        # A vertical layout is perfect for stacking the label and button.
        layout = QVBoxLayout()
        layout.addWidget(welcome_label) # Add label to layout
        layout.addWidget(self.about_button)   # Add button to layout
        
        self.setLayout(layout)

        # --- Signal and Slot Connection ---
        # Connect the button's 'clicked' signal to our custom method.
        self.about_button.clicked.connect(self.show_about_dialog)

    def show_about_dialog(self):
        """
        This method is called when the 'About' button is clicked.
        It displays a simple message box with version information.
        """
        title = "About This Application"
        text = f"""
        <b>My PyQt App</b><br>
        Version: {__version__}<br><br>
        A simple application built with Python and PyQt6.
        """
        # Using a standard QMessageBox is the idiomatic way to show 'About' info.
        QMessageBox.about(self, title, text)

# ===== INITIALIZATION & STARTUP =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = WelcomeApp()
    main_window.show()
    sys.exit(app.exec())