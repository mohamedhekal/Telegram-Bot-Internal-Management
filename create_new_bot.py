#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إنشاء بوت جديد والحصول على توكن صالح
"""

import requests
import json
import time

def create_new_bot():
    """إنشاء بوت جديد"""
    print("🤖 إنشاء بوت جديد...")
    print("=" * 50)
    
    print("📝 خطوات إنشاء البوت:")
    print("1. اذهب إلى @BotFather في تيليجرام")
    print("2. أرسل /newbot")
    print("3. أدخل اسم البوت (مثال: RKS Order Bot)")
    print("4. أدخل معرف البوت (مثال: rks_order_bot)")
    print("5. انسخ التوكن الذي ستحصل عليه")
    print()
    
    # طلب التوكن من المستخدم
    token = input("🔑 أدخل التوكن الجديد هنا: ").strip()
    
    if not token:
        print("❌ لم يتم إدخال التوكن")
        return False
    
    # اختبار التوكن
    print("🔍 اختبار التوكن...")
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            bot_info = data['result']
            print(f"✅ البوت صالح!")
            print(f"🤖 اسم البوت: {bot_info['first_name']}")
            print(f"👤 معرف البوت: @{bot_info['username']}")
            print(f"🆔 معرف البوت: {bot_info['id']}")
            
            # تحديث ملف config.py
            update_config_token(token)
            return True
        else:
            print(f"❌ خطأ في التوكن: {data.get('description', 'خطأ غير معروف')}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False

def update_config_token(token):
    """تحديث التوكن في ملف config.py"""
    try:
        # قراءة الملف الحالي
        with open('config.py', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # تحديث التوكن
        import re
        pattern = r'TELEGRAM_TOKEN = "[^"]*"'
        new_content = re.sub(pattern, f'TELEGRAM_TOKEN = "{token}"', content)
        
        # كتابة الملف المحدث
        with open('config.py', 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("✅ تم تحديث التوكن في config.py")
        
    except Exception as e:
        print(f"❌ خطأ في تحديث الملف: {e}")

def reset_bot_state(token):
    """إعادة تعيين حالة البوت"""
    print("🔄 إعادة تعيين حالة البوت...")
    
    try:
        # حذف webhook
        webhook_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
        response = requests.post(webhook_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ تم حذف webhook")
        else:
            print(f"⚠️ مشكلة في حذف webhook: {response.status_code}")
        
        # حذف التحديثات المعلقة
        updates_url = f"https://api.telegram.org/bot{token}/getUpdates?offset=-1"
        response = requests.post(updates_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ تم حذف التحديثات المعلقة")
        else:
            print(f"⚠️ مشكلة في حذف التحديثات: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إعادة تعيين البوت: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🚀 أداة إنشاء بوت جديد")
    print("=" * 50)
    
    # إنشاء بوت جديد
    if create_new_bot():
        print("\n" + "=" * 50)
        print("🎉 تم إنشاء البوت بنجاح!")
        print("✅ يمكنك الآن تشغيل البوت باستخدام:")
        print("   python3 start_bot.py")
        print("\n" + "=" * 50)
    else:
        print("\n❌ فشل في إنشاء البوت")
        print("💡 يرجى المحاولة مرة أخرى")

if __name__ == "__main__":
    main() 