#!/bin/bash

echo "📦 تثبيت متطلبات البوت..."
echo "=========================="

# التحقق من Python3
echo "🔍 التحقق من Python3..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت"
    echo "💡 قم بتثبيت Python3 أولاً:"
    echo "   sudo apt update && sudo apt install python3 python3-pip"
    exit 1
fi
echo "✅ Python3 مثبت"

# التحقق من pip3
echo "🔍 التحقق من pip3..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 غير مثبت"
    echo "💡 قم بتثبيت pip3 أولاً:"
    echo "   sudo apt install python3-pip"
    exit 1
fi
echo "✅ pip3 مثبت"

# إنشاء بيئة افتراضية
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
try:
    import telegram
    print('✅ python-telegram-bot')
except ImportError:
    print('❌ python-telegram-bot')
    
try:
    import pandas
    print('✅ pandas')
except ImportError:
    print('❌ pandas')
    
try:
    import openpyxl
    print('✅ openpyxl')
except ImportError:
    print('❌ openpyxl')
    
try:
    import requests
    print('✅ requests')
except ImportError:
    print('❌ requests')
    
try:
    import schedule
    print('✅ schedule')
except ImportError:
    print('❌ schedule')
    
try:
    import aiohttp
    print('✅ aiohttp')
except ImportError:
    print('❌ aiohttp')
"

echo "=========================="
echo "✅ تم تثبيت المتطلبات بنجاح!"
echo ""
echo "📋 الأوامر المتاحة:"
echo "  source venv/bin/activate  - تفعيل البيئة الافتراضية"
echo "  python3 start_bot.py      - تشغيل البوت"
echo "  ./quick_start.sh          - تشغيل البوت"
echo ""
echo "�� المتطلبات جاهزة!"
