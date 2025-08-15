#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار ميزات إعادة تعيين النظام
"""

from database_manager import DatabaseManager
import config

def test_system_stats():
    """اختبار الحصول على إحصائيات النظام"""
    print("🧪 اختبار الحصول على إحصائيات النظام...")
    print("=" * 60)
    
    # تهيئة مدير قاعدة البيانات
    db_manager = DatabaseManager()
    
    # الحصول على إحصائيات النظام
    stats = db_manager.get_system_stats()
    
    if stats:
        print("✅ تم الحصول على إحصائيات النظام بنجاح")
        print(f"📊 إحصائيات النظام:")
        print(f"   📋 الفواتير: {stats['invoices_count']} فاتورة")
        print(f"   👥 المستخدمين: {stats['users_count']} مستخدم")
        print(f"   🔄 المرتجعات: {stats['returns_count']} مرتجع")
        print(f"   🌐 سجلات API: {stats['api_orders_count']} سجل")
        print(f"   🔐 كلمات المرور: {stats['passwords_count']} كلمة مرور")
    else:
        print("❌ فشل في الحصول على إحصائيات النظام")
    
    print()

def test_reset_statistics():
    """اختبار تصفير الإحصائيات"""
    print("🧪 اختبار تصفير الإحصائيات...")
    print("=" * 60)
    
    # تهيئة مدير قاعدة البيانات
    db_manager = DatabaseManager()
    
    # الحصول على إحصائيات النظام قبل التصفير
    stats_before = db_manager.get_system_stats()
    print("📊 إحصائيات النظام قبل التصفير:")
    print(f"   📋 الفواتير: {stats_before['invoices_count']} فاتورة")
    print(f"   👥 المستخدمين: {stats_before['users_count']} مستخدم")
    print(f"   🔄 المرتجعات: {stats_before['returns_count']} مرتجع")
    print(f"   🌐 سجلات API: {stats_before['api_orders_count']} سجل")
    print(f"   🔐 كلمات المرور: {stats_before['passwords_count']} كلمة مرور")
    
    # تصفير الإحصائيات
    print("\n🔄 جاري تصفير الإحصائيات...")
    result = db_manager.reset_statistics_only()
    
    if result.get('success'):
        print("✅ تم تصفير الإحصائيات بنجاح")
        print(f"📈 ما تم تصفيره:")
        print(f"   📊 الإحصائيات اليومية: {result['stats_deleted']} سجل")
        print(f"   📈 إحصائيات الشحن: {result['shipping_stats_deleted']} سجل")
        
        # الحصول على إحصائيات النظام بعد التصفير
        stats_after = db_manager.get_system_stats()
        print("\n📊 إحصائيات النظام بعد التصفير:")
        print(f"   📋 الفواتير: {stats_after['invoices_count']} فاتورة (محفوظة)")
        print(f"   👥 المستخدمين: {stats_after['users_count']} مستخدم (محفوظ)")
        print(f"   🔄 المرتجعات: {stats_after['returns_count']} مرتجع (محفوظ)")
        print(f"   🌐 سجلات API: {stats_after['api_orders_count']} سجل (محفوظ)")
        print(f"   🔐 كلمات المرور: {stats_after['passwords_count']} كلمة مرور (محفوظة)")
    else:
        print(f"❌ فشل في تصفير الإحصائيات: {result.get('error')}")
    
    print()

def test_delete_old_invoices():
    """اختبار حذف الفواتير القديمة"""
    print("🧪 اختبار حذف الفواتير القديمة...")
    print("=" * 60)
    
    # تهيئة مدير قاعدة البيانات
    db_manager = DatabaseManager()
    
    # الحصول على إحصائيات النظام قبل الحذف
    stats_before = db_manager.get_system_stats()
    print("📊 إحصائيات النظام قبل الحذف:")
    print(f"   📋 الفواتير: {stats_before['invoices_count']} فاتورة")
    print(f"   👥 المستخدمين: {stats_before['users_count']} مستخدم")
    print(f"   🔄 المرتجعات: {stats_before['returns_count']} مرتجع")
    print(f"   🌐 سجلات API: {stats_before['api_orders_count']} سجل")
    print(f"   🔐 كلمات المرور: {stats_before['passwords_count']} كلمة مرور")
    
    # حذف الفواتير القديمة
    print("\n🗑️ جاري حذف الفواتير القديمة...")
    result = db_manager.delete_old_invoices()
    
    if result.get('success'):
        print("✅ تم حذف الفواتير القديمة بنجاح")
        print(f"🗑️ ما تم حذفه:")
        print(f"   📋 الفواتير: {result['invoices_deleted']} فاتورة")
        print(f"   🌐 سجلات API: {result['api_orders_deleted']} سجل")
        print(f"   🔄 المرتجعات: {result['returns_deleted']} مرتجع")
        print(f"   📊 الإحصائيات اليومية: {result['stats_deleted']} سجل")
        print(f"   📈 إحصائيات الشحن: {result['shipping_stats_deleted']} سجل")
        
        # الحصول على إحصائيات النظام بعد الحذف
        stats_after = db_manager.get_system_stats()
        print("\n📊 إحصائيات النظام بعد الحذف:")
        print(f"   📋 الفواتير: {stats_after['invoices_count']} فاتورة (محذوفة)")
        print(f"   👥 المستخدمين: {stats_after['users_count']} مستخدم (محفوظ)")
        print(f"   🔄 المرتجعات: {stats_after['returns_count']} مرتجع (محذوفة)")
        print(f"   🌐 سجلات API: {stats_after['api_orders_count']} سجل (محذوفة)")
        print(f"   🔐 كلمات المرور: {stats_after['passwords_count']} كلمة مرور (محفوظة)")
    else:
        print(f"❌ فشل في حذف الفواتير القديمة: {result.get('error')}")
    
    print()

def test_reset_system_complete():
    """اختبار إعادة تعيين النظام بالكامل"""
    print("🧪 اختبار إعادة تعيين النظام بالكامل...")
    print("=" * 60)
    
    # تهيئة مدير قاعدة البيانات
    db_manager = DatabaseManager()
    
    # الحصول على إحصائيات النظام قبل إعادة التعيين
    stats_before = db_manager.get_system_stats()
    print("📊 إحصائيات النظام قبل إعادة التعيين:")
    print(f"   📋 الفواتير: {stats_before['invoices_count']} فاتورة")
    print(f"   👥 المستخدمين: {stats_before['users_count']} مستخدم")
    print(f"   🔄 المرتجعات: {stats_before['returns_count']} مرتجع")
    print(f"   🌐 سجلات API: {stats_before['api_orders_count']} سجل")
    print(f"   🔐 كلمات المرور: {stats_before['passwords_count']} كلمة مرور")
    
    # إعادة تعيين النظام
    print("\n🔄 جاري إعادة تعيين النظام...")
    result = db_manager.reset_system_complete()
    
    if result.get('success'):
        print("✅ تم إعادة تعيين النظام بنجاح")
        print(f"🗑️ ما تم حذفه:")
        print(f"   📋 الفواتير: {result['invoices_deleted']} فاتورة")
        print(f"   🌐 سجلات API: {result['api_orders_deleted']} سجل")
        print(f"   🔄 المرتجعات: {result['returns_deleted']} مرتجع")
        print(f"   📊 الإحصائيات اليومية: {result['stats_deleted']} سجل")
        print(f"   📈 إحصائيات الشحن: {result['shipping_stats_deleted']} سجل")
        print(f"   🔐 كلمات المرور: {result['passwords_deleted']} كلمة مرور")
        
        # الحصول على إحصائيات النظام بعد إعادة التعيين
        stats_after = db_manager.get_system_stats()
        print("\n📊 إحصائيات النظام بعد إعادة التعيين:")
        print(f"   📋 الفواتير: {stats_after['invoices_count']} فاتورة (محذوفة)")
        print(f"   👥 المستخدمين: {stats_after['users_count']} مستخدم (محفوظ)")
        print(f"   🔄 المرتجعات: {stats_after['returns_count']} مرتجع (محذوفة)")
        print(f"   🌐 سجلات API: {stats_after['api_orders_count']} سجل (محذوفة)")
        print(f"   🔐 كلمات المرور: {stats_after['passwords_count']} كلمة مرور (محذوفة)")
    else:
        print(f"❌ فشل في إعادة تعيين النظام: {result.get('error')}")
    
    print()

def test_safety_measures():
    """اختبار إجراءات الأمان"""
    print("🧪 اختبار إجراءات الأمان...")
    print("=" * 60)
    
    # تهيئة مدير قاعدة البيانات
    db_manager = DatabaseManager()
    
    # التحقق من وجود المستخدمين بعد إعادة التعيين
    stats = db_manager.get_system_stats()
    
    if stats and stats['users_count'] > 0:
        print("✅ إجراءات الأمان تعمل بشكل صحيح")
        print(f"👥 تم الاحتفاظ بـ {stats['users_count']} مستخدم")
    else:
        print("❌ تحذير: لم يتم الاحتفاظ بالمستخدمين!")
    
    print()

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء اختبار ميزات إعادة تعيين النظام")
    print("=" * 60)
    
    # اختبار الحصول على إحصائيات النظام
    test_system_stats()
    
    # اختبار تصفير الإحصائيات
    test_reset_statistics()
    
    # اختبار حذف الفواتير القديمة
    test_delete_old_invoices()
    
    # اختبار إعادة تعيين النظام بالكامل
    test_reset_system_complete()
    
    # اختبار إجراءات الأمان
    test_safety_measures()
    
    print("=" * 60)
    print("✅ انتهى اختبار ميزات إعادة تعيين النظام")
    print("💡 إذا كانت جميع الاختبارات ناجحة، فإن الميزات تعمل بشكل صحيح")

if __name__ == "__main__":
    main()
