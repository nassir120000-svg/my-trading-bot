import streamlit as st
import telebot
import threading
import os
import time
from binance.client import Client
from requests.exceptions import ConnectionError

# --- 1. إعدادات الأمان والاتصال ---
# جلب المفاتيح من "خزنة" Render (Environment Variables)
TOKEN = os.getenv("TELEGRAM_TOKEN")
BINANCE_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET = os.getenv("BINANCE_API_SECRET")

# تعريف البوت
bot = telebot.TeleBot(TOKEN)

# محاولة الاتصال ببينانس
try:
    if BINANCE_KEY and BINANCE_SECRET:
        binance_client = Client(BINANCE_KEY, BINANCE_SECRET)
    else:
        binance_client = None
except Exception:
    binance_client = None

# --- 2. واجهة التحكم (Streamlit) ---
st.set_page_config(page_title="Nasser Terminal", page_icon="⚡", layout="wide")

st.title("📈 لوحة تحكم ناصر الاحترافية")
st.markdown("---")

# عرض حالة الأنظمة في أعمدة
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("حالة البوت", "يعمل بنشاط ✅")
with col2:
    status = "متصل ✅" if binance_client else "غير متصل ❌"
    st.metric("بينانس", status)
with col3:
    st.metric("تحديث البيانات", "تلقائي 🔄")

# قائمة جانبية للمعلومات
st.sidebar.header("⚙️ الإعدادات السرية")
st.sidebar.info("يتم جلب المفاتيح بأمان من بيئة العمل المشفرة.")
if binance_client:
    try:
        usdt_balance = binance_client.get_asset_balance(asset='USDT')
        st.sidebar.success(f"رصيد USDT الحالي: {usdt_balance['free']}$")
    except:
        pass

# --- 3. وظائف تليجرام الاحترافية ---

@bot.message_handler(commands=['start'])
def welcome(message):
    user = message.from_user.first_name
    msg = (f"👋 أهلاً بك يا {user} في نظامك الخاص!\n\n"
           "🚀 البوت الآن مربوط بالسيرفر ويعمل 24/7.\n"
           "أوامرك المتاحة:\n"
           "💰 /balance - لعرض محفظتك بالكامل\n"
           "📊 /price BTC - لمعرفة سعر عملة معينة")
    bot.reply_to(message, msg)

@bot.message_handler(commands=['balance'])
def show_balance(message):
    if not binance_client:
        bot.reply_to(message, "⚠️ فشل الاتصال ببينانس. تحقق من المفاتيح في Render.")
        return
    
    try:
        account = binance_client.get_account()
        # تصفية المحفظة لعرض العملات التي تملك فيها رصيد فقط
        balances = [f"🔹 {b['asset']}: {b['free']}" for b in account['balances'] if float(b['free']) > 0.0001]
        
        if balances:
            result = "💰 **أرصدتك الحقيقية في بينانس:**\n\n" + "\n".join(balances)
        else:
            result = "💰 المحفظة فارغة حالياً."
        bot.reply_to(message, result, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في جلب البيانات: {e}")

@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        symbol = message.text.split()[1].upper() + "USDT"
        price = binance_client.get_symbol_ticker(symbol=symbol)
        bot.reply_to(message, f"📊 سعر {symbol} الآن هو: {float(price['price']):,.2f}$")
    except:
        bot.reply_to(message, "⚠️ يرجى كتابة اسم العملة بشكل صحيح. مثال: `/price BTC`")

# --- 4. محرك التشغيل الذكي (Anti-Crash) ---
def run_bot_safe():
    while True:
        try:
            # حل مشكلة Conflict 409 وحذف أي اتصالات معلقة
            bot.remove_webhook()
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception:
            time.sleep(5) # انتظار بسيط قبل إعادة المحاولة في حال انقطاع الإنترنت

if __name__ == "__main__":
    # تشغيل البوت في الخلفية (Thread) لضمان عمل الموقع في نفس الوقت
    t = threading.Thread(target=run_bot_safe)
    t.daemon = True
    t.start()
    
    st.write("🛰️ السيرفر يبث الآن.. يمكنك استخدام البوت في تليجرام.")
