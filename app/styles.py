# ===== SECTION BEING MODIFIED: app/styles.py =====
# ===== IMPORTS & DEPENDENCIES =====
# (No imports needed for this file, just string return)

def load_stylesheet():
    """Return the QSS stylesheet for the application with updated visual requirements."""
    return """
        /* --- Global Settings & Fonts --- */
        QWidget {
            background-color: #FDFBF5; 
            color: #333333; 
            font-family: 'Vazirmatn', 'Tahoma', 'Segoe UI', sans-serif;
            font-size: 14px;
        }
        
        /* --- Main Window --- */
        QMainWindow, QDialog { background-color: #FDFBF5; }

        /* --- Dashboard Header & Footer --- */
        QWidget#HeaderContainer {
            background-color: #1A3E6E; /* Navy Blue */
        }

        QLabel#HeaderTitle {
            color: #FFFFFF;
            font-size: 36px;
            font-weight: bold;
            background-color: transparent;
        }
        
        QLabel#HeaderSubtitle {
            color: #E6AD30; /* Gold Accent */
            font-size: 18px;
            background-color: transparent;
        }

        QWidget#FooterContainer {
            background-color: #FFFFFF;
            border-top: 1px solid #E0E0E0;
        }
        
        QLabel#FooterLabel {
            font-size: 12px;
            color: #999999;
            background-color: transparent;
        }

        /* --- Group Boxes --- */
        QGroupBox {
            border: 2px solid #D0D0D0; 
            border-radius: 8px; 
            margin-top: 25px;
            font-weight: bold; 
            font-size: 15px;
            color: #1A3E6E;
        }
        QGroupBox::title {
            subcontrol-origin: margin; 
            subcontrol-position: top right;
            padding: 0 10px; 
            background-color: #FDFBF5;
            right: 20px;
        }

        /* --- Page Top Bar & Back Button --- */
        QWidget#PageTopBar {
            background-color: #1A3E6E; /* Navy Blue Background */
            border-bottom: 2px solid #E6AD30; /* Gold Border */
        }
        
        QPushButton#BackButton {
            background-color: transparent;
            color: #FFFFFF; /* White Text */
            border: 1px solid #FFFFFF;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 6px;
        }
        QPushButton#BackButton:hover {
            background-color: #E6AD30; /* Gold Background on Hover */
            color: #1A3E6E; /* Navy Text on Hover */
            border-color: #FFFFFF;
        }

        /* --- Dashboard Card Styles --- */
        QFrame#ActionCard {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 12px;
        }
        
        QFrame#ActionCard:hover {
            border: 2px solid #1A3E6E;
            background-color: #F8FAFC;
        }
        
        QFrame#ActionCard:disabled {
            background-color: #F5F5F5;
        }
        
        QLabel#CardTitle {
            font-size: 16px;
            font-weight: bold;
            color: #1A3E6E;
            background-color: transparent;
        }

        QLabel#CardTitle:disabled {
            color: #999999;
        }
        
        /* --- General Buttons --- */
        QPushButton {
            background-color: #1A3E6E; 
            color: #FFFFFF; 
            border-radius: 6px;
            padding: 12px 20px; 
            font-size: 14px; 
            font-weight: bold; 
            border: 1px solid #0d2445;
        }
        QPushButton:hover { 
            background-color: #2B508A; 
            border-color: #E6AD30;
        }
        QPushButton:pressed { 
            background-color: #122C4D; 
            margin-top: 1px;
        }

        /* --- Table Views --- */
        QTableView {
            border: 1px solid #D0D0D0; 
            gridline-color: #E0E0D0;
            background-color: #FFFFFF;
            selection-background-color: #E6AD30;
            selection-color: #1A3E6E;
            font-size: 13px;
        }
        
        QHeaderView::section {
            background-color: #E8ECF1; 
            padding: 10px;
            border: 1px solid #D0D0D0; 
            font-weight: bold;
            font-size: 13px;
            color: #1A3E6E;
        }

        /* --- ScrollBar --- */
        QScrollBar:vertical {
            border: none; background: #E8ECF1; width: 12px; margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #B0B8C0; min-height: 20px; border-radius: 6px;
        }
    """