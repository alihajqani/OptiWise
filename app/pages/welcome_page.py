# ===== SECTION BEING MODIFIED: app/pages/welcome_page.py =====
# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, 
                             QGraphicsDropShadowEffect, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor

# ===== CUSTOM COMPONENTS =====

class ActionCard(QFrame):
    """ A clickable card widget for the main dashboard. """
    clicked = pyqtSignal(int) # Emits the page index when clicked

    def __init__(self, page_index, title, icon_path):
        super().__init__()
        self.page_index = page_index
        self.setObjectName("ActionCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(240, 180)

        # Shadow Effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(15)

        # Icon
        self.icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            self.icon_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.icon_label.setText("💠") # Fallback
            self.icon_label.setStyleSheet("font-size: 48px;")
        
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("CardTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)

        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.title_label)
    
    def mousePressEvent(self, event):
        if self.isEnabled() and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.page_index)
            super().mousePressEvent(event)

# ===== MAIN WELCOME PAGE (DASHBOARD) =====
class WelcomePage(QWidget):
    page_selected = pyqtSignal(int)

    def __init__(self, version="N/A", pages_info=None):
        super().__init__()
        self.version = version
        self.pages_info = pages_info or []
        self.cards = [] # To keep track of card widgets
        self.initUI()

    def initUI(self):
        # Main layout divided into Header, Content, Footer
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

    # --- 1. HEADER SECTION ---
        header_container = QWidget()
        header_container.setObjectName("HeaderContainer")
        header_container.setFixedHeight(150)
        
        header_layout = QVBoxLayout(header_container)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setSpacing(5)

        title_label = QLabel("OptiWise")
        title_label.setObjectName("HeaderTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # --- FIX: Center the text inside the label ---
        
        subtitle_label = QLabel("سیستم هوشمند پشتیبانی تصمیم")
        subtitle_label.setObjectName("HeaderSubtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # --- FIX: Center the text inside the label ---
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        self.main_layout.addWidget(header_container)

        # --- 2. CONTENT SECTION (SCROLLABLE GRID) ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Grid Layout for Navigation Cards
        grid_layout = QGridLayout()
        grid_layout.setSpacing(30)
        grid_layout.setContentsMargins(50, 50, 50, 50) # Added top margin for spacing from header
        
        row, col = 0, 0
        max_cols = 4

        for index, page in enumerate(self.pages_info):
            if index == 0: continue

            card = ActionCard(index, page["name"], page["icon"])
            card.clicked.connect(self.page_selected.emit)
            self.cards.append(card)
            grid_layout.addWidget(card, row, col, Qt.AlignmentFlag.AlignCenter)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        content_layout.addLayout(grid_layout)
        scroll_area.setWidget(content_widget)
        self.main_layout.addWidget(scroll_area)

        # --- 3. FOOTER SECTION ---
        footer_container = QWidget()
        footer_container.setObjectName("FooterContainer")
        footer_container.setFixedHeight(50)
        
        footer_layout = QHBoxLayout(footer_container)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        developer_label = QLabel("توسعه‌دهنده: الهه معمار مسجد")
        developer_label.setObjectName("FooterLabel")
        
        footer_layout.addWidget(developer_label)
        
        self.main_layout.addWidget(footer_container)

    def disable_all_cards(self):
        """Disables all navigation cards."""
        for card in self.cards:
            card.setEnabled(False)
            card.setToolTip("این نسخه منقضی شده است")
            card.setCursor(Qt.CursorShape.ForbiddenCursor)

    def show_expiration_message(self, message: str):
        """Disables cards and shows an expiration message below the header."""
        self.disable_all_cards()
        
        expiry_label = QLabel(f"نسخه برنامه منقضی شده است\n{message}")
        expiry_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        expiry_label.setStyleSheet("font-size: 16px; color: #D32F2F; background-color: #FFF1F0; border: 1px solid #FFCCC7; padding: 15px; border-radius: 8px; margin: 20px 50px;")
        
        # Insert the message between the header (index 0) and content (index 1)
        self.main_layout.insertWidget(1, expiry_label)