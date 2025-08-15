#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار ميزة إعادة توجيه الرسائل للبوت
"""

from database_manager import DatabaseManager
from api_manager import api_manager
import config
from datetime import datetime

def test_forward_message_parsing():
    """اختبار تحليل الرسائل المعاد توجيهها"""
    print("🧪 اختبار تحليل الرسائل المعاد توجيهها...")
    print("=" * 60)
    
    # بيانات اختبار
    test_messages = [
        # التنسيق الجديد - كل حقل في سطر منفصل
        """اسم الموظفة /نور
أسم العميل/ محمد
المحافظة/ الانبار
اقرب نقطة دالة / الرمادي
الرقم/ 0782444
العدد/ 1
السعر / 40000
الملاحظات/ لاشيئ""",
        
        # التنسيق القديم - سطر واحد
        "نور/محمد/الانبار/الرمادي/0782444/1/40000/لاشيئ",
        
        # تنسيق بدون /
        """اسم الموظفة نور
أسم العميل محمد
المحافظة الانبار
اقرب نقطة دالة الرمادي
الرقم 0782444
العدد 1
السعر 40000
الملاحظات لاشيئ""",
        
        # تنسيق مختلط
        """اسم الموظفة /نور
أسم العميل محمد
المحافظة /الانبار
اقرب نقطة دالة الرمادي
الرقم /0782444
العدد 1
السعر /40000
الملاحظات لاشيئ"""
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 اختبار {i}:")
        print("الرسالة:")
        print(message)
        print("\nالنتيجة المتوقعة:")
        
        # محاكاة تحليل الرسالة
        lines = [line.strip() for line in message.split('\n') if line.strip()]
        
        if len(lines) == 1:
            # التنسيق القديم
            parts = [part.strip() for part in message.split('/')]
            if len(parts) >= 8:
                print(f"✅ التنسيق القديم - تم العثور على {len(parts)} حقل")
                print(f"   👤 الموظف: {parts[0]}")
                print(f"   👥 العميل: {parts[1]}")
                print(f"   🏛️ المحافظة: {parts[2]}")
                print(f"   📍 النقطة: {parts[3]}")
                print(f"   📞 الهاتف: {parts[4]}")
                print(f"   📦 العدد: {parts[5]}")
                print(f"   💰 السعر: {parts[6]}")
                print(f"   📝 الملاحظات: {parts[7] if len(parts) > 7 else ''}")
            else:
                print(f"❌ التنسيق القديم - عدد الحقول غير كافي: {len(parts)}")
        else:
            # التنسيق الجديد
            if len(lines) >= 8:
                print(f"✅ التنسيق الجديد - تم العثور على {len(lines)} سطر")
                
                # محاولة استخراج البيانات
                try:
                    employee_name = lines[0].split('/')[1].strip() if '/' in lines[0] else lines[0]
                    client_name = lines[1].split('/')[1].strip() if '/' in lines[1] else lines[1]
                    governorate = lines[2].split('/')[1].strip() if '/' in lines[2] else lines[2]
                    nearest_point = lines[3].split('/')[1].strip() if '/' in lines[3] else lines[3]
                    phone_number = lines[4].split('/')[1].strip() if '/' in lines[4] else lines[4]
                    quantity = lines[5].split('/')[1].strip() if '/' in lines[5] else lines[5]
                    price = lines[6].split('/')[1].strip() if '/' in lines[6] else lines[6]
                    notes = lines[7].split('/')[1].strip() if '/' in lines[7] else lines[7]
                    
                    print(f"   👤 الموظف: {employee_name}")
                    print(f"   👥 العميل: {client_name}")
                    print(f"   🏛️ المحافظة: {governorate}")
                    print(f"   📍 النقطة: {nearest_point}")
                    print(f"   📞 الهاتف: {phone_number}")
                    print(f"   📦 العدد: {quantity}")
                    print(f"   💰 السعر: {price}")
                    print(f"   📝 الملاحظات: {notes}")
                except IndexError:
                    print("❌ خطأ في استخراج البيانات من التنسيق الجديد")
            else:
                print(f"❌ التنسيق الجديد - عدد الأسطر غير كافي: {len(lines)}")
        
        print("-" * 40)

def test_invoice_creation():
    """اختبار إنشاء فاتورة من رسالة معاد توجيهها"""
    print("\n🧪 اختبار إنشاء فاتورة من رسالة معاد توجيهها...")
    print("=" * 60)
    
    # بيانات اختبار
    test_data = {
        'receipt_number': 'TEST-FORWARD-20240115000000',
        'employee_name': 'نور',
        'client_name': 'محمد',
        'client_phone': '0782444',
        'governorate': 'الانبار',
        'nearest_point': 'الرمادي',
        'quantity': 1,
        'price': 40000.0,
        'total_sales': 40000.0,
        'notes': 'لاشيئ'
    }
    
    # تهيئة مدير قاعدة البيانات
    db_manager = DatabaseManager()
    
    # اختبار إضافة الفاتورة
    print("1️⃣ اختبار إضافة الفاتورة إلى قاعدة البيانات...")
    result = db_manager.add_invoice(test_data)
    
    if result.get('success'):
        print("✅ تم إضافة الفاتورة بنجاح")
        invoice_id = result.get('invoice_id')
        print(f"🆔 معرف الفاتورة: {invoice_id}")
    else:
        print(f"❌ فشل في إضافة الفاتورة: {result.get('error', 'خطأ غير معروف')}")
        return
    
    # اختبار إرسال الطلب إلى API
    print("\n2️⃣ اختبار إرسال الطلب إلى API...")
    api_result = api_manager.send_order_to_api(test_data)
    
    if api_result.get('success'):
        print("✅ تم إرسال الطلب إلى API بنجاح")
        print(f"🆔 معرف الطلب: {api_result.get('api_order_id', 'غير محدد')}")
        print(f"📋 مجموعة الطلب: {api_result.get('api_order_group_id', 'غير محدد')}")
    else:
        print(f"❌ فشل في إرسال الطلب إلى API: {api_result.get('message', 'خطأ غير معروف')}")
    
    # اختبار تسجيل نتيجة API
    print("\n3️⃣ اختبار تسجيل نتيجة API...")
    success = db_manager.record_api_order(invoice_id, test_data['receipt_number'], api_result)
    
    if success:
        print("✅ تم تسجيل نتيجة API بنجاح")
    else:
        print("❌ فشل في تسجيل نتيجة API")
    
    # اختبار الحصول على حالة API
    print("\n4️⃣ اختبار الحصول على حالة API...")
    api_status = db_manager.get_api_order_status(test_data['receipt_number'])
    
    if api_status:
        print(f"✅ تم العثور على حالة API: {api_status['api_status']}")
        print(f"💬 الرسالة: {api_status['api_message']}")
    else:
        print("❌ لم يتم العثور على حالة API")

def test_forward_message_workflow():
    """اختبار سير العمل الكامل لإعادة توجيه الرسائل"""
    print("\n🧪 اختبار سير العمل الكامل لإعادة توجيه الرسائل...")
    print("=" * 60)
    
    # رسالة اختبار
    test_message = """اسم الموظفة /نور
