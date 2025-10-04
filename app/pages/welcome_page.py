from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class WelcomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        title = QLabel("سیستم هوشمند پشتیبانی تصمیم")
        title.setObjectName("TitleLabel") # For styling
        
        subtitle = QLabel("برای شروع، یکی از گزینه‌ها را از منوی کنار انتخاب کنید.")
        subtitle.setObjectName("SubtitleLabel")
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        self.setLayout(layout)