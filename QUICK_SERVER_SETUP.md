# 🚀 إعداد سريع للبوت على السيرفر

## 📋 معلومات السيرفر
- **السيرفر**: 31.97.233.18
- **المسار**: `/var/www/leads_rockli_usr/data/www/leads.rocklis.com`

## ⚡ التشغيل السريع

### 1. الدخول إلى السيرفر
```bash
ssh user@31.97.233.18
cd /var/www/leads_rockli_usr/data/www/leads.rocklis.com
```

### 2. تشغيل البوت فوراً
```bash
chmod +x quick_start.sh
./quick_start.sh
```

## 🛠️ الأوامر الأساسية

### تشغيل البوت
```bash
./server_bot_manager.sh start
```

### إيقاف البوت
```bash
./server_bot_manager.sh stop
```

### عرض حالة البوت
```bash
./server_bot_manager.sh status
```

### مراقبة السجلات
```bash
./server_bot_manager.sh monitor
```

## 🔍 اختبار البوت

### 1. اختبار الاتصال
```bash
./server_bot_manager.sh test
```

### 2. إرسال رسالة في تيليجرام
- ابحث عن البوت في تيليجرام
- أرسل `/start`

## 📊 مراقبة البوت

### عرض السجلات
```bash
tail -f bot.log
```

### عرض العمليات
```bash
ps aux | grep bot_clean
```

## 🚨 حل المشاكل السريع

### البوت لا يعمل
```bash
./server_bot_manager.sh restart
```

### خطأ في المكتبات
```bash
./server_bot_manager.sh install
```

### خطأ في الاتصال
```bash
./server_bot_manager.sh test
```

## 📱 البوت جاهز!

بعد التشغيل، يمكنك استخدام البوت في تيليجرام مباشرة.

---

**✅ البوت يعمل على السيرفر الجديد!**
