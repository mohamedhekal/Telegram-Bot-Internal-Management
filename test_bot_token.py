#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار توكن البوت والاتصال
"""

import asyncio
import aiohttp
import config
from telegram import Bot
from telegram.error import InvalidToken, TimedOut, NetworkError

async def test_bot_connection():
    """اختبار اتصال البوت"""
    print("🔍 اختبار توكن البوت...")
    
    try:
        # إنشاء جلسة HTTP مع إعدادات SSL محسنة
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # اختبار API تيليجرام
            url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/getMe"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        bot_info = data['result']
                        print(f"✅ البوت متصل بنجاح!")
                        print(f"🤖 اسم البوت: {bot_info['first_name']}")
                        print(f"👤 معرف البوت: @{bot_info['username']}")
                        print(f"🆔 معرف البوت: {bot_info['id']}")
                        return True
                    else:
                        print(f"❌ خطأ في استجابة API: {data}")
                        return False
                else:
                    print(f"❌ خطأ في الاتصال: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False

async def test_telegram_api():
    """اختبار الاتصال بـ API تيليجرام"""
    print("\n🌐 اختبار الاتصال بـ API تيليجرام...")
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            url = "https://api.telegram.org"
            async with session.get(url) as response:
                if response.status == 200:
                    print("✅ الاتصال بـ API تيليجرام يعمل")
                    return True
                else:
                    print(f"❌ مشكلة في الاتصال: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    print("🚀 بدء اختبار البوت...\n")
    
    # اختبار الاتصال بـ API تيليجرام
    api_ok = await test_telegram_api()
    
    if api_ok:
        # اختبار توكن البوت
        bot_ok = await test_bot_connection()
        
        if bot_ok:
            print("\n🎉 جميع الاختبارات نجحت!")
            print("✅ البوت جاهز للتشغيل")
            print("🚀 يمكنك الآن تشغيل البوت باستخدام: python3 start_bot.py")
        else:
            print("\n❌ مشكلة في توكن البوت")
            print("💡 يرجى التحقق من:")
            print("   1. صحة التوكن في ملف config.py")
            print("   2. أن البوت لم يتم حذفه")
            print("   3. أن البوت مفعل")
    else:
        print("\n❌ مشكلة في الاتصال بـ API تيليجرام")
        print("💡 الحلول المقترحة:")
        print("   1. تحقق من اتصال الإنترنت")
        print("   2. جرب استخدام VPN")
        print("   3. تحقق من إعدادات الشبكة")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الاختبار")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}") 