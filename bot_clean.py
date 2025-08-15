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
from api_manager import api_manager

# تهيئة مدير قاعدة البيانات
db_manager = DatabaseManager()

# Bot States
MAIN_MENU = 1
ADD_INVOICE_SINGLE = 2
ADMIN_MENU = 3
STATISTICS_MENU = 4
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

        # التحقق من الرسائل المعاد توجيهها
        if update.message.forward_from or update.message.forward_from_chat:
            return await handle_forwarded_message(update, context)

        # إضافة المستخدم لقاعدة البيانات
        username = update.message.from_user.username or ""
        full_name = update.message.from_user.full_name or ""
        role = "warehouse_manager" if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3] else "employee"
        db_manager.add_user(user_id, username, full_name, role)

        # عرض القائمة المناسبة
        if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
            # قائمة مدير المخزن - نظام شبكة (3 أزرار في كل صف)
            keyboard = [
                ["🔙 العودة للقائمة الرئيسية", "📝 إضافة فاتورة", "📊 الإحصائيات"],
                ["📋 تحميل ملف الطلبات", "🔄 إدارة المرتجعات", "👤 إدارة المستخدمين"],
                ["🔐 إدارة كلمات المرور", "⚙️ إعدادات النظام"]
            ]
            await update.message.reply_text(
                "مرحبًا بك في بوت إدارة الفواتير! 🎉\n"
                "أنت مدير المخزن - لديك صلاحيات إضافية\n\n"
                "اختر الخدمة المطلوبة:",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            )
            return ADMIN_MENU
        else:
            # قائمة الموظف العادي - نظام شبكة (3 أزرار في كل صف)
            keyboard = [
                ["📝 إضافة فاتورة", "📊 إحصائياتي", "🔙 العودة للقائمة الرئيسية"]
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
    
    # التحقق من الرسائل المعاد توجيهها
    if update.message.forward_from or update.message.forward_from_chat:
        return await handle_forwarded_message(update, context)
    
    if text == "📝 إضافة فاتورة":
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
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
            "ملاحظة: استخدم / للفصل بين الحقول\n\n"
            "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
        )
        return ADD_INVOICE_SINGLE
    
    elif text == "📊 الإحصائيات":
        return await show_statistics_menu(update, context)
    
    elif text == "📋 تحميل ملف الطلبات":
        await download_shipping_file(update, context)
        return await show_admin_menu(update, context)
    
    elif text == "👥 إحصائيات الموظفين":
        await show_all_employees_stats(update, context)
        return await show_admin_menu(update, context)
    
    elif text == "👥 إحصائيات الموظفين بتاريخ محدد":
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📅 إحصائيات الموظفين بتاريخ محدد\n\n"
            "الرجاء إدخال التاريخ بالشكل التالي:\n"
            "YYYY-MM-DD إلى YYYY-MM-DD\n\n"
            "مثال:\n"
            "2024-01-01 إلى 2024-01-31\n"
            "أو\n"
            "2024-01-01 إلى 2024-12-31\n\n"
            "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
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
    
    elif text == "🌐 حالة API":
        # الحصول على الطلبات الفاشلة في API
        failed_orders = db_manager.get_failed_api_orders()
        
        if failed_orders:
            status_text = f"""
🌐 حالة API - الطلبات الفاشلة
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 عدد الطلبات الفاشلة: {len(failed_orders)}

📋 آخر 5 طلبات فاشلة:
"""
            for i, order in enumerate(failed_orders[:5], 1):
                status_text += f"""
{i}. رقم الإيصال: {order['receipt_number']}
   👤 الموظف: {order['employee_name']}
   👥 العميل: {order['client_name']}
   💰 المبلغ: {order['total_sales']:,.0f} دينار
   ⚠️ السبب: {order['api_message']}
   🔄 المحاولات: {order['retry_count']}
   📅 التاريخ: {order['sent_at']}
"""
        else:
            status_text = """
🌐 حالة API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ جميع الطلبات تم إرسالها بنجاح!
📊 لا توجد طلبات فاشلة حالياً
"""
        
        # اختبار الاتصال بـ API
        test_result = api_manager.test_api_connection()
        if test_result.get('success'):
            status_text += f"""
🔗 حالة الاتصال:
✅ الاتصال بـ API يعمل بشكل صحيح
📡 رمز الحالة: {test_result.get('status_code', 'غير محدد')}
"""
        else:
            status_text += f"""
🔗 حالة الاتصال:
❌ مشكلة في الاتصال بـ API
⚠️ السبب: {test_result.get('message', 'خطأ غير معروف')}
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 إعادة المحاولة للطلبات الفاشلة", callback_data="retry_failed_orders")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            status_text,
            reply_markup=reply_markup
        )
        return ADMIN_MENU
    
    elif text == "⚙️ إعدادات النظام":
        await show_system_settings(update, context)
        return await show_admin_menu(update, context)
    
    elif text == "🔙 العودة للقائمة الرئيسية":
        return await start(update, context)
    
    elif text == "🔐 إدارة كلمات المرور":
        return await show_password_management_menu(update, context)
    
    elif "إدارة كلمات المرور" in text:
        return await show_password_management_menu(update, context)
    
    else:
        # إذا كان المستخدم في حالة إدارة كلمات المرور، إعادة توجيه للمعالج المناسب
        if context.user_data.get('password_action'):
            return await password_management_handler(update, context)
        else:
            await update.message.reply_text("الرجاء اختيار خيار صحيح من القائمة.")
            return ADMIN_MENU

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج القائمة الرئيسية للموظفين"""
    text = update.message.text
    
    # التحقق من الرسائل المعاد توجيهها
    if update.message.forward_from or update.message.forward_from_chat:
        return await handle_forwarded_message(update, context)
    
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
            "💡 يمكنك أيضاً إعادة توجيه رسالة تحتوي على بيانات الفاتورة!",
            reply_markup=ReplyKeyboardRemove()
        )
        return ADD_INVOICE_SINGLE
    
    elif text == "📊 إحصائياتي":
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "الرجاء إدخال اسم الموظف لعرض إحصائياته التفصيلية:\n\n"
            "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
        )
        return STATISTICS
    
    elif text == "🔙 العودة للقائمة الرئيسية":
        return await start(update, context)
    
    else:
        await update.message.reply_text("الرجاء اختيار خيار صحيح من القائمة.")
        return MAIN_MENU

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل المعاد توجيهها"""
    try:
        # التحقق من أن المستخدم مصرح له
        user_id = update.message.from_user.id
        if user_id not in config.ALLOWED_USERS:
            await update.message.reply_text("عذراً، هذا البوت مخصص لموظفي الشركة فقط.")
            return ConversationHandler.END
        
        # الحصول على نص الرسالة المعاد توجيهها
        text = update.message.text.strip()
        
        if not text:
            await update.message.reply_text(
                "❌ الرسالة المعاد توجيهها فارغة!\n\n"
                "الرجاء إعادة توجيه رسالة تحتوي على بيانات الفاتورة بالشكل التالي:\n\n"
                "اسم الموظفة /نور\n"
                "أسم العميل/ محمد\n"
                "المحافظة/ الانبار\n"
                "اقرب نقطة دالة / الرمادي\n"
                "الرقم/ 0782444\n"
                "العدد/ 1\n"
                "السعر / 40000\n"
                "الملاحظات/ لاشيئ"
            )
            return MAIN_MENU
        
        # إرسال رسالة تأكيد
        await update.message.reply_text(
            "🔄 جاري معالجة الرسالة المعاد توجيهها...\n\n"
            "📋 البيانات المستلمة:\n" + text[:500] + ("..." if len(text) > 500 else "")
        )
        
        # معالجة البيانات كفاتورة جديدة
        return await process_invoice_data(update, context, text)
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطأ في معالجة الرسالة المعاد توجيهها: {str(e)}\n\n"
            "الرجاء التأكد من تنسيق البيانات وإعادة المحاولة."
        )
        return MAIN_MENU

async def process_invoice_data(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """معالجة بيانات الفاتورة (مشتركة بين الإدخال اليدوي والمعاد توجيهه)"""
    try:
        # تقسيم النص حسب السطر الجديد أولاً
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # إذا كان التنسيق على سطر واحد، نقسم حسب /
        if len(lines) == 1:
            parts = [part.strip() for part in text.split('/')]
            if len(parts) < 8:
                keyboard = [
                    [InlineKeyboardButton("🔙 تجاهل والعودة للقائمة الرئيسية", callback_data="back_to_main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
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
                    "الملاحظات/ لاشيئ\n\n"
                    "💡 يمكنك تجاهل هذا الخطأ والعودة للقائمة الرئيسية",
                    reply_markup=reply_markup
                )
                return MAIN_MENU
            
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
                keyboard = [
                    [InlineKeyboardButton("🔙 تجاهل والعودة للقائمة الرئيسية", callback_data="back_to_main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
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
                    "الملاحظات/ لاشيئ\n\n"
                    "💡 يمكنك تجاهل هذا الخطأ والعودة للقائمة الرئيسية",
                    reply_markup=reply_markup
                )
                return MAIN_MENU
            
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
                keyboard = [
                    [InlineKeyboardButton("🔙 تجاهل والعودة للقائمة الرئيسية", callback_data="back_to_main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
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
                    "الملاحظات/ لاشيئ\n\n"
                    "💡 يمكنك تجاهل هذا الخطأ والعودة للقائمة الرئيسية",
                    reply_markup=reply_markup
                )
                return MAIN_MENU
        
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
            keyboard = [
                [InlineKeyboardButton("🔙 تجاهل والعودة للقائمة الرئيسية", callback_data="back_to_main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "❌ خطأ: العدد يجب أن يكون رقماً صحيحاً أكبر من صفر\n\n"
                "💡 يمكنك تجاهل هذا الخطأ والعودة للقائمة الرئيسية",
                reply_markup=reply_markup
            )
            return MAIN_MENU
        
        try:
            # فلترة السعر - إزالة جميع العلامات والرموز والمسافات (عربية وإنجليزية)
            import re
            
            # قائمة العلامات العربية والإنجليزية التي يجب إزالتها
            arabic_english_chars = {
                # علامات الترقيم العربية
                '،': '',  # فاصلة عربية
                '؛': '',  # فاصلة منقوطة عربية
                '؟': '',  # علامة استفهام عربية
                '!': '',  # علامة تعجب
                'ـ': '',  # كسرة عربية
                '،': '',  # فاصلة عربية
                '؛': '',  # فاصلة منقوطة عربية
                '؟': '',  # علامة استفهام عربية
                '!': '',  # علامة تعجب
                'ـ': '',  # كسرة عربية
                
                # علامات الترقيم الإنجليزية
                ',': '',  # فاصلة إنجليزية
                ';': '',  # فاصلة منقوطة إنجليزية
                '?': '',  # علامة استفهام إنجليزية
                '!': '',  # علامة تعجب إنجليزية
                '-': '',  # شرطة
                '_': '',  # شرطة سفلية
                '+': '',  # علامة زائد
                '=': '',  # علامة يساوي
                '*': '',  # علامة ضرب
                '/': '',  # علامة قسمة
                '\\': '',  # شرطة مائلة
                '|': '',  # خط عمودي
                '`': '',  # علامة اقتباس
                '~': '',  # علامة تيلدا
                '@': '',  # علامة @
                '#': '',  # علامة #
                '$': '',  # علامة $
                '%': '',  # علامة %
                '^': '',  # علامة ^
                '&': '',  # علامة &
                '(': '',  # قوس مفتوح
                ')': '',  # قوس مغلق
                '[': '',  # قوس مربع مفتوح
                ']': '',  # قوس مربع مغلق
                '{': '',  # قوس مجعد مفتوح
                '}': '',  # قوس مجعد مغلق
                '<': '',  # علامة أصغر من
                '>': '',  # علامة أكبر من
                '"': '',  # علامة اقتباس مزدوجة
                "'": '',  # علامة اقتباس مفردة
                ' ': '',  # مسافة
                '\t': '',  # تبويب
                '\n': '',  # سطر جديد
                '\r': '',  # عودة السطر
            }
            
            # تطبيق الاستبدالات
            price_clean = price
            for char, replacement in arabic_english_chars.items():
                price_clean = price_clean.replace(char, replacement)
            
            # تحويل الأرقام العربية إلى أرقام إنجليزية
            arabic_to_english = {
                '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
                '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
            }
            for arabic, english in arabic_to_english.items():
                price_clean = price_clean.replace(arabic, english)
            
            # إزالة جميع الأحرف غير الرقمية والنقطة العشرية (للأمان)
            price_clean = re.sub(r'[^\d.]', '', price_clean)
            
            # إزالة النقاط العشرية المتعددة (الاحتفاظ بالأولى فقط)
            if price_clean.count('.') > 1:
                parts = price_clean.split('.')
                price_clean = parts[0] + '.' + ''.join(parts[1:])
            
            # التحقق من أن النص يحتوي على أرقام
            if not price_clean or price_clean == '.':
                raise ValueError("السعر يجب أن يحتوي على أرقام")
            
            price = float(price_clean)
            if price <= 0:
                raise ValueError("السعر يجب أن يكون أكبر من صفر")
                
        except ValueError as e:
            keyboard = [
                [InlineKeyboardButton("🔙 تجاهل والعودة للقائمة الرئيسية", callback_data="back_to_main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"❌ خطأ في السعر: {str(e)}\n\n"
                f"السعر المدخل: '{price}'\n"
                f"الرجاء التأكد من أن السعر يحتوي على أرقام فقط\n\n"
                f"💡 يمكنك تجاهل هذا الخطأ والعودة للقائمة الرئيسية",
                reply_markup=reply_markup
            )
            return MAIN_MENU
        
        # التحقق من رقم الهاتف
        if not phone_number.replace(' ', '').isdigit() or len(phone_number.replace(' ', '')) < 10:
            keyboard = [
                [InlineKeyboardButton("🔙 تجاهل والعودة للقائمة الرئيسية", callback_data="back_to_main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "❌ خطأ: رقم الهاتف غير صحيح\n\n"
                "💡 يمكنك تجاهل هذا الخطأ والعودة للقائمة الرئيسية",
                reply_markup=reply_markup
            )
            return MAIN_MENU
        
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
        db_result = db_manager.add_invoice(invoice_data)
        if db_result.get('success'):
            invoice_id = db_result.get('invoice_id')
            
            # إرسال الطلب إلى API
            api_result = api_manager.send_order_to_api(invoice_data)
            
            # تسجيل نتيجة API في قاعدة البيانات
            db_manager.record_api_order(invoice_id, receipt_number, api_result)
            
            # إعداد رسالة التأكيد
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
            
            # إضافة معلومات API إلى رسالة التأكيد
            if api_result.get('success'):
                confirmation_text += f"""
