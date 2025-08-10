import os
import asyncio
import schedule
import time
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, filters, ContextTypes, CallbackQueryHandler
)
from telegram.error import TimedOut, NetworkError, RetryAfter, Conflict
import config
from database_manager import DatabaseManager

# تهيئة مدير قاعدة البيانات
db_manager = DatabaseManager()

# Bot States
MAIN_MENU = 1
ADD_INVOICE_SINGLE = 2
ADMIN_MENU = 3
STATISTICS = 10
STATISTICS_DATE_SELECTION = 16
STATISTICS_EXPORT = 17
ALL_EMPLOYEES_DATE_SELECTION = 18
USER_MANAGEMENT_MENU = 20
ADD_USER_ROLE = 21
ADD_USER_DATA = 22
STATISTICS_PASSWORD = 23
PASSWORD_MANAGEMENT = 24
RETURNS_MENU = 25
RETURN_INVOICE_SELECTION = 26
RETURN_TYPE_SELECTION = 27
RETURN_QUANTITY_INPUT = 28
RETURN_REASON_INPUT = 29

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء البوت وعرض القائمة الرئيسية"""
    try:
        user_id = update.message.from_user.id
        if user_id not in config.ALLOWED_USERS:
            await update.message.reply_text("عذرًا، هذا البوت مخصص لموظفي الشركة فقط.")
            return ConversationHandler.END

        # إضافة المستخدم لقاعدة البيانات
        username = update.message.from_user.username or ""
        full_name = update.message.from_user.full_name or ""
        role = "warehouse_manager" if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3] else "employee"
        db_manager.add_user(user_id, username, full_name, role)

        # عرض القائمة المناسبة
        if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
            # قائمة مدير المخزن
            keyboard = [
                ["📝 إضافة فاتورة"],
                ["📊 إحصائياتي"],
                ["📊 إحصائيات بتاريخ محدد"],
                ["📋 تحميل ملف الطلبات"],
                ["👥 إحصائيات الموظفين"],
                ["👥 إحصائيات الموظفين بتاريخ محدد"],
                ["📤 تصدير التقارير"],
                ["🔄 إدارة المرتجعات"],
                ["👤 إدارة المستخدمين"],
                ["🔐 إدارة كلمات المرور"],
                ["⚙️ إعدادات النظام"]
            ]
            await update.message.reply_text(
                "مرحبًا بك في بوت إدارة الفواتير! 🎉\n"
                "أنت مدير المخزن - لديك صلاحيات إضافية\n\n"
                "اختر الخدمة المطلوبة:",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            )
            return ADMIN_MENU
        else:
            # قائمة الموظف العادي
            keyboard = [
                ["📝 إضافة فاتورة"],
                ["📊 إحصائياتي"]
            ]
            await update.message.reply_text(
                "مرحبًا بك في بوت إدارة الفواتير! 🎉\n\n"
                "اختر الخدمة المطلوبة:",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            )
            return MAIN_MENU
    except (TimedOut, NetworkError) as e:
        print(f"خطأ في الاتصال: {e}")
        await update.message.reply_text("⚠️ حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.")
        return ConversationHandler.END
    except Exception as e:
        print(f"خطأ غير متوقع: {e}")
        await update.message.reply_text("❌ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.")
        return ConversationHandler.END

async def admin_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج قائمة مدير المخزن"""
    text = update.message.text
    
    if text == "📝 إضافة فاتورة":
        await update.message.reply_text(
            "📝 إضافة فاتورة جديدة\n\n"
            "الرجاء إرسال جميع البيانات في رسالة واحدة بالترتيب التالي:\n\n"
            "اسم الموظفة /نور\n"
            "أسم العميل/ محمد\n"
            "المحافظة/ الانبار\n"
            "اقرب نقطة دالة / الرمادي\n"
            "الرقم/ 0782444\n"
            "العدد/ 1\n"
            "السعر / 40000\n"
            "الملاحظات/ لاشيئ\n\n"
            "ملاحظة: استخدم / للفصل بين الحقول",
            reply_markup=ReplyKeyboardRemove()
        )
        return ADD_INVOICE_SINGLE
    
    elif text == "📊 إحصائياتي":
        await update.message.reply_text(
            "الرجاء إدخال اسم الموظف لعرض إحصائياته التفصيلية:",
            reply_markup=ReplyKeyboardRemove()
        )
        return STATISTICS
    
    elif text == "📊 إحصائيات بتاريخ محدد":
        await update.message.reply_text(
            "📅 إحصائيات بتاريخ محدد\n\n"
            "الرجاء إدخال اسم الموظف أولاً:",
            reply_markup=ReplyKeyboardRemove()
        )
        return STATISTICS_DATE_SELECTION
    
    elif text == "📋 تحميل ملف الطلبات":
        await download_shipping_file(update, context)
        return await show_admin_menu(update, context)
    
    elif text == "👥 إحصائيات الموظفين":
        await show_all_employees_stats(update, context)
        return await show_admin_menu(update, context)
    
    elif text == "👥 إحصائيات الموظفين بتاريخ محدد":
        await update.message.reply_text(
            "📅 إحصائيات الموظفين بتاريخ محدد\n\n"
            "الرجاء إدخال التاريخ بالشكل التالي:\n"
            "YYYY-MM-DD إلى YYYY-MM-DD\n\n"
            "مثال:\n"
            "2024-01-01 إلى 2024-01-31\n"
            "أو\n"
            "2024-01-01 إلى 2024-12-31",
            reply_markup=ReplyKeyboardRemove()
        )
        return ALL_EMPLOYEES_DATE_SELECTION
    
    elif text == "📤 تصدير التقارير":
        await show_export_menu(update, context)
        return STATISTICS_EXPORT
    
    elif text == "🔄 إدارة المرتجعات":
        return await show_returns_management_menu(update, context)
    
    elif text == "👤 إدارة المستخدمين":
        return await show_user_management_menu(update, context)
    
    elif text == "�� إدارة كلمات المرور":
        return await show_password_management_menu(update, context)
    
    elif text == "⚙️ إعدادات النظام":
        await show_system_settings(update, context)
        return await show_admin_menu(update, context)
    
    else:
        await update.message.reply_text("الرجاء اختيار خيار صحيح من القائمة.")
        return ADMIN_MENU

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج القائمة الرئيسية للموظفين"""
    text = update.message.text
    
    if text == "📝 إضافة فاتورة":
        await update.message.reply_text(
            "📝 إضافة فاتورة جديدة\n\n"
            "الرجاء إرسال جميع البيانات في رسالة واحدة بالترتيب التالي:\n\n"
            "اسم الموظفة /نور\n"
            "أسم العميل/ محمد\n"
            "المحافظة/ الانبار\n"
            "اقرب نقطة دالة / الرمادي\n"
            "الرقم/ 0782444\n"
            "العدد/ 1\n"
            "السعر / 40000\n"
            "الملاحظات/ لاشيئ\n\n"
            "ملاحظة: استخدم / للفصل بين الحقول",
            reply_markup=ReplyKeyboardRemove()
        )
        return ADD_INVOICE_SINGLE
    
    elif text == "📊 إحصائياتي":
        await update.message.reply_text(
            "الرجاء إدخال اسم الموظف لعرض إحصائياته التفصيلية:",
            reply_markup=ReplyKeyboardRemove()
        )
        return STATISTICS
    
    else:
        await update.message.reply_text("الرجاء اختيار خيار صحيح من القائمة.")
        return MAIN_MENU

async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة مدير المخزن"""
    keyboard = [
        ["📝 إضافة فاتورة"],
        ["📊 إحصائياتي"],
        ["📊 إحصائيات بتاريخ محدد"],
        ["📋 تحميل ملف الطلبات"],
        ["👥 إحصائيات الموظفين"],
        ["👥 إحصائيات الموظفين بتاريخ محدد"],
        ["📤 تصدير التقارير"],
        ["🔄 إدارة المرتجعات"],
        ["👤 إدارة المستخدمين"],
        ["🔐 إدارة كلمات المرور"],
        ["⚙️ إعدادات النظام"]
    ]
    await update.message.reply_text(
        "اختر الخدمة التالية:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return ADMIN_MENU

async def download_shipping_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحميل ملف طلبات شركة التوصيل"""
    try:
        await update.message.reply_text("🔄 جاري إنشاء ملف الطلبات...")
        
        filename = db_manager.create_shipping_excel(days=1)
        
        if filename:
            with open(filename, 'rb') as file:
                await update.message.reply_document(
                    document=file,
                    filename=f"طلبات_التوصيل_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    caption="📋 ملف طلبات شركة التوصيل للآخر 24 ساعة"
                )
            # حذف الملف المؤقت
            os.remove(filename)
        else:
            await update.message.reply_text("❌ لا توجد طلبات في آخر 24 ساعة")
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في إنشاء الملف: {e}")

async def show_all_employees_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات جميع الموظفين"""
    try:
        stats = db_manager.get_all_employees_stats()
        
        if stats:
            stats_text = f"""
📊 إحصائيات جميع الموظفين - {datetime.now().strftime('%B %Y')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            total_orders = 0
            total_quantity = 0
            total_sales = 0
            
            for i, (employee, orders, quantity, sales) in enumerate(stats, 1):
                avg_price = sales / quantity if quantity > 0 else 0
                stats_text += f"""
{i}. 👤 {employee}
   📋 عدد الفواتير: {orders}
   📦 إجمالي القطع: {quantity}
   💰 إجمالي المبيعات: {sales:,.0f} دينار
   📈 متوسط سعر القطعة: {avg_price:,.0f} دينار
"""
                total_orders += orders
                total_quantity += quantity
                total_sales += sales
            
            # إضافة الإجمالي العام
            stats_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 الإجمالي العام:
📋 إجمالي الفواتير: {total_orders}
📦 إجمالي القطع: {total_quantity}
💰 إجمالي المبيعات: {total_sales:,.0f} دينار
📈 متوسط سعر القطعة: {(total_sales / total_quantity if total_quantity > 0 else 0):,.0f} دينار
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        else:
            stats_text = "❌ لا توجد بيانات للموظفين في الشهر الحالي"
        
        await update.message.reply_text(stats_text)
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في عرض الإحصائيات: {e}")

async def show_system_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إعدادات النظام"""
    settings_text = f"""
⚙️ إعدادات النظام
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 قاعدة البيانات: ✅ متصلة
📅 إرسال التقارير التلقائي: {'✅ مفعل' if config.AUTO_SEND_REPORTS else '❌ معطل'}
⏰ فترة الإرسال: كل {config.REPORT_INTERVAL_HOURS} ساعة
👤 مدير المخزن: {config.WAREHOUSE_MANAGER_ID}

📈 إحصائيات النظام:
• قاعدة البيانات: {db_manager.db_path}
• عدد المستخدمين: {len(config.ALLOWED_USERS)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(settings_text)

# معالج إدخال جميع بيانات الفاتورة في رسالة واحدة
async def add_invoice_single_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدخال جميع بيانات الفاتورة في رسالة واحدة"""
    try:
        text = update.message.text.strip()
        
        # تقسيم النص حسب السطر الجديد أولاً
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # إذا كان التنسيق على سطر واحد، نقسم حسب /
        if len(lines) == 1:
            parts = [part.strip() for part in text.split('/')]
            if len(parts) < 8:
                await update.message.reply_text(
                    "❌ خطأ في تنسيق البيانات!\n\n"
                    "الرجاء إدخال جميع البيانات بالترتيب:\n"
                    "اسم الموظفة /نور\n"
                    "أسم العميل/ محمد\n"
                    "المحافظة/ الانبار\n"
                    "اقرب نقطة دالة / الرمادي\n"
                    "الرقم/ 0782444\n"
                    "العدد/ 1\n"
                    "السعر / 40000\n"
                    "الملاحظات/ لاشيئ"
                )
                return ADD_INVOICE_SINGLE
            
            # استخراج البيانات من التنسيق القديم
            employee_name = parts[0]
            client_name = parts[1]
            governorate = parts[2]
            nearest_point = parts[3]
            phone_number = parts[4]
            quantity = parts[5]
            price = parts[6]
            notes = parts[7] if len(parts) > 7 else ""
        else:
            # التنسيق الجديد - كل حقل في سطر منفصل
            if len(lines) < 8:
                await update.message.reply_text(
                    "❌ خطأ في تنسيق البيانات!\n\n"
                    "الرجاء إدخال جميع البيانات بالترتيب:\n"
                    "اسم الموظفة /نور\n"
                    "أسم العميل/ محمد\n"
                    "المحافظة/ الانبار\n"
                    "اقرب نقطة دالة / الرمادي\n"
                    "الرقم/ 0782444\n"
                    "العدد/ 1\n"
                    "السعر / 40000\n"
                    "الملاحظات/ لاشيئ"
                )
                return ADD_INVOICE_SINGLE
            
            # استخراج البيانات من التنسيق الجديد
            try:
                employee_name = lines[0].split('/')[1].strip() if '/' in lines[0] else lines[0]
                client_name = lines[1].split('/')[1].strip() if '/' in lines[1] else lines[1]
                governorate = lines[2].split('/')[1].strip() if '/' in lines[2] else lines[2]
                nearest_point = lines[3].split('/')[1].strip() if '/' in lines[3] else lines[3]
                phone_number = lines[4].split('/')[1].strip() if '/' in lines[4] else lines[4]
                quantity = lines[5].split('/')[1].strip() if '/' in lines[5] else lines[5]
                price = lines[6].split('/')[1].strip() if '/' in lines[6] else lines[6]
                notes = lines[7].split('/')[1].strip() if '/' in lines[7] else lines[7]
            except IndexError:
                await update.message.reply_text(
                    "❌ خطأ في تنسيق البيانات!\n\n"
                    "الرجاء التأكد من تنسيق البيانات:\n"
                    "اسم الموظفة /نور\n"
                    "أسم العميل/ محمد\n"
                    "المحافظة/ الانبار\n"
                    "اقرب نقطة دالة / الرمادي\n"
                    "الرقم/ 0782444\n"
                    "العدد/ 1\n"
                    "السعر / 40000\n"
                    "الملاحظات/ لاشيئ"
                )
                return ADD_INVOICE_SINGLE
        
        # تنظيف البيانات من المسافات الزائدة
        employee_name = employee_name.strip()
        client_name = client_name.strip()
        governorate = governorate.strip()
        nearest_point = nearest_point.strip()
        phone_number = phone_number.strip()
        quantity = quantity.strip()
        price = price.strip()
        notes = notes.strip()
        
        # التحقق من صحة البيانات
        try:
            # إزالة المسافات من العدد
            quantity_clean = quantity.replace(' ', '')
            quantity = int(quantity_clean)
            if quantity <= 0:
                raise ValueError("العدد يجب أن يكون أكبر من صفر")
        except ValueError:
            await update.message.reply_text("❌ خطأ: العدد يجب أن يكون رقماً صحيحاً أكبر من صفر")
            return ADD_INVOICE_SINGLE
        
        try:
            # إزالة المسافات والفواصل من السعر
            price_clean = price.replace(' ', '').replace(',', '')
            price = float(price_clean)
            if price <= 0:
                raise ValueError("السعر يجب أن يكون أكبر من صفر")
        except ValueError:
            await update.message.reply_text("❌ خطأ: السعر يجب أن يكون رقماً أكبر من صفر")
            return ADD_INVOICE_SINGLE
        
        # التحقق من رقم الهاتف
        if not phone_number.replace(' ', '').isdigit() or len(phone_number.replace(' ', '')) < 10:
            await update.message.reply_text("❌ خطأ: رقم الهاتف غير صحيح")
            return ADD_INVOICE_SINGLE
        
        # إنشاء رقم الإيصال
        receipt_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        total_sales = price  # السعر كما هو بدون ضرب بالعدد
        
        # إعداد بيانات الفاتورة
        invoice_data = {
            'receipt_number': receipt_number,
            'employee_name': employee_name,
            'client_name': client_name,
            'client_phone': phone_number,
            'governorate': governorate,
            'nearest_point': nearest_point,
            'quantity': quantity,
            'price': price,
            'total_sales': total_sales,
            'notes': notes
        }
        
        # حفظ الفاتورة في قاعدة البيانات
        if db_manager.add_invoice(invoice_data):
            # رسالة التأكيد
            confirmation_text = f"""
✅ تم إضافة الفاتورة بنجاح!

📋 تفاصيل الفاتورة:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔢 رقم الإيصال: {receipt_number}
👤 اسم الموظفة: {employee_name}
👥 أسم العميل: {client_name}
🏛️ المحافظة: {governorate}
📍 أقرب نقطة دالة: {nearest_point}
📞 الرقم: {phone_number}
📦 العدد: {quantity}
💰 السعر: {price:,.0f} دينار
📝 الملاحظات: {notes}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
            
            # إعادة عرض القائمة المناسبة
            user_id = update.message.from_user.id
            if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
                keyboard = [
                    ["📝 إضافة فاتورة"],
                    ["📊 إحصائياتي"],
                    ["📋 تحميل ملف الطلبات"],
                    ["👥 إحصائيات الموظفين"],
                    ["⚙️ إعدادات النظام"]
                ]
                await update.message.reply_text(
                    confirmation_text,
                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                )
                return ADMIN_MENU
            else:
                keyboard = [
                    ["📝 إضافة فاتورة"],
                    ["📊 إحصائياتي"]
                ]
                await update.message.reply_text(
                    confirmation_text,
                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                )
                return MAIN_MENU
        else:
            await update.message.reply_text("❌ خطأ في حفظ الفاتورة. الرجاء المحاولة مرة أخرى.")
            return ADD_INVOICE_SINGLE
            
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في معالجة البيانات: {e}\nالرجاء المحاولة مرة أخرى.")
        return ADD_INVOICE_SINGLE

# معالج الإحصائيات
async def statistics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الإحصائيات"""
    employee_name = update.message.text
    
    # التحقق من وجود كلمة مرور للموظف
    if db_manager.has_password(employee_name):
        # حفظ اسم الموظف وطلب كلمة المرور
        context.user_data['employee_name'] = employee_name
        await update.message.reply_text(
            f"🔐 كلمة المرور مطلوبة\n\n"
            f"الرجاء إدخال كلمة المرور الخاصة بـ {employee_name}:",
            reply_markup=ReplyKeyboardRemove()
        )
        return STATISTICS_PASSWORD
    else:
        # لا توجد كلمة مرور، عرض الإحصائيات مباشرة
        return await show_employee_statistics(update, context, employee_name)

async def statistics_password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج كلمة مرور الإحصائيات"""
    password = update.message.text
    employee_name = context.user_data.get('employee_name', '')
    
    # التحقق من كلمة المرور
    if db_manager.verify_employee_password(employee_name, password):
        # كلمة المرور صحيحة، عرض الإحصائيات
        return await show_employee_statistics(update, context, employee_name)
    else:
        # كلمة المرور خاطئة
        await update.message.reply_text(
            "❌ كلمة المرور غير صحيحة!\n\n"
            "الرجاء المحاولة مرة أخرى أو إدخال اسم موظف آخر:",
            reply_markup=ReplyKeyboardRemove()
        )
        # مسح اسم الموظف من الذاكرة
        context.user_data.pop('employee_name', None)
        return STATISTICS

async def show_employee_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE, employee_name):
    """عرض إحصائيات الموظف مع المرتجعات"""
    # الحصول على إحصائيات الشهر الحالي مع المرتجعات
    stats = db_manager.get_employee_stats_with_returns(employee_name)
    
    if stats and stats['total_invoices'] > 0:
        current_month = datetime.now().strftime("%B %Y")
        stats_text = f"""
📊 إحصائيات {employee_name} - {current_month}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 عدد الفواتير: {stats['total_invoices']}
📦 إجمالي القطع: {stats['total_quantity']}
💰 إجمالي المبيعات: {stats['total_sales']:,.0f} دينار
"""
        
        # إضافة معلومات المرتجعات إذا وجدت
        if stats['returned_quantity'] > 0 or stats['returned_amount'] > 0:
            stats_text += f"""
🔄 المرتجعات:
   📦 القطع المرتجعة: {stats['returned_quantity']}
   💰 المبلغ المرتجع: {stats['returned_amount']:,.0f} دينار
"""
        
        # الإحصائيات النهائية
        stats_text += f"""
🏆 الإحصائيات النهائية:
   📦 القطع النهائية: {stats['final_quantity']}
   💰 المبيعات النهائية: {stats['final_sales']:,.0f} دينار
   📈 متوسط سعر القطعة: {(stats['final_sales'] / stats['final_quantity']):,.0f} دينار
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # إضافة تفاصيل آخر 5 فواتير (من الإحصائيات القديمة للحصول على التفاصيل)
        old_stats = db_manager.get_employee_monthly_stats(employee_name)
        if old_stats and old_stats['invoices']:
            stats_text += "\n📋 آخر 5 فواتير:\n"
            for i, invoice in enumerate(old_stats['invoices'][:5], 1):
                receipt_num = invoice[1]  # receipt_number
                client_name = invoice[3]  # client_name
                quantity = invoice[7]     # quantity (index 7)
                price = invoice[9]        # total_sales (index 9)
                date = datetime.strptime(invoice[11], '%Y-%m-%d %H:%M:%S').strftime('%d/%m')  # created_at (index 11)
                
                stats_text += f"{i}. {receipt_num} - {client_name} ({quantity} قطعة - {price:,.0f} د) - {date}\n"
    
    else:
        stats_text = f"❌ لم يتم العثور على بيانات لـ {employee_name} في الشهر الحالي."
    
    # إعادة عرض القائمة المناسبة
    user_id = update.message.from_user.id
    if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
        await update.message.reply_text(stats_text)
        return await show_admin_menu(update, context)
    else:
        keyboard = [
            ["📝 إضافة فاتورة"],
            ["📊 إحصائياتي"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(stats_text, reply_markup=reply_markup)
        return MAIN_MENU

async def statistics_date_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار التاريخ للإحصائيات"""
    text = update.message.text.strip()
    
    # إذا لم يكن اسم الموظف محفوظاً، احفظه واطلب التاريخ
    if 'employee_name' not in context.user_data:
        context.user_data['employee_name'] = text
        await update.message.reply_text(
            f"📅 إحصائيات {text} بتاريخ محدد\n\n"
            "الرجاء إدخال التاريخ بالشكل التالي:\n"
            "YYYY-MM-DD إلى YYYY-MM-DD\n\n"
            "مثال:\n"
            "2024-01-01 إلى 2024-01-31\n"
            "أو\n"
            "2024-01-01 إلى 2024-12-31"
        )
        return STATISTICS_DATE_SELECTION
    else:
        # إذا كان اسم الموظف محفوظاً، فهذا تاريخ
        return await statistics_date_range_handler(update, context)

async def statistics_date_range_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج نطاق التاريخ للإحصائيات"""
    text = update.message.text.strip()
    
    try:
        # تحليل نطاق التاريخ
        if "إلى" not in text:
            await update.message.reply_text(
                "❌ خطأ في تنسيق التاريخ!\n\n"
                "الرجاء استخدام التنسيق:\n"
                "YYYY-MM-DD إلى YYYY-MM-DD"
            )
            return STATISTICS_DATE_SELECTION
        
        date_range = text.split("إلى")
        start_date = date_range[0].strip()
        end_date = date_range[1].strip()
        
        # التحقق من صحة التواريخ
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
        
        employee_name = context.user_data.get('employee_name', '')
        
        # الحصول على الإحصائيات
        stats = db_manager.get_employee_stats_by_date_range(employee_name, start_date, end_date)
        
        if stats and stats['total_orders'] > 0:
            stats_text = f"""
📊 إحصائيات {employee_name} - من {start_date} إلى {end_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 عدد الفواتير: {stats['total_orders']}
📦 إجمالي القطع: {stats['total_quantity']}
💰 إجمالي المبيعات: {stats['total_sales']:,.0f} دينار
📈 متوسط سعر القطعة: {(stats['total_sales'] / stats['total_quantity']):,.0f} دينار
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            # إضافة تفاصيل آخر 5 فواتير
            if stats['invoices']:
                stats_text += "\n📋 آخر 5 فواتير:\n"
                for i, invoice in enumerate(stats['invoices'][:5], 1):
                    receipt_num = invoice[1]  # receipt_number
                    client_name = invoice[3]  # client_name
                    quantity = invoice[7]     # quantity (index 7)
                    price = invoice[9]        # total_sales (index 9)
                    date = datetime.strptime(invoice[11], '%Y-%m-%d %H:%M:%S').strftime('%d/%m')  # created_at (index 11)
                    
                    stats_text += f"{i}. {receipt_num} - {client_name} ({quantity} قطعة - {price:,.0f} د) - {date}\n"
            
            # إضافة أزرار التصدير
            keyboard = [
                [InlineKeyboardButton("📤 تصدير التقرير", callback_data=f"export_employee_{employee_name}_{start_date}_{end_date}")],
                [InlineKeyboardButton("🔙 العودة للقائمة", callback_data="back_to_admin_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(stats_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(f"❌ لم يتم العثور على بيانات لـ {employee_name} في الفترة المحددة.")
        
        return await show_admin_menu(update, context)
        
    except ValueError:
        await update.message.reply_text(
            "❌ خطأ في تنسيق التاريخ!\n\n"
            "الرجاء استخدام التنسيق:\n"
            "YYYY-MM-DD إلى YYYY-MM-DD"
        )
        return STATISTICS_DATE_SELECTION
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في معالجة الطلب: {e}")
        return await show_admin_menu(update, context)

async def all_employees_date_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار التاريخ لإحصائيات جميع الموظفين"""
    text = update.message.text.strip()
    
    try:
        # تحليل نطاق التاريخ
        if "إلى" not in text:
            await update.message.reply_text(
                "❌ خطأ في تنسيق التاريخ!\n\n"
                "الرجاء استخدام التنسيق:\n"
                "YYYY-MM-DD إلى YYYY-MM-DD"
            )
            return ALL_EMPLOYEES_DATE_SELECTION
        
        date_range = text.split("إلى")
        start_date = date_range[0].strip()
        end_date = date_range[1].strip()
        
        # التحقق من صحة التواريخ
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
        
        # الحصول على الإحصائيات
        stats = db_manager.get_all_employees_stats_by_date_range(start_date, end_date)
        
        if stats:
            stats_text = f"""
📊 إحصائيات جميع الموظفين - من {start_date} إلى {end_date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            total_orders = 0
            total_quantity = 0
            total_sales = 0
            
            for i, (employee, orders, quantity, sales) in enumerate(stats, 1):
                avg_price = sales / quantity if quantity > 0 else 0
                stats_text += f"""
{i}. 👤 {employee}
   📋 عدد الفواتير: {orders}
   📦 إجمالي القطع: {quantity}
   💰 إجمالي المبيعات: {sales:,.0f} دينار
   📈 متوسط سعر القطعة: {avg_price:,.0f} دينار
"""
                total_orders += orders
                total_quantity += quantity
                total_sales += sales
            
            # إضافة الإجمالي العام
            stats_text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 الإجمالي العام:
📋 إجمالي الفواتير: {total_orders}
📦 إجمالي القطع: {total_quantity}
💰 إجمالي المبيعات: {total_sales:,.0f} دينار
📈 متوسط سعر القطعة: {(total_sales / total_quantity if total_quantity > 0 else 0):,.0f} دينار
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            # إضافة أزرار التصدير
            keyboard = [
                [InlineKeyboardButton("📤 تصدير التقرير", callback_data=f"export_all_employees_{start_date}_{end_date}")],
                [InlineKeyboardButton("🔙 العودة للقائمة", callback_data="back_to_admin_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(stats_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text("❌ لا توجد بيانات للموظفين في الفترة المحددة.")
        
        return await show_admin_menu(update, context)
        
    except ValueError:
        await update.message.reply_text(
            "❌ خطأ في تنسيق التاريخ!\n\n"
            "الرجاء استخدام التنسيق:\n"
            "YYYY-MM-DD إلى YYYY-MM-DD"
        )
        return ALL_EMPLOYEES_DATE_SELECTION
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في معالجة الطلب: {e}")
        return await show_admin_menu(update, context)

async def show_export_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة تصدير التقارير"""
    keyboard = [
        [InlineKeyboardButton("📊 تصدير إحصائيات الشهر الحالي", callback_data="export_current_month")],
        [InlineKeyboardButton("📊 تصدير إحصائيات الشهر السابق", callback_data="export_previous_month")],
        [InlineKeyboardButton("📊 تصدير إحصائيات السنة الحالية", callback_data="export_current_year")],
        [InlineKeyboardButton("🔙 العودة للقائمة", callback_data="back_to_admin_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📤 تصدير التقارير\n\n"
        "اختر نوع التقرير المراد تصديره:",
        reply_markup=reply_markup
    )

async def export_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار التصدير"""
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data == "back_to_admin_menu":
            await query.edit_message_text("تم العودة للقائمة الرئيسية.")
            return await show_admin_menu(update, context)
        
        elif query.data == "export_current_month":
            # تصدير إحصائيات الشهر الحالي
            current_month = datetime.now().month
            current_year = datetime.now().year
            stats = db_manager.get_all_employees_stats(current_month, current_year)
            
            if stats:
                filename = db_manager.create_statistics_excel(
                    stats, 
                    "all_employees", 
                    f"{current_year}-{current_month:02d}"
                )
                if filename:
                    with open(filename, 'rb') as file:
                        await context.bot.send_document(
                            chat_id=query.from_user.id,
                            document=file,
                            caption=f"📊 تقرير إحصائيات الشهر الحالي ({current_year}-{current_month:02d})"
                        )
                    os.remove(filename)  # حذف الملف بعد الإرسال
                else:
                    await query.edit_message_text("❌ خطأ في إنشاء ملف التقرير.")
            else:
                await query.edit_message_text("❌ لا توجد بيانات للتصدير في الشهر الحالي.")
        
        elif query.data == "export_previous_month":
            # تصدير إحصائيات الشهر السابق
            previous_month = datetime.now().month - 1
            current_year = datetime.now().year
            if previous_month == 0:
                previous_month = 12
                current_year -= 1
            
            stats = db_manager.get_all_employees_stats(previous_month, current_year)
            
            if stats:
                filename = db_manager.create_statistics_excel(
                    stats, 
                    "all_employees", 
                    f"{current_year}-{previous_month:02d}"
                )
                if filename:
                    with open(filename, 'rb') as file:
                        await context.bot.send_document(
                            chat_id=query.from_user.id,
                            document=file,
                            caption=f"📊 تقرير إحصائيات الشهر السابق ({current_year}-{previous_month:02d})"
                        )
                    os.remove(filename)  # حذف الملف بعد الإرسال
                else:
                    await query.edit_message_text("❌ خطأ في إنشاء ملف التقرير.")
            else:
                await query.edit_message_text("❌ لا توجد بيانات للتصدير في الشهر السابق.")
        
        elif query.data == "export_current_year":
            # تصدير إحصائيات السنة الحالية
            current_year = datetime.now().year
            start_date = f"{current_year}-01-01"
            end_date = f"{current_year}-12-31"
            
            stats = db_manager.get_all_employees_stats_by_date_range(start_date, end_date)
            
            if stats:
                filename = db_manager.create_statistics_excel(
                    stats, 
                    "all_employees", 
                    f"{current_year}"
                )
                if filename:
                    with open(filename, 'rb') as file:
                        await context.bot.send_document(
                            chat_id=query.from_user.id,
                            document=file,
                            caption=f"📊 تقرير إحصائيات السنة الحالية ({current_year})"
                        )
                    os.remove(filename)  # حذف الملف بعد الإرسال
                else:
                    await query.edit_message_text("❌ خطأ في إنشاء ملف التقرير.")
            else:
                await query.edit_message_text("❌ لا توجد بيانات للتصدير في السنة الحالية.")
        
        elif query.data.startswith("export_employee_"):
            # تصدير إحصائيات موظف محدد
            parts = query.data.split("_")
            employee_name = parts[2]
            start_date = parts[3]
            end_date = parts[4]
            
            stats = db_manager.get_employee_stats_by_date_range(employee_name, start_date, end_date)
            
            if stats:
                filename = db_manager.create_statistics_excel(
                    stats, 
                    "employee", 
                    f"{start_date}_to_{end_date}"
                )
                if filename:
                    with open(filename, 'rb') as file:
                        await context.bot.send_document(
                            chat_id=query.from_user.id,
                            document=file,
                            caption=f"📊 تقرير إحصائيات {employee_name} - من {start_date} إلى {end_date}"
                        )
                    os.remove(filename)  # حذف الملف بعد الإرسال
                else:
                    await query.edit_message_text("❌ خطأ في إنشاء ملف التقرير.")
            else:
                await query.edit_message_text("❌ لا توجد بيانات للتصدير.")
        
        elif query.data.startswith("export_all_employees_"):
            # تصدير إحصائيات جميع الموظفين لفترة محددة
            parts = query.data.split("_")
            start_date = parts[3]
            end_date = parts[4]
            
            stats = db_manager.get_all_employees_stats_by_date_range(start_date, end_date)
            
            if stats:
                filename = db_manager.create_statistics_excel(
                    stats, 
                    "all_employees", 
                    f"{start_date}_to_{end_date}"
                )
                if filename:
                    with open(filename, 'rb') as file:
                        await context.bot.send_document(
                            chat_id=query.from_user.id,
                            document=file,
                            caption=f"📊 تقرير إحصائيات جميع الموظفين - من {start_date} إلى {end_date}"
                        )
                    os.remove(filename)  # حذف الملف بعد الإرسال
                else:
                    await query.edit_message_text("❌ خطأ في إنشاء ملف التقرير.")
            else:
                await query.edit_message_text("❌ لا توجد بيانات للتصدير.")
        
        return await show_admin_menu(update, context)
        
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ في تصدير التقرير: {e}")
        return await show_admin_menu(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء العملية"""
    context.user_data.clear()
    await update.message.reply_text("تم إلغاء العملية.", reply_markup=ReplyKeyboardRemove())
    
    # إعادة عرض القائمة المناسبة
    user_id = update.message.from_user.id
    if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
        return await show_admin_menu(update, context)
    else:
        keyboard = [
            ["📝 إضافة فاتورة"],
            ["📊 إحصائياتي"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("اختر الخدمة المطلوبة:", reply_markup=reply_markup)
        return MAIN_MENU

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة"""
    user_id = update.message.from_user.id
    
    if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
        help_text = """
🤖 دليل استخدام البوت (مدير المخزن)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 إضافة فاتورة:
• أرسل جميع البيانات في رسالة واحدة
• التنسيق: اسم الموظفة /نور
أسم العميل/ محمد
المحافظة/ الانبار
اقرب نقطة دالة / الرمادي
الرقم/ 0782444
العدد/ 1
السعر / 40000
الملاحظات/ لاشيئ

📊 إحصائياتي:
• أدخل اسم الموظف لعرض إحصائياته التفصيلية
• ستظهر عدد الفواتير، القطع، المبيعات، ومتوسط السعر

📊 إحصائيات بتاريخ محدد:
• أدخل اسم الموظف ثم التاريخ المطلوب
• يمكنك تحديد فترة زمنية محددة للإحصائيات

📋 تحميل ملف الطلبات:
• تحميل ملف Excel لطلبات شركة التوصيل
• يحتوي على طلبات آخر 24 ساعة

👥 إحصائيات الموظفين:
• عرض إحصائيات جميع الموظفين مع التفاصيل
• ترتيب حسب المبيعات مع الإجمالي العام

👥 إحصائيات الموظفين بتاريخ محدد:
• عرض إحصائيات جميع الموظفين لفترة زمنية محددة
• مفيد للتقارير الشهرية والسنوية

📤 تصدير التقارير:
• تصدير التقارير بصيغة Excel
• يشمل الشهر الحالي، السابق، والسنة الحالية

👤 إدارة المستخدمين:
• إضافة مستخدمين جدد للبوت
• تحديد صلاحيات المستخدمين

�� إدارة كلمات المرور:
• إضافة كلمات مرور جديدة للمستخدمين

⚙️ إعدادات النظام:
• عرض حالة النظام والإعدادات

🔧 الأوامر المتاحة:
/start - بدء البوت
/help - عرض هذا الدليل
/cancel - إلغاء العملية الحالية

📞 للدعم الفني، تواصل مع إدارة النظام
        """
    else:
        help_text = """
🤖 دليل استخدام البوت
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 إضافة فاتورة:
• أرسل جميع البيانات في رسالة واحدة
• التنسيق: اسم الموظفة /نور
أسم العميل/ محمد
المحافظة/ الانبار
اقرب نقطة دالة / الرمادي
الرقم/ 0782444
العدد/ 1
السعر / 40000
الملاحظات/ لاشيئ

📊 إحصائياتي:
• أدخل اسم الموظف لعرض إحصائياته التفصيلية
• ستظهر عدد الفواتير، القطع، المبيعات، ومتوسط السعر

🔧 الأوامر المتاحة:
/start - بدء البوت
/help - عرض هذا الدليل
/cancel - إلغاء العملية الحالية

📞 للدعم الفني، تواصل مع إدارة النظام
        """
    
    await update.message.reply_text(help_text)

async def show_user_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة إدارة المستخدمين"""
    # عرض المستخدمين الحاليين
    current_users_text = "👥 المستخدمين الحاليين:\n"
    current_users_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    for i, user_id in enumerate(config.ALLOWED_USERS, 1):
        role = "مدير مخزن" if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3] else "موظف"
        current_users_text += f"{i}. {user_id} - {role}\n"
    
    current_users_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    current_users_text += "اختر الإجراء المطلوب:"
    
    # إنشاء أزرار تفاعلية
    keyboard = [
        [InlineKeyboardButton("➕ إضافة مستخدم جديد", callback_data="add_user")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(current_users_text, reply_markup=reply_markup)
    return USER_MANAGEMENT_MENU

async def user_management_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار إدارة المستخدمين"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "add_user":
        # عرض خيارات دور المستخدم
        keyboard = [
            [InlineKeyboardButton("👤 موظف عادي", callback_data="role_employee")],
            [InlineKeyboardButton("👑 مدير مخزن", callback_data="role_manager")],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_user_management")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔐 اختر دور المستخدم الجديد:\n\n"
            "👤 موظف عادي - صلاحيات أساسية\n"
            "👑 مدير مخزن - صلاحيات إدارية كاملة",
            reply_markup=reply_markup
        )
        return ADD_USER_ROLE
    
    elif query.data == "back_to_admin":
        return await show_admin_menu(update, context)
    
    elif query.data == "back_to_user_management":
        return await show_user_management_menu(update, context)

async def add_user_role_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار دور المستخدم"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("role_"):
        role = query.data.split("_")[1]
        context.user_data['new_user_role'] = role
        
        role_text = "موظف عادي" if role == "employee" else "مدير مخزن"
        
        await query.edit_message_text(
            f"✅ تم اختيار دور: {role_text}\n\n"
            "📝 الآن أرسل بيانات المستخدم بالشكل التالي:\n\n"
            "@ll2005m\n"
            "Id: 5808690567\n\n"
            "أو أرسل البيانات المطلوبة مباشرة:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_user_management")
            ]])
        )
        return ADD_USER_DATA

async def user_management_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدارة المستخدمين - إدخال بيانات المستخدم"""
    try:
        text = update.message.text.strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # التحقق من التنسيق المبسط
        if len(lines) < 2:
            await update.message.reply_text(
                "❌ خطأ في تنسيق البيانات!\n\n"
                "الرجاء إرسال البيانات بالشكل التالي:\n\n"
                "@ll2005m\n"
                "Id: 5808690567\n\n"
                "أو التنسيق الكامل:\n"
                "@username\n"
                "Id: user_id\n"
                "First: FirstName\n"
                "Last: LastName"
            )
            return ADD_USER_DATA
        
        # استخراج البيانات
        username = lines[0].replace('@', '') if lines[0].startswith('@') else lines[0]
        
        # استخراج معرف المستخدم
        id_line = next((line for line in lines if line.startswith('Id:')), None)
        if not id_line:
            await update.message.reply_text("❌ خطأ: لم يتم العثور على معرف المستخدم")
            return ADD_USER_DATA
        
        user_id = int(id_line.split(':')[1].strip())
        
        # استخراج الاسم (إذا كان موجوداً)
        first_name = "User"
        last_name = username.capitalize()
        
        if len(lines) >= 4:
            first_line = next((line for line in lines if line.startswith('First:')), None)
            last_line = next((line for line in lines if line.startswith('Last:')), None)
            
            if first_line:
                first_name = first_line.split(':')[1].strip()
            if last_line:
                last_name = last_line.split(':')[1].strip()
        
        full_name = f"{first_name} {last_name}"
        
        # الحصول على الدور المختار
        role = context.user_data.get('new_user_role', 'employee')
        role_text = "مدير مخزن" if role == "manager" else "موظف"
        
        # إضافة المستخدم إلى قائمة المستخدمين المصرح لهم
        if user_id not in config.ALLOWED_USERS:
            # تحديث ملف config.py
            await update_config_file(user_id)
            
            # إذا كان مدير مخزن، تحديث WAREHOUSE_MANAGER_ID_2
            if role == "manager":
                await update_manager_config(user_id)
            
            # إضافة المستخدم لقاعدة البيانات
            db_role = "warehouse_manager" if role == "manager" else "employee"
            db_manager.add_user(user_id, username, full_name, db_role)
            
            success_text = f"""
✅ تم إضافة المستخدم بنجاح!

👤 اسم المستخدم: @{username}
🆔 معرف المستخدم: {user_id}
📝 الاسم الكامل: {full_name}
🔐 الصلاحية: {role_text}

يمكن للمستخدم الآن الوصول إلى البوت!
"""
            
            # إضافة زر للعودة
            keyboard = [[InlineKeyboardButton("🔙 العودة لإدارة المستخدمين", callback_data="back_to_user_management")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(success_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(
                f"⚠️ المستخدم موجود بالفعل في النظام!\n\n"
                f"👤 اسم المستخدم: @{username}\n"
                f"🆔 معرف المستخدم: {user_id}"
            )
        
        return ADD_USER_DATA
        
    except ValueError:
        await update.message.reply_text("❌ خطأ: معرف المستخدم يجب أن يكون رقماً صحيحاً")
        return ADD_USER_DATA
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في إضافة المستخدم: {e}")
        return ADD_USER_DATA

async def update_manager_config(user_id):
    """تحديث ملف config.py لتعيين مدير مخزن جديد"""
    try:
        # قراءة الملف الحالي
        with open('config.py', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # تحديث WAREHOUSE_MANAGER_ID_2
        import re
        pattern = r'WAREHOUSE_MANAGER_ID_2 = \d+'
        new_content = re.sub(pattern, f'WAREHOUSE_MANAGER_ID_2 = {user_id}', content)
        
        # كتابة الملف المحدث
        with open('config.py', 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        # إعادة تحميل config
        import importlib
        import config
        importlib.reload(config)
        
    except Exception as e:
        print(f"خطأ في تحديث إعدادات المدير: {e}")

async def update_config_file(user_id):
    """تحديث ملف config.py"""
    try:
        # قراءة الملف الحالي
        with open('config.py', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # إضافة معرف المستخدم الجديد إلى ALLOWED_USERS
        if f"ALLOWED_USERS = [" in content:
            # إضافة المعرف الجديد
            content = content.replace(
                "ALLOWED_USERS = [",
                f"ALLOWED_USERS = [\n    {user_id},"
            )
        
        # كتابة المحتوى المحدث
        with open('config.py', 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"✅ تم تحديث ملف config.py بنجاح")
        
    except Exception as e:
        print(f"❌ خطأ في تحديث ملف config.py: {e}")

async def show_password_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة إدارة كلمات المرور"""
    keyboard = [
        [InlineKeyboardButton("➕ إضافة كلمة مرور", callback_data="add_password")],
        [InlineKeyboardButton("🔍 عرض كلمات المرور", callback_data="view_passwords")],
        [InlineKeyboardButton("✏️ تعديل كلمة مرور", callback_data="edit_password")],
        [InlineKeyboardButton("🗑️ حذف كلمة مرور", callback_data="delete_password")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🔐 إدارة كلمات المرور\n\n"
        "اختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def password_management_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار إدارة كلمات المرور"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "add_password":
        await query.edit_message_text(
            "➕ إضافة كلمة مرور جديدة\n\n"
            "الرجاء إدخال اسم الموظف وكلمة المرور بالشكل التالي:\n"
            "اسم الموظف:كلمة المرور\n\n"
            "مثال:\n"
            "أحمد:123456",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
            ]])
        )
        context.user_data['password_action'] = 'add'
        return PASSWORD_MANAGEMENT
    
    elif query.data == "view_passwords":
        passwords = db_manager.get_all_passwords()
        if passwords:
            text = "🔍 كلمات المرور الحالية:\n\n"
            for i, (employee, password) in enumerate(passwords, 1):
                text += f"{i}. {employee}: {'*' * len(password)}\n"
        else:
            text = "❌ لا توجد كلمات مرور محفوظة."
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
            ]])
        )
        return PASSWORD_MANAGEMENT
    
    elif query.data == "edit_password":
        await query.edit_message_text(
            "✏️ تعديل كلمة مرور\n\n"
            "الرجاء إدخال اسم الموظف وكلمة المرور الجديدة بالشكل التالي:\n"
            "اسم الموظف:كلمة المرور الجديدة\n\n"
            "مثال:\n"
            "أحمد:654321",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
            ]])
        )
        context.user_data['password_action'] = 'edit'
        return PASSWORD_MANAGEMENT
    
    elif query.data == "delete_password":
        await query.edit_message_text(
            "🗑️ حذف كلمة مرور\n\n"
            "الرجاء إدخال اسم الموظف:\n\n"
            "مثال:\n"
            "أحمد",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
            ]])
        )
        context.user_data['password_action'] = 'delete'
        return PASSWORD_MANAGEMENT
    
    elif query.data == "back_to_password_menu":
        return await show_password_management_menu(update, context)
    
    elif query.data == "back_to_admin":
        return await show_admin_menu(update, context)

