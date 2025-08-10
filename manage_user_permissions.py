#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إدارة صلاحيات المستخدمين
"""

import config
from database_manager import DatabaseManager

def show_current_permissions():
    """عرض الصلاحيات الحالية"""
    print("🔐 الصلاحيات الحالية:")
    print("=" * 50)
    
    print("👑 مدراء المخزن:")
    print(f"   • {config.WAREHOUSE_MANAGER_ID} (مدير مخزن رئيسي)")
    print(f"   • {config.WAREHOUSE_MANAGER_ID_2} (مدير مخزن ثاني)")
    print(f"   • {config.WAREHOUSE_MANAGER_ID_3} (مدير مخزن ثالث)")
    
    print("\n👥 جميع المستخدمين المصرح لهم:")
    for i, user_id in enumerate(config.ALLOWED_USERS, 1):
        role = "مدير مخزن" if user_id in [config.WAREHOUSE_MANAGER_ID, config.WAREHOUSE_MANAGER_ID_2, config.WAREHOUSE_MANAGER_ID_3] else "موظف"
        print(f"   {i}. {user_id} - {role}")

def upgrade_to_manager(user_id):
    """ترقية المستخدم إلى مدير مخزن"""
    print(f"🔧 ترقية المستخدم {user_id} إلى مدير مخزن...")
    
    # قراءة الملف الحالي
    with open('config.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث WAREHOUSE_MANAGER_ID_2
    import re
    pattern = r'WAREHOUSE_MANAGER_ID_2 = \d+'
    new_content = re.sub(pattern, f'WAREHOUSE_MANAGER_ID_2 = {user_id}', content)
    
    # كتابة الملف المحدث
    with open('config.py', 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    # تحديث قاعدة البيانات
    db_manager = DatabaseManager()
    db_manager.add_user(user_id, "ll2005m", "LL2005M", "warehouse_manager")
    
    print(f"✅ تم ترقية المستخدم {user_id} إلى مدير مخزن بنجاح!")

def downgrade_to_employee(user_id):
    """تخفيض المستخدم إلى موظف عادي"""
    print(f"🔧 تخفيض المستخدم {user_id} إلى موظف عادي...")
    
    # قراءة الملف الحالي
    with open('config.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # إزالة من WAREHOUSE_MANAGER_ID_2 إذا كان هو
    if user_id == config.WAREHOUSE_MANAGER_ID_2:
        import re
        pattern = r'WAREHOUSE_MANAGER_ID_2 = \d+'
        new_content = re.sub(pattern, 'WAREHOUSE_MANAGER_ID_2 = 0', content)
        
        # كتابة الملف المحدث
        with open('config.py', 'w', encoding='utf-8') as file:
            file.write(new_content)
    
    # تحديث قاعدة البيانات
    db_manager = DatabaseManager()
    db_manager.add_user(user_id, "ll2005m", "LL2005M", "employee")
    
    print(f"✅ تم تخفيض المستخدم {user_id} إلى موظف عادي بنجاح!")

def main():
    """الدالة الرئيسية"""
    print("=" * 60)
    print("🔐 سكريبت إدارة صلاحيات المستخدمين")
    print("=" * 60)
    
    show_current_permissions()
    
    print("\n" + "=" * 60)
    print("💡 خيارات إدارة الصلاحيات:")
    print("1. ترقية المستخدم 5808690567 إلى مدير مخزن")
    print("2. تخفيض المستخدم 5808690567 إلى موظف عادي")
    print("3. عرض الصلاحيات الحالية فقط")
    
    choice = input("\nاختر الخيار (1-3): ").strip()
    
    if choice == "1":
        upgrade_to_manager(5808690567)
    elif choice == "2":
        downgrade_to_employee(5808690567)
    elif choice == "3":
        print("✅ تم عرض الصلاحيات الحالية")
    else:
        print("❌ خيار غير صحيح")
    
    print("\n" + "=" * 60)
    print("📋 الصلاحيات بعد التحديث:")
    show_current_permissions()

if __name__ == "__main__":
    main() 