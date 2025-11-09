# ===== IMPORTS & DEPENDENCIES =====
def load_stylesheet():
    """Return the QSS stylesheet for the application."""
    return """
        /* ... Global Styles, QMainWindow, QGroupBox ... */
        QWidget {
            background-color: #FDFBF5; color: #333333; font-family: Tahoma, Arial, sans-serif;
        }
        QMainWindow, QDialog { background-color: #FDFBF5; }
        QGroupBox {
            border: 1px solid #D0D0D0; border-radius: 8px; margin-top: 10px;
            font-weight: bold; color: #1A3E6E;
        }
        QGroupBox::title {
            subcontrol-origin: margin; subcontrol-position: top right;
            padding: 0 10px; background-color: #FDFBF5;
        }

        /* --- Modern Navigation Bar Styles --- */
        #NavBar {
            background-color: #1A3E6E;
        }
        
        #NavBar QToolButton {
            color: #FFFFFF;
            background-color: transparent;
            border: none;
            border-radius: 0px; 
            /* --- UPDATED: Increased right padding to create space next to the icon --- */
            padding: 15px 30px 15px 20px; /* top, right, bottom, left */
            font-size: 14px;
            font-weight: bold;
            text-align: right;
            border-bottom: 1px solid #2B508A;
        }

        #NavBar QToolButton:hover {
            background-color: #2B508A;
        }

        #NavBar QToolButton:checked {
            background-color: #E6AD30;
            color: #1A3E6E;
        }
        
        #NavBar QToolButton:disabled {
            color: #708090;
            background-color: transparent;
        }
        
        #NavBar QToolButton:last-child {
            border-bottom: none;
        }


        /* ... Buttons ... */
        QPushButton {
            background-color: #1A3E6E; color: #FFFFFF; border-radius: 5px;
            padding: 10px 15px; font-size: 14px; font-weight: bold; border: none;
            cursor: pointer;
        }
        QPushButton:hover { background-color: #2B508A; }
        QPushButton:pressed { background-color: #122C4D; }

        /* --- CheckBox Styling for RTL --- */
        QCheckBox {
            spacing: 5px;
        }
        QCheckBox::indicator {
            width: 15px;
            height: 15px;
        }

        /* ... Labels ... */
        QLabel#TitleLabel {
            font-size: 28px; font-weight: bold; color: #1A3E6E; padding-bottom: 10px;
        }
        QLabel#SubtitleLabel { font-size: 16px; color: #555555; }
        
        /* --- Table Views --- */
        QTableView {
            border: 1px solid #D0D0D0; gridline-color: #E0E0D0;
            background-color: #FFFFFF;
        }
        
        QHeaderView::section {
            background-color: #E8ECF1; padding: 8px;
            border: 1px solid #D0D0D0; font-weight: bold;
        }
        
        /* --- Sorting Indicator Style --- */
        QHeaderView::down-arrow {
            image: url(./assets/icons/down_arrow.png);
            width: 16px; height: 16px;
        }
        QHeaderView::up-arrow {
            image: url(./assets/icons/up_arrow.png);
            width: 16px; height: 16px;
        }

        /* --- Global Item Alignment for Tables --- */
        QTableView::item {
            padding: 5px;
            text-align: center;
        }

        /* ... ScrollBar ... */
        QScrollBar:vertical {
            border: none; background: #E8ECF1; width: 10px; margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #B0B8C0; min-height: 20px; border-radius: 5px;
        }
    """