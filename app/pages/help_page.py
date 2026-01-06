# ===== SECTION BEING MODIFIED: app/pages/help_page.py =====
# file: app/pages/help_page.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt6.QtCore import Qt
# --- MODIFIED: Import BasePage ---
from .utils import BasePage

# --- MODIFIED: Inherit from BasePage instead of QWidget ---
class HelpPage(BasePage):
    def __init__(self):
        super().__init__()
        # --- MODIFIED: Use self.content_layout provided by BasePage ---
        # The line `layout = QVBoxLayout(self)` is no longer needed.
        
        text_browser = QTextBrowser()
        text_browser.setReadOnly(True)
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml(self.get_help_html())

        # --- MODIFIED: Add the widget to the content_layout ---
        self.content_layout.addWidget(text_browser)
        # The line `self.setLayout(layout)` is no longer needed.

    def get_help_html(self):
        return"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: 'Vazirmatn', 'Tahoma', sans-serif; 
            font-size: 15px; 
            line-height: 2; 
            color: #333;
            background-color: #fdfdfd;
            text-align: justify; /* Justified text */
        }
        h1 { 
            color: #2c3e50; 
            font-size: 26px;
            text-align: center;
            border-bottom: 3px solid #E6AD30;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        h2 { 
            color: #1A3E6E; 
            font-size: 22px;
            border-bottom: 1px solid #bdc3c7; 
            padding-bottom: 10px;
            margin-top: 40px;
        }
        h3 { 
            color: #2980b9; 
            font-size: 18px;
            margin-top: 30px;
            font-weight: bold;
        }
        p { 
            margin-bottom: 15px;
        }
        ul, ol { 
            padding-right: 25px;
            margin-bottom: 20px;
        }
        li {
            margin-bottom: 12px;
        }
        strong {
            color: #c0392b;
        }
        code { 
            background-color: #ecf0f1; 
            padding: 2px 6px; 
            border-radius: 4px; 
            font-family: 'Consolas', 'Courier New', monospace;
            color: #2c3e50;
            border: 1px solid #bdc3c7;
        }
        .note {
            background-color: #eaf5ff;
            border-right: 5px solid #3498db;
            padding: 20px;
            margin: 25px 0;
            border-radius: 6px;
        }
    </style>
