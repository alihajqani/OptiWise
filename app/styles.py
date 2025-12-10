# ===== SECTION BEING MODIFIED: styles.py =====
# ===== IMPORTS & DEPENDENCIES =====
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

        /* --- Modern Navigation Bar Styles (Sidebar) --- */
        #NavBar {
            background-color: #1A3E6E;
            border-left: 1px solid #122C4D;
        }
        
        /* Sidebar Buttons - 3D Key Look */
        #NavBar QToolButton {
            color: #FFFFFF;
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2B508A, stop:1 #1A3E6E);
            border: 1px solid #0d2445;
            border-radius: 8px; 
            margin: 6px 0px; /* Reduced side margin inside layout, relying on padding */
            
            /* --- MODIFIED: Adjusted padding to ensure text fits --- */
            padding: 10px 15px; 
            
            font-size: 15px;
            font-weight: bold;
            text-align: right; /* Ensure text aligns right next to icon */
        }

        #NavBar QToolButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3E64A3, stop:1 #2B508A);
            border: 1px solid #E6AD30;
        }

        #NavBar QToolButton:checked {
            background-color: #E6AD30; /* Active State Gold */
            color: #1A3E6E;
            border: 1px solid #FFFFFF;
        }
        
        #NavBar QToolButton:disabled {
            color: #A0A0A0;
            background-color: #122C4D;
            border: 1px solid #000;
        }

        /* Remove Dotted Focus Border */
        QToolButton:focus, QPushButton:focus, QTableView:focus {
            outline: none;
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
            margin-top: 1px; /* Click effect */
        }
        
        /* --- Specific Buttons (Optional) --- */
        QPushButton#ExportButton {
            background-color: #27ae60;
        }
        QPushButton#ExportButton:hover {
            background-color: #2ecc71;
        }

        /* --- CheckBox Styling for RTL --- */
        QCheckBox {
            spacing: 8px;
            font-size: 14px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }

        /* --- Labels --- */
        QLabel#TitleLabel {
            font-size: 24px; 
            font-weight: bold; 
            color: #1A3E6E; 
            padding: 10px 0 20px 0;
            border-bottom: 2px solid #E6AD30;
            margin-bottom: 15px;
        }
        QLabel { 
            font-size: 14px; 
            color: #333; 
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

        /* --- ScrollBar --- */
        QScrollBar:vertical {
            border: none; background: #E8ECF1; width: 12px; margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #B0B8C0; min-height: 20px; border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover {
            background: #1A3E6E;
        }
    """