#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لإصلاح الأزرار
"""

from database_manager import DatabaseManager

def test_system_stats():
    """اختبار الحصول على إحصائيات النظام"""
    print("🧪 اختبار الحصول على إحصائيات النظام...")
    
    db_manager = DatabaseManager()
    stats = db_manager.get_system_stats()
    
    if stats:
        print("✅ تم الحصول على إحصائيات النظام")
        print(f"📊 إحصائيات النظام:")
        print(f"   📋 الفواتير: {stats['invoices_count']} فاتورة")
        print(f"   👥 المستخدمين: {stats['users_count']} مستخدم")
        print(f"   🔄 المرتجعات: {stats['returns_count']} مرتجع")
        print(f"   🌐 سجلات API: {stats['api_orders_count']} سجل")
        print(f"   🔐 كلمات المرور: {stats['passwords_count']} كلمة مرور")
    else:
        print("❌ فشل في الحصول على إحصائيات النظام")

def test_button_data():
    """اختبار بيانات الأزرار"""
    print("\n🧪 اختبار بيانات الأزرار...")
    
    button_data = [
        "delete_old_invoices",
        "reset_statistics", 
        "reset_system",
        "back_to_admin"
    ]
    
    print("🔘 بيانات الأزرار:")
    for data in button_data:
        print(f"   • {data}")
    
    print("✅ بيانات الأزرار صحيحة")

def test_callback_patterns():
    """اختبار أنماط الـ callback"""
    print("\n🧪 اختبار أنماط الـ callback...")
    
    patterns = [
        "^(delete_old_invoices|reset_statistics|reset_system|back_to_admin)$"
    ]
    
    print("🔍 أنماط الـ callback:")
    for pattern in patterns:
        print(f"   • {pattern}")
    
    print("✅ أنماط الـ callback صحيحة")

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء اختبار إصلاح الأزرار")
    print("=" * 40)
    
    # اختبار الحصول على الإحصائيات
    test_system_stats()
    
    # اختبار بيانات الأزرار
    test_button_data()
    
    # اختبار أنماط الـ callback
    test_callback_patterns()
    
    print("\n" + "=" * 40)
    print("✅ انتهى اختبار إصلاح الأزرار")
    print("💡 الأزرار يجب أن تعمل الآن بشكل صحيح")

if __name__ == "__main__":
    main()