🌐 حالة API:
✅ تم إرسال الطلب إلى النظام الخارجي بنجاح
🆔 معرف الطلب: {api_result.get('api_order_id', 'غير محدد')}
📋 مجموعة الطلب: {api_result.get('api_order_group_id', 'غير محدد')}
"""
            elif api_result.get('is_duplicate'):
                # حالة التكرار - حذف الفاتورة من قاعدة البيانات المحلية
                db_manager.delete_invoice_by_receipt(receipt_number)
                confirmation_text = f"""
❌ تم إلغاء إضافة الفاتورة!

📋 تفاصيل الفاتورة الملغية:
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

🌐 سبب الإلغاء:
⚠️ {api_result.get('message', 'تكرار في الطلب')}
💡 تم العثور على طلب مشابه في آخر 24 ساعة
"""
            else:
                confirmation_text += f"""
🌐 حالة API:
❌ فشل في إرسال الطلب إلى النظام الخارجي
⚠️ السبب: {api_result.get('message', 'خطأ غير معروف')}
💡 سيتم إعادة المحاولة تلقائياً
"""
            
            # إعادة عرض القائمة المناسبة
            user_id = update.message.from_user.id
            if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
                keyboard = [
                    ["📝 إضافة فاتورة", "📊 إحصائياتي", "📋 تحميل ملف الطلبات"],
                    ["👥 إحصائيات الموظفين", "🌐 حالة API", "⚙️ إعدادات النظام"],
                    ["🔙 العودة للقائمة الرئيسية"]
                ]
                await update.message.reply_text(
                    confirmation_text,
                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                )
                return ADMIN_MENU
            else:
                keyboard = [
                    ["📝 إضافة فاتورة", "📊 إحصائياتي", "🔙 العودة للقائمة الرئيسية"]
                ]
                await update.message.reply_text(
                    confirmation_text,
                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                )
                return MAIN_MENU
        else:
            keyboard = [
                [InlineKeyboardButton("🔙 تجاهل والعودة للقائمة الرئيسية", callback_data="back_to_main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "❌ خطأ في حفظ الفاتورة. الرجاء المحاولة مرة أخرى.\n\n"
                "💡 يمكنك تجاهل هذا الخطأ والعودة للقائمة الرئيسية",
                reply_markup=reply_markup
            )
            return MAIN_MENU
            
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطأ في معالجة البيانات: {e}\nالرجاء المحاولة مرة أخرى."
        )
        return MAIN_MENU

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض القائمة الرئيسية للموظفين العاديين"""
    keyboard = [
        ["📝 إضافة فاتورة", "📊 إحصائياتي", "🔙 العودة للقائمة الرئيسية"]
    ]
    
    if update.callback_query:
        # عند استخدام callback_query، نرسل رسالة جديدة بدلاً من تعديل الرسالة
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            "اختر الخدمة المطلوبة:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
    else:
        await update.message.reply_text(
            "اختر الخدمة المطلوبة:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
    return MAIN_MENU

async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة مدير المخزن"""
    if update.callback_query:
        # عند استخدام callback_query، نرسل رسالة جديدة بدلاً من تعديل الرسالة
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            "اختر الخدمة التالية:",
            reply_markup=ReplyKeyboardMarkup([
                ["🔙 العودة للقائمة الرئيسية", "📝 إضافة فاتورة", "📊 الإحصائيات"],
                ["📋 تحميل ملف الطلبات", "🔄 إدارة المرتجعات", "👤 إدارة المستخدمين"],
                ["🔐 إدارة كلمات المرور", "⚙️ إعدادات النظام"]
            ], one_time_keyboard=True, resize_keyboard=True)
        )
    else:
        await update.message.reply_text(
            "اختر الخدمة التالية:",
            reply_markup=ReplyKeyboardMarkup([
                ["🔙 العودة للقائمة الرئيسية", "📝 إضافة فاتورة", "📊 الإحصائيات"],
                ["📋 تحميل ملف الطلبات", "🔄 إدارة المرتجعات", "👤 إدارة المستخدمين"],
                ["🔐 إدارة كلمات المرور", "⚙️ إعدادات النظام"]
            ], one_time_keyboard=True, resize_keyboard=True)
        )
    return ADMIN_MENU

async def show_statistics_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة الإحصائيات"""
    keyboard = [
        ["📊 إحصائياتي", "📊 إحصائيات بتاريخ محدد"],
        ["👥 إحصائيات الموظفين", "👥 إحصائيات الموظفين بتاريخ محدد"],
        ["📤 تصدير التقارير", "🔙 العودة للقائمة الرئيسية"]
    ]
    
    if update.callback_query:
        # عند استخدام callback_query، نرسل رسالة جديدة بدلاً من تعديل الرسالة
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            "📊 قائمة الإحصائيات\n\n"
            "اختر نوع الإحصائيات المطلوبة:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
    else:
        await update.message.reply_text(
            "📊 قائمة الإحصائيات\n\n"
            "اختر نوع الإحصائيات المطلوبة:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
    return STATISTICS_MENU

async def statistics_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج قائمة الإحصائيات"""
    text = update.message.text
    
    if text == "📊 إحصائياتي":
        keyboard = [
            [InlineKeyboardButton("🔙 العودة لقائمة الإحصائيات", callback_data="back_to_statistics_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "الرجاء إدخال اسم الموظف لعرض إحصائياته التفصيلية:\n\n"
            "💡 أو اضغط على زر العودة للرجوع لقائمة الإحصائيات",
            reply_markup=reply_markup
        )
        return STATISTICS
    
    elif text == "📊 إحصائيات بتاريخ محدد":
        keyboard = [
            [InlineKeyboardButton("🔙 العودة لقائمة الإحصائيات", callback_data="back_to_statistics_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📅 إحصائيات بتاريخ محدد\n\n"
            "الرجاء إدخال اسم الموظف أولاً:\n\n"
            "💡 أو اضغط على زر العودة للرجوع لقائمة الإحصائيات",
            reply_markup=reply_markup
        )
        return STATISTICS_DATE_SELECTION
    
    elif text == "👥 إحصائيات الموظفين":
        await show_all_employees_stats(update, context)
        return await show_statistics_menu(update, context)
    
    elif text == "👥 إحصائيات الموظفين بتاريخ محدد":
        # حساب التواريخ
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        
        keyboard = [
            [InlineKeyboardButton("📅 اليوم", callback_data="all_employees_date_today")],
            [InlineKeyboardButton("📅 هذا الأسبوع", callback_data="all_employees_date_week")],
            [InlineKeyboardButton("📅 هذا الشهر", callback_data="all_employees_date_month")],
            [InlineKeyboardButton("📅 هذا العام", callback_data="all_employees_date_year")],
            [InlineKeyboardButton("📝 تاريخ مخصص", callback_data="all_employees_date_custom")],
            [InlineKeyboardButton("🔙 العودة لقائمة الإحصائيات", callback_data="back_to_statistics_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📅 إحصائيات الموظفين بتاريخ محدد\n\n"
            "اختر الفترة الزمنية المطلوبة:\n\n"
            "📅 اليوم - إحصائيات اليوم الحالي\n"
            "📅 هذا الأسبوع - إحصائيات الأسبوع الحالي\n"
            "📅 هذا الشهر - إحصائيات الشهر الحالي\n"
            "📅 هذا العام - إحصائيات السنة الحالية\n"
            "📝 تاريخ مخصص - إدخال تاريخ محدد\n\n"
            "💡 أو اضغط على زر العودة للرجوع لقائمة الإحصائيات",
            reply_markup=reply_markup
        )
        return ALL_EMPLOYEES_DATE_SELECTION
    
    elif text == "📤 تصدير التقارير":
        await show_export_menu(update, context)
        return STATISTICS_EXPORT
    
    elif text == "🔙 العودة للقائمة الرئيسية":
        return await start(update, context)
    
    else:
        await update.message.reply_text("الرجاء اختيار خيار صحيح من القائمة.")
        return STATISTICS_MENU

async def statistics_menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار قائمة الإحصائيات التفاعلية"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_statistics_menu":
        return await show_statistics_menu(update, context)

async def date_selection_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار اختيار التواريخ"""
    query = update.callback_query
    await query.answer()
    
    # استخراج نوع التاريخ واسم الموظف
    parts = query.data.split('_', 2)
    date_type = parts[1]
    employee_name = parts[2]
    
    # حساب التواريخ
    today = datetime.now()
    
    if date_type == "today":
        start_date = today.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_text = "اليوم"
    elif date_type == "week":
        start_of_week = today - timedelta(days=today.weekday())
        end_date = today.strftime('%Y-%m-%d')
        start_date = start_of_week.strftime('%Y-%m-%d')
        period_text = "هذا الأسبوع"
    elif date_type == "month":
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_text = "هذا الشهر"
    elif date_type == "year":
        start_date = today.replace(month=1, day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_text = "هذا العام"
    elif date_type == "custom":
        # طلب إدخال تاريخ مخصص
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"📝 تاريخ مخصص لـ {employee_name}\n\n"
            "الرجاء إدخال التاريخ بالشكل التالي:\n"
            "YYYY-MM-DD إلى YYYY-MM-DD\n\n"
            "مثال:\n"
            "2024-01-01 إلى 2024-01-31\n\n"
            "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
        )
        context.user_data['employee_name'] = employee_name
        return STATISTICS_DATE_SELECTION
    
    # الحصول على الإحصائيات
    stats = db_manager.get_employee_stats_by_date_range(employee_name, start_date, end_date)
    
    if stats and stats['total_orders'] > 0:
        stats_text = f"""
📊 إحصائيات {employee_name} - {period_text}
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
        
        # إضافة أزرار التصدير والعودة
        keyboard = [
            [InlineKeyboardButton("📤 تصدير التقرير", callback_data=f"export_employee_{employee_name}_{start_date}_{end_date}")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(stats_text, reply_markup=reply_markup)
    else:
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"❌ لم يتم العثور على بيانات لـ {employee_name} في {period_text}.\n\n"
            "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
        )

async def all_employees_date_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار اختيار التواريخ لإحصائيات جميع الموظفين"""
    query = update.callback_query
    await query.answer()
    
    # استخراج نوع التاريخ
    date_type = query.data.split('_')[3]  # all_employees_date_today -> today
    
    # حساب التواريخ
    today = datetime.now()
    
    if date_type == "today":
        start_date = today.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_text = "اليوم"
    elif date_type == "week":
        start_of_week = today - timedelta(days=today.weekday())
        end_date = today.strftime('%Y-%m-%d')
        start_date = start_of_week.strftime('%Y-%m-%d')
        period_text = "هذا الأسبوع"
    elif date_type == "month":
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_text = "هذا الشهر"
    elif date_type == "year":
        start_date = today.replace(month=1, day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        period_text = "هذا العام"
    elif date_type == "custom":
        # طلب إدخال تاريخ مخصص
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📝 تاريخ مخصص لإحصائيات جميع الموظفين\n\n"
            "الرجاء إدخال التاريخ بالشكل التالي:\n"
            "YYYY-MM-DD إلى YYYY-MM-DD\n\n"
            "مثال:\n"
            "2024-01-01 إلى 2024-01-31\n\n"
            "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
        )
        return ALL_EMPLOYEES_DATE_SELECTION
    
    # الحصول على الإحصائيات
    stats = db_manager.get_all_employees_stats_by_date_range(start_date, end_date)
    
    if stats:
        stats_text = f"""
📊 إحصائيات جميع الموظفين - {period_text}
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
        
        # إضافة أزرار التصدير والعودة
        keyboard = [
            [InlineKeyboardButton("📤 تصدير التقرير", callback_data=f"export_all_employees_{start_date}_{end_date}")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(stats_text, reply_markup=reply_markup)
    else:
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"❌ لم يتم العثور على بيانات للموظفين في {period_text}.\n\n"
            "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
        )

async def input_screens_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار الشاشات التي تطلب إدخال بيانات"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_admin":
        return await show_admin_menu(update, context)
    elif query.data == "back_to_main_menu":
        return await start(update, context)
    elif query.data == "retry_failed_orders":
        return await retry_failed_api_orders(update, context)

async def show_shipping_period_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة اختيار فترة تحميل الطلبات"""
    try:
        # الحصول على إحصائيات التصدير
        export_stats = db_manager.get_export_stats()
        
        stats_text = ""
        if export_stats:
            stats_text = f"""
📊 إحصائيات الطلبات:
• إجمالي الطلبات: {export_stats['total_invoices']}
• الطلبات المصدرة: {export_stats['exported_invoices']}
• الطلبات الجديدة: {export_stats['new_invoices']}
"""
        
        text = f"""
📋 تحميل ملف طلبات التوصيل
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{stats_text}
اختر فترة التحميل:
"""
        
        keyboard = [
            [InlineKeyboardButton("📋 الكل", callback_data="shipping_all")],
            [InlineKeyboardButton("⏰ آخر 24 ساعة", callback_data="shipping_1")],
            [InlineKeyboardButton("📅 آخر يومين", callback_data="shipping_2")],
            [InlineKeyboardButton("📆 آخر أسبوع", callback_data="shipping_7")],
            [InlineKeyboardButton("📊 آخر شهر", callback_data="shipping_30")],
            [InlineKeyboardButton("📈 آخر 3 شهور", callback_data="shipping_90")],
            [InlineKeyboardButton("🆕 الجديد فقط", callback_data="shipping_new")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في عرض القائمة: {e}")

async def download_shipping_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحميل ملف طلبات شركة التوصيل (الوظيفة القديمة - للتوافق)"""
    await show_shipping_period_menu(update, context)

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
    
    keyboard = [
        [InlineKeyboardButton("🗑️ حذف الفواتير القديمة", callback_data="delete_old_invoices")],
        [InlineKeyboardButton("📊 تصفير الإحصائيات", callback_data="reset_statistics")],
        [InlineKeyboardButton("🔄 إعادة تعيين النظام", callback_data="reset_system")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        settings_text + "\nاختر الإعداد المطلوب:\n\n"
        "🗑️ حذف الفواتير القديمة - حذف الفواتير والإحصائيات مع الاحتفاظ بالمستخدمين\n"
        "📊 تصفير الإحصائيات - تصفير الإحصائيات فقط\n"
        "🔄 إعادة تعيين النظام - حذف كل شيء ما عدا المستخدمين",
        reply_markup=reply_markup
    )

# معالج إدخال جميع بيانات الفاتورة في رسالة واحدة
async def add_invoice_single_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدخال جميع بيانات الفاتورة في رسالة واحدة"""
    try:
        text = update.message.text.strip()
        
        # التحقق من وجود أمر العودة
        if text.lower() in ['عودة', 'رجوع', 'back', 'cancel', 'إلغاء', 'الغاء']:
            user_id = update.message.from_user.id
            if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
                return await show_admin_menu(update, context)
            else:
                return await show_main_menu(update, context)
        
        # استخدام الدالة المشتركة لمعالجة البيانات
        return await process_invoice_data(update, context, text)
        
    except Exception as e:
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"❌ خطأ في معالجة البيانات: {e}\nالرجاء المحاولة مرة أخرى.\n\n"
            "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
        )
        return ADD_INVOICE_SINGLE

# معالج الإحصائيات
async def statistics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الإحصائيات"""
    employee_name = update.message.text.strip()
    
    # التحقق من وجود أمر العودة
    if employee_name.lower() in ['عودة', 'رجوع', 'back', 'cancel', 'إلغاء', 'الغاء']:
        user_id = update.message.from_user.id
        if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
            return await show_admin_menu(update, context)
        else:
            return await show_main_menu(update, context)
    
    # التحقق من وجود كلمة مرور للموظف
    if db_manager.has_password(employee_name):
        # حفظ اسم الموظف وطلب كلمة المرور
        context.user_data['employee_name'] = employee_name
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🔐 كلمة المرور مطلوبة\n\n"
            f"الرجاء إدخال كلمة المرور الخاصة بـ {employee_name}:\n\n"
            f"💡 أو اكتب 'عودة' للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
        )
        return STATISTICS_PASSWORD
    else:
        # لا توجد كلمة مرور، عرض الإحصائيات مباشرة
        return await show_employee_statistics(update, context, employee_name)

async def statistics_password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج كلمة مرور الإحصائيات"""
    password = update.message.text.strip()
    employee_name = context.user_data.get('employee_name', '')
    
    # التحقق من وجود أمر العودة
    if password.lower() in ['عودة', 'رجوع', 'back', 'cancel', 'إلغاء', 'الغاء']:
        user_id = update.message.from_user.id
        if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
            return await show_admin_menu(update, context)
        else:
            return await show_main_menu(update, context)
    
    # التحقق من كلمة المرور
    if db_manager.verify_employee_password(employee_name, password):
        # كلمة المرور صحيحة، عرض الإحصائيات
        return await show_employee_statistics(update, context, employee_name)
    else:
        # كلمة المرور خاطئة
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❌ كلمة المرور غير صحيحة!\n\n"
            "الرجاء المحاولة مرة أخرى أو إدخال اسم موظف آخر:\n\n"
            "💡 أو اكتب 'عودة' للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
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
            ["📝 إضافة فاتورة", "📊 إحصائياتي", "🔙 العودة للقائمة الرئيسية"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(stats_text, reply_markup=reply_markup)
        return MAIN_MENU

async def statistics_date_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار التاريخ للإحصائيات"""
    text = update.message.text.strip()
    
    # التحقق من وجود أمر العودة
    if text.lower() in ['عودة', 'رجوع', 'back', 'cancel', 'إلغاء', 'الغاء']:
        user_id = update.message.from_user.id
        if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
            return await show_admin_menu(update, context)
        else:
            return await show_main_menu(update, context)
    
    # إذا لم يكن اسم الموظف محفوظاً، احفظه واطلب التاريخ
    if 'employee_name' not in context.user_data:
        context.user_data['employee_name'] = text
        
        # حساب التواريخ
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        
        keyboard = [
            [InlineKeyboardButton("📅 اليوم", callback_data=f"date_today_{text}")],
            [InlineKeyboardButton("📅 هذا الأسبوع", callback_data=f"date_week_{text}")],
            [InlineKeyboardButton("📅 هذا الشهر", callback_data=f"date_month_{text}")],
            [InlineKeyboardButton("📅 هذا العام", callback_data=f"date_year_{text}")],
            [InlineKeyboardButton("📝 تاريخ مخصص", callback_data=f"date_custom_{text}")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📅 إحصائيات {text} بتاريخ محدد\n\n"
            "اختر الفترة الزمنية المطلوبة:\n\n"
            "📅 اليوم - إحصائيات اليوم الحالي\n"
            "📅 هذا الأسبوع - إحصائيات الأسبوع الحالي\n"
            "📅 هذا الشهر - إحصائيات الشهر الحالي\n"
            "📅 هذا العام - إحصائيات السنة الحالية\n"
            "📝 تاريخ مخصص - إدخال تاريخ محدد\n\n"
            "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
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
            keyboard = [
                [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "❌ خطأ في تنسيق التاريخ!\n\n"
                "الرجاء استخدام التنسيق:\n"
                "YYYY-MM-DD إلى YYYY-MM-DD\n\n"
                "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
                reply_markup=reply_markup
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
                [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(stats_text, reply_markup=reply_markup)
        else:
            keyboard = [
                [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"❌ لم يتم العثور على بيانات لـ {employee_name} في الفترة المحددة.\n\n"
                "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
                reply_markup=reply_markup
            )
        
        return await show_admin_menu(update, context)
        
    except ValueError:
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ خطأ في تنسيق التاريخ!\n\n"
            "الرجاء استخدام التنسيق:\n"
            "YYYY-MM-DD إلى YYYY-MM-DD\n\n"
            "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
        )
        return STATISTICS_DATE_SELECTION
    except Exception as e:
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"❌ خطأ في معالجة الطلب: {e}\n\n"
            "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
            reply_markup=reply_markup
        )
        return await show_admin_menu(update, context)

async def all_employees_date_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار التاريخ لإحصائيات جميع الموظفين"""
    text = update.message.text.strip()
    
    try:
        # تحليل نطاق التاريخ
        if "إلى" not in text:
            keyboard = [
                [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "❌ خطأ في تنسيق التاريخ!\n\n"
                "الرجاء استخدام التنسيق:\n"
                "YYYY-MM-DD إلى YYYY-MM-DD\n\n"
                "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
                reply_markup=reply_markup
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

async def shipping_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار اختيار فترة تحميل الطلبات"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = query.from_user.id
        
        if query.data == "back_to_main_menu":
            await query.edit_message_text("تم العودة للقائمة الرئيسية.")
            return await show_main_menu(update, context)
        
        elif query.data.startswith("shipping_"):
            period = query.data.replace("shipping_", "")
            
            # تحديد نوع التصدير والفترة
            if period == "all":
                days = 3650  # 10 سنوات (تقريباً الكل)
                export_type = "all"
                period_text = "الكل"
            elif period == "new":
                days = 0
                export_type = "new_only"
                period_text = "الجديد فقط"
            else:
                days = int(period)
                export_type = f"{days}_days"
                if days == 1:
                    period_text = "آخر 24 ساعة"
                elif days == 2:
                    period_text = "آخر يومين"
                elif days == 7:
                    period_text = "آخر أسبوع"
                elif days == 30:
                    period_text = "آخر شهر"
                elif days == 90:
                    period_text = "آخر 3 شهور"
                else:
                    period_text = f"آخر {days} يوم"
            
            # تحديث الرسالة
            await query.edit_message_text(f"🔄 جاري إنشاء ملف الطلبات لـ {period_text}...")
            
            # إنشاء الملف
            filename = db_manager.create_shipping_excel(days, export_type, user_id)
            
            if filename:
                # الحصول على عدد الطلبات
                df = db_manager.get_all_invoices_for_shipping(days, export_type, user_id)
                orders_count = len(df) if df is not None else 0
                
                with open(filename, 'rb') as file:
                    await context.bot.send_document(
                        chat_id=query.from_user.id,
                        document=file,
                        filename=f"طلبات_التوصيل_{period_text}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        caption=f"📋 ملف طلبات التوصيل لـ {period_text}\n📊 عدد الطلبات: {orders_count}"
                    )
                
                # حذف الملف المؤقت
                os.remove(filename)
                
                # رسالة تأكيد
                await context.bot.send_message(
                    chat_id=query.from_user.id,
                    text=f"✅ تم إنشاء ملف الطلبات بنجاح!\n📋 الفترة: {period_text}\n📊 عدد الطلبات: {orders_count}"
                )
            else:
                await query.edit_message_text(f"❌ لا توجد طلبات لـ {period_text}")
    
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ في إنشاء الملف: {e}")

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
    
    elif query.data == "back_to_user_management":
        return await show_user_management_menu(update, context)

async def user_management_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدارة المستخدمين - إدخال بيانات المستخدم"""
    try:
        text = update.message.text.strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # التحقق من التنسيق المبسط
        if len(lines) < 2:
            keyboard = [
                [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "❌ خطأ في تنسيق البيانات!\n\n"
                "الرجاء إرسال البيانات بالشكل التالي:\n\n"
                "@ll2005m\n"
                "Id: 5808690567\n\n"
                "أو التنسيق الكامل:\n"
                "@username\n"
                "Id: user_id\n\n"
                "💡 أو اضغط على زر العودة للرجوع للقائمة الرئيسية",
                reply_markup=reply_markup
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
            
            # تحديث قائمة ALLOWED_USERS في الذاكرة
            if user_id not in config.ALLOWED_USERS:
                config.ALLOWED_USERS.add(user_id)
            
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
        keyboard = [
            [InlineKeyboardButton("🔙 تجاهل والعودة للقائمة الرئيسية", callback_data="back_to_main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ خطأ: معرف المستخدم يجب أن يكون رقماً صحيحاً\n\n"
            "💡 يمكنك تجاهل هذا الخطأ والعودة للقائمة الرئيسية",
            reply_markup=reply_markup
        )
        return MAIN_MENU
    except Exception as e:
        keyboard = [
            [InlineKeyboardButton("🔙 تجاهل والعودة للقائمة الرئيسية", callback_data="back_to_main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"❌ خطأ في إضافة المستخدم: {e}\n\n"
            "💡 يمكنك تجاهل هذا الخطأ والعودة للقائمة الرئيسية",
            reply_markup=reply_markup
        )
        return MAIN_MENU

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
        
        # تحديث WAREHOUSE_MANAGER_ID_2 في الذاكرة
        config.WAREHOUSE_MANAGER_ID_2 = user_id
        
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
        
        # تحديث قائمة ALLOWED_USERS في الذاكرة
        if user_id not in config.ALLOWED_USERS:
            config.ALLOWED_USERS.add(user_id)
        
        print(f"✅ تم تحديث ملف config.py بنجاح")
        
    except Exception as e:
        print(f"❌ خطأ في تحديث ملف config.py: {e}")

async def show_password_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة إدارة كلمات المرور"""
    keyboard = [
        [InlineKeyboardButton("➕ إضافة كلمة مرور", callback_data="add_password")],
        [InlineKeyboardButton("🎲 توليد كلمة مرور", callback_data="generate_password")],
        [InlineKeyboardButton("🔍 عرض كلمات المرور", callback_data="view_passwords")],
        [InlineKeyboardButton("✏️ تعديل كلمة مرور", callback_data="edit_password")],
        [InlineKeyboardButton("🗑️ حذف كلمة مرور", callback_data="delete_password")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_admin")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # الحصول على عدد كلمات المرور الموجودة
    passwords = db_manager.get_all_passwords()
    password_count = len(passwords)
    
    if update.callback_query:
        # عند استخدام callback_query، نعدل الرسالة الحالية
        await update.callback_query.edit_message_text(
            f"🔐 إدارة كلمات المرور\n\n"
            f"📊 إجمالي كلمات المرور: {password_count}\n\n"
            f"اختر العملية المطلوبة:\n\n"
            f"➕ إضافة كلمة مرور - إضافة كلمة مرور لموظف جديد\n"
            f"🎲 توليد كلمة مرور - توليد كلمة مرور عشوائية\n"
            f"🔍 عرض كلمات المرور - عرض جميع كلمات المرور المحفوظة\n"
            f"✏️ تعديل كلمة مرور - تغيير كلمة مرور موظف موجود\n"
            f"🗑️ حذف كلمة مرور - حذف كلمة مرور موظف",
            reply_markup=reply_markup
        )
    else:
        # عند استخدام message، نرسل رسالة جديدة
        await update.message.reply_text(
            f"🔐 إدارة كلمات المرور\n\n"
            f"📊 إجمالي كلمات المرور: {password_count}\n\n"
            f"اختر العملية المطلوبة:\n\n"
            f"➕ إضافة كلمة مرور - إضافة كلمة مرور لموظف جديد\n"
            f"🎲 توليد كلمة مرور - توليد كلمة مرور عشوائية\n"
            f"🔍 عرض كلمات المرور - عرض جميع كلمات المرور المحفوظة\n"
            f"✏️ تعديل كلمة مرور - تغيير كلمة مرور موظف موجود\n"
            f"🗑️ حذف كلمة مرور - حذف كلمة مرور موظف",
            reply_markup=reply_markup
        )

async def password_management_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار إدارة كلمات المرور"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "add_password":
        # عرض قائمة الموظفين لاختيار الموظف
        employees = db_manager.get_all_employees()
        if employees:
            keyboard = []
            for employee in employees:
                keyboard.append([InlineKeyboardButton(f"👤 {employee}", callback_data=f"select_employee_add_{employee}")])
            keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")])
            
            await query.edit_message_text(
                "➕ إضافة كلمة مرور جديدة\n\n"
                "اختر الموظف لإضافة كلمة المرور له:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                "❌ لا يوجد موظفين في النظام!\n\n"
                "يجب إضافة موظفين أولاً من قسم إدارة المستخدمين.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
                ]])
            )
        return PASSWORD_MANAGEMENT
    
    elif query.data == "generate_password":
        # عرض قائمة الموظفين لاختيار الموظف
        employees = db_manager.get_all_employees()
        if employees:
            keyboard = []
            for employee in employees:
                keyboard.append([InlineKeyboardButton(f"👤 {employee}", callback_data=f"select_employee_generate_{employee}")])
            keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")])
            
            await query.edit_message_text(
                "🎲 توليد كلمة مرور عشوائية\n\n"
                "اختر الموظف لتوليد كلمة مرور عشوائية له:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                "❌ لا يوجد موظفين في النظام!\n\n"
                "يجب إضافة موظفين أولاً من قسم إدارة المستخدمين.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
                ]])
            )
        return PASSWORD_MANAGEMENT
    
    elif query.data.startswith("select_employee_generate_"):
        employee = query.data.replace("select_employee_generate_", "")
        context.user_data['selected_employee'] = employee
        context.user_data['password_action'] = 'generate'
        
        # توليد كلمة مرور عشوائية
        import random
        import string
        
        # توليد كلمة مرور من 8 أحرف تحتوي على أحرف وأرقام
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # حفظ كلمة المرور
        if db_manager.set_employee_password(employee, password):
            keyboard = [
                [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"✅ تم توليد كلمة مرور عشوائية بنجاح!\n\n"
                f"👤 الموظف: {employee}\n"
                f"🔐 كلمة المرور الجديدة: {password}\n\n"
                f"💡 يرجى إبلاغ الموظف بكلمة المرور الجديدة.",
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"❌ فشل في توليد كلمة المرور لـ {employee}",
                reply_markup=reply_markup
            )
        return PASSWORD_MANAGEMENT
    
    elif query.data == "view_passwords":
        passwords = db_manager.get_all_passwords()
        if passwords:
            text = "🔍 كلمات المرور الحالية:\n\n"
            for i, (employee, password) in enumerate(passwords, 1):
                # إظهار كلمة المرور بشكل مقنع
                masked_password = password[0] + '*' * (len(password) - 2) + password[-1] if len(password) > 2 else '*' * len(password)
                text += f"{i}. 👤 {employee}\n   🔐 {masked_password}\n\n"
            
            text += f"📊 إجمالي كلمات المرور: {len(passwords)}"
        else:
            text = "❌ لا توجد كلمات مرور محفوظة."
        
        keyboard = [
            [InlineKeyboardButton("👁️ إظهار كلمات المرور", callback_data="show_passwords")],
            [InlineKeyboardButton("🔄 تحديث", callback_data="view_passwords")],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return PASSWORD_MANAGEMENT
    
    elif query.data == "show_passwords":
        passwords = db_manager.get_all_passwords()
        if passwords:
            text = "🔍 كلمات المرور الحالية (مفصلة):\n\n"
            for i, (employee, password) in enumerate(passwords, 1):
                text += f"{i}. 👤 {employee}\n   🔐 {password}\n\n"
            
            text += f"📊 إجمالي كلمات المرور: {len(passwords)}"
        else:
            text = "❌ لا توجد كلمات مرور محفوظة."
        
        keyboard = [
            [InlineKeyboardButton("🙈 إخفاء كلمات المرور", callback_data="view_passwords")],
            [InlineKeyboardButton("🔄 تحديث", callback_data="show_passwords")],
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return PASSWORD_MANAGEMENT
    
    elif query.data == "edit_password":
        # عرض قائمة الموظفين الذين لديهم كلمات مرور
        employees_with_passwords = db_manager.get_employees_with_passwords()
        if employees_with_passwords:
            keyboard = []
            for employee in employees_with_passwords:
                keyboard.append([InlineKeyboardButton(f"👤 {employee}", callback_data=f"select_employee_edit_{employee}")])
            keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")])
            
            await query.edit_message_text(
                "✏️ تعديل كلمة مرور\n\n"
                "اختر الموظف لتعديل كلمة المرور الخاصة به:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                "❌ لا توجد كلمات مرور محفوظة!\n\n"
                "يجب إضافة كلمات مرور أولاً.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
                ]])
            )
        return PASSWORD_MANAGEMENT
    
    elif query.data == "delete_password":
        # عرض قائمة الموظفين الذين لديهم كلمات مرور
        employees_with_passwords = db_manager.get_employees_with_passwords()
        if employees_with_passwords:
            keyboard = []
            for employee in employees_with_passwords:
                keyboard.append([InlineKeyboardButton(f"🗑️ {employee}", callback_data=f"select_employee_delete_{employee}")])
            keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")])
            
            await query.edit_message_text(
                "🗑️ حذف كلمة مرور\n\n"
                "اختر الموظف لحذف كلمة المرور الخاصة به:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                "❌ لا توجد كلمات مرور محفوظة!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
                ]])
            )
        return PASSWORD_MANAGEMENT
    
    elif query.data.startswith("select_employee_add_"):
        employee = query.data.replace("select_employee_add_", "")
        context.user_data['selected_employee'] = employee
        context.user_data['password_action'] = 'add'
        
        await query.edit_message_text(
            f"➕ إضافة كلمة مرور لـ {employee}\n\n"
            "الرجاء إدخال كلمة المرور الجديدة:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
            ]])
        )
        return PASSWORD_MANAGEMENT
    
    elif query.data.startswith("select_employee_edit_"):
        employee = query.data.replace("select_employee_edit_", "")
        context.user_data['selected_employee'] = employee
        context.user_data['password_action'] = 'edit'
        
        # عرض كلمة المرور الحالية
        current_password = db_manager.get_employee_password(employee)
        if current_password:
            masked_password = current_password[0] + '*' * (len(current_password) - 2) + current_password[-1] if len(current_password) > 2 else '*' * len(current_password)
            await query.edit_message_text(
                f"✏️ تعديل كلمة مرور لـ {employee}\n\n"
                f"كلمة المرور الحالية: {masked_password}\n\n"
                "الرجاء إدخال كلمة المرور الجديدة:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
                ]])
            )
        else:
            await query.edit_message_text(
                f"❌ لا توجد كلمة مرور لـ {employee}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
                ]])
            )
        return PASSWORD_MANAGEMENT
    
    elif query.data.startswith("select_employee_delete_"):
        employee = query.data.replace("select_employee_delete_", "")
        context.user_data['selected_employee'] = employee
        
        # طلب تأكيد الحذف
        keyboard = [
            [InlineKeyboardButton("✅ نعم، احذف", callback_data=f"confirm_delete_{employee}")],
            [InlineKeyboardButton("❌ لا، إلغاء", callback_data="back_to_password_menu")]
        ]
        
        await query.edit_message_text(
            f"🗑️ تأكيد حذف كلمة المرور\n\n"
            f"هل أنت متأكد من حذف كلمة المرور الخاصة بـ {employee}؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return PASSWORD_MANAGEMENT
    
    elif query.data.startswith("confirm_delete_"):
        employee = query.data.replace("confirm_delete_", "")
        
        if db_manager.delete_employee_password(employee):
            await query.edit_message_text(
                f"✅ تم حذف كلمة المرور بنجاح!\n\n"
                f"الموظف: {employee}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
                ]])
            )
        else:
            await query.edit_message_text(
                f"❌ فشل في حذف كلمة المرور لـ {employee}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")
                ]])
            )
        return PASSWORD_MANAGEMENT
    
    elif query.data == "back_to_password_menu":
        return await show_password_management_menu(update, context)
    
    elif query.data == "back_to_admin":
        return await show_admin_menu(update, context)
    
    # إضافة return افتراضي
    return PASSWORD_MANAGEMENT

