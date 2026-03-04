import streamlit as st
import telebot
import threading
import os
import time
from binance.client import Client

# --- 1. جلب جميع المفاتيح من Render (أمان 100%) ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BINANCE_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_API_SECRET")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# إعداد اتصال بينانس (بشكل آمن)
try:
    binance_client = Client(BINANCE_KEY, BINANCE_SECRET)
except Exception as e:
    binance_client = None

# --- 2. واجهة الموقع (Streamlit) لتعرف حالة السيرفر ---
st.set_page_config(page_title="Nasser Trading Bot", page_icon="📈")
st.title("🤖 منصة ناصر للتداول الذكي")
st.markdown("---")

# عرض حالة الاتصال في الجانب
st.sidebar.header("لوحة التحكم")
if binance_client:
    st.sidebar.success("✅ متصل ببينانس")
    try:
        # عرض رصيد USDT سريع في الموقع
        res = binance_client.get_asset_balance(asset='USDT')
        st.sidebar.metric("رصيد USDT الحالي", f"${res['free']}")
    except:
        st.sidebar.warning("⚠️ لا يمكن جلب الرصيد حالياً")
else:
    st.sidebar.error("❌ غير متصل ببينانس")

# --- 3. أوامر التليجرام (المخ) ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً ناصر! البوت يعمل الآن بقوة.\n\nاستخدم الأوامر التالية:\n💰 /balance - لعرض الرصيد\n📊 /price BTC - لمعرفة سعر البيتكوين")

@bot.message_handler(commands=['balance'])
def get_balance(message):
    if not binance_client:
        bot.reply_to(message, "❌ المفاتيح غير موجودة في إعدادات Render.")
        return
    
    try:
        # جلب الأرصدة الحقيقية فقط
        account = binance_client.get_account()
        balances = [f"🔸 {b['asset']}: {b['free']}" for b in account['balances'] if float(b['free']) > 0.0001]
        
        if balances:
            response = "💰 **أرصدتك المتوفرة:**\n\n" + "\n".join(balances)
        else:
            response = "💰 المحفظة لا تحتوي على أرصدة حالياً."
        
        bot.reply_to(message, response, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل جلب الرصيد: {e}")

# --- 4. تشغيل النظام ---
def run_bot():
    try:
        bot.infinity_polling()
    except:
        time.sleep(5)

if __name__ == "__main__":
    # تشغيل تليجرام في الخلفية
    threading.Thread(target=run_bot, daemon=True).start()
    st.write("✨ النظام يعمل الآن ومستعد لتلقي الأوامر.")
