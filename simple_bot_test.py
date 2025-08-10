import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simple start command"""
    await update.message.reply_text("مرحباً! البوت يعمل بشكل صحيح! 🎉")

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test command to verify bot is working"""
    await update.message.reply_text("✅ البوت يستجيب بشكل صحيح!")

async def main():
    """Main function"""
    print("🚀 بدء تشغيل البوت التجريبي...")
    
    # إنشاء التطبيق
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("test", test_command))
    
    print("✅ البوت جاهز للاختبار!")
    print("📱 جرب إرسال /start أو /test في تيليجرام")
    
    # تشغيل البوت
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main()) 