async def password_management_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدارة كلمات المرور"""
    text = update.message.text.strip()
    action = context.user_data.get('password_action', '')
    selected_employee = context.user_data.get('selected_employee', '')
    
    if action == 'add':
        try:
            if not text:
                keyboard = [
                    [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "❌ كلمة المرور فارغة!\n\n"
                    "الرجاء إدخال كلمة مرور صحيحة.",
                    reply_markup=reply_markup
                )
                return PASSWORD_MANAGEMENT
            
            if len(text) < 4:
                keyboard = [
                    [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "❌ كلمة المرور قصيرة جداً!\n\n"
                    "يجب أن تكون كلمة المرور 4 أحرف على الأقل.",
                    reply_markup=reply_markup
                )
                return PASSWORD_MANAGEMENT
            
            if db_manager.set_employee_password(selected_employee, text):
                keyboard = [
                    [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    f"✅ تم إضافة كلمة المرور بنجاح!\n\n"
                    f"👤 الموظف: {selected_employee}\n"
                    f"🔐 كلمة المرور: {text}",
                    reply_markup=reply_markup
                )
            else:
                keyboard = [
                    [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "❌ فشل في إضافة كلمة المرور.",
                    reply_markup=reply_markup
                )
            
        except Exception as e:
            keyboard = [
                [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"❌ خطأ: {e}",
                reply_markup=reply_markup
            )
    
    elif action == 'edit':
        try:
            if not text:
                keyboard = [
                    [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "❌ كلمة المرور فارغة!\n\n"
                    "الرجاء إدخال كلمة مرور صحيحة.",
                    reply_markup=reply_markup
                )
                return PASSWORD_MANAGEMENT
            
            if len(text) < 4:
                keyboard = [
                    [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "❌ كلمة المرور قصيرة جداً!\n\n"
                    "يجب أن تكون كلمة المرور 4 أحرف على الأقل.",
                    reply_markup=reply_markup
                )
                return PASSWORD_MANAGEMENT
            
            if db_manager.set_employee_password(selected_employee, text):
                keyboard = [
                    [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    f"✅ تم تحديث كلمة المرور بنجاح!\n\n"
                    f"👤 الموظف: {selected_employee}\n"
                    f"🔐 كلمة المرور الجديدة: {text}",
                    reply_markup=reply_markup
                )
            else:
                keyboard = [
                    [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "❌ فشل في تحديث كلمة المرور.",
                    reply_markup=reply_markup
                )
            
        except Exception as e:
            keyboard = [
                [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"❌ خطأ: {e}",
                reply_markup=reply_markup
            )
    
    # إذا لم يكن هناك action محدد، إعادة توجيه للقائمة الرئيسية
    if not action:
        keyboard = [
            [InlineKeyboardButton("🔙 العودة", callback_data="back_to_password_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ لا يوجد إجراء محدد!\n\n"
            "الرجاء اختيار إجراء من القائمة.",
            reply_markup=reply_markup
        )
        return PASSWORD_MANAGEMENT
    
    # مسح البيانات من الذاكرة فقط بعد نجاح العملية
    if action in ['add', 'edit']:
        context.user_data.pop('password_action', None)
        context.user_data.pop('selected_employee', None)
    
    return PASSWORD_MANAGEMENT

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

async def retry_failed_api_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إعادة المحاولة للطلبات الفاشلة في API"""
    try:
        # إرسال رسالة "جاري المعالجة"
        await update.callback_query.answer("🔄 جاري إعادة المحاولة...")

        # الحصول على الطلبات الفاشلة
        failed_orders = db_manager.get_failed_api_orders()

        if not failed_orders:
            await update.callback_query.message.reply_text(
                "✅ لا توجد طلبات فاشلة لإعادة المحاولة!"
            )
            return await show_admin_menu(update, context)

        # إعادة المحاولة للطلبات الفاشلة
        success_count = 0
        failed_count = 0
        error_details = []

        for order in failed_orders:
            try:
                # الحصول على بيانات الفاتورة الكاملة
                invoice_data = db_manager.get_invoice_by_receipt(order['receipt_number'])
                if invoice_data:
                    # إعادة إرسال الطلب إلى API
                    api_result = api_manager.send_order_to_api(invoice_data)

                    # تحديث عدد المحاولات
                    db_manager.update_api_order_retry(order['receipt_number'])

                    if api_result.get('success'):
                        success_count += 1
                        # تسجيل النجاح
                        db_manager.record_api_order(
                            invoice_data.get('id'),
                            order['receipt_number'],
                            api_result
                        )
                    else:
                        failed_count += 1
                        error_details.append(f"• {order['receipt_number']}: {api_result.get('message', 'خطأ غير معروف')}")
                else:
                    failed_count += 1
                    error_details.append(f"• {order['receipt_number']}: لم يتم العثور على بيانات الفاتورة")
            except Exception as e:
                failed_count += 1
                error_details.append(f"• {order['receipt_number']}: {str(e)}")

        # رسالة النتيجة
        result_text = f"""
🔄 إعادة المحاولة للطلبات الفاشلة
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 النتائج:
✅ نجح: {success_count} طلب
❌ فشل: {failed_count} طلب
📋 إجمالي: {len(failed_orders)} طلب
"""

        if success_count > 0:
            result_text += "\n🎉 تم إعادة إرسال بعض الطلبات بنجاح!"

        if failed_count > 0:
            result_text += f"\n⚠️ {failed_count} طلب لا يزال فاشلاً"
            if error_details:
                result_text += "\n\n📋 تفاصيل الأخطاء:\n" + "\n".join(error_details[:5])  # عرض أول 5 أخطاء فقط
                if len(error_details) > 5:
                    result_text += f"\n... و {len(error_details) - 5} خطأ آخر"

        await update.callback_query.message.reply_text(result_text)
        return await show_admin_menu(update, context)

    except Exception as e:
        await update.callback_query.message.reply_text(
            f"❌ خطأ في إعادة المحاولة: {str(e)}"
        )
        return await show_admin_menu(update, context)

