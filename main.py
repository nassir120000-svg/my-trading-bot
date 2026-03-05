import streamlit as st
import telebot
import threading
import os
import time
import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException

# --- [1] الإعدادات الأمنية والربط ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
BINANCE_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_API_SECRET")

# إنشاء كائن البوت مع ميزة الرد الذكي
bot = telebot.TeleBot(TOKEN, threaded=True)

# محاولة الاتصال ببينانس مع نظام فحص الأخطاء
def get_binance_client():
    try:
        if BINANCE_KEY and BINANCE_SECRET:
            return Client(BINANCE_KEY, BINANCE_SECRET, {"timeout": 20})
    except:
        return None
    return None

client = get_binance_client()

# --- [2] واجهة الويب الاحترافية (Streamlit) ---
st.set_page_config(page_title="Nasser Quantum Bot", page_icon="💎", layout="wide")

# تصميم الواجهة بلمسة تقنية
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 نظام ناصر للتداول الذكي (Pro)")
st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="حالة النظام", value="نشط ⚡", delta="متصل")
with col2:
    status_text = "متصل ✅" if client else "غير متصل ❌"
    st.metric(label="ربط بينانس", value=status_text)
with col3:
    st.metric(label="الحماية", value="عالية 🛡️")

# --- [3] وظائف تليجرام الاحترافية (لا تتوقف) ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👑 **مرحباً بك في لوحة تحكم ناصر!**\n\n"
        "هذا البوت يعمل بنظام الـ Multi-threading لضمان عدم التوقف.\n\n"
        "📜 **الأوامر المتاحة:**\n"
        "💰 `/balance` - عرض أرصدة محفظتك الحقيقية\n"
        "📈 `/price BTC` - سعر أي عملة مقابل USDT\n"
        "🛠️ `/status` - فحص جودة اتصال السيرفر"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['balance'])
def check_balance(message):
    if not client:
        bot.reply_to(message, "⚠️ خطأ: مفاتيح بينانس غير صحيحة أو مفقودة في إعدادات Render.")
        return
    
    msg = bot.reply_to(message, "🔍 جاري فحص المحفظة...")
    try:
        account = client.get_account()
        balances = [f"● *{b['asset']}*: `{float(b['free']):.4f}`" 
                    for b in account['balances'] if float(b['free']) > 0.0001]
        
        response = "💰 **أرصدتك المتوفرة:**\n\n" + "\n".join(balances) if balances else "⚠️ المحفظة فارغة."
        bot.edit_message_text(response, message.chat.id, msg.message_id, parse_mode="Markdown")
    except BinanceAPIException as e:
        bot.edit_message_text(f"❌ خطأ من بينانس: {e.message}", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ حدث خطأ تقني، يرجى المحاولة لاحقاً.", message.chat.id, msg.message_id)

@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "💡 مثال: `/price ETH` أو `/price SOL`", parse_mode="Markdown")
            return
        
        symbol = args[1].upper() + "USDT"
        ticker = client.get_symbol_ticker(symbol=symbol)
        price = float(ticker['price'])
        
        bot.reply_to(message, f"📊 سعر *{symbol}* الآن:\n💰 `${price:,.2f}`", parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ تأكد من اسم العملة (مثال: BTC, ETH, SOL)")

# --- [4] محرك التشغيل المستمر (Anti-Crash Engine) ---
def run_bot_forever():
    while True:
        try:
            bot.remove_webhook() # تنظيف أي تضارب قديم
            print("إقلاع نظام تليجرام...")
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            print(f"إعادة محاولة التشغيل بعد 10 ثواني بسبب: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # تشغيل البوت في مسار منفصل تماماً عن الموقع
    bot_thread = threading.Thread(target=run_bot_forever)
    bot_thread.daemon = True
    bot_thread.start()
    
    st.success("🛰️ السيرفر يبث الآن بنجاح. البوت جاهز للاستخدام في تليجرام.")
