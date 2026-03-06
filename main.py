import os
import time
import threading
import telebot
from telebot import types
from binance.client import Client
import pandas as pd
import pandas_ta as ta

# --- 1. الإعدادات والربط ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
CHAT_ID = os.getenv("CHAT_ID") # تأكد من إضافته في Render

bot = telebot.TeleBot(TOKEN)
client = Client(API_KEY, API_SECRET)

# ذاكرة النظام الذكية
state = {
    "is_active": True,  # التداول مفعل تلقائياً عند البدء
    "symbol": "BTCUSDT",
    "amount_usd": 15.0, # المبلغ الافتراضي
    "position": None,   # لمتابعة إذا كان هناك صفقة مفتوحة
    "last_price": 0.0
}

# --- 2. العقل التحليلي (Trading Engine) ---
def trading_engine():
    print("🚀 انطلاق العقل التحليلي لنظام ناصر...")
    while True:
        if state["is_active"]:
            try:
                # جلب بيانات السوق (شموع 15 دقيقة للتحليل المتوسط)
                bars = client.get_klines(symbol=state["symbol"], interval=Client.KLINE_INTERVAL_15MINUTE, limit=100)
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'ct', 'qv', 'nt', 'tb', 'tv', 'i'])
                df['close'] = df['close'].astype(float)

                # مؤشرات احترافية: RSI (لقوة الاتجاه) و EMA (لاتجاه السعر)
                df['rsi'] = ta.rsi(df['close'], length=14)
                df['ema'] = ta.ema(df['close'], length=20)
                
                current_rsi = df['rsi'].iloc[-1]
                current_price = df['close'].iloc[-1]
                ema_price = df['ema'].iloc[-1]

                # --- منطق التداول الآلي الذكي ---
                
                # حالة الشراء: إذا كان السعر فوق المتوسط و RSI منخفض (فرصة ذهبية)
                if state["position"] is None and current_rsi < 35 and current_price > ema_price:
                    execute_buy(current_price, current_rsi)

                # حالة البيع: إذا حققنا ربحاً أو وصل RSI لمنطقة تشبع (70+)
                elif state["position"] == "BUY" and (current_rsi > 70 or current_price > state["buy_price"] * 1.02):
                    execute_sell(current_price, current_rsi)

            except Exception as e:
                print(f"⚠️ تنبيه النظام: {e}")
        
        time.sleep(30) # فحص السوق كل 30 ثانية بدون توقف

def execute_buy(price, rsi):
    try:
        msg = f"🟢 **قرار شراء آلي (قوي)**\n💰 السعر: `{price}`\n📊 RSI: `{rsi:.2f}`\n💵 المبلغ: `{state['amount_usd']}$`"
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
        state["position"] = "BUY"
        state["buy_price"] = price
        # تفعيل الأمر الحقيقي:
        # client.order_market_buy(symbol=state["symbol"], quoteOrderQty=state["amount_usd"])
    except Exception as e:
        bot.send_message(CHAT_ID, f"❌ فشل تنفيذ الشراء: {e}")

def execute_sell(price, rsi):
    try:
        profit = ((price - state["buy_price"]) / state["buy_price"]) * 100
        msg = f"🔴 **قرار بيع آلي (جني أرباح)**\n💰 السعر: `{price}`\n📈 الربح: `%{profit:.2f}`\n📊 RSI: `{rsi:.2f}`"
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
        state["position"] = None
        # تفعيل الأمر الحقيقي:
        # client.order_market_sell(symbol=state["symbol"], quantity=...)
    except Exception as e:
        bot.send_message(CHAT_ID, f"❌ فشل تنفيذ البيع: {e}")

# --- 3. واجهة التحكم في تليجرام ---
@bot.message_handler(commands=['start', 'status'])
def send_status(message):
    status = "نشط ⚡" if state["is_active"] else "متوقف 💤"
    msg = (f"🛡️ **نظام ناصر للتداول المستقل**\n\n"
           f"• الحالة: `{status}`\n"
           f"• المبلغ لكل صفقة: `{state['amount_usd']}$`\n"
           f"• العملة الحالية: `{state['symbol']}`\n"
           f"• الوضع الحالي: `{'في صفقة' if state['position'] else 'بحث عن فرصة'}`")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🟢 تشغيل", callback_data="on"), 
               types.InlineKeyboardButton("🔴 إيقاف", callback_data="off"))
    bot.reply_to(message, msg, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "on":
        state["is_active"] = True
        bot.answer_callback_query(call.id, "بدأ التداول الآلي")
        bot.edit_message_text("✅ النظام الآن يحلل ويتداول بشكل دائم...", call.message.chat.id, call.message.message_id)
    elif call.data == "off":
        state["is_active"] = False
        bot.answer_callback_query(call.id, "توقف التداول")
        bot.edit_message_text("🛑 تم إيقاف النظام عن العمل.", call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['set_amount'])
def set_amount(message):
    try:
        amt = float(message.text.split()[1])
        state["amount_usd"] = amt
        bot.reply_to(message, f"✅ تم تحديد مبلغ التداول بـ `{amt}$` لكل صفقة.")
    except:
        bot.reply_to(message, "⚠️ استخدم: `/set_amount 50` لتحديد المبلغ.")

# --- 4. نظام التشغيل اللانهائي ---
if __name__ == "__main__":
    # تشغيل محرك التداول في مسار مستقل
    t = threading.Thread(target=trading_engine, daemon=True)
    t.start()
    bot.infinity_polling()
