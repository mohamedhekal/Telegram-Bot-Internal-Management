#!/bin/bash

# سكريبت نشر وتشغيل البوت على السيرفر الجديد
# Server: 31.97.233.18
# Path: /var/www/leads_rockli_usr/data/www/leads.rocklis.com

echo "🚀 بدء نشر البوت على السيرفر الجديد..."
echo "=================================="

# تحديد المسار
SERVER_PATH="/var/www/leads_rockli_usr/data/www/leads.rocklis.com"
SERVER_IP="31.97.233.18"

echo "📍 المسار: $SERVER_PATH"
echo "🌐 السيرفر: $SERVER_IP"

# التحقق من وجود Python3
echo "🔍 التحقق من Python3..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت"
    echo "💡 قم بتثبيت Python3 أولاً:"
    echo "   sudo apt update && sudo apt install python3 python3-pip"
    exit 1
fi
echo "✅ Python3 مثبت"

# التحقق من وجود pip3
echo "🔍 التحقق من pip3..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 غير مثبت"
    echo "💡 قم بتثبيت pip3 أولاً:"
    echo "   sudo apt install python3-pip"
    exit 1
fi
echo "✅ pip3 مثبت"

# الانتقال إلى مجلد المشروع
echo "📁 الانتقال إلى مجلد المشروع..."
cd "$SERVER_PATH" || {
    echo "❌ فشل في الانتقال إلى $SERVER_PATH"
    exit 1
}
echo "✅ تم الانتقال إلى $SERVER_PATH"

# إنشاء بيئة افتراضية (اختياري)
echo "🔧 إنشاء بيئة افتراضية..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ تم إنشاء البيئة الافتراضية"
else
    echo "✅ البيئة الافتراضية موجودة"
fi

# تفعيل البيئة الافتراضية
echo "🔧 تفعيل البيئة الافتراضية..."
source venv/bin/activate
echo "✅ تم تفعيل البيئة الافتراضية"

# تثبيت المكتبات المطلوبة
echo "📦 تثبيت المكتبات المطلوبة..."
pip3 install --upgrade pip
pip3 install -r requirements.txt
echo "✅ تم تثبيت المكتبات"

# التحقق من ملف الإعدادات
echo "🔍 التحقق من ملف الإعدادات..."
if [ ! -f "config.py" ]; then
    echo "❌ ملف config.py غير موجود"
    exit 1
fi
echo "✅ ملف الإعدادات موجود"

# إيقاف البوتات الجارية
echo "🛑 إيقاف البوتات الجارية..."
pkill -f "python.*bot_clean" || true
pkill -f "python.*start_bot" || true
sleep 2
echo "✅ تم إيقاف البوتات الجارية"

# اختبار الاتصال
echo "🔍 اختبار اتصال البوت..."
python3 test_bot_token.py
if [ $? -ne 0 ]; then
    echo "❌ فشل في اختبار الاتصال"
    echo "💡 تأكد من صحة التوكن في config.py"
    exit 1
fi
echo "✅ اختبار الاتصال ناجح"

# تشغيل البوت في الخلفية
echo "🚀 تشغيل البوت..."
nohup python3 start_bot.py > bot.log 2>&1 &
BOT_PID=$!
echo "✅ البوت يعمل في الخلفية (PID: $BOT_PID)"

# حفظ معرف العملية
echo $BOT_PID > bot.pid
echo "✅ تم حفظ معرف العملية في bot.pid"

# انتظار قليل للتأكد من التشغيل
sleep 5

# التحقق من أن البوت يعمل
if ps -p $BOT_PID > /dev/null; then
    echo "🎉 البوت يعمل بنجاح!"
    echo "📱 يمكنك الآن استخدام البوت في تيليجرام"
    echo "📊 لمراقبة السجلات: tail -f bot.log"
    echo "🛑 لإيقاف البوت: kill $BOT_PID"
else
    echo "❌ فشل في تشغيل البوت"
    echo "📋 راجع السجلات: cat bot.log"
    exit 1
fi

echo "=================================="
echo "✅ تم نشر البوت بنجاح على السيرفر!"
echo "🌐 السيرفر: $SERVER_IP"
echo "📁 المسار: $SERVER_PATH"
