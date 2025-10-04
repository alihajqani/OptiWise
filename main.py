# ===== IMPORTS & DEPENDENCIES =====
import sys
from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow

# ===== CONFIGURATION & CONSTANTS =====
__version__ = "0.3.0"

# ===== INITIALIZATION & STARTUP =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Pass the version to the main window
    main_window = MainWindow(__version__)
    main_window.show()
    
    sys.exit(app.exec())