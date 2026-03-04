import streamlit as st
import telebot
import threading
import os
import time
from binance.client import Client

# --- الإعدادات الأمنية ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
BINANCE_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_API_SECRET")

# إنشاء كائن البوت
bot = telebot.TeleBot(TOKEN)

# إعداد اتصال بينانس
try:
    binance_client = Client(BINANCE_KEY, BINANCE_SECRET)
except:
    binance_client = None

# --- واجهة المستخدم (Streamlit) ---
st.set_page_config(page_title="منصة ناصر للتداول", page_icon="📈")
st.title("🤖 نظام التداول الذكي لـ ناصر")
st.markdown("---")

st.sidebar.header("📊 حالة الأنظمة")
if binance_client:
    st.sidebar.success("بينانس: متصل ✅")
    try:
        balance = binance_client.get_asset_balance(asset='USDT')
        st.sidebar.metric("رصيد USDT", f"${balance['free']}")
    except:
        st.sidebar.warning("تعذر جلب الرصيد")
else:
    st.sidebar.error("بينانس: غير متصل ❌")

# --- محرك التليجرام ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً ناصر! البوت يعمل الآن بأقصى احترافية.\n\nاستخدم /balance لعرض أرصدتك الحقيقية.")

@bot.message_handler(commands=['balance'])
def show_balance(message):
    if not binance_client:
        bot.reply_to(message, "⚠️ مفاتيح بينانس غير مبرمجة في Render.")
        return
    try:
        account = binance_client.get_account()
        assets = [f"💰 {b['asset']}: {b['free']}" for b in account['balances'] if float(b['free']) > 0.001]
        msg = "**أرصدتك الحالية:**\n\n" + "\n".join(assets) if assets else "المحفظة فارغة."
        bot.reply_to(message, msg, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

# دالة تشغيل البوت مع معالجة خطأ التصادم (Conflict)
def start_bot():
    while True:
        try:
            bot.remove_webhook() # تنظيف أي اتصال قديم
            print("جاري بدء البوت...")
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"إعادة محاولة بسبب: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # تشغيل البوت في خلفية السيرفر
    t = threading.Thread(target=start_bot)
    t.daemon = True
    t.start()
    st.write("✨ جميع الأنظمة تعمل الآن بصمت في الخلفية.")
