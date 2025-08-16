#!/bin/bash

# سكريبت إعداد البيئة الافتراضية والمكتبات
# Server: 31.97.233.18
# Path: /var/www/leads_rockli_usr/data/www/leads.rocklis.com

echo "🔧 إعداد البيئة الافتراضية..."
echo "================================"

# الانتقال إلى مجلد المشروع
cd /var/www/leads_rockli_usr/data/www/leads.rocklis.com || {
    echo "❌ فشل في الانتقال إلى مجلد المشروع"
    exit 1
}

# التحقق من وجود Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت"
    echo "💡 قم بتثبيت Python3 أولاً:"
    echo "   sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# التحقق من وجود pip3
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 غير مثبت"
    echo "💡 قم بتثبيت pip3 أولاً:"
    echo "   sudo apt install python3-pip"
    exit 1
fi

echo "✅ Python3 و pip3 مثبتان"

# إنشاء البيئة الافتراضية
echo "🔧 إنشاء البيئة الافتراضية..."
if [ -d "venv" ]; then
    echo "⚠️ البيئة الافتراضية موجودة بالفعل"
    read -p "هل تريد إعادة إنشائها؟ (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✅ تم إعادة إنشاء البيئة الافتراضية"
    fi
else
    python3 -m venv venv
    echo "✅ تم إنشاء البيئة الافتراضية"
fi

# تفعيل البيئة الافتراضية
echo "🔧 تفعيل البيئة الافتراضية..."
source venv/bin/activate

# تحديث pip
echo "📦 تحديث pip..."
pip3 install --upgrade pip

# تثبيت المكتبات
echo "📦 تثبيت المكتبات المطلوبة..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo "✅ تم تثبيت المكتبات"
else
    echo "❌ ملف requirements.txt غير موجود"
    exit 1
fi

# التحقق من التثبيت
echo "🔍 التحقق من المكتبات..."
python3 -c "
import telegram
import pandas
import openpyxl
import requests
import schedule
import aiohttp
print('✅ جميع المكتبات مثبتة بنجاح')
"

# إنشاء ملف تفعيل البيئة
echo "🔧 إنشاء ملف تفعيل البيئة..."
cat > activate_env.sh << 'EOF'
#!/bin/bash
cd /var/www/leads_rockli_usr/data/www/leads.rocklis.com
source venv/bin/activate
echo "✅ تم تفعيل البيئة الافتراضية"
echo "🔧 يمكنك الآن تشغيل البوت"
EOF

chmod +x activate_env.sh

echo "================================"
echo "✅ تم إعداد البيئة الافتراضية بنجاح!"
echo ""
echo "📋 الأوامر المتاحة:"
echo "  ./activate_env.sh    - تفعيل البيئة الافتراضية"
echo "  ./quick_start.sh     - تشغيل البوت"
echo "  ./server_bot_manager.sh start  - تشغيل البوت"
echo ""
echo "🎉 البيئة جاهزة لتشغيل البوت!"
