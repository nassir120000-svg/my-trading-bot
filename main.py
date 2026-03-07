import os
import time
import threading
import telebot
from binance.client import Client
import pandas as pd
import ta 

# --- إعدادات البيئة ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)
client = Client(API_KEY, API_SECRET)

# ذاكرة النظام
state = {"active": True, "pos": None, "buy_p": 0.0, "symbol": "BTCUSDT"}

def trading_brain():
    print("🚀 انطلاق العقل التحليلي الاحترافي...")
    while True:
        if state["active"]:
            try:
                # جلب البيانات (شمعة 15 دقيقة)
                bars = client.get_klines(symbol=state["symbol"], interval="15m", limit=100)
                df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'n', 'tb', 'tv', 'i'])
                df['c'] = df['c'].astype(float)
                
                # حساب RSI (مؤشر القوة النسبية) - نسخة خفيفة ومستقرة
                rsi_indicator = ta.momentum.RSIIndicator(close=df['c'], window=14)
                rsi = rsi_indicator.rsi().iloc[-1]
                price = df['c'].iloc[-1]

                # --- منطق التداول الآلي ---
                # 🟢 شراء: إذا كان السعر "متشبع بيعياً" (RSI تحت 30)
                if state["pos"] is None and rsi < 30:
                    msg = f"🟢 **قرار شراء آلي**\n💰 السعر: `{price}`\n📊 RSI: `{rsi:.2f}`"
                    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                    state["pos"] = "BUY"
                    state["buy_p"] = price

                # 🔴 بيع: إذا كان السعر "متشبع شرائياً" (RSI فوق 70) أو ربح 2%
                elif state["pos"] == "BUY":
                    profit = ((price - state["buy_p"]) / state["buy_p"]) * 100
                    if rsi > 70 or profit >= 2.0:
                        msg = f"🔴 **قرار بيع آلي**\n💰 السعر: `{price}`\n📈 الربح: `%{profit:.2f}`"
                        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                        state["pos"] = None

            except Exception as e:
                print(f"⚠️ تنبيه النظام: {e}")
        
        time.sleep(30) # فحص كل 30 ثانية لضمان الاستقرار

if __name__ == "__main__":
    # تشغيل المحرك في مسار مستقل لضمان عدم توقف التليجرام
    threading.Thread(target=trading_brain, daemon=True).start()
    print("🤖 البوت متصل الآن بنجاح...")
    bot.infinity_polling()