async def password_management_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدارة كلمات المرور"""
    text = update.message.text
    action = context.user_data.get('password_action', '')
    
    if action == 'add':
        try:
            if ':' not in text:
                await update.message.reply_text(
                    "❌ خطأ في التنسيق!\n\n"
                    "الرجاء استخدام التنسيق:\n"
                    "اسم الموظف:كلمة المرور"
                )
                return PASSWORD_MANAGEMENT
            
            employee_name, password = text.split(':', 1)
            employee_name = employee_name.strip()
            password = password.strip()
            
            if db_manager.set_employee_password(employee_name, password):
                await update.message.reply_text(
                    f"✅ تم إضافة كلمة المرور بنجاح!\n\n"
                    f"الموظف: {employee_name}\n"
                    f"كلمة المرور: {password}"
                )
            else:
                await update.message.reply_text("❌ فشل في إضافة كلمة المرور.")
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {e}")
    
    elif action == 'edit':
        try:
            if ':' not in text:
                await update.message.reply_text(
                    "❌ خطأ في التنسيق!\n\n"
                    "الرجاء استخدام التنسيق:\n"
                    "اسم الموظف:كلمة المرور الجديدة"
                )
                return PASSWORD_MANAGEMENT
            
            employee_name, new_password = text.split(':', 1)
            employee_name = employee_name.strip()
            new_password = new_password.strip()
            
            if db_manager.set_employee_password(employee_name, new_password):
                await update.message.reply_text(
                    f"✅ تم تحديث كلمة المرور بنجاح!\n\n"
                    f"الموظف: {employee_name}\n"
                    f"كلمة المرور الجديدة: {new_password}"
                )
            else:
                await update.message.reply_text("❌ فشل في تحديث كلمة المرور.")
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {e}")
    
    elif action == 'delete':
        employee_name = text.strip()
        
        if db_manager.delete_employee_password(employee_name):
            await update.message.reply_text(
                f"✅ تم حذف كلمة المرور بنجاح!\n\n"
                f"الموظف: {employee_name}"
            )
        else:
            await update.message.reply_text("❌ فشل في حذف كلمة المرور.")
    
    # مسح الإجراء من الذاكرة
    context.user_data.pop('password_action', None)
    
    # العودة للقائمة الرئيسية
    return await show_admin_menu(update, context)

# ==================== دوال إدارة المرتجعات ====================

async def show_returns_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة إدارة المرتجعات"""
    try:
        keyboard = [
            [InlineKeyboardButton("➕ إضافة مرتجع جديد", callback_data="add_return")],
            [InlineKeyboardButton("📋 عرض المرتجعات", callback_data="view_returns")],
            [InlineKeyboardButton("📊 إحصائيات مع المرتجعات", callback_data="stats_with_returns")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "🔄 إدارة المرتجعات\n\n"
                "اختر العملية المطلوبة:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "🔄 إدارة المرتجعات\n\n"
                "اختر العملية المطلوبة:",
                reply_markup=reply_markup
            )
        
        return RETURNS_MENU
    except (TimedOut, NetworkError) as e:
        print(f"خطأ في الاتصال: {e}")
        if update.callback_query:
            await update.callback_query.answer("⚠️ حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.")
        else:
            await update.message.reply_text("⚠️ حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.")
        return ADMIN_MENU
    except Exception as e:
        print(f"خطأ غير متوقع: {e}")
        if update.callback_query:
            await update.callback_query.answer("❌ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.")
        else:
            await update.message.reply_text("❌ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.")
        return ADMIN_MENU

async def returns_management_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار إدارة المرتجعات"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "add_return":
        await query.edit_message_text(
            "➕ إضافة مرتجع جديد\n\n"
            "الرجاء إدخال رقم الإيصال للفاتورة المراد إرجاعها:\n\n"
            "💡 يمكنك إدخال الرقم بالشكل التالي:\n"
            "• INV-20250809233907 (كامل)\n"
            "• 20250809233907 (بدون البادئة)",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_returns_menu")
            ]])
        )
        return RETURN_INVOICE_SELECTION
    
    elif query.data == "view_returns":
        await query.edit_message_text(
            "📋 عرض المرتجعات\n\n"
            "الرجاء إدخال اسم الموظف لعرض مرتجعاته:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_returns_menu")
            ]])
        )
        context.user_data['returns_action'] = 'view'
        return RETURN_INVOICE_SELECTION
    
    elif query.data == "stats_with_returns":
        await query.edit_message_text(
            "📊 إحصائيات مع المرتجعات\n\n"
            "الرجاء إدخال اسم الموظف لعرض إحصائياته مع خصم المرتجعات:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_returns_menu")
            ]])
        )
        context.user_data['returns_action'] = 'stats'
        return RETURN_INVOICE_SELECTION
    
    elif query.data == "back_to_returns_menu":
        return await show_returns_management_menu(update, context)
    
    elif query.data == "back_to_admin":
        return await show_admin_menu(update, context)

