import os
import time
import threading
import telebot
from telebot import types
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import pandas_ta as ta

# --- 1. الإعدادات والربط ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)
client = Client(API_KEY, API_SECRET)

state = {
    "is_trading": True,
    "symbol": "BTCUSDT",
    "amount_usd": 15.0,
    "position": None,
    "buy_price": 0.0,
    "quantity": 0.0
}

# --- 2. محرك التداول الاحترافي ---
def trading_engine():
    print("🚀 انطلاق النظام السيبراني للتداول الآلي...")
    while True:
        if state["is_trading"]:
            try:
                # جلب البيانات وحساب المؤشرات
                bars = client.get_klines(symbol=state["symbol"], interval=Client.KLINE_INTERVAL_15MINUTE, limit=100)
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'ct', 'qv', 'nt', 'tb', 'tv', 'i'])
                df['close'] = df['close'].astype(float)
                
                df['rsi'] = ta.rsi(df['close'], length=14)
                df['ema'] = ta.ema(df['close'], length=20)
                
                curr_rsi = df['rsi'].iloc[-1]
                curr_price = df['close'].iloc[-1]
                ema_val = df['ema'].iloc[-1]

                # --- منطق القرارات ---
                # 🟢 الشراء
                if state["position"] is None and curr_rsi < 35 and curr_price > ema_val:
                    execute_real_buy(curr_price, curr_rsi)

                # 🔴 البيع (ربح 2% أو وقف خسارة 3% أو RSI عالي)
                elif state["position"] == "BUY":
                    profit = ((curr_price - state["buy_price"]) / state["buy_price"]) * 100
                    if curr_rsi > 70 or profit >= 2.0 or profit <= -3.0:
                        execute_real_sell(curr_price, curr_rsi, profit)

            except Exception as e:
                print(f"⚠️ خطأ مؤقت: {e}")
                time.sleep(10) # انتظار للتعافي
        
        time.sleep(30)

# --- 3. وظائف التنفيذ الفعلي (بينانس) ---
def execute_real_buy(price, rsi):
    try:
        # حساب الكمية وتقريبها لتناسب قوانين بينانس
        info = client.get_symbol_info(state["symbol"])
        step_size = float([f['stepSize'] for f in info['filters'] if f['filterType'] == 'LOT_SIZE'][0])
        
        raw_qty = state["amount_usd"] / price
        state["quantity"] = float(round(raw_qty // step_size * step_size, 6))

        # تنفيذ الأمر الحقيقي في المنصة
        order = client.order_market_buy(symbol=state["symbol"], quoteOrderQty=state["amount_usd"])
        
        state["position"] = "BUY"
        state["buy_price"] = price
        
        msg = f"✅ **تم الشراء بنجاح!**\n💰 السعر: `{price}`\n💵 الكمية: `{state['quantity']}`\n📊 RSI: `{rsi:.2f}`"
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(CHAT_ID, f"❌ فشل الشراء المالي: {e}")

def execute_real_sell(price, rsi, profit):
    try:
        # تنفيذ البيع الحقيقي لجميع الكمية المشتراة
        order = client.order_market_sell(symbol=state["symbol"], quantity=state["quantity"])
        
        msg = f"🔔 **تم البيع بنجاح!**\n💰 السعر: `{price}`\n📈 الربح/الخسارة: `%{profit:.2f}`\n📊 RSI: `{rsi:.2f}`"
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
        state["position"] = None
        state["quantity"] = 0.0
    except Exception as e:
        bot.send_message(CHAT_ID, f"❌ فشل البيع المالي: {e}")

# --- 4. واجهة تليجرام ---
@bot.message_handler(commands=['start', 'status'])
def send_panel(message):
    status = "نشط ⚡" if state["is_trading"] else "متوقف 💤"
    msg = (f"🛡️ **نظام ناصر V5 المطور**\n"
           f"الحالة: `{status}`\n"
           f"المبلغ: `{state['amount_usd']}$`\n"
           f"الوضع: `{'في صفقة 💹' if state['position'] else 'انتظار 🔍'}`")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🟢 تشغيل", callback_data="on"), 
               types.InlineKeyboardButton("🔴 إيقاف", callback_data="off"))
    bot.reply_to(message, msg, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def btn_handler(call):
    if call.data == "on": state["is_trading"] = True
    else: state["is_trading"] = False
    bot.answer_callback_query(call.id, "تم التحديث")
    bot.send_message(CHAT_ID, f"🔄 تم تغيير حالة البوت إلى: {'نشط' if state['is_trading'] else 'متوقف'}")

if __name__ == "__main__":
    threading.Thread(target=trading_engine, daemon=True).start()
    bot.infinity_polling()
