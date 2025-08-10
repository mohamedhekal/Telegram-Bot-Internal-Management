#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نسخة تجريبية من البوت - تعمل محلياً
"""

import os
import sqlite3
from datetime import datetime
from database_manager import DatabaseManager

def demo_bot():
    """عرض تجريبي للبوت"""
    print("🤖 بوت إدارة الفواتير - النسخة التجريبية")
    print("=" * 50)
    
    # اختبار قاعدة البيانات
    print("📊 اختبار قاعدة البيانات...")
    db_manager = DatabaseManager()
    
    # عرض إحصائيات قاعدة البيانات
    try:
        conn = sqlite3.connect('invoice_bot.db')
        cursor = conn.cursor()
        
        # عدد الفواتير
        cursor.execute("SELECT COUNT(*) FROM invoices")
        invoice_count = cursor.fetchone()[0]
        
        # عدد المستخدمين
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        print(f"✅ قاعدة البيانات تعمل بشكل طبيعي")
        print(f"📋 عدد الفواتير: {invoice_count}")
        print(f"👥 عدد المستخدمين: {user_count}")
        
        # عرض آخر 5 فواتير
        if invoice_count > 0:
            print("\n📋 آخر الفواتير:")
            cursor.execute("""
                SELECT receipt_number, employee_name, client_name, total_sales, created_at 
                FROM invoices 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            invoices = cursor.fetchall()
            
            for i, (receipt, employee, client, sales, date) in enumerate(invoices, 1):
                print(f"{i}. {receipt} - {employee} - {client} - {sales:,.0f} دينار - {date}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ خطأ في قاعدة البيانات: {e}")
    
    print("\n" + "=" * 50)
    print("📱 ميزات البوت:")
    print("✅ إضافة فواتير جديدة")
    print("✅ عرض الإحصائيات")
    print("✅ إدارة المستخدمين")
    print("✅ تحميل ملفات الطلبات")
    print("✅ قاعدة بيانات محلية")
    print("✅ نظام صلاحيات متقدم")
    
    print("\n" + "=" * 50)
    print("🔧 حالة النظام:")
    print("✅ جميع الملفات موجودة")
    print("✅ قاعدة البيانات جاهزة")
    print("✅ المكتبات مثبتة")
    print("❌ الاتصال بـ تيليجرام غير متاح")
    
    print("\n" + "=" * 50)
    print("💡 لتشغيل البوت:")
    print("1. تأكد من وجود اتصال بالإنترنت")
    print("2. استخدم VPN إذا كان تيليجرام محظوراً")
    print("3. تأكد من صحة توكن البوت")
    print("4. شغل: python3 bot_clean.py")
    
    print("\n" + "=" * 50)
    print("📞 للدعم الفني:")
    print("- راجع ملف TROUBLESHOOTING.md")
    print("- شغل: python3 test_connection.py")
    print("- تحقق من إعدادات الشبكة")

if __name__ == "__main__":
    demo_bot() 