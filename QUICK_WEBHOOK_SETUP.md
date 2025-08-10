# دليل سريع لإعداد Webhook 🚀

## الخيار الأسهل: Ngrok (للاختبار)

### 1. تثبيت Ngrok:
```bash
brew install ngrok
```

### 2. تشغيل Ngrok:
```bash
ngrok http 8443
```

### 3. نسخ الرابط:
ستحصل على رابط مثل: `https://abc123.ngrok.io`

### 4. تعديل ملف webhook_bot.py:
```python
WEBHOOK_URL = "https://abc123.ngrok.io/webhook"
```

### 5. تشغيل البوت:
```bash
python3 webhook_bot.py
```

## الخيار للإنتاج: Heroku

### 1. تثبيت Heroku CLI:
```bash
brew install heroku
```

### 2. تسجيل الدخول:
```bash
heroku login
```

### 3. إنشاء تطبيق:
```bash
heroku create your-bot-name
```

### 4. إعداد متغيرات البيئة:
```bash
heroku config:set TELEGRAM_TOKEN=your_bot_token
heroku config:set WEBHOOK_URL=https://your-bot-name.herokuapp.com/webhook
```

### 5. رفع الكود:
```bash
git add .
git commit -m "Add webhook support"
git push heroku main
```

## الخيار الأسهل: Railway

### 1. اذهب إلى [railway.app](https://railway.app)
### 2. اربط حساب GitHub
### 3. اختر المستودع
### 4. أضف متغيرات البيئة:
- `TELEGRAM_TOKEN`: توكن البوت
- `WEBHOOK_URL`: https://your-app.railway.app/webhook

## الخيار المجاني: Render

### 1. اذهب إلى [render.com](https://render.com)
### 2. اربط حساب GitHub
### 3. اختر "Web Service"
### 4. اختر المستودع
### 5. أضف متغيرات البيئة

## أوامر مفيدة:

### عرض معلومات Webhook:
```
/webhook_info
```

### حذف Webhook (للعودة للـ Polling):
```python
await bot.delete_webhook()
```

## استكشاف الأخطاء:

### مشكلة: "Invalid webhook URL"
- تأكد من أن الرابط يبدأ بـ `https://`
- تأكد من أن المنفذ مفتوح

### مشكلة: "Connection timeout"
- تحقق من إعدادات الجدار الناري
- تأكد من أن الخادم متاح من الإنترنت

## نصائح:

1. **للاختبار**: استخدم Ngrok
2. **للإنتاج**: استخدم Heroku أو Railway
3. **للحماية**: استخدم متغيرات البيئة
4. **للمراقبة**: تحقق من السجلات بانتظام

---

**ملاحظة**: Webhook يتطلب خادم عام مع HTTPS. للاختبار المحلي، استخدم Ngrok. للإنتاج، استخدم منصة سحابية. 