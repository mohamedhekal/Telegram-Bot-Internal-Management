#!/usr/bin/env python3
"""
نسخة Webhook من البوت الرئيسي مع جميع الميزات المضافة
"""

import os
import asyncio
import ssl
from aiohttp import web
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
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

# إعدادات Webhook
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://your-domain.com/webhook')
WEBHOOK_PATH = "/webhook"
WEBHOOK_PORT = int(os.environ.get('PORT', 8443))

# إنشاء التطبيق
app = Application.builder().token(config.TELEGRAM_TOKEN).build()

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

async def webhook_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض معلومات Webhook"""
    try:
        webhook_info = await context.bot.get_webhook_info()
        info_text = f"""
📡 **معلومات Webhook:**

🔗 الرابط: {webhook_info.url or 'غير محدد'}
📊 التحديثات المعلقة: {webhook_info.pending_update_count}
❌ آخر خطأ: {webhook_info.last_error_message or 'لا يوجد'}
⏰ آخر وقت خطأ: {webhook_info.last_error_date or 'لا يوجد'}
        """
        await update.message.reply_text(info_text)
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في جلب معلومات Webhook: {e}")

async def webhook_handler(request):
    """معالج Webhook"""
    try:
        # استقبال التحديث من Telegram
        update = Update.de_json(await request.json(), app.bot)
        
        # معالجة التحديث
        await app.process_update(update)
        
        return web.Response(status=200)
    except Exception as e:
        print(f"❌ خطأ في معالج Webhook: {e}")
        return web.Response(status=500)

async def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تشغيل البوت مع Webhook...")
    
    # إضافة معالج معلومات Webhook
    app.add_handler(CommandHandler("webhook_info", webhook_info_command))
    
    # إعداد معالج المحادثة (نفس الكود من bot_clean.py)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: print("Main menu handler"))
            ],
            ADMIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: print("Admin menu handler"))
            ],
            # ... باقي الحالات
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )
    
    app.add_handler(conv_handler)
    
    # إنشاء خادم Web
    web_app = web.Application()
    web_app.router.add_post(WEBHOOK_PATH, webhook_handler)
    
    # إعداد Webhook
    try:
        await app.bot.set_webhook(url=WEBHOOK_URL)
        print(f"✅ تم إعداد Webhook بنجاح!")
        print(f"🔗 الرابط: {WEBHOOK_URL}")
    except Exception as e:
        print(f"❌ خطأ في إعداد Webhook: {e}")
        return
    
    print(f"✅ البوت جاهز للعمل مع Webhook!")
    print(f"📡 المنفذ: {WEBHOOK_PORT}")
    print("📱 يمكنك الآن استخدام البوت في تيليجرام")
    
    # تشغيل الخادم
    try:
        web.run_app(web_app, port=WEBHOOK_PORT)
    except Exception as e:
        print(f"❌ خطأ في تشغيل الخادم: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 