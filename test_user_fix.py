#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار إصلاحات أزرار العودة في شاشة إضافة المستخدم
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# استيراد الدوال المطلوبة من البوت
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot_clean import (
    user_management_callback_handler,
    add_user_role_handler,
    user_management_handler,
    show_user_management_menu,
    show_admin_menu,
    USER_MANAGEMENT_MENU,
    ADD_USER_ROLE,
    ADD_USER_DATA,
    ADMIN_MENU
)

async def test_user_management_callback_handler():
    """اختبار معالج أزرار إدارة المستخدمين"""
    print("🧪 اختبار معالج أزرار إدارة المستخدمين...")
    
    # إنشاء mock objects
    update = Mock(spec=Update)
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    
    # اختبار زر "إضافة مستخدم جديد"
    query = Mock()
    query.data = "add_user"
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    update.callback_query = query
    
    result = await user_management_callback_handler(update, context)
    
    assert result == ADD_USER_ROLE, f"توقع ADD_USER_ROLE، حصل على {result}"
    query.answer.assert_called_once()
    query.edit_message_text.assert_called_once()
    
    print("✅ اختبار زر 'إضافة مستخدم جديد' نجح")
    
    # اختبار زر "العودة للقائمة الرئيسية"
    query.data = "back_to_admin"
    query.answer.reset_mock()
    query.edit_message_text.reset_mock()
    
    # Mock show_admin_menu
    show_admin_menu_mock = AsyncMock(return_value=ADMIN_MENU)
    import bot_clean
    bot_clean.show_admin_menu = show_admin_menu_mock
    
    result = await user_management_callback_handler(update, context)
    
    assert result == ADMIN_MENU, f"توقع ADMIN_MENU، حصل على {result}"
    show_admin_menu_mock.assert_called_once_with(update, context)
    
    print("✅ اختبار زر 'العودة للقائمة الرئيسية' نجح")
    
    # اختبار زر "العودة لإدارة المستخدمين"
    query.data = "back_to_user_management"
    query.answer.reset_mock()
    
    # Mock show_user_management_menu
    show_user_management_menu_mock = AsyncMock(return_value=USER_MANAGEMENT_MENU)
    bot_clean.show_user_management_menu = show_user_management_menu_mock
    
    result = await user_management_callback_handler(update, context)
    
    assert result == USER_MANAGEMENT_MENU, f"توقع USER_MANAGEMENT_MENU، حصل على {result}"
    show_user_management_menu_mock.assert_called_once_with(update, context)
    
    print("✅ اختبار زر 'العودة لإدارة المستخدمين' نجح")

async def test_add_user_role_handler():
    """اختبار معالج اختيار دور المستخدم"""
    print("\n🧪 اختبار معالج اختيار دور المستخدم...")
    
    # إنشاء mock objects
    update = Mock(spec=Update)
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    
    # اختبار اختيار دور "موظف"
    query = Mock()
    query.data = "role_employee"
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    update.callback_query = query
    
    result = await add_user_role_handler(update, context)
    
    assert result == ADD_USER_DATA, f"توقع ADD_USER_DATA، حصل على {result}"
    assert context.user_data['new_user_role'] == "employee"
    query.answer.assert_called_once()
    query.edit_message_text.assert_called_once()
    
    print("✅ اختبار اختيار دور 'موظف' نجح")
    
    # اختبار زر "العودة"
    query.data = "back_to_user_management"
    query.answer.reset_mock()
    query.edit_message_text.reset_mock()
    
    # Mock show_user_management_menu
    show_user_management_menu_mock = AsyncMock(return_value=USER_MANAGEMENT_MENU)
    import bot_clean
    bot_clean.show_user_management_menu = show_user_management_menu_mock
    
    result = await add_user_role_handler(update, context)
    
    assert result == USER_MANAGEMENT_MENU, f"توقع USER_MANAGEMENT_MENU، حصل على {result}"
    show_user_management_menu_mock.assert_called_once_with(update, context)
    
    print("✅ اختبار زر 'العودة' في اختيار الدور نجح")

async def test_user_management_handler_errors():
    """اختبار معالج أخطاء إدارة المستخدمين"""
    print("\n🧪 اختبار معالج أخطاء إدارة المستخدمين...")
    
    # إنشاء mock objects
    update = Mock(spec=Update)
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    
    # اختبار خطأ في تنسيق البيانات
    message = Mock()
    message.text = "بيانات غير صحيحة"
    message.reply_text = AsyncMock()
    update.message = message
    
    result = await user_management_handler(update, context)
    
    assert result == ADD_USER_DATA, f"توقع ADD_USER_DATA، حصل على {result}"
    message.reply_text.assert_called_once()
    
    # التحقق من أن الرسالة تحتوي على زر العودة
    call_args = message.reply_text.call_args
    assert "🔙 العودة لإدارة المستخدمين" in str(call_args), "زر العودة غير موجود في رسالة الخطأ"
    
    print("✅ اختبار خطأ تنسيق البيانات نجح")
    
    # اختبار خطأ في معرف المستخدم
    message.text = "@testuser\nId: abc"  # معرف غير صحيح
    message.reply_text.reset_mock()
    
    result = await user_management_handler(update, context)
    
    assert result == ADD_USER_DATA, f"توقع ADD_USER_DATA، حصل على {result}"
    message.reply_text.assert_called_once()
    
    print("✅ اختبار خطأ معرف المستخدم نجح")

async def main():
    """الدالة الرئيسية للاختبار"""
    print("🚀 بدء اختبار إصلاحات أزرار العودة في شاشة إضافة المستخدم")
    print("=" * 60)
    
    try:
        await test_user_management_callback_handler()
        await test_add_user_role_handler()
        await test_user_management_handler_errors()
        
        print("\n" + "=" * 60)
        print("🎉 جميع الاختبارات نجحت!")
        print("✅ تم إصلاح مشكلة أزرار العودة في شاشة إضافة المستخدم")
        print("\n📋 ملخص الإصلاحات:")
        print("• تم إصلاح تعريف الحالات في ConversationHandler")
        print("• تم إضافة أزرار العودة لجميع رسائل الخطأ")
        print("• تم تحسين تجربة المستخدم في التنقل بين الشاشات")
        
    except Exception as e:
        print(f"\n❌ فشل في الاختبار: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
