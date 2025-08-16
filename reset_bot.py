#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إعادة تعيين حالة البوت
"""

import asyncio
import aiohttp
import config
from telegram import Bot
from telegram.error import Conflict, TimedOut, NetworkError

async def reset_bot_state():
    """إعادة تعيين حالة البوت"""
    print("🔄 إعادة تعيين حالة البوت...")
    
    try:
        # إنشاء جلسة HTTP
        async with aiohttp.ClientSession() as session:
            # حذف webhook
            webhook_url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/deleteWebhook"
            async with session.post(webhook_url) as response:
                if response.status == 200:
                    print("✅ تم حذف webhook بنجاح")
                else:
                    print(f"⚠️ مشكلة في حذف webhook: {response.status}")
            
            # حذف جميع التحديثات المعلقة
            updates_url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/getUpdates?offset=-1"
            async with session.post(updates_url) as response:
                if response.status == 200:
                    print("✅ تم حذف التحديثات المعلقة")
                else:
                    print(f"⚠️ مشكلة في حذف التحديثات: {response.status}")
            
            # اختبار الاتصال بالبوت
            bot = Bot(token=config.TELEGRAM_TOKEN)
            me = await bot.get_me()
            print(f"✅ البوت متصل بنجاح: {me.first_name} (@{me.username})")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في إعادة تعيين البوت: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    print("🔄 بدء عملية إعادة تعيين البوت...\n")
    
    success = await reset_bot_state()
    
    if success:
        print("\n✅ تم إعادة تعيين البوت بنجاح!")
        print("🚀 يمكنك الآن تشغيل البوت باستخدام: python3 start_bot.py")
    else:
        print("\n❌ فشلت عملية إعادة التعيين")
        print("💡 يرجى التحقق من:")
        print("   1. صحة توكن البوت")
        print("   2. اتصال الإنترنت")
        print("   3. عدم وجود نسخ أخرى من البوت تعمل")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف العملية")
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}") 