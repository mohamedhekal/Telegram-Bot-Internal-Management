#!/bin/bash

# سكريبت التشغيل السريع للبوت على السيرفر
# Server: 31.97.233.18
# Path: /var/www/leads_rockli_usr/data/www/leads.rocklis.com

echo "🚀 تشغيل سريع للبوت..."
echo "========================"

# الانتقال إلى مجلد المشروع
cd /var/www/leads_rockli_usr/data/www/leads.rocklis.com || {
    echo "❌ فشل في الانتقال إلى مجلد المشروع"
    exit 1
}

# إيقاف البوتات الجارية
echo "🛑 إيقاف البوتات الجارية..."
pkill -f "python.*bot_clean" 2>/dev/null || true
sleep 2

# تفعيل البيئة الافتراضية إذا وجدت
if [ -d "venv" ]; then
    echo "🔧 تفعيل البيئة الافتراضية..."
    source venv/bin/activate
fi

# تشغيل البوت
echo "🚀 تشغيل البوت..."
nohup python3 start_bot.py > bot.log 2>&1 &
BOT_PID=$!

# حفظ معرف العملية
echo $BOT_PID > bot.pid

# انتظار قليل
sleep 3

# التحقق من التشغيل
if ps -p $BOT_PID > /dev/null; then
    echo "✅ البوت يعمل بنجاح! (PID: $BOT_PID)"
    echo "📱 يمكنك الآن استخدام البوت في تيليجرام"
    echo "📊 لمراقبة السجلات: tail -f bot.log"
    echo "🛑 لإيقاف البوت: kill $BOT_PID"
else
    echo "❌ فشل في تشغيل البوت"
    echo "📋 راجع السجلات: cat bot.log"
    exit 1
fi

echo "========================"
echo "🎉 البوت جاهز للاستخدام!"
