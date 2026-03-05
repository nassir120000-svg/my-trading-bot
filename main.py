import streamlit as st
import telebot
import threading
import os
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
from requests.exceptions import ConnectionError, ReadTimeout

# 1. إعدادات الهوية والأمان
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# إنشاء كائن البوت مع ميزة تعدد المسارات
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=20)

# 2. محرك الاتصال ببينانس مع نظام "إعادة المحاولة الذكي"
class BinanceEngine:
    def __init__(self):
        self.client = self.connect()

    def connect(self):
        if not API_KEY or not API_SECRET: return None
        try:
            c = Client(API_KEY, API_SECRET, {"timeout": 60})
            c.get_account_status()
            return c
        except: return None

    def get_balance(self):
        if not self.client: self.client = self.connect()
        try:
            acc = self.client.get_account()
            return [b for b in acc['balances'] if float(b['free']) > 0.0001]
        except: return None

engine = BinanceEngine()

# 3. واجهة التحكم (Streamlit)
st.set_page_config(page_title="Nasser OS", layout="wide")
st.title("🛡️ نظام ناصر الفائق")

if engine.client:
    st.success("✅ بينانس: متصل")
else:
    st.error("❌ بينانس: غير متصل (تحقق من المفاتيح في Render)")

# 4. أوامر تليجرام المستقرة
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 النظام نشط الآن ومحمي من التعارض.")

@bot.message_handler(commands=['balance'])
def balance(message):
    data = engine.get_balance()
    if data:
        res = "💰 **أرصدتك الحالية:**\n\n" + "\n".join([f"🔹 {b['asset']}: {b['free']}" for b in data])
        bot.reply_to(message, res, parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ فشل جلب البيانات، تأكد من مفاتيح API.")

# 5. الحل النهائي لمشكلة التعارض (Anti-Conflict)
def run_bot_safe():
    while True:
        try:
            # السطر التالي هو الأهم لحل مشكلة Error 409
            bot.remove_webhook() 
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception:
            time.sleep(10) # انتظار قبل إعادة التشغيل تلقائياً

if __name__ == "__main__":
    threading.Thread(target=run_bot_safe, daemon=True).start()
    st.info("🛰️ السيرفر يبث الآن بنجاح.")
