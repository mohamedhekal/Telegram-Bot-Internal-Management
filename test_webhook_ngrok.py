#!/usr/bin/env python3
"""
اختبار سريع لـ Webhook مع Ngrok
"""

import asyncio
import subprocess
import time
import requests
from telegram import Bot
from config import TELEGRAM_TOKEN

async def test_webhook():
    print("🧪 اختبار Webhook مع Ngrok...")
    
    # 1. تشغيل Ngrok
    print("1️⃣ تشغيل Ngrok...")
    try:
        # تشغيل ngrok في الخلفية
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", "8443"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # انتظار قليلاً لبدء Ngrok
        time.sleep(3)
        
        # الحصول على معلومات Ngrok
        ngrok_info = requests.get("http://localhost:4040/api/tunnels").json()
        
        if ngrok_info['tunnels']:
            webhook_url = ngrok_info['tunnels'][0]['public_url'] + "/webhook"
            print(f"✅ Ngrok يعمل!")
            print(f"🔗 الرابط: {webhook_url}")
        else:
            print("❌ فشل في الحصول على رابط Ngrok")
            return
            
    except Exception as e:
        print(f"❌ خطأ في تشغيل Ngrok: {e}")
        return
    
    # 2. اختبار البوت
    print("\n2️⃣ اختبار البوت...")
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        me = await bot.get_me()
        print(f"✅ البوت متصل: {me.first_name}")
        
        # 3. إعداد Webhook
        print("\n3️⃣ إعداد Webhook...")
        success = await bot.set_webhook(url=webhook_url)
        if success:
            print(f"✅ تم إعداد Webhook بنجاح!")
            
            # 4. عرض معلومات Webhook
            print("\n4️⃣ معلومات Webhook:")
            webhook_info = await bot.get_webhook_info()
            print(f"🔗 الرابط: {webhook_info.url}")
            print(f"📊 التحديثات المعلقة: {webhook_info.pending_update_count}")
            
            print("\n🎉 البوت جاهز للاختبار!")
            print(f"📱 جرب إرسال /start في تيليجرام")
            print(f"🔗 رابط Webhook: {webhook_url}")
            
            # انتظار المستخدم
            input("\n⏸️ اضغط Enter لإيقاف الاختبار...")
            
            # 5. حذف Webhook
            print("\n5️⃣ حذف Webhook...")
            await bot.delete_webhook()
            print("✅ تم حذف Webhook")
            
        else:
            print("❌ فشل في إعداد Webhook")
            
    except Exception as e:
        print(f"❌ خطأ في اختبار البوت: {e}")
    
    # إيقاف Ngrok
    print("\n🛑 إيقاف Ngrok...")
    ngrok_process.terminate()
    print("✅ تم إيقاف Ngrok")

if __name__ == "__main__":
    asyncio.run(test_webhook()) 