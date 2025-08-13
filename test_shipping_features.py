#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار ميزات تحميل الطلبات الجديدة
"""

from database_manager import DatabaseManager
from datetime import datetime
import pandas as pd

def test_shipping_features():
    """اختبار ميزات تحميل الطلبات الجديدة"""
    
    print("🧪 اختبار ميزات تحميل الطلبات الجديدة")
    print("=" * 50)
    
    db_manager = DatabaseManager()
    
    # 1. اختبار إحصائيات التصدير
    print("\n1️⃣ اختبار إحصائيات التصدير:")
    print("-" * 30)
    
    export_stats = db_manager.get_export_stats()
    if export_stats:
        print(f"✅ إجمالي الطلبات: {export_stats['total_invoices']}")
        print(f"✅ الطلبات المصدرة: {export_stats['exported_invoices']}")
        print(f"✅ الطلبات الجديدة: {export_stats['new_invoices']}")
        
        if export_stats['last_export']:
            last_export_date, last_export_type, last_export_count = export_stats['last_export']
            print(f"✅ آخر تصدير: {last_export_date} - {last_export_type} - {last_export_count} طلب")
        else:
            print("ℹ️ لا توجد تصديرات سابقة")
    else:
        print("❌ فشل في الحصول على إحصائيات التصدير")
    
    # 2. اختبار الحصول على الطلبات لفترات مختلفة
    print("\n2️⃣ اختبار الحصول على الطلبات لفترات مختلفة:")
    print("-" * 40)
    
    periods = [
        (1, "آخر 24 ساعة"),
        (2, "آخر يومين"),
        (7, "آخر أسبوع"),
        (30, "آخر شهر"),
        (90, "آخر 3 شهور")
    ]
    
    for days, period_name in periods:
        df = db_manager.get_all_invoices_for_shipping(days, "period")
        count = len(df) if df is not None else 0
        print(f"✅ {period_name}: {count} طلب")
    
    # 3. اختبار الطلبات الجديدة فقط
    print("\n3️⃣ اختبار الطلبات الجديدة فقط:")
    print("-" * 30)
    
    df_new = db_manager.get_all_invoices_for_shipping(0, "new_only")
    new_count = len(df_new) if df_new is not None else 0
    print(f"✅ الطلبات الجديدة (غير مصدرة): {new_count} طلب")
    
    if new_count > 0:
        print("📋 تفاصيل الطلبات الجديدة:")
        for i, (_, row) in enumerate(df_new.head(3).iterrows(), 1):
            print(f"   {i}. {row['receipt_number']} - {row['client_name']} - {row['governorate']}")
    
    # 4. اختبار إنشاء ملف تجريبي
    print("\n4️⃣ اختبار إنشاء ملف تجريبي:")
    print("-" * 30)
    
    try:
        # إنشاء ملف للطلبات الجديدة فقط
        filename = db_manager.create_shipping_excel(0, "new_only", 12345)  # user_id تجريبي
        
        if filename:
            print(f"✅ تم إنشاء الملف: {filename}")
            
            # التحقق من تحديث الإحصائيات
            updated_stats = db_manager.get_export_stats()
            if updated_stats:
                print(f"✅ الطلبات المصدرة بعد التصدير: {updated_stats['exported_invoices']}")
                print(f"✅ الطلبات الجديدة بعد التصدير: {updated_stats['new_invoices']}")
        else:
            print("❌ فشل في إنشاء الملف")
    except Exception as e:
        print(f"❌ خطأ في إنشاء الملف: {e}")
    
    # 5. عرض ملخص النتائج
    print("\n5️⃣ ملخص النتائج:")
    print("-" * 20)
    
    final_stats = db_manager.get_export_stats()
    if final_stats:
        print(f"📊 إجمالي الطلبات: {final_stats['total_invoices']}")
        print(f"📤 الطلبات المصدرة: {final_stats['exported_invoices']}")
        print(f"🆕 الطلبات الجديدة: {final_stats['new_invoices']}")
        
        if final_stats['total_invoices'] > 0:
            export_percentage = (final_stats['exported_invoices'] / final_stats['total_invoices']) * 100
            print(f"📈 نسبة التصدير: {export_percentage:.1f}%")
    
    print("\n🎯 اختبار الميزات الجديدة مكتمل!")

def show_export_history():
    """عرض تاريخ التصدير"""
    
    print("\n📋 عرض تاريخ التصدير:")
    print("=" * 30)
    
    db_manager = DatabaseManager()
    
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # الحصول على تاريخ التصدير
        cursor.execute("""
            SELECT export_date, export_type, COUNT(*) as count, exported_by
            FROM exported_invoices 
            GROUP BY export_date, export_type, exported_by
            ORDER BY export_date DESC 
            LIMIT 10
        """)
        
        exports = cursor.fetchall()
        conn.close()
        
        if exports:
            print("📅 آخر 10 عمليات تصدير:")
            for i, (export_date, export_type, count, exported_by) in enumerate(exports, 1):
                print(f"   {i}. {export_date} - {export_type} - {count} طلب - المستخدم: {exported_by}")
        else:
            print("ℹ️ لا توجد عمليات تصدير مسجلة")
            
    except Exception as e:
        print(f"❌ خطأ في عرض تاريخ التصدير: {e}")

if __name__ == "__main__":
    print("🚀 بدء اختبار ميزات تحميل الطلبات الجديدة...")
    
    # اختبار الميزات الأساسية
    test_shipping_features()
    
    # عرض تاريخ التصدير
    show_export_history()
    
    print("\n✅ انتهى الاختبار بنجاح!")
