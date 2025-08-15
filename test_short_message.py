#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار استخراج الرسائل المختصرة من API
"""

import json

def extract_short_message(response_text: str) -> str:
    """
    استخراج رسالة مختصرة من رد API
    
    Args:
        response_text: النص الكامل للرد من API
        
    Returns:
        str: رسالة مختصرة
    """
    try:
        # محاولة تحليل JSON
        data = json.loads(response_text)
        
        # البحث عن رسالة في الحقول الشائعة
        message_fields = ['message', 'error', 'msg', 'description', 'detail']
        for field in message_fields:
            if field in data and data[field]:
                message = str(data[field])
                # تقصير الرسالة إذا كانت طويلة
                if len(message) > 100:
                    message = message[:100] + "..."
                return message
        
        # إذا لم نجد رسالة، نعيد أول 100 حرف من النص
        if len(response_text) > 100:
            return response_text[:100] + "..."
        return response_text
        
    except (json.JSONDecodeError, TypeError):
        # إذا فشل تحليل JSON، نعيد أول 100 حرف
        if len(response_text) > 100:
            return response_text[:100] + "..."
        return response_text

def test_short_message_extraction():
    """اختبار استخراج الرسائل المختصرة"""
    print("🧪 اختبار استخراج الرسائل المختصرة...")
    
    # أمثلة على ردود API مختلفة
    test_responses = [
        {
            "name": "رد بسيط مع message",
            "response": '{"message": "Invalid credentials", "status": "error"}',
            "expected": "Invalid credentials"
        },
        {
            "name": "رد مع error",
            "response": '{"error": "Unauthorized access", "code": 401}',
            "expected": "Unauthorized access"
        },
        {
            "name": "رد مع description",
            "response": '{"description": "Database connection failed", "timestamp": "2024-01-15"}',
            "expected": "Database connection failed"
        },
        {
            "name": "رد مع msg",
            "response": '{"msg": "Validation failed", "errors": {"field": "required"}}',
            "expected": "Validation failed"
        },
        {
            "name": "رد طويل مع message",
            "response": '{"message": "This is a very long error message that contains many details about what went wrong and how to fix it and what the user should do next and additional information that might be helpful for debugging purposes", "code": 500}',
            "expected": "This is a very long error message that contains many details about what went wrong and how to fix it and what the user should do next and additional information that might be helpful for debugging purposes..."
        },
        {
            "name": "رد بدون message",
            "response": '{"status": "error", "code": 404, "timestamp": "2024-01-15T10:30:00Z"}',
            "expected": '{"status": "error", "code": 404, "timestamp": "2024-01-15T10:30:00Z"}'
        },
        {
            "name": "رد طويل بدون message",
            "response": '{"status": "error", "code": 500, "timestamp": "2024-01-15T10:30:00Z", "details": "This is a very long response with many details and information that goes on and on and contains a lot of data that might not be necessary for the user to see in the error message"}',
            "expected": '{"status": "error", "code": 500, "timestamp": "2024-01-15T10:30:00Z", "details": "This is a very long response with many details and information that goes on and on and contains a lot of data that might not be necessary for the user to see in the error message"...'
        },
        {
            "name": "رد غير صحيح JSON",
            "response": "This is not a valid JSON response but a plain text error message",
            "expected": "This is not a valid JSON response but a plain text error message"
        },
        {
            "name": "رد طويل غير صحيح JSON",
            "response": "This is a very long plain text error message that contains many details about what went wrong and how to fix it and what the user should do next and additional information that might be helpful for debugging purposes and more text that goes on and on",
            "expected": "This is a very long plain text error message that contains many details about what went wrong and how to fix it and what the user should do next and additional information that might be helpful for debugging purposes and more text that goes on and on..."
        }
    ]
    
    print("📊 نتائج الاختبار:")
    print("-" * 60)
    
    for i, test in enumerate(test_responses, 1):
        result = extract_short_message(test['response'])
        print(f"{i}. {test['name']}")
        print(f"   الرد الأصلي: {test['response']}")
        print(f"   الرسالة المختصرة: {result}")
        print(f"   متوقع: {test['expected']}")
        print(f"   ✅ صحيح" if result == test['expected'] else f"   ❌ خطأ")
        print()

def test_error_message_formatting():
    """اختبار تنسيق رسائل الخطأ"""
    print("\n🧪 اختبار تنسيق رسائل الخطأ...")
    
    error_scenarios = [
        {
            "status_code": 401,
            "response_text": '{"error": "Unauthorized", "message": "Invalid credentials"}',
            "expected": "خطأ في المصادقة: Invalid credentials"
        },
        {
            "status_code": 422,
            "response_text": '{"message": "Validation failed", "errors": {"phone": ["Invalid phone number"]}}',
            "expected": "خطأ في التحقق من البيانات: Validation failed"
        },
        {
            "status_code": 500,
            "response_text": '{"error": "Internal server error", "message": "Database connection failed"}',
            "expected": "خطأ في الخادم: Database connection failed"
        },
        {
            "status_code": 404,
            "response_text": '{"error": "Not found", "message": "API endpoint not found"}',
            "expected": "خطأ غير متوقع: 404 - API endpoint not found"
        }
    ]
    
    print("📊 تنسيق رسائل الخطأ:")
    print("-" * 60)
    
    for i, scenario in enumerate(error_scenarios, 1):
        short_message = extract_short_message(scenario['response_text'])
        
        if scenario['status_code'] == 401:
            formatted_message = f"خطأ في المصادقة: {short_message}"
        elif scenario['status_code'] == 422:
            formatted_message = f"خطأ في التحقق من البيانات: {short_message}"
        elif scenario['status_code'] == 500:
            formatted_message = f"خطأ في الخادم: {short_message}"
        else:
            formatted_message = f"خطأ غير متوقع: {scenario['status_code']} - {short_message}"
        
        print(f"{i}. رمز الحالة: {scenario['status_code']}")
        print(f"   الرد الأصلي: {scenario['response_text']}")
        print(f"   الرسالة المختصرة: {short_message}")
        print(f"   الرسالة المنسقة: {formatted_message}")
        print(f"   متوقع: {scenario['expected']}")
        print(f"   ✅ صحيح" if formatted_message == scenario['expected'] else f"   ❌ خطأ")
        print()

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء اختبار استخراج الرسائل المختصرة")
    print("=" * 70)
    
    # اختبار استخراج الرسائل المختصرة
    test_short_message_extraction()
    
    # اختبار تنسيق رسائل الخطأ
    test_error_message_formatting()
    
    print("=" * 70)
    print("✅ انتهى اختبار استخراج الرسائل المختصرة")
    print("💡 الآن رسائل الخطأ مختصرة ومفيدة!")

if __name__ == "__main__":
    main()
