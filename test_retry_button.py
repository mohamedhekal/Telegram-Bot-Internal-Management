#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار زر إعادة المحاولة للطلبات الفاشلة
"""

from database_manager import DatabaseManager
from api_manager import api_manager
import config

def test_retry_functionality():
    """اختبار وظيفة إعادة المحاولة"""
    print("🧪 اختبار وظيفة إعادة المحاولة للطلبات الفاشلة...")
    print("=" * 60)
    
    # تهيئة مدير قاعدة البيانات
    db_manager = DatabaseManager()
    
    # 1. اختبار الحصول على الطلبات الفاشلة
    print("1️⃣ اختبار الحصول على الطلبات الفاشلة...")
    failed_orders = db_manager.get_failed_api_orders()
    
    if failed_orders:
        print(f"✅ تم العثور على {len(failed_orders)} طلب فاشل")
        for i, order in enumerate(failed_orders[:3], 1):  # عرض أول 3 طلبات فقط
            print(f"   {i}. {order['receipt_number']} - {order['employee_name']} - {order['api_message']}")
    else:
        print("ℹ️ لا توجد طلبات فاشلة حالياً")
    
    print()
    
    # 2. اختبار الحصول على بيانات الفاتورة
    print("2️⃣ اختبار الحصول على بيانات الفاتورة...")
    if failed_orders:
        test_receipt = failed_orders[0]['receipt_number']
        invoice_data = db_manager.get_invoice_by_receipt(test_receipt)
        
        if invoice_data:
            print(f"✅ تم العثور على بيانات الفاتورة: {test_receipt}")
            print(f"   👤 الموظف: {invoice_data['employee_name']}")
            print(f"   👥 العميل: {invoice_data['client_name']}")
            print(f"   💰 المبلغ: {invoice_data['total_sales']:,.0f} دينار")
        else:
            print(f"❌ لم يتم العثور على بيانات الفاتورة: {test_receipt}")
    else:
        print("ℹ️ لا توجد طلبات فاشلة لاختبار الحصول على البيانات")
    
    print()
    
    # 3. اختبار إرسال طلب تجريبي إلى API
    print("3️⃣ اختبار إرسال طلب تجريبي إلى API...")
    test_invoice = {
        'receipt_number': 'TEST-RETRY-20240115000000',
        'employee_name': 'اختبار إعادة المحاولة',
        'client_name': 'عميل اختبار',
        'client_phone': '+964700000000',
        'governorate': 'بغداد',
        'nearest_point': 'شارع الرشيد',
        'quantity': 1,
        'price': 100.0,
        'total_sales': 100.0,
        'notes': 'طلب اختبار إعادة المحاولة'
    }
    
    api_result = api_manager.send_order_to_api(test_invoice)
    print(f"📡 نتيجة الإرسال: {'نجح' if api_result.get('success') else 'فشل'}")
    print(f"💬 الرسالة: {api_result.get('message', 'غير محدد')}")
    
    print()
    
    # 4. اختبار تحديث عدد المحاولات
    print("4️⃣ اختبار تحديث عدد المحاولات...")
    if failed_orders:
        test_receipt = failed_orders[0]['receipt_number']
        success = db_manager.update_api_order_retry(test_receipt)
        print(f"✅ تحديث عدد المحاولات: {'نجح' if success else 'فشل'}")
    else:
        print("ℹ️ لا توجد طلبات فاشلة لاختبار تحديث المحاولات")
    
    print()
    
    # 5. اختبار تسجيل نتيجة API
    print("5️⃣ اختبار تسجيل نتيجة API...")
    test_api_result = {
        'success': False,
        'message': 'اختبار تسجيل النتيجة',
        'api_order_id': None,
        'api_order_group_id': None
    }
    
    # محاولة تسجيل نتيجة تجريبية
    success = db_manager.record_api_order(1, 'TEST-RECORD-20240115000000', test_api_result)
    print(f"✅ تسجيل نتيجة API: {'نجح' if success else 'فشل'}")
    
    print()
    print("=" * 60)
    print("✅ انتهى اختبار وظيفة إعادة المحاولة")
    print("💡 إذا كانت جميع الاختبارات ناجحة، فإن زر إعادة المحاولة يجب أن يعمل بشكل صحيح")

if __name__ == "__main__":
    test_retry_functionality()
