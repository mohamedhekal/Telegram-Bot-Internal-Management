#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار الاتصال بـ API
"""

from api_manager import api_manager
import config

def test_api_connection():
    """اختبار الاتصال بـ API"""
    print("🔍 اختبار الاتصال بـ API...")
    print("=" * 50)
    
    # اختبار الاتصال
    result = api_manager.test_api_connection()
    
    if result.get('success'):
        print("✅ الاتصال بـ API يعمل بشكل صحيح!")
        print(f"📡 رمز الحالة: {result.get('status_code', 'غير محدد')}")
        print(f"💬 الرسالة: {result.get('message', 'غير محدد')}")
    else:
        print("❌ فشل في الاتصال بـ API!")
        print(f"⚠️ السبب: {result.get('message', 'خطأ غير معروف')}")
    
    print("\n" + "=" * 50)
    
    # عرض إعدادات API
    print("⚙️ إعدادات API:")
    print(f"🔗 الرابط: {config.API_BASE_URL}")
    print(f"👤 اسم المستخدم: {config.API_USERNAME}")
    print(f"🔐 كلمة المرور: {'*' * len(config.API_PASSWORD)}")
    print(f"⏱️ مهلة الاتصال: {config.API_TIMEOUT} ثانية")
    print(f"🔄 API مفعل: {'نعم' if config.API_ENABLED else 'لا'}")
    
    print("\n" + "=" * 50)
    
    # اختبار إرسال طلب تجريبي
    if config.API_ENABLED:
        print("🧪 اختبار إرسال طلب تجريبي...")
        
        test_invoice = {
            'receipt_number': 'TEST-20240115000000',
            'employee_name': 'اختبار',
            'client_name': 'عميل اختبار',
            'client_phone': '+964700000000',
            'governorate': 'بغداد',
            'nearest_point': 'شارع الرشيد',
            'quantity': 1,
            'price': 100.0,
            'total_sales': 100.0,
            'notes': 'طلب اختبار'
        }
        
        api_result = api_manager.send_order_to_api(test_invoice)
        
        if api_result.get('success'):
            print("✅ تم إرسال الطلب التجريبي بنجاح!")
            print(f"🆔 معرف الطلب: {api_result.get('api_order_id', 'غير محدد')}")
            print(f"📋 مجموعة الطلب: {api_result.get('api_order_group_id', 'غير محدد')}")
        else:
            print("❌ فشل في إرسال الطلب التجريبي!")
            print(f"⚠️ السبب: {api_result.get('message', 'خطأ غير معروف')}")
    else:
        print("⚠️ API معطل - تم تخطي اختبار الإرسال")

if __name__ == "__main__":
    test_api_connection()