async def return_invoice_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار الفاتورة للمرتجع"""
    text = update.message.text.strip()
    action = context.user_data.get('returns_action', 'add')
    
    if action == 'add':
        # التحقق من أن النص ليس فارغاً
        if not text:
            await update.message.reply_text(
                "❌ الرجاء إدخال رقم الإيصال!"
            )
            return RETURN_INVOICE_SELECTION
        
        # البحث عن الفاتورة
        invoice = db_manager.get_invoice_by_receipt(text)
        
        if not invoice:
            await update.message.reply_text(
                "❌ لم يتم العثور على فاتورة بهذا الرقم!\n\n"
                "الرجاء التأكد من رقم الإيصال والمحاولة مرة أخرى.\n\n"
                "💡 تلميح: يمكنك إدخال الرقم بالشكل التالي:\n"
                "• INV-20250809233907 (كامل)\n"
                "• 20250809233907 (بدون البادئة)"
            )
            return RETURN_INVOICE_SELECTION
        
        # حفظ بيانات الفاتورة
        context.user_data['invoice_data'] = invoice
        
        # عرض تفاصيل الفاتورة واختيار نوع المرتجع
        keyboard = [
            [InlineKeyboardButton("🔄 مرتجع كلي", callback_data="return_full")],
            [InlineKeyboardButton("↩️ مرتجع جزئي", callback_data="return_partial")],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_returns_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📋 تفاصيل الفاتورة:\n\n"
            f"رقم الإيصال: {invoice['receipt_number']}\n"
            f"الموظف: {invoice['employee_name']}\n"
            f"العميل: {invoice['client_name']}\n"
            f"الكمية: {invoice['quantity']}\n"
            f"السعر: {invoice['price']:,} دينار\n"
            f"الإجمالي: {invoice['total_sales']:,} دينار\n\n"
            f"اختر نوع المرتجع:",
            reply_markup=reply_markup
        )
        return RETURN_TYPE_SELECTION
    
    elif action == 'view':
        # عرض مرتجعات الموظف
        returns = db_manager.get_returns_by_employee(text.strip())
        
        if not returns:
            await update.message.reply_text(
                f"❌ لا توجد مرتجعات للموظف: {text.strip()}"
            )
            return await show_returns_management_menu(update, context)
        
        text_response = f"📋 مرتجعات الموظف: {text.strip()}\n\n"
        for i, ret in enumerate(returns[:10], 1):  # عرض أول 10 مرتجعات
            text_response += f"{i}. رقم الإيصال: {ret['receipt_number']}\n"
            text_response += f"   النوع: {'كلي' if ret['return_type'] == 'full' else 'جزئي'}\n"
            text_response += f"   الكمية المرتجعة: {ret['returned_quantity']}\n"
            text_response += f"   المبلغ المرتجع: {ret['returned_amount']:,} دينار\n"
            text_response += f"   المبلغ المتبقي: {ret['remaining_amount']:,} دينار\n"
            text_response += f"   السبب: {ret['return_reason']}\n"
            text_response += f"   التاريخ: {ret['created_at'][:10]}\n\n"
        
        if len(returns) > 10:
            text_response += f"... والمزيد ({len(returns) - 10} مرتجع إضافي)"
        
        await update.message.reply_text(text_response)
        return await show_returns_management_menu(update, context)
    
    elif action == 'stats':
        # عرض إحصائيات الموظف مع المرتجعات
        stats = db_manager.get_employee_stats_with_returns(text.strip())
        
        if not stats:
            await update.message.reply_text(
                f"❌ لا توجد إحصائيات للموظف: {text.strip()}"
            )
            return await show_returns_management_menu(update, context)
        
        text_response = f"📊 إحصائيات الموظف: {text.strip()}\n\n"
        text_response += f"إجمالي الفواتير: {stats['total_invoices']}\n"
        text_response += f"إجمالي الكمية: {stats['total_quantity']}\n"
        text_response += f"إجمالي المبيعات: {stats['total_sales']:,} دينار\n\n"
        text_response += f"الكمية المرتجعة: {stats['returned_quantity']}\n"
        text_response += f"المبلغ المرتجع: {stats['returned_amount']:,} دينار\n\n"
        text_response += f"🏆 الإحصائيات النهائية:\n"
        text_response += f"الكمية النهائية: {stats['final_quantity']}\n"
        text_response += f"المبيعات النهائية: {stats['final_sales']:,} دينار"
        
        await update.message.reply_text(text_response)
        return await show_returns_management_menu(update, context)

async def return_type_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار نوع المرتجع"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "return_full":
        context.user_data['return_type'] = 'full'
        invoice = context.user_data['invoice_data']
        
        await query.edit_message_text(
            f"🔄 مرتجع كلي\n\n"
            f"رقم الإيصال: {invoice['receipt_number']}\n"
            f"الكمية المراد إرجاعها: {invoice['quantity']}\n"
            f"المبلغ المراد إرجاعه: {invoice['total_sales']:,} دينار\n\n"
            f"الرجاء إدخال سبب الإرجاع:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_returns_menu")
            ]])
        )
        return RETURN_REASON_INPUT
    
    elif query.data == "return_partial":
        context.user_data['return_type'] = 'partial'
        invoice = context.user_data['invoice_data']
        
        await query.edit_message_text(
            f"↩️ مرتجع جزئي\n\n"
            f"رقم الإيصال: {invoice['receipt_number']}\n"
            f"الكمية الأصلية: {invoice['quantity']}\n"
            f"المبلغ الإجمالي: {invoice['total_sales']:,} دينار\n\n"
            f"الرجاء إدخال الكمية المراد إرجاعها:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_returns_menu")
            ]])
        )
        return RETURN_QUANTITY_INPUT
    
    elif query.data == "back_to_returns_menu":
        return await show_returns_management_menu(update, context)

async def return_quantity_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدخال كمية المرتجع الجزئي"""
    try:
        returned_quantity = int(update.message.text.strip())
        invoice = context.user_data['invoice_data']
        
        if returned_quantity <= 0 or returned_quantity >= invoice['quantity']:
            await update.message.reply_text(
                "❌ الكمية غير صحيحة!\n\n"
                f"يجب أن تكون الكمية بين 1 و {invoice['quantity'] - 1}"
            )
            return RETURN_QUANTITY_INPUT
        
        # حساب المبالغ
        returned_amount = (returned_quantity / invoice['quantity']) * invoice['total_sales']
        remaining_amount = invoice['total_sales'] - returned_amount
        
        context.user_data['returned_quantity'] = returned_quantity
        context.user_data['returned_amount'] = returned_amount
        context.user_data['remaining_amount'] = remaining_amount
        
        await update.message.reply_text(
            f"↩️ مرتجع جزئي\n\n"
            f"الكمية المراد إرجاعها: {returned_quantity}\n"
            f"المبلغ المراد إرجاعه: {returned_amount:,.0f} دينار\n"
            f"المبلغ المتبقي: {remaining_amount:,.0f} دينار\n\n"
            f"الرجاء إدخال سبب الإرجاع:"
        )
        return RETURN_REASON_INPUT
        
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح!")
        return RETURN_QUANTITY_INPUT