async def system_settings_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار إعدادات النظام"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "delete_old_invoices":
        return await delete_old_invoices_handler(update, context)
    elif query.data == "reset_statistics":
        return await reset_statistics_handler(update, context)
    elif query.data == "reset_system":
        return await reset_system_handler(update, context)
    elif query.data == "back_to_admin":
        # إرسال رسالة جديدة مع القائمة الرئيسية
        await update.callback_query.message.reply_text(
            "اختر الخدمة التالية:",
            reply_markup=ReplyKeyboardMarkup([
                ["🔙 العودة للقائمة الرئيسية", "📝 إضافة فاتورة", "📊 الإحصائيات"],
                ["📋 تحميل ملف الطلبات", "🔄 إدارة المرتجعات", "👤 إدارة المستخدمين"],
                ["🔐 إدارة كلمات المرور", "⚙️ إعدادات النظام"]
            ], one_time_keyboard=True, resize_keyboard=True)
        )
        return ADMIN_MENU

async def delete_old_invoices_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج حذف الفواتير القديمة"""
    try:
        # الحصول على إحصائيات النظام قبل الحذف
        stats_before = db_manager.get_system_stats()
        
        # إرسال رسالة تأكيد
        await update.callback_query.answer("🗑️ جاري حذف الفواتير القديمة...")
        
        # حذف الفواتير والإحصائيات
        result = db_manager.delete_old_invoices()
        
        if result.get('success'):
            # الحصول على إحصائيات النظام بعد الحذف
            stats_after = db_manager.get_system_stats()
            
            result_text = f"""
