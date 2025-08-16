#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف اختبار الاتصال بخوادم تيليجرام
"""

import asyncio
import aiohttp
import config
from telegram import Bot
from telegram.error import TimedOut, NetworkError, InvalidToken

async def test_internet_connection():
    """اختبار الاتصال بالإنترنت"""
    print("🌐 اختبار الاتصال بالإنترنت...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.google.com', timeout=10) as response:
                if response.status == 200:
                    print("✅ الاتصال بالإنترنت يعمل بشكل طبيعي")
                    return True
                else:
                    print(f"⚠️ الاتصال بالإنترنت غير مستقر (الحالة: {response.status})")
                    return False
    except Exception as e:
        print(f"❌ فشل في الاتصال بالإنترنت: {e}")
        return False

async def test_telegram_api():
    """اختبار الاتصال بخوادم تيليجرام"""
    print("📱 اختبار الاتصال بخوادم تيليجرام...")
    
    try:
        # اختبار الاتصال بـ API تيليجرام
        async with aiohttp.ClientSession() as session:
            url = "https://api.telegram.org"
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    print("✅ الاتصال بخوادم تيليجرام يعمل")
                    return True
                else:
                    print(f"⚠️ مشكلة في الاتصال بخوادم تيليجرام (الحالة: {response.status})")
                    return False
    except Exception as e:
        print(f"❌ فشل في الاتصال بخوادم تيليجرام: {e}")
        return False

async def test_bot_token():
    """اختبار صحة توكن البوت"""
    print("🔑 اختبار صحة توكن البوت...")
    
    try:
        bot = Bot(token=config.TELEGRAM_TOKEN)
        me = await bot.get_me()
        print(f"✅ توكن البوت صحيح")
        print(f"🤖 اسم البوت: {me.first_name}")
        print(f"👤 معرف البوت: @{me.username}")
        return True
    except InvalidToken:
        print("❌ توكن البوت غير صحيح")
        return False
    except TimedOut:
        print("❌ انتهت مهلة الاتصال - تحقق من الإنترنت")
        return False
    except NetworkError as e:
        print(f"❌ خطأ في الشبكة: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return False

async def main():
    """الدالة الرئيسية لاختبار الاتصال"""
    print("🔍 بدء اختبار الاتصال...\n")
    
    # اختبار الاتصال بالإنترنت
    internet_ok = await test_internet_connection()
    print()
    
    if not internet_ok:
        print("❌ لا يمكن الاتصال بالإنترنت")
        print("💡 الحلول:")
        print("   1. تحقق من اتصال الإنترنت")
        print("   2. تحقق من إعدادات الشبكة")
        print("   3. جرب إعادة تشغيل الراوتر")
        return False
    
    # اختبار الاتصال بخوادم تيليجرام
    telegram_ok = await test_telegram_api()
    print()
    
    if not telegram_ok:
        print("❌ لا يمكن الاتصال بخوادم تيليجرام")
        print("💡 الحلول:")
        print("   1. تحقق من حظر تيليجرام في بلدك")
        print("   2. جرب استخدام VPN")
        print("   3. انتظر قليلاً وحاول مرة أخرى")
        return False
    
    # اختبار توكن البوت
    token_ok = await test_bot_token()
    print()
    
    if not token_ok:
        print("❌ مشكلة في توكن البوت")
        print("💡 الحلول:")
        print("   1. تحقق من صحة التوكن في ملف config.py")
        print("   2. تأكد من أن البوت لم يتم حذفه")
        print("   3. أنشئ بوت جديد واحصل على توكن جديد")
        return False
    
    print("🎉 جميع الاختبارات نجحت!")
    print("✅ البوت جاهز للتشغيل")
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result:
            print("\n🚀 يمكنك الآن تشغيل البوت باستخدام: python start_bot.py")
        else:
            print("\n❌ يرجى حل المشاكل قبل تشغيل البوت")
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الاختبار")
    except Exception as e:
        print(f"\n❌ خطأ في الاختبار: {e}") 