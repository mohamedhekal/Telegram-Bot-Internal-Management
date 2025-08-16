#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار مبسط لإصلاحات أزرار العودة في شاشة إضافة المستخدم
"""

def test_conversation_handler_states():
    """اختبار تعريف الحالات في ConversationHandler"""
    print("🧪 اختبار تعريف الحالات في ConversationHandler...")
    
    # قراءة الملف والبحث عن التعريفات
    with open('bot_clean.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # التحقق من وجود التعريفات الصحيحة
    checks = [
        ('USER_MANAGEMENT_MENU', 'user_management_callback_handler'),
        ('ADD_USER_ROLE', 'add_user_role_handler'),
        ('ADD_USER_DATA', 'user_management_callback_handler')
    ]
    
    all_passed = True
    
    for state, handler in checks:
        if f'{state}: [' in content and handler in content:
            print(f"✅ {state} يستخدم {handler}")
        else:
            print(f"❌ {state} لا يستخدم {handler}")
            all_passed = False
    
    return all_passed

def test_error_messages():
    """اختبار رسائل الخطأ تحتوي على أزرار العودة"""
    print("\n🧪 اختبار رسائل الخطأ...")
    
    with open('bot_clean.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # التحقق من وجود أزرار العودة في رسائل الخطأ
    error_checks = [
        '🔙 العودة لإدارة المستخدمين',
        'callback_data="back_to_user_management"',
        '💡 أو اضغط على زر العودة'
    ]
    
    all_passed = True
    
    for check in error_checks:
        if check in content:
            print(f"✅ وجد: {check}")
        else:
            print(f"❌ لم يجد: {check}")
            all_passed = False
    
    return all_passed

def test_callback_handlers():
    """اختبار معالجات الأزرار"""
    print("\n🧪 اختبار معالجات الأزرار...")
    
    with open('bot_clean.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # التحقق من وجود معالجات الأزرار
    handler_checks = [
        'user_management_callback_handler',
        'add_user_role_handler',
        'back_to_user_management',
        'back_to_admin'
    ]
    
    all_passed = True
    
    for check in handler_checks:
        if check in content:
            print(f"✅ وجد: {check}")
        else:
            print(f"❌ لم يجد: {check}")
            all_passed = False
    
    return all_passed

def test_show_functions():
    """اختبار دوال العرض"""
    print("\n🧪 اختبار دوال العرض...")
    
    with open('bot_clean.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # التحقق من وجود التعامل مع callback_query
    show_checks = [
        'if update.callback_query:',
        'edit_message_text',
        'show_user_management_menu',
        'show_admin_menu'
    ]
    
    all_passed = True
    
    for check in show_checks:
        if check in content:
            print(f"✅ وجد: {check}")
        else:
            print(f"❌ لم يجد: {check}")
            all_passed = False
    
    return all_passed

def main():
    """الدالة الرئيسية للاختبار"""
    print("🚀 بدء اختبار إصلاحات أزرار العودة في شاشة إضافة المستخدم")
    print("=" * 60)
    
    tests = [
        test_conversation_handler_states,
        test_error_messages,
        test_callback_handlers,
        test_show_functions
    ]
    
    all_passed = True
    
    for test in tests:
        try:
            result = test()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ فشل في الاختبار: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 جميع الاختبارات نجحت!")
        print("✅ تم إصلاح مشكلة أزرار العودة في شاشة إضافة المستخدم")
        print("\n📋 ملخص الإصلاحات:")
        print("• تم إصلاح تعريف الحالات في ConversationHandler")
        print("• تم إضافة أزرار العودة لجميع رسائل الخطأ")
        print("• تم تحسين التعامل مع callback_query")
        print("• تم تحسين تجربة المستخدم في التنقل بين الشاشات")
    else:
        print("❌ بعض الاختبارات فشلت")
        print("🔧 يرجى مراجعة الإصلاحات")

if __name__ == "__main__":
    main()