🗑️ تم حذف الفواتير القديمة بنجاح!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 ما تم حذفه:
• الفواتير: {result['invoices_deleted']} فاتورة
• سجلات API: {result['api_orders_deleted']} سجل
• المرتجعات: {result['returns_deleted']} مرتجع
• الإحصائيات اليومية: {result['stats_deleted']} سجل
• إحصائيات الشحن: {result['shipping_stats_deleted']} سجل

✅ تم الاحتفاظ بـ:
• المستخدمين: {stats_after['users_count']} مستخدم
• كلمات المرور: {stats_after['passwords_count']} كلمة مرور

📈 حالة النظام الحالية:
• الفواتير: {stats_after['invoices_count']} فاتورة
• المرتجعات: {stats_after['returns_count']} مرتجع
• سجلات API: {stats_after['api_orders_count']} سجل
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        else:
            result_text = f"""
❌ فشل في حذف الفواتير القديمة!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ السبب: {result.get('error', 'خطأ غير معروف')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        await update.callback_query.message.reply_text(result_text)
        # إرسال رسالة جديدة مع القائمة الرئيسية
        await update.callback_query.message.reply_text(
            "اختر الخدمة التالية:",
            reply_markup=ReplyKeyboardMarkup([
                ["🔙 العودة للقائمة الرئيسية", "📝 إضافة فاتورة", "📊 الإحصائيات"],
                ["📋 تحميل ملف الطلبات", "🔄 إدارة المرتجعات", "👤 إدارة المستخدمين"],
                ["🔐 إدارة كلمات المرور", "⚙️ إعدادات النظام"]
            ], one_time_keyboard=True, resize_keyboard=True)
        )
        return ADMIN_MENU
        
    except Exception as e:
        await update.callback_query.message.reply_text(
            f"❌ خطأ في حذف الفواتير القديمة: {str(e)}"
        )
        # إرسال رسالة جديدة مع القائمة الرئيسية
        await update.callback_query.message.reply_text(
            "اختر الخدمة التالية:",
            reply_markup=ReplyKeyboardMarkup([
                ["🔙 العودة للقائمة الرئيسية", "📝 إضافة فاتورة", "📊 الإحصائيات"],
                ["📋 تحميل ملف الطلبات", "🔄 إدارة المرتجعات", "👤 إدارة المستخدمين"],
                ["🔐 إدارة كلمات المرور", "⚙️ إعدادات النظام"]
            ], one_time_keyboard=True, resize_keyboard=True)
        )
        return ADMIN_MENU

async def reset_statistics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج تصفير الإحصائيات"""
    try:
        # إرسال رسالة تأكيد
        await update.callback_query.answer("📊 جاري تصفير الإحصائيات...")
        
        # تصفير الإحصائيات
        result = db_manager.reset_statistics_only()
        
        if result.get('success'):
            result_text = f"""
📊 تم تصفير الإحصائيات بنجاح!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 ما تم تصفيره:
• الإحصائيات اليومية: {result['stats_deleted']} سجل
• إحصائيات الشحن: {result['shipping_stats_deleted']} سجل

✅ تم الاحتفاظ بـ:
• جميع الفواتير
• جميع المرتجعات
• جميع سجلات API
• جميع المستخدمين
• جميع كلمات المرور
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        else:
            result_text = f"""
