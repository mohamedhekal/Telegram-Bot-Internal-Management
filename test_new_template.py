#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار القالب الجديد لملفات الشحن
"""

from database_manager import DatabaseManager
from datetime import datetime

def test_new_template():
    """اختبار القالب الجديد"""
    
    print("🧪 اختبار القالب الجديد لملفات الشحن")
    print("=" * 50)
    
    db_manager = DatabaseManager()
    
    # اختبار الحصول على البيانات
    print("\n1️⃣ اختبار الحصول على البيانات:")
    print("-" * 30)
    
    df = db_manager.get_all_invoices_for_shipping(7, "period")
    if df is not None and not df.empty:
        print(f"✅ تم الحصول على {len(df)} طلب")
        print("📋 عينة من البيانات:")
        for i, (_, row) in enumerate(df.head(2).iterrows(), 1):
            print(f"   {i}. {row['receipt_number']} - {row['client_name']} - {row['governorate']}")
    else:
        print("❌ لا توجد بيانات للاختبار")
        return
    
    # اختبار إنشاء الملف بالقالب الجديد
    print("\n2️⃣ اختبار إنشاء الملف بالقالب الجديد:")
    print("-" * 40)
    
    try:
        filename = db_manager.create_shipping_excel(7, "period", 12345)
        
        if filename:
            print(f"✅ تم إنشاء الملف: {filename}")
            
            # التحقق من الإحصائيات
            stats = db_manager.get_export_stats()
            if stats:
                print(f"✅ الطلبات المصدرة: {stats['exported_invoices']}")
                print(f"✅ الطلبات الجديدة: {stats['new_invoices']}")
        else:
            print("❌ فشل في إنشاء الملف")
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء الملف: {e}")
    
    print("\n🎯 انتهى اختبار القالب الجديد!")

if __name__ == "__main__":
    test_new_template()
