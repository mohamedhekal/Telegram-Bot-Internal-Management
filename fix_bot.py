#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إصلاح البوت وحل مشاكل التعارض
"""

import requests
import time
import config
import os

def kill_existing_processes():
    """إيقاف جميع عمليات البوت الجارية"""
    print("🛑 إيقاف جميع عمليات البوت...")
    
    try:
        # إيقاف عمليات Python التي تحتوي على bot
        os.system("pkill -f 'python.*bot'")
        os.system("pkill -f 'python3.*bot'")
        time.sleep(2)
        print("✅ تم إيقاف العمليات الجارية")
        return True
    except Exception as e:
        print(f"⚠️ خطأ في إيقاف العمليات: {e}")
        return False

def reset_bot_webhook():
    """إعادة تعيين webhook البوت"""
    print("🔄 إعادة تعيين webhook البوت...")
    
    try:
        # حذف webhook
        webhook_url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/deleteWebhook"
        response = requests.post(webhook_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ تم حذف webhook بنجاح")
        else:
            print(f"⚠️ مشكلة في حذف webhook: {response.status_code}")
        
        # حذف التحديثات المعلقة
        updates_url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/getUpdates?offset=-1"
        response = requests.post(updates_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ تم حذف التحديثات المعلقة")
        else:
            print(f"⚠️ مشكلة في حذف التحديثات: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إعادة تعيين webhook: {e}")
        return False

def test_bot_connection():
    """اختبار اتصال البوت"""
    print("🔍 اختبار اتصال البوت...")
    
    try:
        url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            bot_info = data['result']
            print(f"✅ البوت متصل بنجاح!")
            print(f"🤖 اسم البوت: {bot_info['first_name']}")
            print(f"👤 معرف البوت: @{bot_info['username']}")
            return True
        else:
            print(f"❌ خطأ في التوكن: {data.get('description', 'خطأ غير معروف')}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 أداة إصلاح البوت")
    print("=" * 50)
    
    # إيقاف العمليات الجارية
    kill_existing_processes()
    
    # اختبار اتصال البوت
    if not test_bot_connection():
        print("\n❌ مشكلة في التوكن")
        print("💡 يرجى تشغيل: python3 create_new_bot.py")
        return
    
    # إعادة تعيين webhook
    if reset_bot_webhook():
        print("\n✅ تم إصلاح البوت بنجاح!")
        print("🚀 يمكنك الآن تشغيل البوت:")
        print("   python3 start_bot.py")
    else:
        print("\n❌ فشل في إصلاح البوت")
        print("💡 يرجى المحاولة مرة أخرى")

if __name__ == "__main__":
    main() 