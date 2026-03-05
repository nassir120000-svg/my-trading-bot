import streamlit as st
import telebot
import threading
import os
import time
from binance.client import Client

# جلب المفاتيح بأمان
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# إعداد البوت
bot = telebot.TeleBot(TOKEN, threaded=True)

# محاولة الاتصال ببينانس
def get_client():
    if not API_KEY or not API_SECRET: return None
    try:
        c = Client(API_KEY, API_SECRET, {"timeout": 30})
        c.get_account_status()
        return c
    except: return None

client = get_client()

# واجهة Streamlit
st.set_page_config(page_title="Nasser System")
st.title("🛡️ نظام ناصر المتكامل")
st.write(f"الحالة: {'✅ متصل ببينانس' if client else '❌ تحقق من المفاتيح في رندر'}")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 النظام يعمل الآن بنجاح وبدون تعارض!")

@bot.message_handler(commands=['balance'])
def balance(message):
    if not client:
        bot.reply_to(message, "⚠️ فشل جلب البيانات. تأكد من مفاتيح API.")
        return
    try:
        acc = client.get_account()
        assets = [f"{b['asset']}: {b['free']}" for b in acc['balances'] if float(b['free']) > 0.0001]
        bot.reply_to(message, "💰 محفظتك:\n" + "\n".join(assets))
    except:
        bot.reply_to(message, "❌ خطأ في الاتصال.")

# --- المحرك القوي لحل مشكلة 409 ---
def run_bot():
    while True:
        try:
            # تنظيف أي اتصال قديم (الحل الجذري لصورك)
            bot.remove_webhook() 
            time.sleep(1)
            bot.infinity_polling(timeout=20)
        except Exception:
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    st.success("🛰️ السيرفر يبث الآن.. البوت جاهز للاستخدام.")
