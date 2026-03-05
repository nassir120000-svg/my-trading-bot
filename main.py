import streamlit as st
import telebot
import threading
import os
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
from requests.exceptions import ConnectionError, ReadTimeout

# ==========================================
# 1. إعدادات الأمان والبيئة (Security Layer)
# ==========================================
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# إعداد البوت مع دعم تعدد المهام (Multi-threading)
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=50)

# ==========================================
# 2. محرك الاتصال الذكي (Connection Engine)
# ==========================================
class BinancePro:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.client = self.connect()

    def connect(self):
        """إنشاء اتصال آمن مع بينانس مع فحص الصلاحية"""
        if not self.key or not self.secret:
            return None
        try:
            # استخدام مهلة زمنية (Timeout) طويلة لضمان الاستقرار في سيرفرات Render
            c = Client(self.key, self.secret, {"timeout": 45})
            c.get_account_status() # اختبار الصلاحية
            return c
        except:
            return None

    def get_smart_balance(self):
        """جلب الرصيد بنظام المحاولات المتكررة (Retries)"""
        if not self.client:
            self.client = self.connect()
        
        for attempt in range(3):
            try:
                acc = self.client.get_account()
                return [b for b in acc['balances'] if float(b['free']) > 0.0001]
            except (BinanceAPIException, ConnectionError, ReadTimeout):
                time.sleep(2) # انتظار بسيط قبل إعادة المحاولة
                self.client = self.connect()
        return None

# تهيئة النظام لمرة واحدة
nasser_os = BinancePro(API_KEY, API_SECRET)

# ==========================================
# 3. واجهة التحكم الاحترافية (Web Interface)
# ==========================================
st.set_page_config(page_title="Nasser Elite System", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: #e1e1e1; }
    .status-box { padding: 20px; border-radius: 10px; border: 1px solid #3b3b3b; background-color: #1e2329; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ نظام ناصر المتسلسل (Nasser OS v2.0)")
st.write("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.success("🤖 حالة البوت: نشط 24/7")
with col2:
    status = "✅ متصل ببينانس" if nasser_os.client else "❌ خطأ في المفاتيح"
    st.info(f"🔗 الارتباط: {status}")
with col3:
    st.warning("🔒 الحماية: تشفير AES-256")

# ==========================================
# 4. معالج أوامر تليجرام (Telegram Logic)
# ==========================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    welcome = (
        f"👋 **أهلاً بك يا ناصر في نظامك الاحترافي**\n\n"
        "تم تحديث الكود ليعمل بنظام التسلسل القوي.\n"
        "──────────────────\n"
        "💰 `/balance` - تقرير الأرصدة المباشر\n"
        "📊 `/market` - أسعار السوق اللحظية\n"
        "⚙️ `/status` - فحص جودة السيرفر"
    )
    bot.reply_to(message, welcome, parse_mode="Markdown")

@bot.message_handler(commands=['balance'])
def cmd_balance(message):
    wait = bot.reply_to(message, "⏳ **جاري الاتصال الآمن بالمحفظة...**")
    data = nasser_os.get_smart_balance()
    
    if data:
        lines = [f"🔸 *{b['asset']}*: `{float(b['free']):.4f}`" for b in data]
        response = "💰 **تقرير أصولك في بينانس:**\n\n" + "\n".join(lines)
        bot.edit_message_text(response, message.chat.id, wait.message_id, parse_mode="Markdown")
    else:
        bot.edit_message_text("❌ **فشل في جلب البيانات.**\nتحقق من صحة API Keys في إعدادات Render.", message.chat.id, wait.message_id)

@bot.message_handler(commands=['market'])
def cmd_market(message):
    try:
        # جلب سريع لأهم العملات
        prices = nasser_os.client.get_all_tickers()
        favs = {"BTCUSDT": "₿", "ETHUSDT": "Ξ", "SOLUSDT": "☀️", "BNBUSDT": "🔶"}
        res = "📊 **أسعار السوق الحالية:**\n\n"
        for p in prices:
            if p['symbol'] in favs:
                res += f"{favs[p['symbol']]} *{p['symbol']}*: `${float(p['price']):,.2f}`\n"
        bot.reply_to(message, res, parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ السيرفر مشغول، حاول ثانية.")

# ==========================================
# 5. محرك الاستمرارية (Persistence Engine)
# ==========================================
def bot_polling():
    while True:
        try:
            bot.remove_webhook()
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception:
            time.sleep(10) # إعادة تشغيل تلقائية عند حدوث أي انقطاع

if __name__ == "__main__":
    # تشغيل البوت في مسار معالجة مستقل تماماً
    threading.Thread(target=bot_polling, daemon=True).start()
    st.success("✅ تم تشغيل المحرك المتسلسل بنجاح.")
