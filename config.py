import os
# Removed dotenv loading since token is hardcoded

# Telegram Bot Token
TELEGRAM_TOKEN = "8200047179:AAEy-8qPtxFy4TmznGE6BywR5pEpI_g644o"
# TELEGRAM_TOKEN = "8421954162:AAEpPfhw61cCy60Ql_deD-ToEBJvbZ3r7_o"
# Database Settings
DATABASE_PATH = "invoice_bot.db"

# Warehouse Manager Settings
WAREHOUSE_MANAGER_ID = 6842382908  # معرف مدير المخزن الرئيسي
WAREHOUSE_MANAGER_ID_2 = 1801438595  # معرف مدير المخزن الثاني
WAREHOUSE_MANAGER_ID_3 = 1849001861  # معرف مدير المخزن الثالث
AUTO_SEND_REPORTS = True  # إرسال التقارير تلقائياً
REPORT_INTERVAL_HOURS = 24  # كل 24 ساعة
# Shipping Template File
SHIPPING_TEMPLATE_FILE = "rocklis.xls"

# Allowed Users (Telegram User IDs)
ALLOWED_USERS = {788101322, 6842382908, 1801438595, 5808690567, 1849001861, 5368965836, 1871428204, 844380852, 1334676785}  # يمكن إضافة المزيد من الموظفين هنا

# API Settings
API_ENABLED = True  # تفعيل/إلغاء تفعيل إرسال الطلبات إلى API
API_BASE_URL = "https://rocklis.com/api/v1/admin/order/create"
API_USERNAME = "admin"  # اسم المستخدم للـ API
API_PASSWORD = "admin123"  # كلمة المرور للـ API
API_TIMEOUT = 30  # مهلة الاتصال بالثواني

# Bot States
MAIN_MENU = 0
ADD_INVOICE = 1
EMPLOYEE_NAME = 2
CLIENT_NAME = 3
GOVERNORATE = 4
NEAREST_POINT = 5
PHONE_NUMBER = 6
QUANTITY = 7
PRICE = 8
NOTES = 9
STATISTICS = 10 