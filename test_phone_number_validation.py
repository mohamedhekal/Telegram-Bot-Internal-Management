#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار قبول أرقام التليفون المختلفة
"""

def test_phone_number_validation():
    """اختبار التحقق من أرقام التليفون"""
    print("🧪 اختبار قبول أرقام التليفون المختلفة...")
    print("=" * 60)
    
    # قائمة أرقام التليفون للاختبار
    test_phone_numbers = [
        # أرقام عادية
        "0782444",
        "0782444000",
        "07824440000",
        "078244400000",
        
        # أرقام مع مسافات
        "078 2444",
        "078 244 4000",
        "078 244 400 00",
        
        # أرقام مع شرطات
        "078-2444",
        "078-244-4000",
        "078-244-400-00",
        
        # أرقام مع علامة +
        "+964782444",
        "+964782444000",
        
        # أرقام عربية
        "٠٧٨٢٤٤٤",
        "٠٧٨٢٤٤٤٠٠٠",
        
        # أرقام مختلطة
        "078٢٤٤٤",
        "٠٧٨2444",
        
        # أرقام قصيرة
        "123",
        "1234",
        "12345",
        
        # أرقام طويلة
        "123456789012345",
        "12345678901234567890",
    ]
    
    def validate_phone_number(phone_number):
        """دالة التحقق من رقم الهاتف (محدثة)"""
        # تنظيف الرقم
        phone_clean = phone_number.replace(' ', '').replace('-', '').replace('_', '').replace('+', '')
        
        # تحويل الأرقام العربية إلى أرقام إنجليزية
        arabic_to_english = {
            '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
        }
        for arabic, english in arabic_to_english.items():
            phone_clean = phone_clean.replace(arabic, english)
        
        # التحقق من أن الرقم يحتوي على أرقام فقط
        if not phone_clean.isdigit():
            return False, f"يحتوي على أحرف غير رقمية: '{phone_number}' -> '{phone_clean}'"
        
        return True, phone_clean
    
    print("📱 اختبار أرقام التليفون:")
    print("-" * 40)
    
    valid_count = 0
    invalid_count = 0
    
    for phone in test_phone_numbers:
        is_valid, result = validate_phone_number(phone)
        
        if is_valid:
            print(f"✅ صحيح: '{phone}' -> '{result}'")
            valid_count += 1
        else:
            print(f"❌ خطأ: '{phone}' - {result}")
            invalid_count += 1
    
    print("\n📊 نتائج الاختبار:")
    print("-" * 30)
    print(f"✅ الأرقام المقبولة: {valid_count}")
    print(f"❌ الأرقام المرفوضة: {invalid_count}")
    print(f"📈 نسبة القبول: {(valid_count/(valid_count+invalid_count)*100):.1f}%")
    
    print("\n💡 ملاحظات:")
    print("-" * 20)
    print("• النظام يقبل الآن أي رقم تليفون عادي")
    print("• يتم تنظيف الرقم من المسافات والشرطات")
    print("• يتم تحويل الأرقام العربية إلى إنجليزية")
    print("• لا يوجد حد أدنى أو أقصى لطول الرقم")
    print("• يجب أن يحتوي الرقم على أرقام فقط")

def test_phone_number_examples():
    """اختبار أمثلة عملية لأرقام التليفون"""
    print("\n🧪 أمثلة عملية لأرقام التليفون:")
    print("=" * 50)
    
    examples = [
        ("0782444", "رقم عادي"),
        ("078-244-4000", "رقم مع شرطات"),
        ("078 244 4000", "رقم مع مسافات"),
        ("+964782444", "رقم مع رمز الدولة"),
        ("٠٧٨٢٤٤٤", "رقم بالعربية"),
        ("123", "رقم قصير"),
        ("123456789012345", "رقم طويل"),
    ]
    
    for phone, description in examples:
        phone_clean = phone.replace(' ', '').replace('-', '').replace('_', '').replace('+', '')
        
        # تحويل الأرقام العربية
        arabic_to_english = {
            '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
        }
        for arabic, english in arabic_to_english.items():
            phone_clean = phone_clean.replace(arabic, english)
        
        print(f"📱 {description}:")
        print(f"   الأصلي: '{phone}'")
        print(f"   المنظف: '{phone_clean}'")
        print(f"   صحيح: {'✅' if phone_clean.isdigit() else '❌'}")
        print()

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار قبول أرقام التليفون المختلفة")
    print("=" * 60)
    print()
    
    # اختبار التحقق من أرقام التليفون
    test_phone_number_validation()
    
    # اختبار أمثلة عملية
    test_phone_number_examples()
    
    print("✅ تم الانتهاء من جميع الاختبارات")
    print("\n📋 ملخص التحديثات:")
    print("   • إزالة الحد الأدنى لطول الرقم (10 أرقام)")
    print("   • قبول أي رقم تليفون عادي")
    print("   • تنظيف الرقم من المسافات والشرطات")
    print("   • تحويل الأرقام العربية إلى إنجليزية")
    print("   • رسائل خطأ أكثر وضوحاً")

if __name__ == "__main__":
    main()
