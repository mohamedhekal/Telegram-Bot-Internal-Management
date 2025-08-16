#!/bin/bash

# سكريبت إدارة البوت على السيرفر
# Server: 31.97.233.18
# Path: /var/www/leads_rockli_usr/data/www/leads.rocklis.com

SERVER_PATH="/var/www/leads_rockli_usr/data/www/leads.rocklis.com"
BOT_LOG="bot.log"
PID_FILE="bot.pid"

# الألوان للعرض
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# دالة عرض المساعدة
show_help() {
    echo -e "${BLUE}🤖 مدير البوت على السيرفر${NC}"
    echo "=================================="
    echo -e "${GREEN}الاستخدام:${NC}"
    echo "  $0 [أمر]"
    echo ""
    echo -e "${YELLOW}الأوامر المتاحة:${NC}"
    echo "  start     - تشغيل البوت"
    echo "  stop      - إيقاف البوت"
    echo "  restart   - إعادة تشغيل البوت"
    echo "  status    - حالة البوت"
    echo "  logs      - عرض السجلات"
    echo "  monitor   - مراقبة السجلات مباشرة"
    echo "  install   - تثبيت المكتبات"
    echo "  test      - اختبار الاتصال"
    echo "  help      - عرض هذه المساعدة"
    echo ""
    echo -e "${BLUE}أمثلة:${NC}"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 logs"
}

# دالة الانتقال إلى مجلد المشروع
cd_to_project() {
    cd "$SERVER_PATH" || {
        echo -e "${RED}❌ فشل في الانتقال إلى $SERVER_PATH${NC}"
        exit 1
    }
}

# دالة تشغيل البوت
start_bot() {
    echo -e "${BLUE}🚀 تشغيل البوت...${NC}"
    cd_to_project
    
    # تفعيل البيئة الافتراضية إذا وجدت
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # إيقاف البوتات الجارية
    stop_bot_quiet
    
    # تشغيل البوت
    nohup python3 start_bot.py > "$BOT_LOG" 2>&1 &
    BOT_PID=$!
    echo $BOT_PID > "$PID_FILE"
    
    sleep 3
    
    if ps -p $BOT_PID > /dev/null; then
        echo -e "${GREEN}✅ البوت يعمل بنجاح! (PID: $BOT_PID)${NC}"
    else
        echo -e "${RED}❌ فشل في تشغيل البوت${NC}"
        echo "راجع السجلات: cat $BOT_LOG"
        exit 1
    fi
}

# دالة إيقاف البوت (هادئة)
stop_bot_quiet() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID 2>/dev/null
            sleep 2
        fi
    fi
    pkill -f "python.*bot_clean" 2>/dev/null || true
}

# دالة إيقاف البوت
stop_bot() {
    echo -e "${YELLOW}🛑 إيقاف البوت...${NC}"
    cd_to_project
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            echo -e "${GREEN}✅ تم إيقاف البوت (PID: $PID)${NC}"
        else
            echo -e "${YELLOW}⚠️ البوت غير متوقف بالفعل${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ ملف PID غير موجود${NC}"
    fi
    
    # إيقاف أي عمليات أخرى
    pkill -f "python.*bot_clean" 2>/dev/null || true
    echo -e "${GREEN}✅ تم إيقاف جميع عمليات البوت${NC}"
}

# دالة حالة البوت
status_bot() {
    echo -e "${BLUE}📊 حالة البوت:${NC}"
    cd_to_project
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${GREEN}✅ البوت يعمل (PID: $PID)${NC}"
            
            # معلومات إضافية
            UPTIME=$(ps -o etime= -p $PID 2>/dev/null || echo "غير متوفر")
            MEMORY=$(ps -o rss= -p $PID 2>/dev/null || echo "غير متوفر")
            echo "⏱️ وقت التشغيل: $UPTIME"
            echo "💾 استخدام الذاكرة: $MEMORY KB"
        else
            echo -e "${RED}❌ البوت متوقف${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ ملف PID غير موجود${NC}"
    fi
    
    # التحقق من العمليات الجارية
    RUNNING_PROCESSES=$(pgrep -f "python.*bot_clean" | wc -l)
    echo "🔄 العمليات الجارية: $RUNNING_PROCESSES"
}

# دالة عرض السجلات
show_logs() {
    echo -e "${BLUE}📋 آخر 50 سطر من السجلات:${NC}"
    cd_to_project
    
    if [ -f "$BOT_LOG" ]; then
        tail -n 50 "$BOT_LOG"
    else
        echo -e "${YELLOW}⚠️ ملف السجلات غير موجود${NC}"
    fi
}

# دالة مراقبة السجلات
monitor_logs() {
    echo -e "${BLUE}👀 مراقبة السجلات مباشرة (Ctrl+C للإيقاف):${NC}"
    cd_to_project
    
    if [ -f "$BOT_LOG" ]; then
        tail -f "$BOT_LOG"
    else
        echo -e "${YELLOW}⚠️ ملف السجلات غير موجود${NC}"
    fi
}

# دالة تثبيت المكتبات
install_dependencies() {
    echo -e "${BLUE}📦 تثبيت المكتبات المطلوبة...${NC}"
    cd_to_project
    
    # تفعيل البيئة الافتراضية إذا وجدت
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "🔧 تفعيل البيئة الافتراضية..."
    fi
    
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    
    echo -e "${GREEN}✅ تم تثبيت المكتبات${NC}"
}

# دالة اختبار الاتصال
test_connection() {
    echo -e "${BLUE}🔍 اختبار اتصال البوت...${NC}"
    cd_to_project
    
    # تفعيل البيئة الافتراضية إذا وجدت
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python3 test_bot_token.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ اختبار الاتصال ناجح${NC}"
    else
        echo -e "${RED}❌ فشل في اختبار الاتصال${NC}"
        exit 1
    fi
}

# دالة إعادة تشغيل البوت
restart_bot() {
    echo -e "${BLUE}🔄 إعادة تشغيل البوت...${NC}"
    stop_bot_quiet
    sleep 2
    start_bot
}

# التحقق من الأمر
case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    status)
        status_bot
        ;;
    logs)
        show_logs
        ;;
    monitor)
        monitor_logs
        ;;
    install)
        install_dependencies
        ;;
    test)
        test_connection
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ أمر غير صحيح${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
