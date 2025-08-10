#!/usr/bin/env python3
"""
عرض ميزات إدارة المرتجعات المضافة حديثاً
"""

from database_manager import DatabaseManager
from datetime import datetime, timedelta
import pandas as pd

def demo_returns_features():
    print("🔄 عرض ميزات إدارة المرتجعات المضافة حديثاً")
    print("=" * 50)
    
    db_manager = DatabaseManager()
    
    # 1. عرض جدول المرتجعات
    print("\n1️⃣ جدول المرتجعات:")
    print("-" * 30)
    
    # إنشاء بعض البيانات التجريبية للمراجعة
    try:
        # البحث عن فاتورة موجودة
        invoices_df = db_manager.get_all_invoices_for_shipping(days=30)
        if not invoices_df.empty:
            sample_invoice = invoices_df.iloc[0]
            receipt_number = sample_invoice['receipt_number']  # رقم الإيصال
            employee_name = sample_invoice['employee_name']   # اسم الموظف
            
            print(f"📋 فاتورة تجريبية: {receipt_number} - {employee_name}")
            
            # إضافة مرتجع تجريبي
            return_data = {
                'invoice_id': sample_invoice['id'],
                'receipt_number': receipt_number,
                'employee_name': employee_name,
                'return_type': 'partial',
                'returned_quantity': 2,
                'returned_amount': 50.0,
                'remaining_amount': sample_invoice['total_sales'] - 50.0,
                'return_reason': 'تجربة ميزة المرتجعات',
                'processed_by': 'admin'
            }
            
            db_manager.add_return(return_data)
            print("✅ تم إضافة مرتجع تجريبي")
            
        else:
            print("❌ لا توجد فواتير في قاعدة البيانات")
            return
            
    except Exception as e:
        print(f"❌ خطأ في إنشاء البيانات التجريبية: {e}")
        return
    
    # 2. عرض المرتجعات للموظف
    print("\n2️⃣ المرتجعات للموظف:")
    print("-" * 30)
    
    returns = db_manager.get_returns_by_employee(employee_name)
    if returns:
        for ret in returns:
            print(f"🔄 مرتجع: {ret['receipt_number']} - نوع: {ret['return_type']} - كمية: {ret['returned_quantity']} - مبلغ: {ret['returned_amount']}")
    else:
        print("❌ لا توجد مرتجعات")
    
    # 3. عرض إحصائيات الموظف مع المرتجعات
    print("\n3️⃣ إحصائيات الموظف مع المرتجعات:")
    print("-" * 30)
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    stats = db_manager.get_employee_stats_with_returns(employee_name, current_month, current_year)
    if stats:
        print(f"👤 الموظف: {employee_name}")
        print(f"📊 عدد الفواتير: {stats['total_invoices']}")
        print(f"📦 الكمية المباعة: {stats['total_quantity']}")
        print(f"💰 إجمالي المبيعات: {stats['total_sales']:.2f}")
        print(f"🔄 الكمية المرتجعة: {stats['returned_quantity']}")
        print(f"💸 المبلغ المرتجع: {stats['returned_amount']:.2f}")
        print(f"📈 الكمية النهائية: {stats['final_quantity']}")
        print(f"💵 المبيعات النهائية: {stats['final_sales']:.2f}")
    
    # 4. عرض إحصائيات جميع الموظفين مع المرتجعات
    print("\n4️⃣ إحصائيات جميع الموظفين مع المرتجعات:")
    print("-" * 30)
    
    all_stats = db_manager.get_all_employees_stats_with_returns(current_month, current_year)
    if all_stats:
        print("📊 جدول إحصائيات الموظفين:")
        print(f"{'الموظف':<15} {'الفواتير':<8} {'الكمية':<8} {'المبيعات':<10} {'المرتجعات':<10} {'النهائي':<10}")
        print("-" * 70)
        
        for stat in all_stats:
            print(f"{stat['employee_name']:<15} {stat['total_invoices']:<8} {stat['total_quantity']:<8} "
                  f"{stat['total_sales']:<10.2f} {stat['returned_quantity']:<10} {stat['final_quantity']:<10}")
    
    # 5. عرض ميزات إدارة كلمات المرور
    print("\n5️⃣ ميزات إدارة كلمات المرور:")
    print("-" * 30)
    
    # إضافة كلمة مرور تجريبية
    try:
        db_manager.set_employee_password(employee_name, "123456")
        print(f"✅ تم إضافة كلمة مرور للموظف: {employee_name}")
        
        # التحقق من كلمة المرور
        is_valid = db_manager.verify_employee_password(employee_name, "123456")
        print(f"🔐 التحقق من كلمة المرور: {'✅ صحيح' if is_valid else '❌ خطأ'}")
        
        # عرض جميع كلمات المرور
        passwords = db_manager.get_all_passwords()
        if passwords:
            print("📋 كلمات المرور المخزنة:")
            for pwd in passwords:
                print(f"   👤 {pwd[0]}: {'*' * len(pwd[1])}")
        
    except Exception as e:
        print(f"❌ خطأ في إدارة كلمات المرور: {e}")
    
    print("\n" + "=" * 50)
    print("✅ تم عرض جميع الميزات المضافة حديثاً")
    print("💡 هذه الميزات متاحة الآن في البوت:")
    print("   - إدارة المرتجعات (كاملة وجزئية)")
    print("   - حساب الإحصائيات النهائية بعد المرتجعات")
    print("   - حماية الإحصائيات بكلمات مرور")
    print("   - إدارة كلمات المرور للموظفين")

if __name__ == "__main__":
    demo_returns_features() 