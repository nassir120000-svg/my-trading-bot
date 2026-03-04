import streamlit as st
import telebot
import threading
import os
import time
from binance.client import Client
from requests.exceptions import ConnectionError

# جلب المفاتيح بأمان
TOKEN = os.getenv("TELEGRAM_TOKEN")
BINANCE_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_API_SECRET")

# إنشاء كائن البوت
bot = telebot.TeleBot(TOKEN)

# إعداد اتصال بينانس مع فحص الأمان
def get_binance_client():
    try:
        if BINANCE_KEY and BINANCE_SECRET:
            return Client(BINANCE_KEY, BINANCE_SECRET)
    except:
        return None
    return None

client = get_binance_client()

# --- واجهة Streamlit ---
st.set_page_config(page_title="Nasser Super Bot", layout="centered")
st.title("🚀 منصة ناصر المتكاملة")

if client:
    st.success("بينانس: متصل بنجاح ✅")
else:
    st.error("بينانس: غير متصل ❌ (تحقق من المفاتيح في Render)")

# --- محرك تليجرام الاحترافي ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "أهلاً ناصر! النظام يعمل الآن بكفاءة 100%.\n\nأرسل /balance لجلب بيانات محفظتك.")

@bot.message_handler(commands=['balance'])
def balance(message):
    if not client:
        bot.reply_to(message, "⚠️ لا يمكن الاتصال ببينانس حالياً.")
        return
    try:
        acc = client.get_account()
        assets = [f"💰 {b['asset']}: {b['free']}" for b in acc['balances'] if float(b['free']) > 0.001]
        res = "✅ **أرصدتك الحالية:**\n\n" + "\n".join(assets) if assets else "المحفظة فارغة."
        bot.reply_to(message, res, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {e}")

# دالة التشغيل الذكي لمنع التوقف (Anti-Crash)
def run_bot_safe():
    while True:
        try:
            bot.remove_webhook() # حل مشكلة Conflict 409 نهائياً
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            time.sleep(10) # انتظار قبل إعادة المحاولة

if __name__ == "__main__":
    t = threading.Thread(target=run_bot_safe)
    t.daemon = True
    t.start()
    st.info("🤖 البوت يعمل الآن في الخلفية...")
