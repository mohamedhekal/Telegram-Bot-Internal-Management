#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إيقاف جميع عمليات البوت
"""

import os
import subprocess
import time

def stop_all_bot_processes():
    """إيقاف جميع عمليات البوت الجارية"""
    print("🛑 محاولة إيقاف جميع عمليات البوت...")
    
    try:
        # البحث عن عمليات Python التي تحتوي على bot_clean
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # تجاهل العنوان
            python_processes = []
            
            for line in lines:
                if line.strip():
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        pid = parts[1].strip('"')
                        python_processes.append(pid)
            
            if python_processes:
                print(f"📋 تم العثور على {len(python_processes)} عملية Python:")
                for pid in python_processes:
                    print(f"   - PID: {pid}")
                
                # محاولة إيقاف كل عملية
                stopped_count = 0
                for pid in python_processes:
                    try:
                        subprocess.run(['taskkill', '/F', '/PID', pid], 
                                     capture_output=True, check=True)
                        print(f"✅ تم إيقاف العملية {pid}")
                        stopped_count += 1
                    except subprocess.CalledProcessError:
                        print(f"❌ فشل في إيقاف العملية {pid} (قد تكون محمية)")
                
                print(f"\n📊 تم إيقاف {stopped_count} من {len(python_processes)} عملية")
            else:
                print("✅ لا توجد عمليات Python جارية")
        
        # انتظار قليل للتأكد من إيقاف العمليات
        print("⏳ انتظار 3 ثوان للتأكد من إيقاف العمليات...")
        time.sleep(3)
        
        # التحقق مرة أخرى
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            remaining = len([line for line in result.stdout.strip().split('\n')[1:] if line.strip()])
            if remaining == 0:
                print("✅ تم إيقاف جميع عمليات البوت بنجاح!")
                return True
            else:
                print(f"⚠️ لا تزال هناك {remaining} عملية Python جارية")
                return False
                
    except Exception as e:
        print(f"❌ خطأ في إيقاف العمليات: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("=" * 50)
    print("🛑 سكريبت إيقاف البوت")
    print("=" * 50)
    
    success = stop_all_bot_processes()
    
    if success:
        print("\n🎉 يمكنك الآن تشغيل البوت مرة أخرى بأمان!")
        print("💡 استخدم الأمر: python start_bot.py")
    else:
        print("\n⚠️ قد تحتاج لإعادة تشغيل الكمبيوتر لإيقاف جميع العمليات")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 