# ===== IMPORTS & DEPENDENCIES =====
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt # Import Qt for LayoutDirection
from app.main_window import MainWindow

# ===== CONFIGURATION & CONSTANTS =====
__version__ = "0.5.0"

# ===== INITIALIZATION & STARTUP =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # --- Right-to-Left (RTL) Configuration ---
    # This is the single most important change for a Persian UI.
    # It reverses the layout direction for the entire application.
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    # Pass the version to the main window
    main_window = MainWindow(__version__)
    main_window.show()
    
    sys.exit(app.exec())