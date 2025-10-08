from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class WelcomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25) # Add some padding
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center the content vertically

        title = QLabel("سیستم هوشمند پشتیبانی تصمیم")
        title.setObjectName("TitleLabel")
        # Align the text inside the label to the right
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("برای شروع، یکی از گزینه‌ها را از منوی کنار انتخاب کنید.")
        subtitle.setObjectName("SubtitleLabel")
        # Align the text inside the label to the right
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch() # Add spacer to push content up
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch() # Add spacer to push content down

        self.setLayout(layout)