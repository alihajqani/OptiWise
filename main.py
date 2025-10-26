import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app.main_window import MainWindow

__version__ = "0.10.0"

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set Right-to-Left layout for Persian UI
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    # Launch main window with version
    main_window = MainWindow(__version__)
    main_window.show()

    sys.exit(app.exec())