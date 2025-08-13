#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار أزرار الشحن
"""

import re

def test_button_patterns():
    """اختبار أنماط الأزرار"""
    
    print("🧪 اختبار أنماط أزرار الشحن")
    print("=" * 40)
    
    # الأنماط المطلوبة
    required_patterns = [
        "shipping_all",
        "shipping_1", 
        "shipping_2",
        "shipping_7",
        "shipping_30",
        "shipping_90",
        "shipping_new",
        "back_to_main_menu"
    ]
    
    # النمط المستخدم في الكود
    pattern = "^(shipping_all|shipping_1|shipping_2|shipping_7|shipping_30|shipping_90|shipping_new|back_to_main_menu)$"
    
    print(f"النمط المستخدم: {pattern}")
    print()
    
    # اختبار كل نمط
    for test_pattern in required_patterns:
        match = re.match(pattern, test_pattern)
        if match:
            print(f"✅ {test_pattern} - متطابق")
        else:
            print(f"❌ {test_pattern} - غير متطابق")
    
    print()
    
    # اختبار أنماط غير صحيحة
    invalid_patterns = [
        "shipping_",
        "shipping_abc",
        "shipping_123",
        "other_button"
    ]
    
    print("اختبار الأنماط غير الصحيحة:")
    for test_pattern in invalid_patterns:
        match = re.match(pattern, test_pattern)
        if match:
            print(f"❌ {test_pattern} - متطابق (غير متوقع)")
        else:
            print(f"✅ {test_pattern} - غير متطابق (متوقع)")

def test_callback_data():
    """اختبار بيانات الأزرار"""
    
    print("\n🔍 اختبار بيانات الأزرار")
    print("=" * 30)
    
    # بيانات الأزرار المتوقعة
    button_data = {
        "📋 الكل": "shipping_all",
        "⏰ آخر 24 ساعة": "shipping_1",
        "📅 آخر يومين": "shipping_2", 
        "📆 آخر أسبوع": "shipping_7",
        "📊 آخر شهر": "shipping_30",
        "📈 آخر 3 شهور": "shipping_90",
        "🆕 الجديد فقط": "shipping_new",
        "🔙 رجوع": "back_to_main_menu"
    }
    
    for button_text, callback_data in button_data.items():
        print(f"✅ {button_text} -> {callback_data}")

if __name__ == "__main__":
    test_button_patterns()
    test_callback_data()
    
    print("\n🎯 اختبار الأنماط مكتمل!")
