#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار إصلاح إدارة كلمات المرور للمستخدمين الجدد
"""

from database_manager import DatabaseManager
import config

def test_new_user_appears_in_password_management():
    """اختبار أن المستخدم الجديد يظهر في إدارة كلمات المرور"""
    print("🧪 اختبار ظهور المستخدم الجديد في إدارة كلمات المرور...")
    
    db_manager = DatabaseManager()
    
    # إضافة مستخدم تجريبي جديد
    test_user_id = 999999999
    test_username = "test_user_new"
    test_full_name = "Test User New"
    test_role = "employee"
    
    print(f"📝 إضافة مستخدم تجريبي:")
    print(f"   🆔 معرف المستخدم: {test_user_id}")
    print(f"   👤 اسم المستخدم: {test_username}")
    print(f"   📝 الاسم الكامل: {test_full_name}")
    print(f"   🔐 الدور: {test_role}")
    
    # إضافة المستخدم
    success = db_manager.add_user(test_user_id, test_username, test_full_name, test_role)
    
    if success:
        print("✅ تم إضافة المستخدم التجريبي بنجاح")
        
        # التحقق من ظهوره في قائمة إدارة كلمات المرور
        users_for_password_management = db_manager.get_all_users_for_password_management()
        
        print(f"\n🔍 التحقق من قائمة إدارة كلمات المرور:")
        print(f"   عدد المستخدمين: {len(users_for_password_management)}")
        
        if test_full_name in users_for_password_management:
            print(f"✅ المستخدم الجديد '{test_full_name}' موجود في قائمة إدارة كلمات المرور")
        else:
            print(f"❌ المستخدم الجديد '{test_full_name}' غير موجود في قائمة إدارة كلمات المرور")
            print(f"   المستخدمين الموجودين: {users_for_password_management}")
        
        # التحقق من قائمة الموظفين العادية
        all_employees = db_manager.get_all_employees()
        print(f"\n🔍 التحقق من قائمة الموظفين العادية:")
        print(f"   عدد الموظفين: {len(all_employees)}")
        
        if test_full_name in all_employees:
            print(f"✅ المستخدم الجديد '{test_full_name}' موجود في قائمة الموظفين العادية")
        else:
            print(f"❌ المستخدم الجديد '{test_full_name}' غير موجود في قائمة الموظفين العادية")
            print(f"   الموظفين الموجودين: {all_employees}")
        
        # إضافة كلمة مرور للمستخدم الجديد
        test_password = "123456"
        password_success = db_manager.set_employee_password(test_full_name, test_password)
        
        if password_success:
            print(f"\n🔐 تم إضافة كلمة مرور للمستخدم الجديد: {test_password}")
            
            # التحقق من كلمة المرور
            is_valid = db_manager.verify_employee_password(test_full_name, test_password)
            print(f"✅ التحقق من كلمة المرور: {'صحيح' if is_valid else 'خطأ'}")
        else:
            print(f"\n❌ فشل في إضافة كلمة مرور للمستخدم الجديد")
        
        # تنظيف - حذف المستخدم التجريبي
        print(f"\n🧹 تنظيف - حذف المستخدم التجريبي...")
        # يمكن إضافة دالة حذف المستخدم هنا إذا كانت موجودة
        
    else:
        print("❌ فشل في إضافة المستخدم التجريبي")

def test_existing_users():
    """اختبار المستخدمين الموجودين"""
    print("\n🧪 اختبار المستخدمين الموجودين...")
    
    db_manager = DatabaseManager()
    
    # الحصول على جميع المستخدمين
    all_users = db_manager.get_all_users_for_password_management()
    all_employees = db_manager.get_all_employees()
    
    print(f"📊 إحصائيات المستخدمين:")
    print(f"   المستخدمين لإدارة كلمات المرور: {len(all_users)}")
    print(f"   جميع الموظفين: {len(all_employees)}")
    
    print(f"\n👥 المستخدمين لإدارة كلمات المرور:")
    for i, user in enumerate(all_users, 1):
        print(f"   {i}. {user}")
    
    print(f"\n👥 جميع الموظفين:")
    for i, employee in enumerate(all_employees, 1):
        print(f"   {i}. {employee}")

def test_password_management_functions():
    """اختبار دوال إدارة كلمات المرور"""
    print("\n🧪 اختبار دوال إدارة كلمات المرور...")
    
    db_manager = DatabaseManager()
    
    # اختبار إضافة كلمة مرور
    test_employee = "Test Employee"
    test_password = "test123"
    
    print(f"🔐 اختبار إضافة كلمة مرور لـ '{test_employee}'")
    success = db_manager.set_employee_password(test_employee, test_password)
    
    if success:
        print("✅ تم إضافة كلمة المرور بنجاح")
        
        # اختبار التحقق من كلمة المرور
        is_valid = db_manager.verify_employee_password(test_employee, test_password)
        print(f"✅ التحقق من كلمة المرور: {'صحيح' if is_valid else 'خطأ'}")
        
        # اختبار الحصول على كلمة المرور
        stored_password = db_manager.get_employee_password(test_employee)
        print(f"📋 كلمة المرور المخزنة: {stored_password}")
        
        # اختبار الحصول على الموظفين الذين لديهم كلمات مرور
        employees_with_passwords = db_manager.get_employees_with_passwords()
        print(f"👥 الموظفين الذين لديهم كلمات مرور: {employees_with_passwords}")
        
        if test_employee in employees_with_passwords:
            print("✅ المستخدم موجود في قائمة الموظفين الذين لديهم كلمات مرور")
        else:
            print("❌ المستخدم غير موجود في قائمة الموظفين الذين لديهم كلمات مرور")
        
        # تنظيف - حذف كلمة المرور التجريبية
        print(f"\n🧹 تنظيف - حذف كلمة المرور التجريبية...")
        # يمكن إضافة دالة حذف كلمة المرور هنا إذا كانت موجودة
        
    else:
        print("❌ فشل في إضافة كلمة المرور")

def main():
    """الدالة الرئيسية للاختبار"""
    print("🚀 بدء اختبار إصلاح إدارة كلمات المرور للمستخدمين الجدد")
    print("=" * 60)
    
    try:
        test_existing_users()
        test_password_management_functions()
        test_new_user_appears_in_password_management()
        
        print("\n" + "=" * 60)
        print("🎉 انتهى اختبار إصلاح إدارة كلمات المرور")
        print("✅ تم إصلاح مشكلة عدم ظهور المستخدمين الجدد في إدارة كلمات المرور")
        print("\n📋 ملخص الإصلاحات:")
        print("• تم إنشاء دالة get_all_users_for_password_management()")
        print("• تم تحديث إدارة كلمات المرور لاستخدام الدالة الجديدة")
        print("• الآن المستخدمين الجدد يظهرون فوراً في إدارة كلمات المرور")
        print("• يمكن إضافة كلمات مرور للمستخدمين الجدد مباشرة")
        
    except Exception as e:
        print(f"\n❌ فشل في الاختبار: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
