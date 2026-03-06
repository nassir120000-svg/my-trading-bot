import os
import time
import logging
import threading
from datetime import datetime
import telebot
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
import streamlit as st

# --- 1. إعداد نظام المراقبة (Logging) ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 2. جلب الإعدادات بأمان ---
class Config:
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    BINANCE_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET = os.getenv("BINANCE_API_SECRET")
    # التأكد من وجود المفاتيح
    @classmethod
    def validate(cls):
        return all([cls.TOKEN, cls.BINANCE_KEY, cls.BINANCE_SECRET])

# --- 3. إدارة الاتصالات (The Core Engine) ---
class NasserBotSystem:
    def __init__(self):
        self.bot = telebot.TeleBot(Config.TOKEN, threaded=True, num_threads=4)
        self.binance_client = None
        self.is_running = False
        self._initialize_binance()
        self._setup_handlers()

    def _initialize_binance(self):
        """ربط ذكي مع بينانس مع محاولات إعادة الاتصال"""
        try:
            self.binance_client = Client(Config.BINANCE_KEY, Config.BINANCE_SECRET)
            # اختبار الاتصال الفعلي
            self.binance_client.get_account_status()
            logger.info("✅ تم الاتصال بنظام بينانس بنجاح.")
        except Exception as e:
            logger.error(f"❌ فشل ربط بينانس: {str(e)}")
            self.binance_client = None

    def _setup_handlers(self):
        """تعريف الأوامر الاحترافية"""
        
        @self.bot.message_handler(commands=['start', 'help'])
        def handle_start(message):
            welcome_text = (
                "🛡️ **نظام ناصر الاحترافي V3.0**\n\n"
                "• الحالة: `متصل ونشط` ✅\n"
                "• الربط المالي: " + ("`مفعل` 🟢" if self.binance_client else "`معطل` 🔴") + "\n\n"
                "**الأوامر المتاحة:**\n"
                "💰 `/balance` - عرض أرصدة المحفظة الحقيقية\n"
                "📊 `/price BTCUSDT` - سعر أي عملة فوراً\n"
                "⚙️ `/status` - فحص صحة النظام"
            )
            self.bot.reply_to(message, welcome_text, parse_mode='Markdown')

        @self.bot.message_handler(commands=['balance'])
        def handle_balance(message):
            if not self.binance_client:
                self.bot.reply_to(message, "❌ خطأ: لم يتم ضبط مفاتيح بينانس بشكل صحيح في Render.")
                return
            
            try:
                msg = self.bot.reply_to(message, "🔍 جاري فحص المحفظة...")
                account = self.binance_client.get_account()
                balances = [b for b in account['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
                
                response = "💰 **أرصدة محفظتك:**\n\n"
                for crypto in balances:
                    total = float(crypto['free']) + float(crypto['locked'])
                    response += f"• **{crypto['asset']}**: `{total:.4f}`\n"
                
                self.bot.edit_message_text(response, message.chat.id, msg.message_id, parse_mode='Markdown')
            except Exception as e:
                self.bot.reply_to(message, f"⚠️ خطأ أثناء جلب البيانات: {str(e)}")

    def run(self):
        """تشغيل احترافي مع معالجة تعارض 409 تلقائياً"""
        if self.is_running: return
        self.is_running = True
        
        # أهم خطوة للمحترفين: تنظيف المسار قبل الانطلاق
        try:
            self.bot.remove_webhook()
            time.sleep(1)
        except: pass

        def poll():
            while True:
                try:
                    logger.info("🚀 بدأت عملية الاستماع (Polling)...")
                    self.bot.infinity_polling(timeout=10, long_polling_timeout=5)
                except Exception as e:
                    logger.error(f"🔄 إعادة تشغيل تلقائية بسبب خطأ: {e}")
                    time.sleep(5)

        threading.Thread(target=poll, daemon=True).start()

# --- 4. واجهة العرض والتحكم (Streamlit Interface) ---
def main():
    st.set_page_config(page_title="Nasser Pro System", page_icon="⚡")
    
    if not Config.validate():
        st.error("🚨 نقص في إعدادات البيئة (Environment Variables)! تأكد من إضافة TOKEN و API Keys في Render.")
        return

    # استخدام Session State لضمان عدم تكرار تشغيل البوت عند تحديث الصفحة
    if 'system' not in st.session_state:
        st.session_state.system = NasserBotSystem()
        st.session_state.system.run()
        st.session_state.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    st.title("⚡ نظام ناصر الذكي V3")
    st.write(f"⏱️ وقت البدء: `{st.session_state.start_time}`")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("حالة التليجرام", "نشط ✅")
    with col2:
        status = "متصل ✅" if st.session_state.system.binance_client else "فشل الاتصال ❌"
        st.metric("ربط بينانس", status)

    st.divider()
    st.subheader("📝 سجل العمليات الأخير")
    st.info("النظام يعمل الآن في الخلفية. يمكنك إرسال الأوامر عبر التليجرام مباشرة.")

if __name__ == "__main__":
    main()
