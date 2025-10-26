# ===== IMPORTS & DEPENDENCIES =====
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QFrame
from PyQt6.QtCore import Qt

# ===== UI & APPLICATION LOGIC =====
class WelcomePage(QWidget):
    def __init__(self, version="N/A"):
        super().__init__()
        self.version = version
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setReadOnly(True)
        self.text_browser.setFrameShape(QFrame.Shape.NoFrame)
        
        # HTML content is completely redesigned to match the user's image
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Tahoma', 'Vazirmatn', sans-serif;
                    direction: rtl;
                    background-color: #FFFFFF;
                    color: #333;
                    margin: 40px;
                    text-align: center;
                }}
                h1 {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #003366; /* Navy Blue */
                    margin-top: 50px;
                    margin-bottom: 20px;
                }}
                h2 {{
                    font-size: 18px;
                    font-weight: normal;
                    color: #555;
                    margin-top: 0;
                    margin-bottom: 50px;
                }}
                p {{
                    font-size: 16px;
                    line-height: 2.2; /* Increased line spacing for readability */
                    color: #444;
                    max-width: 700px; /* Constrain width for better readability */
                    margin: 15px auto; /* Center the paragraphs */
                }}
                b {{
                    color: #003366; /* Match the title color for emphasis */
                }}
                .version {{
                    position: absolute;
                    bottom: 20px;
                    left: 0;
                    right: 0;
                    font-size: 14px;
                    color: #AAAAAA;
                }}
            </style>
        </head>
        <body>
            <h1>OptiWise</h1>

            <h2>سیستم هوشمند پشتیبانی تصمیم</h2>

            <p>
                این نرم‌افزار برای بهینه‌سازی منابع و ارزیابی عملکرد واحدهای مختلف طراحی شده است. با استفاده از یک ابزار تحلیلی قدرتمند
                این نرم‌افزار به شما کمک می‌کند تا با استفاده از تکنیک‌های پیشرفته علم داده مانند <b>تحلیل خوشه‌بندی و تحلیل پوششی داده‌ها</b> 
                تصمیمات داده-محور و هوشمندانه‌تری اتخاذ نمایید.
            </p>
            <p>
                برای شروع، از منوی سمت راست، ماژول تحلیلی مورد نظر خود را انتخاب کنید.
            </p>

            <p class="version">نسخه {self.version}</p>
        </body>
        </html>
        """
        self.text_browser.setHtml(html_content)
        layout.addWidget(self.text_browser)

    def show_expiration_message(self, message: str):
        """
        Updates the welcome page to display an expiration message using styled HTML.
        """
        formatted_message = message.replace('\n', '<br>')
        
        expired_html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Tahoma', 'Vazirmatn';
                    direction: rtl;
                    background-color: #FFFFFF;
                    color: #333;
                    margin: 40px;
                    text-align: center;
                }}
                .container {{
                    max-width: 600px;
                    margin: auto;
                    padding-top: 50px;
                }}
                h1 {{ font-size: 32px; color: #D32F2F; margin-bottom: 30px; }}
                .alert {{
                    background-color: #FFF1F0;
                    color: #D32F2F;
                    border: 1px solid #FFCCC7;
                    padding: 20px;
                    border-radius: 8px;
                    font-size: 16px;
                    line-height: 1.8;
                }}
                .version {{
                    position: absolute;
                    bottom: 20px;
                    left: 0;
                    right: 0;
                    font-size: 14px;
                    color: #AAAAAA;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>نسخه برنامه منقضی شده است</h1>
                <div class="alert">
                    {formatted_message}
                </div>
                <p class="version">نسخه {self.version}</p>
            </div>
        </body>
        </html>
        """
        self.text_browser.setHtml(expired_html_content)