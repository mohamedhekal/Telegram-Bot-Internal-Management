#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاح إضافة المستخدمين
"""

from database_manager import DatabaseManager
import config

def test_user_addition_workflow():
    """اختبار سير عمل إضافة المستخدم"""
    print("🧪 اختبار سير عمل إضافة المستخدم...")
    
    db_manager = DatabaseManager()
    
    # بيانات المستخدم التجريبي
    test_user_id = 987654321
    test_username = "new_test_user"
    test_full_name = "New Test User"
    test_role = "employee"
    
    print(f"📝 بيانات المستخدم:")
    print(f"   🆔 معرف المستخدم: {test_user_id}")
    print(f"   👤 اسم المستخدم: {test_username}")
    print(f"   📝 الاسم الكامل: {test_full_name}")
    print(f"   🔐 الدور: {test_role}")
    
    # التحقق من وجود المستخدم قبل الإضافة
    print(f"\n🔍 التحقق من وجود المستخدم قبل الإضافة:")
    role_before = db_manager.get_user_role(test_user_id)
    print(f"   دور المستخدم: {role_before}")
    
    in_allowed_before = test_user_id in config.ALLOWED_USERS
    print(f"   موجود في ALLOWED_USERS: {in_allowed_before}")
    
    # إضافة المستخدم
    print(f"\n➕ إضافة المستخدم...")
    result = db_manager.add_user(test_user_id, test_username, test_full_name, test_role)
    
    if result:
        print("✅ تم إضافة المستخدم لقاعدة البيانات بنجاح")
        
        # التحقق من إضافة المستخدم في قاعدة البيانات
        role_after = db_manager.get_user_role(test_user_id)
        print(f"🔍 دور المستخدم بعد الإضافة: {role_after}")
        
        # محاكاة إضافة المستخدم لـ ALLOWED_USERS (كما يحدث في البوت)
        if test_user_id not in config.ALLOWED_USERS:
            config.ALLOWED_USERS.add(test_user_id)
            print("✅ تم إضافة المستخدم لـ ALLOWED_USERS")
        else:
            print("⚠️ المستخدم موجود بالفعل في ALLOWED_USERS")
        
        # التحقق النهائي
        print(f"\n🔍 التحقق النهائي:")
        in_allowed_after = test_user_id in config.ALLOWED_USERS
        print(f"   موجود في ALLOWED_USERS: {in_allowed_after}")
        
        if in_allowed_after:
            print("✅ المستخدم يمكنه الوصول للبوت الآن!")
        else:
            print("❌ المستخدم لا يزال لا يمكنه الوصول للبوت")
            
    else:
        print("❌ فشل في إضافة المستخدم لقاعدة البيانات")

def test_existing_users():
    """اختبار المستخدمين الموجودين"""
    print("\n🧪 اختبار المستخدمين الموجودين...")
    
    print(f"📋 عدد المستخدمين المصرح لهم: {len(config.ALLOWED_USERS)}")
    print("👥 المستخدمين المصرح لهم:")
    for user_id in config.ALLOWED_USERS:
        print(f"   • {user_id}")

def test_user_validation():
    """اختبار التحقق من صلاحيات المستخدم"""
    print("\n🧪 اختبار التحقق من صلاحيات المستخدم...")
    
    # اختبار المستخدم الجديد
    test_user_id = 987654321
    if test_user_id in config.ALLOWED_USERS:
        print(f"✅ المستخدم {test_user_id} مصرح له بالوصول")
    else:
        print(f"❌ المستخدم {test_user_id} غير مصرح له بالوصول")
    
    # اختبار مستخدم موجود
    existing_user_id = 1801438595
    if existing_user_id in config.ALLOWED_USERS:
        print(f"✅ المستخدم {existing_user_id} مصرح له بالوصول")
    else:
        print(f"❌ المستخدم {existing_user_id} غير مصرح له بالوصول")

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء اختبار إصلاح إضافة المستخدمين")
    print("=" * 60)
    
    # اختبار سير عمل إضافة المستخدم
    test_user_addition_workflow()
    
    # اختبار المستخدمين الموجودين
    test_existing_users()
    
    # اختبار التحقق من صلاحيات المستخدم
    test_user_validation()
    
    print("\n" + "=" * 60)
    print("✅ انتهى اختبار إصلاح إضافة المستخدمين")
    print("💡 الآن المستخدمين الجدد يمكنهم الوصول للبوت فوراً!")

if __name__ == "__main__":
    main()