أسم العميل/ محمد
المحافظة/ الانبار
اقرب نقطة دالة / الرمادي
الرقم/ 0782444
العدد/ 1
السعر / 40000
الملاحظات/ لاشيئ"""
    
    print("📝 الرسالة المعاد توجيهها:")
    print(test_message)
    
    # محاكاة معالجة الرسالة
    print("\n🔄 محاكاة معالجة الرسالة...")
    
    # 1. تحليل الرسالة
    lines = [line.strip() for line in test_message.split('\n') if line.strip()]
    
    if len(lines) >= 8:
        print("✅ تم تحليل الرسالة بنجاح")
        
        # 2. استخراج البيانات
        try:
            employee_name = lines[0].split('/')[1].strip()
            client_name = lines[1].split('/')[1].strip()
            governorate = lines[2].split('/')[1].strip()
            nearest_point = lines[3].split('/')[1].strip()
            phone_number = lines[4].split('/')[1].strip()
            quantity = int(lines[5].split('/')[1].strip())
            price = float(lines[6].split('/')[1].strip())
            notes = lines[7].split('/')[1].strip()
            
            print("✅ تم استخراج البيانات بنجاح")
            
            # 3. إنشاء بيانات الفاتورة
            receipt_number = f"FORWARD-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            invoice_data = {
                'receipt_number': receipt_number,
                'employee_name': employee_name,
                'client_name': client_name,
                'client_phone': phone_number,
                'governorate': governorate,
                'nearest_point': nearest_point,
                'quantity': quantity,
                'price': price,
                'total_sales': price,
                'notes': notes
            }
            
            print("✅ تم إنشاء بيانات الفاتورة")
            
            # 4. حفظ في قاعدة البيانات
            db_manager = DatabaseManager()
            db_result = db_manager.add_invoice(invoice_data)
            
            if db_result.get('success'):
                print("✅ تم حفظ الفاتورة في قاعدة البيانات")
                
                # 5. إرسال إلى API
                api_result = api_manager.send_order_to_api(invoice_data)
                
                if api_result.get('success'):
                    print("✅ تم إرسال الطلب إلى API بنجاح")
                else:
                    print(f"⚠️ فشل في إرسال الطلب إلى API: {api_result.get('message')}")
                
                # 6. تسجيل نتيجة API
                db_manager.record_api_order(db_result.get('invoice_id'), receipt_number, api_result)
                print("✅ تم تسجيل نتيجة API")
                
            else:
                print(f"❌ فشل في حفظ الفاتورة: {db_result.get('error')}")
                
        except (ValueError, IndexError) as e:
            print(f"❌ خطأ في استخراج البيانات: {e}")
    else:
        print(f"❌ خطأ في تحليل الرسالة: عدد الأسطر غير كافي ({len(lines)})")

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء اختبار ميزة إعادة توجيه الرسائل")
    print("=" * 60)
    
    # اختبار تحليل الرسائل
    test_forward_message_parsing()
    
    # اختبار إنشاء الفواتير
    test_invoice_creation()
    
    # اختبار سير العمل الكامل
    test_forward_message_workflow()
    
    print("\n" + "=" * 60)
    print("✅ انتهى اختبار ميزة إعادة توجيه الرسائل")
    print("💡 إذا كانت جميع الاختبارات ناجحة، فإن الميزة تعمل بشكل صحيح")

if __name__ == "__main__":
    main()