❌ فشل في تصفير الإحصائيات!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ السبب: {result.get('error', 'خطأ غير معروف')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        await update.callback_query.message.reply_text(result_text)
        # إرسال رسالة جديدة مع القائمة الرئيسية
        await update.callback_query.message.reply_text(
            "اختر الخدمة التالية:",
            reply_markup=ReplyKeyboardMarkup([
                ["🔙 العودة للقائمة الرئيسية", "📝 إضافة فاتورة", "📊 الإحصائيات"],
                ["📋 تحميل ملف الطلبات", "🔄 إدارة المرتجعات", "👤 إدارة المستخدمين"],
                ["🔐 إدارة كلمات المرور", "⚙️ إعدادات النظام"]
            ], one_time_keyboard=True, resize_keyboard=True)
        )
        return ADMIN_MENU
        
    except Exception as e:
        await update.callback_query.message.reply_text(
            f"❌ خطأ في تصفير الإحصائيات: {str(e)}"
        )
        # إرسال رسالة جديدة مع القائمة الرئيسية
        await update.callback_query.message.reply_text(
            "اختر الخدمة التالية:",
            reply_markup=ReplyKeyboardMarkup([
                ["🔙 العودة للقائمة الرئيسية", "📝 إضافة فاتورة", "📊 الإحصائيات"],
                ["📋 تحميل ملف الطلبات", "🔄 إدارة المرتجعات", "👤 إدارة المستخدمين"],
                ["🔐 إدارة كلمات المرور", "⚙️ إعدادات النظام"]
            ], one_time_keyboard=True, resize_keyboard=True)
        )
        return ADMIN_MENU

async def reset_system_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إعادة تعيين النظام"""
    try:
        # الحصول على إحصائيات النظام قبل الحذف
        stats_before = db_manager.get_system_stats()
        
        # إرسال رسالة تأكيد
        await update.callback_query.answer("🔄 جاري إعادة تعيين النظام...")
        
        # إعادة تعيين النظام
        result = db_manager.reset_system_complete()
        
        if result.get('success'):
            # الحصول على إحصائيات النظام بعد الحذف
            stats_after = db_manager.get_system_stats()
            
            result_text = f"""
🔄 تم إعادة تعيين النظام بنجاح!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗑️ ما تم حذفه:
• الفواتير: {result['invoices_deleted']} فاتورة
• سجلات API: {result['api_orders_deleted']} سجل
• المرتجعات: {result['returns_deleted']} مرتجع
• الإحصائيات اليومية: {result['stats_deleted']} سجل
• إحصائيات الشحن: {result['shipping_stats_deleted']} سجل
• كلمات المرور: {result['passwords_deleted']} كلمة مرور

✅ تم الاحتفاظ بـ:
• المستخدمين: {stats_after['users_count']} مستخدم

📈 حالة النظام الحالية:
• الفواتير: {stats_after['invoices_count']} فاتورة
• المرتجعات: {stats_after['returns_count']} مرتجع
• سجلات API: {stats_after['api_orders_count']} سجل
• كلمات المرور: {stats_after['passwords_count']} كلمة مرور
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ تحذير: تم حذف جميع البيانات ما عدا المستخدمين!
"""
        else:
            result_text = f"""
❌ فشل في إعادة تعيين النظام!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ السبب: {result.get('error', 'خطأ غير معروف')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        await update.callback_query.message.reply_text(result_text)
        # إرسال رسالة جديدة مع القائمة الرئيسية
        await update.callback_query.message.reply_text(
            "اختر الخدمة التالية:",
            reply_markup=ReplyKeyboardMarkup([
                ["🔙 العودة للقائمة الرئيسية", "📝 إضافة فاتورة", "📊 الإحصائيات"],
                ["📋 تحميل ملف الطلبات", "🔄 إدارة المرتجعات", "👤 إدارة المستخدمين"],
                ["🔐 إدارة كلمات المرور", "⚙️ إعدادات النظام"]
            ], one_time_keyboard=True, resize_keyboard=True)
        )
        return ADMIN_MENU
        
    except Exception as e:
        await update.callback_query.message.reply_text(
            f"❌ خطأ في إعادة تعيين النظام: {str(e)}"
        )
        # إرسال رسالة جديدة مع القائمة الرئيسية
        await update.callback_query.message.reply_text(
            "اختر الخدمة التالية:",
            reply_markup=ReplyKeyboardMarkup([
                ["🔙 العودة للقائمة الرئيسية", "📝 إضافة فاتورة", "📊 الإحصائيات"],
                ["📋 تحميل ملف الطلبات", "🔄 إدارة المرتجعات", "👤 إدارة المستخدمين"],
                ["🔐 إدارة كلمات المرور", "⚙️ إعدادات النظام"]
            ], one_time_keyboard=True, resize_keyboard=True)
        )
        return ADMIN_MENU

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
                    MessageHandler(filters.TEXT & ~filters.COMMAND, add_invoice_single_handler),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                ADMIN_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, admin_menu_handler)
                ],
                STATISTICS_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, statistics_menu_handler)
                ],
                STATISTICS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, statistics_handler),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                STATISTICS_PASSWORD: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, statistics_password_handler),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                STATISTICS_DATE_SELECTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, statistics_date_selection_handler),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                STATISTICS_EXPORT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: show_admin_menu(u, c)),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                ALL_EMPLOYEES_DATE_SELECTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, all_employees_date_selection_handler),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                USER_MANAGEMENT_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, user_management_handler),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                ADD_USER_ROLE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, user_management_handler),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                ADD_USER_DATA: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, user_management_handler),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                PASSWORD_MANAGEMENT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, password_management_handler),
                    CallbackQueryHandler(password_management_callback_handler, pattern="^(add_password|generate_password|view_passwords|show_passwords|edit_password|delete_password|back_to_password_menu|back_to_admin|select_employee_add_|select_employee_generate_|select_employee_edit_|select_employee_delete_|confirm_delete_)$"),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                RETURNS_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: show_returns_management_menu(u, c)),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                RETURN_INVOICE_SELECTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, return_invoice_selection_handler),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                RETURN_TYPE_SELECTION: [
                    CallbackQueryHandler(return_type_callback_handler),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                RETURN_QUANTITY_INPUT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, return_quantity_input_handler),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
                RETURN_REASON_INPUT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, return_reason_input_handler),
                    CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$")
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)]
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
        app.add_handler(CallbackQueryHandler(shipping_callback_handler, pattern="^(shipping_all|shipping_1|shipping_2|shipping_7|shipping_30|shipping_90|shipping_new|back_to_main_menu)$"))
        app.add_handler(CallbackQueryHandler(password_management_callback_handler, pattern="^(add_password|generate_password|view_passwords|show_passwords|edit_password|delete_password|back_to_password_menu|back_to_admin|select_employee_add_|select_employee_generate_|select_employee_edit_|select_employee_delete_|confirm_delete_)$"))
        app.add_handler(CallbackQueryHandler(returns_management_callback_handler, pattern="^(add_return|view_returns|stats_with_returns|back_to_returns_menu|back_to_admin)$"))
        app.add_handler(CallbackQueryHandler(return_type_callback_handler, pattern="^(return_full|return_partial|back_to_returns_menu)$"))
        app.add_handler(CallbackQueryHandler(statistics_menu_callback_handler, pattern="^(back_to_statistics_menu)$"))
        app.add_handler(CallbackQueryHandler(date_selection_callback_handler, pattern="^(date_today|date_week|date_month|date_year|date_custom)_"))
        app.add_handler(CallbackQueryHandler(all_employees_date_callback_handler, pattern="^(all_employees_date_today|all_employees_date_week|all_employees_date_month|all_employees_date_year|all_employees_date_custom)$"))
        app.add_handler(CallbackQueryHandler(input_screens_callback_handler, pattern="^(back_to_admin|back_to_main_menu)$"))
        
        # إضافة معالج عام للأزرار التفاعلية للتعامل مع الأزرار غير المعالجة
        async def general_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """معالج عام للأزرار التفاعلية"""
            query = update.callback_query
            await query.answer()
            
            if query.data == "retry_failed_orders":
                return await retry_failed_api_orders(update, context)
            elif query.data == "back_to_returns_menu":
                return await show_returns_management_menu(update, context)
            elif query.data == "back_to_admin_menu":
                return await start(update, context)
            elif query.data == "back_to_user_management":
                return await start(update, context)
            elif query.data == "back_to_password_menu":
                return await start(update, context)
            elif query.data in ["add_password", "generate_password", "view_passwords", "show_passwords", "edit_password", "delete_password"]:
                # إعادة توجيه لأزرار إدارة كلمات المرور
                return await password_management_callback_handler(update, context)
            elif query.data.startswith("select_employee_") or query.data.startswith("confirm_delete_"):
                # إعادة توجيه لأزرار اختيار الموظفين
                return await password_management_callback_handler(update, context)
            elif query.data.startswith("shipping_"):
                # إعادة توجيه لأزرار الشحن
                return await shipping_callback_handler(update, context)
            elif query.data in ["delete_old_invoices", "reset_statistics", "reset_system", "back_to_admin"]:
                # إعادة توجيه لأزرار إعدادات النظام
                return await system_settings_callback_handler(update, context)
            else:
                await query.answer("⚠️ هذا الزر غير متاح حالياً")
        
        # إضافة معالج إعدادات النظام
        app.add_handler(CallbackQueryHandler(system_settings_callback_handler))
        
        # إضافة معالج عام للأزرار التفاعلية (يجب أن يكون آخراً)
        app.add_handler(CallbackQueryHandler(general_callback_handler))
        
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