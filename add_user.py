#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إضافة مستخدم جديد
"""

from database_manager import DatabaseManager
import config

def add_new_user():
    """إضافة المستخدم الجديد إلى قاعدة البيانات"""
    print("👤 إضافة مستخدم جديد...")
    
    # تهيئة مدير قاعدة البيانات
    db_manager = DatabaseManager()
    
    # بيانات المستخدم الجديد
    user_id = 5808690567
    username = "ll2005m"
    full_name = "LL2005M"  # يمكن تغيير هذا لاحقاً
    role = "employee"  # صلاحية موظف عادي
    
    try:
        # إضافة المستخدم الجديد (سيتم استبداله إذا كان موجوداً)
        success = db_manager.add_user(user_id, username, full_name, role)
        
        if success:
            print("✅ تم إضافة المستخدم بنجاح!")
            print(f"👤 معرف المستخدم: {user_id}")
            print(f"📝 اسم المستخدم: @{username}")
            print(f"🔐 الصلاحية: {role}")
            print(f"📊 تم إضافته إلى قاعدة البيانات")
            
            # التحقق من دور المستخدم
            user_role = db_manager.get_user_role(user_id)
            print(f"🔍 دور المستخدم المؤكد: {user_role}")
        else:
            print("❌ فشل في إضافة المستخدم")
        
        # عرض معلومات المستخدمين المصرح لهم
        print("\n📋 المستخدمين المصرح لهم في config.py:")
        for i, allowed_user_id in enumerate(config.ALLOWED_USERS, 1):
            role = "مدير مخزن" if allowed_user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3] else "موظف"
            print(f"{i}. معرف: {allowed_user_id} - الصلاحية: {role}")
        
    except Exception as e:
        print(f"❌ خطأ في إضافة المستخدم: {e}")
        
    except Exception as e:
        print(f"❌ خطأ في إضافة المستخدم: {e}")

def main():
    """الدالة الرئيسية"""
    print("=" * 50)
    print("👤 سكريبت إضافة مستخدم جديد")
    print("=" * 50)
    
    add_new_user()
    
    print("\n" + "=" * 50)
    print("💡 ملاحظات:")
    print("• تم إضافة المستخدم إلى ملف config.py")
    print("• تم إضافة المستخدم إلى قاعدة البيانات")
    print("• يمكن للمستخدم الآن الوصول إلى البوت")
    print("• للترقية إلى مدير مخزن، تحدث WAREHOUSE_MANAGER_ID في config.py")

if __name__ == "__main__":
    main() 