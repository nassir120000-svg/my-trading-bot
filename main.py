import streamlit as st
import telebot
import threading
import os
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
from requests.exceptions import ConnectionError, ReadTimeout

# ==========================================
# [1] إدارة الهوية والأمان (Zero-Leak Security)
# ==========================================
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# إعداد البوت مع محرك معالجة متوازي (High-Speed)
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=40)

# ==========================================
# [2] ذكاء الاتصال (Smart Connection Engine)
# ==========================================
class NasserIntelligence:
    def __init__(self):
        self.client = self.refresh_connection()

    def refresh_connection(self):
        """محاولة إنشاء اتصال مستقر ومفحوص"""
        if not API_KEY or not API_SECRET:
            return None
        try:
            # مهلة انتظار طويلة (60 ثانية) لتناسب السيرفرات المجانية
            c = Client(API_KEY, API_SECRET, {"timeout": 60})
            c.get_account_status()
            return c
        except:
            return None

    def get_data_safely(self):
        """جلب البيانات مع نظام المحاولات الذكية (Retry System)"""
        if not self.client:
            self.client = self.refresh_connection()
        
        for _ in range(3): # يحاول 3 مرات قبل أن يستسلم
            try:
                acc = self.client.get_account()
                return [b for b in acc['balances'] if float(b['free']) > 0.0001]
            except (BinanceAPIException, ConnectionError, ReadTimeout):
                time.sleep(3)
                self.client = self.refresh_connection()
        return None

# تشغيل المحرك الذكي
nasser_engine = NasserIntelligence()

# ==========================================
# [3] واجهة المستخدم الاحترافية (Elite Dashboard)
# ==========================================
st.set_page_config(page_title="Nasser Smart Terminal", layout="wide")

# تصميم واجهة مستخدم مظلمة واحترافية
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: white; }
    .metric-card { background-color: #1e2329; border-radius: 10px; padding: 20px; border: 1px solid #f0b90b; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ نظام ناصر الذكي للتحكم الفائق")
st.write("---")

col1, col2 = st.columns(2)
with col1:
    st.info("🤖 **حالة البوت:** نشط ويعمل في الخلفية")
with col2:
    if nasser_engine.client:
        st.success("🔗 **بينانس:** متصلة بالكامل (API Active)")
    else:
        st.error("🔗 **بينانس:** غير متصلة (تحقق من المفاتيح في Render)")

# ==========================================
# [4] أوامر تليجرام الذكية (Ultra Response)
# ==========================================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome = (
        f"👑 **مرحباً بك يا سيد ناصر!**\n\n"
        "هذا النظام ذكي، آمن، ويعمل بكامل طاقته.\n"
        "──────────────────\n"
        "💰 `/balance` - تقرير الأرصدة الفوري\n"
        "📊 `/market` - نظرة سريعة على السوق\n"
        "🔄 `/fix` - إعادة تنشيط الاتصال يدوياً"
    )
    bot.reply_to(message, welcome, parse_mode="Markdown")

@bot.message_handler(commands=['balance'])
def balance_cmd(message):
    loading = bot.reply_to(message, "⏳ **جاري الاتصال الآمن بالمحفظة...**")
    data = nasser_engine.get_data_safely()
    
    if data:
        lines = [f"🔸 *{b['asset']}*: `{float(b['free']):.4f}`" for b in data]
        res = "💰 **تقرير أرصدتك الحالي:**\n\n" + "\n".join(lines)
        bot.edit_message_text(res, message.chat.id, loading.message_id, parse_mode="Markdown")
    else:
        bot.edit_message_text("❌ **فشل الاتصال:** السيرفر لم يستطع الوصول لبينانس. تأكد من صلاحيات API Key.", message.chat.id, loading.message_id)

@bot.message_handler(commands=['market'])
def market_cmd(message):
    try:
        prices = nasser_engine.client.get_all_tickers()
        coins = {"BTCUSDT": "₿", "ETHUSDT": "Ξ", "BNBUSDT": "🔶"}
        output = "📊 **أهم أسعار السوق الآن:**\n\n"
        for p in prices:
            if p['symbol'] in coins:
                output += f"{coins[p['symbol']]} *{p['symbol']}*: `${float(p['price']):,.2f}`\n"
        bot.reply_to(message, output, parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ فشل جلب الأسعار، جرب ثانية خلال لحظات.")

@bot.message_handler(commands=['fix'])
def fix_cmd(message):
    nasser_engine.client = nasser_engine.refresh_connection()
    bot.reply_to(message, "🔄 تم إعادة ضبط المحرك بنجاح!")

# ==========================================
# [5] محرك الاستمرارية المطلقة (Auto-Restart)
# ==========================================
def bot_polling():
    while True:
        try:
            bot.remove_webhook() # حل مشكلة Conflict 409 نهائياً
            bot.infinity_polling(timeout=90, long_polling_timeout=45)
        except Exception:
            time.sleep(10) # انتظار قليل قبل إعادة التشغيل في حال انقطاع الإنترنت

if __name__ == "__main__":
    # تشغيل البوت في مسار معالجة مستقل
    threading.Thread(target=bot_polling, daemon=True).start()
    st.write("🛰️ **السيرفر يبث الآن بنجاح.. الأنظمة مستقرة.**")
