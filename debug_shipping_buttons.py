#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشخيص مشكلة أزرار الشحن
"""

import re
from database_manager import DatabaseManager

def check_database():
    """فحص قاعدة البيانات"""
    print("🔍 فحص قاعدة البيانات:")
    print("-" * 30)
    
    try:
        db_manager = DatabaseManager()
        
        # فحص جدول exported_invoices
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exported_invoices'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ جدول exported_invoices موجود")
            
            # فحص عدد السجلات
            cursor.execute("SELECT COUNT(*) FROM exported_invoices")
            count = cursor.fetchone()[0]
            print(f"✅ عدد السجلات في جدول التصدير: {count}")
        else:
            print("❌ جدول exported_invoices غير موجود")
        
        # فحص جدول invoices
        cursor.execute("SELECT COUNT(*) FROM invoices")
        invoices_count = cursor.fetchone()[0]
        print(f"✅ عدد الفواتير: {invoices_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ خطأ في فحص قاعدة البيانات: {e}")

def check_shipping_functions():
    """فحص دوال الشحن"""
    print("\n🔍 فحص دوال الشحن:")
    print("-" * 30)
    
    try:
        db_manager = DatabaseManager()
        
        # اختبار get_export_stats
        stats = db_manager.get_export_stats()
        if stats:
            print("✅ دالة get_export_stats تعمل")
            print(f"   - إجمالي الطلبات: {stats['total_invoices']}")
            print(f"   - الطلبات المصدرة: {stats['exported_invoices']}")
            print(f"   - الطلبات الجديدة: {stats['new_invoices']}")
        else:
            print("❌ دالة get_export_stats فشلت")
        
        # اختبار get_all_invoices_for_shipping
        df = db_manager.get_all_invoices_for_shipping(7, "period")
        if df is not None:
            print(f"✅ دالة get_all_invoices_for_shipping تعمل ({len(df)} طلب)")
        else:
            print("❌ دالة get_all_invoices_for_shipping فشلت")
        
        # اختبار get_all_invoices_for_shipping مع new_only
        df_new = db_manager.get_all_invoices_for_shipping(0, "new_only")
        if df_new is not None:
            print(f"✅ دالة get_all_invoices_for_shipping مع new_only تعمل ({len(df_new)} طلب)")
        else:
            print("❌ دالة get_all_invoices_for_shipping مع new_only فشلت")
            
    except Exception as e:
        print(f"❌ خطأ في فحص دوال الشحن: {e}")

def check_button_patterns():
    """فحص أنماط الأزرار"""
    print("\n🔍 فحص أنماط الأزرار:")
    print("-" * 30)
    
    # الأنماط المطلوبة
    patterns = [
        "shipping_all",
        "shipping_1",
        "shipping_2", 
        "shipping_7",
        "shipping_30",
        "shipping_90",
        "shipping_new",
        "back_to_main_menu"
    ]
    
    # النمط المستخدم في الكود
    pattern = "^(shipping_all|shipping_1|shipping_2|shipping_7|shipping_30|shipping_90|shipping_new|back_to_main_menu)$"
    
    print(f"النمط المستخدم: {pattern}")
    print()
    
    for test_pattern in patterns:
        match = re.match(pattern, test_pattern)
        if match:
            print(f"✅ {test_pattern} - متطابق")
        else:
            print(f"❌ {test_pattern} - غير متطابق")

def check_bot_code():
    """فحص كود البوت"""
    print("\n🔍 فحص كود البوت:")
    print("-" * 30)
    
    try:
        with open('bot_clean.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # فحص وجود الدوال
        functions_to_check = [
            'show_shipping_period_menu',
            'shipping_callback_handler',
            'InlineKeyboardButton',
            'InlineKeyboardMarkup'
        ]
        
        for func in functions_to_check:
            if func in content:
                print(f"✅ {func} موجود في الكود")
            else:
                print(f"❌ {func} غير موجود في الكود")
        
        # فحص وجود معالج الأزرار
        if 'CallbackQueryHandler(shipping_callback_handler' in content:
            print("✅ معالج أزرار الشحن موجود")
        else:
            print("❌ معالج أزرار الشحن غير موجود")
            
    except Exception as e:
        print(f"❌ خطأ في فحص كود البوت: {e}")

def generate_test_buttons():
    """إنشاء أزرار اختبار"""
    print("\n🔍 إنشاء أزرار اختبار:")
    print("-" * 30)
    
    buttons = [
        ("📋 الكل", "shipping_all"),
        ("⏰ آخر 24 ساعة", "shipping_1"),
        ("📅 آخر يومين", "shipping_2"),
        ("📆 آخر أسبوع", "shipping_7"),
        ("📊 آخر شهر", "shipping_30"),
        ("📈 آخر 3 شهور", "shipping_90"),
        ("🆕 الجديد فقط", "shipping_new"),
        ("🔙 رجوع", "back_to_main_menu")
    ]
    
    print("الأزرار المتوقعة:")
    for text, callback_data in buttons:
        print(f"   {text} -> {callback_data}")

def show_solutions():
    """عرض الحلول"""
    print("\n💡 الحلول المقترحة:")
    print("=" * 30)
    print("1. تأكد من إعادة تشغيل البوت بعد التحديثات")
    print("2. تحقق من أن البوت يعمل بدون أخطاء")
    print("3. تأكد من أن لديك صلاحية الوصول للبوت")
    print("4. جرب إرسال /start للبوت أولاً")
    print("5. تحقق من سجلات البوت للأخطاء")
    print("6. تأكد من أن قاعدة البيانات محدثة")

if __name__ == "__main__":
    print("🔧 تشخيص مشكلة أزرار الشحن")
    print("=" * 50)
    
    check_database()
    check_shipping_functions()
    check_button_patterns()
    check_bot_code()
    generate_test_buttons()
    show_solutions()
    
    print("\n🎯 انتهى التشخيص!")
