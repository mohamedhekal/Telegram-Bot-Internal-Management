# 🚀 دليل نشر البوت على السيرفر الجديد

## 📋 معلومات السيرفر
- **السيرفر**: 31.97.233.18
- **المسار**: `/var/www/leads_rockli_usr/data/www/leads.rocklis.com`
- **نظام التشغيل**: Ubuntu Linux

## 🔧 المتطلبات الأساسية

### 1. تثبيت Python3 و pip3
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. التحقق من التثبيت
```bash
python3 --version
pip3 --version
```

## 📦 خطوات النشر

### الخطوة 1: رفع الملفات إلى السيرفر
```bash
# رفع جميع ملفات المشروع إلى السيرفر
scp -r ./* user@31.97.233.18:/var/www/leads_rockli_usr/data/www/leads.rocklis.com/
```

### الخطوة 2: الدخول إلى السيرفر
```bash
ssh user@31.97.233.18
cd /var/www/leads_rockli_usr/data/www/leads.rocklis.com
```

### الخطوة 3: تشغيل سكريبت النشر التلقائي
```bash
chmod +x deploy_to_server.sh
./deploy_to_server.sh
```

## 🛠️ إدارة البوت على السيرفر

### استخدام مدير البوت
```bash
chmod +x server_bot_manager.sh
```

### الأوامر المتاحة

#### 1. تشغيل البوت
```bash
./server_bot_manager.sh start
```

#### 2. إيقاف البوت
```bash
./server_bot_manager.sh stop
```

#### 3. إعادة تشغيل البوت
```bash
./server_bot_manager.sh restart
```

#### 4. عرض حالة البوت
```bash
./server_bot_manager.sh status
```

#### 5. عرض السجلات
```bash
./server_bot_manager.sh logs
```

#### 6. مراقبة السجلات مباشرة
```bash
./server_bot_manager.sh monitor
```

#### 7. تثبيت المكتبات
```bash
./server_bot_manager.sh install
```

#### 8. اختبار الاتصال
```bash
./server_bot_manager.sh test
```

#### 9. عرض المساعدة
```bash
./server_bot_manager.sh help
```

## 📊 مراقبة البوت

### 1. مراقبة العمليات
```bash
ps aux | grep bot_clean
```

### 2. مراقبة استخدام الذاكرة
```bash
top -p $(cat bot.pid)
```

### 3. مراقبة السجلات في الوقت الفعلي
```bash
tail -f bot.log
```

### 4. عرض آخر السجلات
```bash
tail -n 100 bot.log
```

## 🔍 استكشاف الأخطاء

### 1. التحقق من حالة البوت
```bash
./server_bot_manager.sh status
```

### 2. فحص السجلات للأخطاء
```bash
grep -i error bot.log
grep -i exception bot.log
```

### 3. اختبار الاتصال
```bash
./server_bot_manager.sh test
```

### 4. إعادة تثبيت المكتبات
```bash
./server_bot_manager.sh install
```

## 🚨 حل المشاكل الشائعة

### المشكلة 1: البوت لا يعمل
```bash
# الحل:
./server_bot_manager.sh stop
./server_bot_manager.sh start
```

### المشكلة 2: خطأ في المكتبات
```bash
# الحل:
./server_bot_manager.sh install
```

### المشكلة 3: خطأ في التوكن
```bash
# الحل:
./server_bot_manager.sh test
# ثم تعديل config.py إذا لزم الأمر
```

### المشكلة 4: البوت يتوقف فجأة
```bash
# الحل:
./server_bot_manager.sh restart
# ثم مراقبة السجلات:
./server_bot_manager.sh monitor
```

## 🔄 التشغيل التلقائي عند إعادة تشغيل السيرفر

### إنشاء خدمة systemd
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

### محتوى ملف الخدمة
```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/leads_rockli_usr/data/www/leads.rocklis.com
Environment=PATH=/var/www/leads_rockli_usr/data/www/leads.rocklis.com/venv/bin
ExecStart=/var/www/leads_rockli_usr/data/www/leads.rocklis.com/venv/bin/python3 bot_clean.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### تفعيل الخدمة
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### إدارة الخدمة
```bash
# تشغيل الخدمة
sudo systemctl start telegram-bot

# إيقاف الخدمة
sudo systemctl stop telegram-bot

# إعادة تشغيل الخدمة
sudo systemctl restart telegram-bot

# عرض حالة الخدمة
sudo systemctl status telegram-bot

# عرض سجلات الخدمة
sudo journalctl -u telegram-bot -f
```

## 📱 اختبار البوت

### 1. اختبار الاتصال
```bash
./server_bot_manager.sh test
```

### 2. إرسال رسالة اختبار
- اذهب إلى تيليجرام
- ابحث عن البوت
- أرسل `/start`

### 3. التحقق من الاستجابة
```bash
./server_bot_manager.sh monitor
```

## 🔒 الأمان

### 1. حماية الملفات
```bash
chmod 600 config.py
chmod 644 *.py
chmod 755 *.sh
```

### 2. إنشاء نسخة احتياطية
```bash
# نسخة احتياطية من قاعدة البيانات
cp invoice_bot.db invoice_bot.db.backup.$(date +%Y%m%d_%H%M%S)

# نسخة احتياطية من الإعدادات
cp config.py config.py.backup.$(date +%Y%m%d_%H%M%S)
```

## 📈 مراقبة الأداء

### 1. مراقبة استخدام الموارد
```bash
# استخدام الذاكرة
free -h

# استخدام المعالج
htop

# استخدام القرص
df -h
```

### 2. مراقبة الشبكة
```bash
# مراقبة الاتصالات
netstat -tulpn | grep python
```

## 🎯 نصائح مهمة

1. **احتفظ بنسخة احتياطية** من قاعدة البيانات والإعدادات
2. **راقب السجلات** بانتظام للكشف عن المشاكل
3. **اختبر البوت** بعد كل تحديث
4. **استخدم البيئة الافتراضية** لعزل المكتبات
5. **قم بتحديث المكتبات** بانتظام

## 📞 الدعم

إذا واجهت أي مشاكل:
1. راجع السجلات: `./server_bot_manager.sh logs`
2. اختبر الاتصال: `./server_bot_manager.sh test`
3. أعد تشغيل البوت: `./server_bot_manager.sh restart`
4. راجع هذا الدليل مرة أخرى

---

**✅ البوت جاهز للاستخدام على السيرفر الجديد!**
