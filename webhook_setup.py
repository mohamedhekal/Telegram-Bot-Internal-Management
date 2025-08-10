#!/usr/bin/env python3
"""
إعداد Webhook للبوت
"""

import asyncio
import ssl
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN

# متغيرات Webhook
WEBHOOK_URL = "https://your-domain.com/webhook"  # استبدل بعنوانك
WEBHOOK_PATH = "/webhook"
WEBHOOK_PORT = 8443

# إنشاء التطبيق
app = Application.builder().token(TELEGRAM_TOKEN).build()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البداية"""
    await update.message.reply_text("مرحباً! البوت يعمل مع Webhook! 🎉")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة"""
    help_text = """
🤖 **أوامر البوت:**

/start - بدء البوت
/help - عرض هذه المساعدة
/webhook_info - معلومات Webhook
/set_webhook - إعداد Webhook
/delete_webhook - حذف Webhook

📊 **الميزات المتاحة:**
- إدارة المرتجعات
- إحصائيات الموظفين
- حماية بكلمات مرور
- تصدير التقارير
    """
    await update.message.reply_text(help_text)

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

async def set_webhook_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إعداد Webhook"""
    try:
        # التحقق من أن المستخدم مدير
        user_id = update.message.from_user.id
        if user_id not in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
            await update.message.reply_text("❌ عذراً، هذا الأمر متاح للمديرين فقط")
            return
        
        # إعداد Webhook
        success = await context.bot.set_webhook(url=WEBHOOK_URL)
        if success:
            await update.message.reply_text(f"✅ تم إعداد Webhook بنجاح!\n🔗 الرابط: {WEBHOOK_URL}")
        else:
            await update.message.reply_text("❌ فشل في إعداد Webhook")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في إعداد Webhook: {e}")

async def delete_webhook_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف Webhook"""
    try:
        # التحقق من أن المستخدم مدير
        user_id = update.message.from_user.id
        if user_id not in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3]:
            await update.message.reply_text("❌ عذراً، هذا الأمر متاح للمديرين فقط")
            return
        
        # حذف Webhook
        success = await context.bot.delete_webhook()
        if success:
            await update.message.reply_text("✅ تم حذف Webhook بنجاح!")
        else:
            await update.message.reply_text("❌ فشل في حذف Webhook")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في حذف Webhook: {e}")

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
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("webhook_info", webhook_info_command))
    app.add_handler(CommandHandler("set_webhook", set_webhook_command))
    app.add_handler(CommandHandler("delete_webhook", delete_webhook_command))
    
    # إنشاء خادم Web
    web_app = web.Application()
    web_app.router.add_post(WEBHOOK_PATH, webhook_handler)
    
    # إعداد SSL (مطلوب لـ Telegram)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain('cert.pem', 'private.key')  # استبدل بملفات الشهادة الخاصة بك
    
    print(f"✅ البوت جاهز للعمل مع Webhook!")
    print(f"🔗 عنوان Webhook: {WEBHOOK_URL}")
    print(f"📡 المنفذ: {WEBHOOK_PORT}")
    
    # تشغيل الخادم
    web.run_app(web_app, port=WEBHOOK_PORT, ssl_context=context)

if __name__ == "__main__":
    asyncio.run(main()) 