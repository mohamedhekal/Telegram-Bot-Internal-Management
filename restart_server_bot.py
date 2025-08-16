#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إعادة تشغيل البوت على الخادم
"""

import os
import subprocess
import time

def restart_pm2_bot():
    """إعادة تشغيل البوت عبر PM2"""
    print("🔄 إعادة تشغيل البوت على الخادم...")
    
    try:
        # إيقاف البوت
        print("⏹️ إيقاف البوت...")
        os.system("pm2 stop rks-order-bot")
        time.sleep(3)
        
        # حذف البوت من PM2
        print("🗑️ حذف البوت من PM2...")
        os.system("pm2 delete rks-order-bot")
        time.sleep(2)
        
        # إعادة تشغيل البوت
        print("🚀 تشغيل البوت...")
        os.system("pm2 start start_bot.py --name rks-order-bot")
        time.sleep(3)
        
        # التحقق من حالة البوت
        print("🔍 التحقق من حالة البوت...")
        result = subprocess.run(["pm2", "status"], capture_output=True, text=True)
        print(result.stdout)
        
        print("✅ تم إعادة تشغيل البوت بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إعادة تشغيل البوت: {e}")
        return False

def check_bot_logs():
    """عرض سجلات البوت"""
    print("📋 سجلات البوت:")
    print("=" * 50)
    
    try:
        # عرض السجلات الأخيرة
        result = subprocess.run(["pm2", "logs", "rks-order-bot", "--lines", "20"], 
                              capture_output=True, text=True, timeout=10)
        print(result.stdout)
        
    except Exception as e:
        print(f"❌ خطأ في عرض السجلات: {e}")

def fix_database():
    """إصلاح مشاكل قاعدة البيانات"""
    print("🔧 إصلاح قاعدة البيانات...")
    
    try:
        # إيقاف البوت مؤقتاً
        os.system("pm2 stop rks-order-bot")
        time.sleep(2)
        
        # حذف ملفات WAL إذا وجدت
        if os.path.exists("invoice_bot.db-wal"):
            os.remove("invoice_bot.db-wal")
            print("✅ تم حذف ملف WAL")
        
        if os.path.exists("invoice_bot.db-shm"):
            os.remove("invoice_bot.db-shm")
            print("✅ تم حذف ملف SHM")
        
        # إعادة تشغيل البوت
        os.system("pm2 start rks-order-bot")
        print("✅ تم إعادة تشغيل البوت")
        
    except Exception as e:
        print(f"❌ خطأ في إصلاح قاعدة البيانات: {e}")

def main():
    """الدالة الرئيسية"""
    print("🖥️ إدارة البوت على الخادم")
    print("=" * 50)
    
    while True:
        print("\nاختر الإجراء:")
        print("1. إعادة تشغيل البوت")
        print("2. عرض سجلات البوت")
        print("3. إصلاح قاعدة البيانات")
        print("4. عرض حالة البوت")
        print("5. خروج")
        
        choice = input("\nأدخل رقم الإجراء: ").strip()
        
        if choice == "1":
            restart_pm2_bot()
        elif choice == "2":
            check_bot_logs()
        elif choice == "3":
            fix_database()
        elif choice == "4":
            os.system("pm2 status")
        elif choice == "5":
            print("👋 وداعاً!")
            break
        else:
            print("❌ اختيار غير صحيح")

if __name__ == "__main__":
    main() 