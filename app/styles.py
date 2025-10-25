# ===== IMPORTS & DEPENDENCIES =====
def load_stylesheet():
    """Return the QSS stylesheet for the application."""
    return """
        /* ... Global Styles, QMainWindow, QGroupBox ... */
        QWidget {
            background-color: #FDFBF5; color: #333333; font-family: Arial, sans-serif;
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

        /* ... Navigation List ... */
        QListWidget {
            border: none; background-color: #1A3E6E; padding: 10px 0px;
        }
        QListWidget::item {
            padding: 12px 20px; color: #FFFFFF; border-bottom: 1px solid #2B508A;
        }
        QListWidget::item:hover { background-color: #2B508A; }
        QListWidget::item:selected {
            background-color: #E6AD30; color: #1A3E6E; font-weight: bold;
        }

        /* ... Buttons ... */
        QPushButton {
            background-color: #1A3E6E; color: #FFFFFF; border-radius: 5px;
            padding: 10px 15px; font-size: 14px; font-weight: bold; border: none;
        }
        QPushButton:hover { background-color: #2B508A; }
        QPushButton:pressed { background-color: #122C4D; }

        /* --- CheckBox Styling for RTL --- */
        QCheckBox {
            spacing: 5px; /* Space between checkbox and text */
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
            border: 1px solid #D0D0D0; gridline-color: #E0E0E0;
            background-color: #FFFFFF;
        }
        
        QHeaderView::section {
            background-color: #E8ECF1; padding: 8px;
            border: 1px solid #D0D0D0; font-weight: bold;
        }
        
        /* --- NEW: Sorting Indicator Style --- */
        QHeaderView::down-arrow {
            image: url(./assets/icons/down_arrow.png);
            width: 16px;
            height: 16px;
        }

        QHeaderView::up-arrow {
            image: url(./assets/icons/up_arrow.png);
            width: 16px;
            height: 16px;
        }

        /* --- Global Item Alignment for Tables --- */
        QTableView::item {
            text-align: center; /* Center-aligns the text in all table cells */
        }

        /* ... ScrollBar ... */
        QScrollBar:vertical {
            border: none; background: #E8ECF1; width: 10px; margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #B0B8C0; min-height: 20px; border-radius: 5px;
        }
    """