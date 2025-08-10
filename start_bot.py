#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت تشغيل البوت المحسن
"""

import subprocess
import time
import sys
import os

def check_dependencies():
    """التحقق من المكتبات المطلوبة"""
    print("🔍 التحقق من المكتبات...")
    
    try:
        import telegram
        import pandas
        import openpyxl
        import requests
        print("✅ جميع المكتبات متوفرة")
        return True
    except ImportError as e:
        print(f"❌ مكتبة مفقودة: {e}")
        print("💡 شغل: pip3 install -r requirements.txt")
        return False

def check_config():
    """التحقق من ملف الإعدادات"""
    print("🔍 التحقق من ملف الإعدادات...")
    
    try:
        import config
        if hasattr(config, 'TELEGRAM_TOKEN') and config.TELEGRAM_TOKEN:
            print("✅ ملف الإعدادات صحيح")
            return True
        else:
            print("❌ التوكن غير موجود")
            return False
    except Exception as e:
        print(f"❌ خطأ في ملف الإعدادات: {e}")
        return False

def test_bot_connection():
    """اختبار اتصال البوت"""
    print("🔍 اختبار اتصال البوت...")
    
    try:
        import config
        import requests
        
        url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            bot_info = data['result']
            print(f"✅ البوت متصل: {bot_info['first_name']} (@{bot_info['username']})")
            return True
        else:
            print(f"❌ خطأ في التوكن: {data.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False

def kill_existing_bots():
    """إيقاف البوتات الجارية"""
    print("🛑 إيقاف البوتات الجارية...")
    
    try:
        os.system("pkill -f 'python.*bot_clean'")
        time.sleep(2)
        print("✅ تم إيقاف البوتات الجارية")
        return True
    except Exception as e:
        print(f"⚠️ خطأ في إيقاف البوتات: {e}")
        return False

def start_bot():
    """تشغيل البوت"""
    print("🚀 تشغيل البوت...")
    
    try:
        # تشغيل البوت في الخلفية
        process = subprocess.Popen([
            sys.executable, 'bot_clean.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # انتظار قليل للتأكد من التشغيل
        time.sleep(3)
        
        # التحقق من أن العملية تعمل
        if process.poll() is None:
            print("✅ البوت يعمل بنجاح!")
            print(f"🆔 معرف العملية: {process.pid}")
            print("📱 يمكنك الآن استخدام البوت في تيليجرام")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ فشل في تشغيل البوت")
            print(f"الخطأ: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
        return None

def main():
    """الدالة الرئيسية"""
    print("🤖 تشغيل بوت إدارة الفواتير")
    print("=" * 50)
    
    # التحقق من المكتبات
    if not check_dependencies():
        return
    
    # التحقق من الإعدادات
    if not check_config():
        print("💡 شغل: python3 create_new_bot.py")
        return
    
    # اختبار الاتصال
    if not test_bot_connection():
        print("💡 شغل: python3 fix_bot.py")
        return
    
    # إيقاف البوتات الجارية
    kill_existing_bots()
    
    # تشغيل البوت
    process = start_bot()
    
    if process:
        print("\n" + "=" * 50)
        print("🎉 البوت جاهز للاستخدام!")
        print("📱 اذهب إلى تيليجرام وابحث عن البوت")
        print("🔗 أو استخدم الرابط المباشر")
        print("=" * 50)
        
        try:
            # انتظار حتى يتم إيقاف البوت
            process.wait()
        except KeyboardInterrupt:
            print("\n⏹️ إيقاف البوت...")
            process.terminate()
            process.wait()
            print("✅ تم إيقاف البوت")
    else:
        print("\n❌ فشل في تشغيل البوت")
        print("💡 راجع الأخطاء أعلاه")

if __name__ == "__main__":
    main() 