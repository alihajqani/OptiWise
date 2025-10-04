# ===== STYLING & THEME (QSS) =====

def load_stylesheet():
    """Returns the QSS stylesheet for the application."""
    return """
        QWidget {
            background-color: #F0F2F5; /* Light gray background */
            color: #333333; /* Dark gray text */
            font-family: Arial, sans-serif;
        }

        QMainWindow, QDialog {
            background-color: #FFFFFF;
        }

        /* Style for the navigation list */
        QListWidget {
            border: 1px solid #D0D0D0;
            background-color: #E8ECF1; /* Lighter blue-gray for nav */
            padding: 5px;
        }

        QListWidget::item {
            padding: 10px 5px;
            border-bottom: 1px solid #D0D0D0;
        }

        QListWidget::item:hover {
            background-color: #DDE5ED; /* Slightly darker on hover */
        }

        QListWidget::item:selected {
            background-color: #4A90E2; /* Main blue for selection */
            color: #FFFFFF; /* White text for selected item */
            font-weight: bold;
        }

        /* Style for buttons */
        QPushButton {
            background-color: #4A90E2; /* Main blue */
            color: #FFFFFF;
            border-radius: 5px;
            padding: 10px 15px;
            font-size: 14px;
            border: none;
        }

        QPushButton:hover {
            background-color: #357ABD; /* Darker blue on hover */
        }

        QPushButton:pressed {
            background-color: #2A6496;
        }

        /* Style for labels */
        QLabel#TitleLabel {
            font-size: 24px;
            font-weight: bold;
            color: #2A6496; /* Darker blue for titles */
        }
        
        QLabel#SubtitleLabel {
            font-size: 16px;
            color: #555555;
        }
    """