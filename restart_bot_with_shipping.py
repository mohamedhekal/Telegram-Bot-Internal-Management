#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعادة تشغيل البوت مع ميزة اختيار فترة الشحن الجديدة
"""

import os
import sys
import subprocess
import time
import signal

def stop_existing_bot():
    """إيقاف البوت الموجود"""
    print("🛑 إيقاف البوت الموجود...")
    
    try:
        # البحث عن عمليات Python التي تشغل start_bot.py
result = subprocess.run(['pgrep', '-f', 'start_bot.py'], capture_output=True, text=True)
        
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"إيقاف العملية {pid}")
                    os.kill(int(pid), signal.SIGTERM)
                    time.sleep(1)
            
            print("✅ تم إيقاف جميع عمليات البوت")
        else:
            print("ℹ️ لا توجد عمليات بوت نشطة")
            
    except Exception as e:
        print(f"⚠️ خطأ في إيقاف البوت: {e}")

def start_bot():
    """تشغيل البوت"""
    print("🚀 تشغيل البوت مع الميزات الجديدة...")
    
    try:
        # تشغيل البوت في الخلفية
        process = subprocess.Popen([
            sys.executable, 'start_bot.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ البوت يعمل الآن (PID: {process.pid})")
        print("📱 يمكنك الآن استخدام ميزة اختيار فترة الشحن!")
        
        return process
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
        return None

def test_shipping_feature():
    """اختبار ميزة الشحن"""
    print("\n🧪 اختبار ميزة الشحن الجديدة:")
    print("=" * 40)
    
    try:
        from database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        
        # اختبار إحصائيات التصدير
        export_stats = db_manager.get_export_stats()
        if export_stats:
            print(f"✅ إحصائيات التصدير: {export_stats['total_invoices']} طلب")
            print(f"✅ الطلبات المصدرة: {export_stats['exported_invoices']}")
            print(f"✅ الطلبات الجديدة: {export_stats['new_invoices']}")
        else:
            print("❌ فشل في الحصول على إحصائيات التصدير")
        
        # اختبار الحصول على الطلبات
        df = db_manager.get_all_invoices_for_shipping(7, "period")
        if df is not None:
            print(f"✅ الطلبات للآخر أسبوع: {len(df)} طلب")
        else:
            print("❌ فشل في الحصول على الطلبات")
            
    except Exception as e:
        print(f"❌ خطأ في اختبار الميزة: {e}")

def show_instructions():
    """عرض التعليمات"""
    print("\n📋 تعليمات استخدام ميزة الشحن الجديدة:")
    print("=" * 50)
    print("1. افتح البوت في تيليجرام")
    print("2. اختر '📋 تحميل ملف طلبات التوصيل'")
    print("3. ستظهر قائمة باختيارات الفترة:")
    print("   • 📋 الكل")
    print("   • ⏰ آخر 24 ساعة")
    print("   • 📅 آخر يومين")
    print("   • 📆 آخر أسبوع")
    print("   • 📊 آخر شهر")
    print("   • 📈 آخر 3 شهور")
    print("   • 🆕 الجديد فقط")
    print("4. اختر الفترة المطلوبة")
    print("5. انتظر إنشاء الملف")
    print("6. استلم الملف مع تفاصيل عدد الطلبات")

if __name__ == "__main__":
    print("🔄 إعادة تشغيل البوت مع ميزة اختيار فترة الشحن...")
    print("=" * 60)
    
    # اختبار الميزة أولاً
    test_shipping_feature()
    
    # إيقاف البوت الموجود
    stop_existing_bot()
    
    # انتظار قليلاً
    print("⏳ انتظار 3 ثوانٍ...")
    time.sleep(3)
    
    # تشغيل البوت الجديد
    bot_process = start_bot()
    
    if bot_process:
        # عرض التعليمات
        show_instructions()
        
        print("\n🎉 البوت جاهز للاستخدام!")
        print("💡 إذا واجهت أي مشاكل، جرب إعادة تشغيل البوت مرة أخرى")
    else:
        print("\n❌ فشل في تشغيل البوت")
        print("💡 تحقق من الأخطاء وحاول مرة أخرى")
