# دليل استخدام Webhook للبوت 🤖

## ما هو Webhook؟

Webhook هو طريقة لتلقي التحديثات من Telegram حيث يرسل Telegram التحديثات مباشرة إلى خادمك بدلاً من أن يطلب البوت التحديثات باستمرار.

### مميزات Webhook:
- ⚡ **أسرع استجابة** - التحديثات تصل فوراً
- 💾 **أقل استهلاك موارد** - لا حاجة للاستطلاع المستمر
- 🔒 **أكثر أماناً** - اتصال مباشر ومشفر
- 📊 **أفضل للأداء** - مناسب للبوتات عالية الاستخدام

## الخيارات المتاحة لك:

### 1. **Ngrok (للاختبار المحلي)** 🧪

#### التثبيت:
```bash
# على macOS
brew install ngrok

# أو تحميل مباشر من
# https://ngrok.com/download
```

#### الاستخدام:
```bash
# تشغيل نفق آمن
ngrok http 8443

# ستحصل على رابط مثل:
# https://abc123.ngrok.io
```

#### إعداد البوت:
```python
WEBHOOK_URL = "https://abc123.ngrok.io/webhook"
```

### 2. **Heroku (مجاني للاستخدام البسيط)** ☁️

#### إنشاء تطبيق:
```bash
# تثبيت Heroku CLI
brew install heroku

# تسجيل الدخول
heroku login

# إنشاء تطبيق
heroku create your-bot-name

# رفع الكود
git add .
git commit -m "Add webhook support"
git push heroku main
```

#### إعداد متغيرات البيئة:
```bash
heroku config:set TELEGRAM_TOKEN=your_bot_token
```

### 3. **Railway (سهل وسريع)** 🚄

#### الخطوات:
1. اذهب إلى [railway.app](https://railway.app)
2. اربط حساب GitHub
3. اختر المستودع
4. أضف متغيرات البيئة
5. انشر التطبيق

### 4. **Render (مجاني)** 🎨

#### الخطوات:
1. اذهب إلى [render.com](https://render.com)
2. اربط حساب GitHub
3. اختر "Web Service"
4. اختر المستودع
5. أضف متغيرات البيئة

## إعداد البوت مع Webhook:

### 1. **تعديل ملف التكوين:**
```python
# config.py
TELEGRAM_TOKEN = "your_bot_token"
WEBHOOK_URL = "https://your-domain.com/webhook"
WEBHOOK_PORT = 8443
```

### 2. **إنشاء ملف requirements.txt:**
```
python-telegram-bot==20.7
aiohttp==3.9.1
pandas
openpyxl
```

### 3. **إنشاء ملف Procfile (لـ Heroku):**
```
web: python3 webhook_bot.py
```

### 4. **إنشاء ملف webhook_bot.py:**
```python
import os
import asyncio
import ssl
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN

# إعداد Webhook
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://your-domain.com/webhook')
WEBHOOK_PATH = "/webhook"
WEBHOOK_PORT = int(os.environ.get('PORT', 8443))

# إنشاء التطبيق
app = Application.builder().token(TELEGRAM_TOKEN).build()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً! البوت يعمل مع Webhook! 🎉")

async def webhook_handler(request):
    """معالج Webhook"""
    try:
        update = Update.de_json(await request.json(), app.bot)
        await app.process_update(update)
        return web.Response(status=200)
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return web.Response(status=500)

async def main():
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start_command))
    
    # إنشاء خادم Web
    web_app = web.Application()
    web_app.router.add_post(WEBHOOK_PATH, webhook_handler)
    
    # إعداد Webhook
    await app.bot.set_webhook(url=WEBHOOK_URL)
    
    print(f"✅ البوت جاهز! Webhook: {WEBHOOK_URL}")
    
    # تشغيل الخادم
    web.run_app(web_app, port=WEBHOOK_PORT)

if __name__ == "__main__":
    asyncio.run(main())
```

## خطوات التشغيل:

### للاختبار المحلي مع Ngrok:

1. **تشغيل Ngrok:**
```bash
ngrok http 8443
```

2. **نسخ الرابط** (مثل: `https://abc123.ngrok.io`)

3. **تعديل WEBHOOK_URL:**
```python
WEBHOOK_URL = "https://abc123.ngrok.io/webhook"
```

4. **تشغيل البوت:**
```bash
python3 webhook_bot.py
```

### للنشر على Heroku:

1. **إنشاء تطبيق Heroku:**
```bash
heroku create your-bot-name
```

2. **إعداد متغيرات البيئة:**
```bash
heroku config:set TELEGRAM_TOKEN=your_bot_token
heroku config:set WEBHOOK_URL=https://your-bot-name.herokuapp.com/webhook
```

3. **رفع الكود:**
```bash
git add .
git commit -m "Add webhook support"
git push heroku main
```

## أوامر مفيدة:

### عرض معلومات Webhook:
```python
webhook_info = await bot.get_webhook_info()
print(f"URL: {webhook_info.url}")
print(f"Pending updates: {webhook_info.pending_update_count}")
```

### حذف Webhook:
```python
await bot.delete_webhook()
```

### إعداد Webhook:
```python
await bot.set_webhook(url="https://your-domain.com/webhook")
```

## استكشاف الأخطاء:

### مشكلة: "Invalid webhook URL"
- تأكد من أن الرابط يبدأ بـ `https://`
- تأكد من أن المنفذ مفتوح
- تأكد من صحة الشهادة SSL

### مشكلة: "Webhook was set by a different bot"
- احذف Webhook الحالي أولاً
- استخدم توكن البوت الصحيح

### مشكلة: "Connection timeout"
- تحقق من إعدادات الجدار الناري
- تأكد من أن الخادم متاح من الإنترنت

## نصائح مهمة:

1. **استخدم HTTPS دائماً** - Telegram يتطلب شهادة SSL
2. **اختبر محلياً أولاً** - استخدم Ngrok للاختبار
3. **راقب السجلات** - تحقق من الأخطاء بانتظام
4. **احتفظ بنسخة احتياطية** - من إعدادات Webhook
5. **استخدم متغيرات البيئة** - لحماية المعلومات الحساسة

## مثال كامل للاستخدام:

```python
# webhook_example.py
import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get('TELEGRAM_TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

app = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً! البوت يعمل! 🎉")

async def webhook_handler(request):
    update = Update.de_json(await request.json(), app.bot)
    await app.process_update(update)
    return web.Response(status=200)

async def main():
    app.add_handler(CommandHandler("start", start))
    
    web_app = web.Application()
    web_app.router.add_post("/webhook", webhook_handler)
    
    await app.bot.set_webhook(url=WEBHOOK_URL)
    
    web.run_app(web_app, port=int(os.environ.get('PORT', 8443)))

if __name__ == "__main__":
    asyncio.run(main())
```

---

**ملاحظة:** Webhook يتطلب خادم عام مع عنوان IP ثابت وشهادة SSL. للاختبار المحلي، استخدم Ngrok. للإنتاج، استخدم منصة سحابية مثل Heroku أو Railway. 