async def return_reason_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدخال سبب المرتجع"""
    reason = update.message.text.strip()
    invoice = context.user_data['invoice_data']
    return_type = context.user_data['return_type']
    
    # تجهيز بيانات المرتجع
    return_data = {
        'invoice_id': invoice['id'],
        'receipt_number': invoice['receipt_number'],
        'employee_name': invoice['employee_name'],
        'return_type': return_type,
        'return_reason': reason,
        'processed_by': f"Admin_{update.message.from_user.id}"
    }
    
    if return_type == 'full':
        return_data['returned_quantity'] = invoice['quantity']
        return_data['returned_amount'] = invoice['total_sales']
        return_data['remaining_amount'] = 0
    else:
        return_data['returned_quantity'] = context.user_data['returned_quantity']
        return_data['returned_amount'] = context.user_data['returned_amount']
        return_data['remaining_amount'] = context.user_data['remaining_amount']
    
    # حفظ المرتجع
    if db_manager.add_return(return_data):
        await update.message.reply_text(
            f"✅ تم إضافة المرتجع بنجاح!\n\n"
            f"رقم الإيصال: {invoice['receipt_number']}\n"
            f"النوع: {'كلي' if return_type == 'full' else 'جزئي'}\n"
            f"الكمية المرتجعة: {return_data['returned_quantity']}\n"
            f"المبلغ المرتجع: {return_data['returned_amount']:,.0f} دينار\n"
            f"المبلغ المتبقي: {return_data['remaining_amount']:,.0f} دينار\n"
            f"السبب: {reason}"
        )
    else:
        await update.message.reply_text("❌ فشل في إضافة المرتجع!")
    
    # مسح البيانات المؤقتة
    context.user_data.clear()
    
    return await show_returns_management_menu(update, context)

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    print("🚀 بدء تشغيل البوت (الإصدار النظيف)...")
    
    try:
        # إنشاء تطبيق البوت مع إعدادات اتصال محسنة
        from telegram.request import HTTPXRequest
        request = HTTPXRequest(
            connection_pool_size=20, 
            connect_timeout=120.0, 
            read_timeout=120.0, 
            write_timeout=120.0,
            http_version="1.1"
        )
        app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).request(request).build()
        
        # إعداد معالج المحادثة
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                MAIN_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)
                ],
                ADD_INVOICE_SINGLE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, add_invoice_single_handler)
                ],
                ADMIN_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_menu_handler)
                ],
                STATISTICS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, statistics_handler)
                ],
                STATISTICS_PASSWORD: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, statistics_password_handler)
                ],
                STATISTICS_DATE_SELECTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, statistics_date_selection_handler)
                ],
                STATISTICS_EXPORT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: show_admin_menu(u, c))
                ],
                ALL_EMPLOYEES_DATE_SELECTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, all_employees_date_selection_handler)
                ],
                USER_MANAGEMENT_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, user_management_handler)
                ],
                ADD_USER_ROLE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, user_management_handler)
                ],
                ADD_USER_DATA: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, user_management_handler)
                ],
                PASSWORD_MANAGEMENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, password_management_handler)
                ],
                RETURNS_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: show_returns_management_menu(u, c))
                ],
                RETURN_INVOICE_SELECTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, return_invoice_selection_handler)
                ],
                RETURN_TYPE_SELECTION: [
                    CallbackQueryHandler(return_type_callback_handler)
                ],
                RETURN_QUANTITY_INPUT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, return_quantity_input_handler)
                ],
                RETURN_REASON_INPUT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, return_reason_input_handler)
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            per_chat=True,
            per_user=True
        )
        
        # إضافة المعالجات
        app.add_handler(conv_handler)
        app.add_handler(CommandHandler("help", help_command))
        
        # إضافة معالج الأخطاء
        async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
            """معالج الأخطاء العام"""
            try:
                if isinstance(context.error, TimedOut):
                    print(f"خطأ في الاتصال - انتهت مهلة الاتصال: {context.error}")
                    if update and hasattr(update, 'message') and update.message:
                        await update.message.reply_text("⚠️ انتهت مهلة الاتصال. يرجى المحاولة مرة أخرى.")
                    elif update and hasattr(update, 'callback_query') and update.callback_query:
                        await update.callback_query.answer("⚠️ انتهت مهلة الاتصال. يرجى المحاولة مرة أخرى.")
                elif isinstance(context.error, NetworkError):
                    print(f"خطأ في الشبكة: {context.error}")
                    if update and hasattr(update, 'message') and update.message:
                        await update.message.reply_text("⚠️ خطأ في الاتصال بالشبكة. يرجى المحاولة مرة أخرى.")
                    elif update and hasattr(update, 'callback_query') and update.callback_query:
                        await update.callback_query.answer("⚠️ خطأ في الاتصال بالشبكة. يرجى المحاولة مرة أخرى.")
                else:
                    print(f"خطأ غير متوقع: {context.error}")
                    if update and hasattr(update, 'message') and update.message:
                        await update.message.reply_text("❌ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.")
                    elif update and hasattr(update, 'callback_query') and update.callback_query:
                        await update.callback_query.answer("❌ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.")
            except Exception as e:
                print(f"خطأ في معالج الأخطاء: {e}")
        
        app.add_error_handler(error_handler)
        
        # إضافة معالج الأزرار التفاعلية
        app.add_handler(CallbackQueryHandler(user_management_callback_handler, pattern="^(add_user|back_to_admin|back_to_user_management)$"))
        app.add_handler(CallbackQueryHandler(add_user_role_handler, pattern="^role_"))
        app.add_handler(CallbackQueryHandler(export_callback_handler, pattern="^(export_|back_to_admin_menu)$"))
        app.add_handler(CallbackQueryHandler(password_management_callback_handler, pattern="^(add_password|view_passwords|edit_password|delete_password|back_to_password_menu|back_to_admin)$"))
        app.add_handler(CallbackQueryHandler(returns_management_callback_handler, pattern="^(add_return|view_returns|stats_with_returns|back_to_returns_menu|back_to_admin)$"))
        app.add_handler(CallbackQueryHandler(return_type_callback_handler, pattern="^(return_full|return_partial|back_to_returns_menu)$"))
        
        print("✅ البوت جاهز للعمل! (الإصدار النظيف)")
        print("📱 يمكنك الآن استخدام البوت في تيليجرام")
        print("💾 البيانات محفوظة في قاعدة البيانات المحلية")
        print("🌐 محاولة الاتصال بخوادم تيليجرام...")
        
        # تشغيل البوت مع إعدادات محسنة
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
            close_loop=False
        )
        
    except Conflict:
        print("❌ نزاع في الاتصال: هناك نسخة أخرى من البوت تعمل بالفعل")
        print("💡 الحلول المقترحة:")
        print("   1. أوقف جميع نسخ البوت الجارية")
        print("   2. انتظر دقيقة واحدة ثم حاول مرة أخرى")
        print("   3. أعد تشغيل الكمبيوتر إذا استمرت المشكلة")
        print("   4. تحقق من عدم وجود نسخ أخرى من البوت في الخلفية")
    except TimedOut:
        print("❌ فشل في الاتصال بخوادم تيليجرام - انتهت مهلة الاتصال")
        print("💡 الحلول المقترحة:")
        print("   1. تحقق من اتصال الإنترنت")
        print("   2. تحقق من صحة توكن البوت")
        print("   3. جرب استخدام VPN إذا كان تيليجرام محظوراً")
        print("   4. انتظر قليلاً وحاول مرة أخرى")
    except NetworkError as e:
        print(f"❌ خطأ في الشبكة: {e}")
        print("💡 تحقق من اتصال الإنترنت وحاول مرة أخرى")
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        print("💡 يرجى التحقق من إعدادات البوت والتوكن")

if __name__ == "__main__":
    main() 