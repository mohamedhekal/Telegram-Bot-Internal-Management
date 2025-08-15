#!/bin/bash
# سكريبت إصلاح خطأ التنسيق في bot_clean.py

echo "🔧 بدء إصلاح خطأ التنسيق في bot_clean.py..."
echo "=========================================="

# 1. نسخ احتياطية
echo "1️⃣ إنشاء نسخة احتياطية..."
BACKUP_FILE="bot_clean_backup_$(date +%Y%m%d_%H%M%S).py"
cp bot_clean.py "$BACKUP_FILE"
echo "✅ تم إنشاء النسخة الاحتياطية: $BACKUP_FILE"

# 2. فحص الملف الحالي
echo ""
echo "2️⃣ فحص الملف الحالي..."
if python3 -m py_compile bot_clean.py; then
    echo "✅ الملف صحيح من ناحية التنسيق"
else
    echo "❌ يوجد خطأ في التنسيق"
fi

# 3. فحص نهاية الملف
echo ""
echo "3️⃣ فحص نهاية الملف..."
tail -5 bot_clean.py

# 4. إصلاح نهاية الملف إذا لزم الأمر
echo ""
echo "4️⃣ إصلاح نهاية الملف..."
# حذف السطر الأخير إذا كان غير صحيح
sed -i '/^[[:space:]]*main()[[:space:]]*$/d' bot_clean.py

# إضافة النهاية الصحيحة
cat >> bot_clean.py << 'EOF'

if __name__ == "__main__":
    main()
EOF

echo "✅ تم إصلاح نهاية الملف"

# 5. اختبار الملف مرة أخرى
echo ""
echo "5️⃣ اختبار الملف بعد الإصلاح..."
if python3 -m py_compile bot_clean.py; then
    echo "✅ الملف صحيح الآن"
else
    echo "❌ لا يزال هناك خطأ"
    echo "💡 استعادة النسخة الاحتياطية..."
    cp "$BACKUP_FILE" bot_clean.py
    exit 1
fi

# 6. فحص حالة الخدمة
echo ""
echo "6️⃣ فحص حالة الخدمة..."
if command -v systemctl &> /dev/null; then
    echo "حالة الخدمة:"
    systemctl status rksorderbot.service --no-pager -l
else
    echo "ℹ️ systemctl غير متاح"
fi

echo ""
echo "=========================================="
echo "✅ انتهى إصلاح خطأ التنسيق"
echo "💡 إذا كنت تريد إعادة تشغيل الخدمة، استخدم:"
echo "   sudo systemctl restart rksorderbot.service"