</head>
<body>
    <h1>راهنمای کاربری نرم‌افزار OptiWise</h1>
    <div class="note">
        <strong>نام OptiWise به چه معناست؟</strong><br>
        این نام از ترکیب دو واژه <b>Opti</b> (برگرفته از Optimize به معنای بهینه‌سازی) و <b>Wise</b> (به معنای خردمندانه) ساخته شده است. هدف این نرم‌افزار، کمک به شما برای گرفتن <b>تصمیمات خردمندانه</b> از طریق <b>بهینه‌سازی</b> و تحلیل کارایی است.
    </div>

    <h2>بخش اول: مفاهیم علمی و الگوریتم‌ها</h2>
    <p>این بخش به ترتیب منوی نرم‌افزار، مفاهیم و روش‌های استفاده شده را توضیح می‌دهد.</p>

    <h3>۱. تحلیل خوشه‌بندی (Clustering)</h3>
    <ul>
        <li><strong>هدف:</strong> گروه‌بندی واحدهای مشابه برای مقایسه دقیق‌تر (مقایسه همگن).</li>
        <li><strong>الگوریتم‌های مورد استفاده:</strong>
            <ul>
                <li><code>K-Means</code>: خوشه‌بندی بر اساس میانگین (مرکز ثقل) خوشه‌ها.</li>
                <li><code>K-Medoids</code>: استفاده از نماینده واقعی هر خوشه (مقاوم در برابر داده‌های پرت).</li>
                <li><code>Ward</code>: روش سلسله‌مراتبی برای ایجاد خوشه‌های فشرده.</li>
            </ul>
        </li>
    </ul>

    <h3>۲. محاسبه بهره‌وری واحدی (DEA)</h3>
    <ul>
        <li><strong>هدف:</strong> محاسبه میزان کارایی هر واحد نسبت به منابع مصرفی.</li>
        <li><strong>مدل مورد استفاده:</strong>
            <ul>
                <li><strong>مدل SBM (Slack-Based Model):</strong> مدلی پیشرفته که علاوه بر امتیاز کارایی، میزان دقیق کمبودها (Slacks) در ورودی‌ها را محاسبه می‌کند.</li>
            </ul>
        </li>
    </ul>

    <h3>۳. تخصیص بهینه منابع (بودجه و تجهیزات)</h3>
    <ul>
        <li><strong>هدف:</strong> تعیین میزان منابع مورد نیاز بر اساس بهره‌وری نیروی انسانی.</li>
        <li><strong>روش کار:</strong> این بخش با استفاده از خروجی‌های بخش "بهره‌وری نیروی انسانی"، میزان بودجه و تجهیزات بهینه برای هر واحد را پیشنهاد می‌دهد.</li>
    </ul>

    <h3>۴. رتبه‌بندی واحدها</h3>
    <ul>
        <li><strong>مدل:</strong> <strong>Super-Efficiency (ابرکارایی)</strong></li>
        <li><strong>کاربرد:</strong> این مدل به واحدهای کارا اجازه می‌دهد امتیازی بیشتر از ۱ کسب کنند تا بتوان آن‌ها را رتبه‌بندی کرد.</li>
    </ul>
    
    <h3>۵. بهره‌وری نیروی انسانی</h3>
    <ul>
        <li><strong>مدل:</strong> <strong>BCC</strong></li>
        <li><strong>کاربرد:</strong> ارزیابی عملکرد پرسنل با در نظر گرفتن بازده متغیر نسبت به مقیاس (مناسب برای مقایسه افراد با سوابق مختلف).</li>
    </ul>

    <h3>۶. پیش‌بینی نیروی انسانی</h3>
    <ul>
        <li><strong>مدل:</strong> <strong>سری زمانی (Time Series)</strong></li>
        <li><strong>کاربرد:</strong> پیش‌بینی تعداد نیروی مورد نیاز برای سال آینده. این مدل نیازمند داده‌های تاریخی حداقل <strong>۵ سال گذشته</strong> است تا بتواند روند تغییرات را شناسایی کند.</li>
    </ul>

    <h2>بخش دوم: راهنمای گام‌به‌گام با نرم‌افزار</h2>

    <h3>ماژول ۱: تحلیل خوشه‌بندی</h3>
    <ol>
        <li>فایل اکسل داده‌ها را بارگذاری کنید.</li>
        <li>شاخص‌های مورد نظر را انتخاب کنید.</li>
        <li>دکمه <strong>"تحلیل خوشه‌بندی"</strong> را بزنید.</li>
        <li>نتایج و بهترین الگوریتم به شما نمایش داده می‌شود.</li>
    </ol>

    <h3>ماژول ۲: محاسبه بهره‌وری واحدی</h3>
    <ol>
        <li>فایل داده‌های ورودی و خروجی واحدها را بارگذاری کنید.</li>
        <li>ورودی‌ها و خروجی‌ها را مشخص کنید.</li>
        <li>دکمه <strong>"محاسبه بهره‌وری واحدی"</strong> را بزنید.</li>
        <li>می‌توانید نتایج را به تفکیک خوشه‌های ایجاد شده در مرحله قبل مشاهده کنید.</li>
    </ol>

    <h3>ماژول ۳: تخصیص بهینه منابع</h3>
    <p>این بخش نیاز به اجرای قبلی "بهره‌وری نیروی انسانی" دارد. پس از اجرا، نتایج تخصیص بودجه و تجهیزات در تب‌های مختلف نمایش داده می‌شود.</p>

    <h3>ماژول ۴: رتبه‌بندی واحدها</h3>
    <ol>
        <li>فایل داده‌ها را بارگذاری و شاخص‌ها را انتخاب کنید.</li>
        <li>دکمه اجرا را بزنید تا رتبه‌بندی دقیق واحدها بر اساس مدل ابرکارایی نمایش داده شود.</li>
    </ol>
    
    <h3>ماژول ۵: بهره‌وری نیروی انسانی</h3>
    <ol>
        <li>فایل اطلاعات پرسنلی را بارگذاری کنید.</li>
        <li>شاخص‌های ورودی (مثل سابقه) و خروجی (مثل عملکرد) را انتخاب کنید.</li>
        <li>نتیجه بهره‌وری هر فرد محاسبه می‌شود.</li>
    </ol>

    <h3>ماژول ۶: پیش‌بینی نیروی انسانی</h3>
    <ol>
        <li>فایل داده‌های ۵ سال گذشته را وارد کنید (ستون سال الزامی است).</li>
        <li>شاخص مورد نظر برای پیش‌بینی را انتخاب کنید.</li>
        <li>نرم‌افزار مقدار سال آینده را پیش‌بینی می‌کند.</li>
    </ol>
</body>
</html>
"""