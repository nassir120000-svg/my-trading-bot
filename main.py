import os
import time
import threading
import telebot
from binance.client import Client
import pandas as pd
import ta  # المكتبة الخفيفة والبديلة

# --- جلب البيانات من البيئة ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)
client = Client(API_KEY, API_SECRET)

# ذاكرة البوت
state = {"is_trading": True, "symbol": "BTCUSDT", "position": None, "buy_price": 0.0}

def trading_engine():
    print("🤖 المحرك الذكي بدأ العمل...")
    while True:
        if state["is_trading"]:
            try:
                # جلب البيانات من بينانس
                bars = client.get_klines(symbol=state["symbol"], interval=Client.KLINE_INTERVAL_15MINUTE, limit=100)
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'ct', 'qv', 'nt', 'tb', 'tv', 'i'])
                df['close'] = df['close'].astype(float)
                
                # حساب RSI بمكتبة ta الخفيفة
                df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
                
                curr_rsi = df['rsi'].iloc[-1]
                curr_price = df['close'].iloc[-1]

                # منطق التداول (شراء تحت 30، بيع فوق 70 أو ربح 2%)
                if state["position"] is None and curr_rsi < 30:
                    bot.send_message(CHAT_ID, f"🟢 **إشارة شراء ذكية**\nالسعر: `{curr_price}`\nRSI: `{curr_rsi:.2f}`")
                    state["position"] = "BUY"
                    state["buy_price"] = curr_price

                elif state["position"] == "BUY":
                    profit = ((curr_price - state["buy_price"]) / state["buy_price"]) * 100
                    if curr_rsi > 70 or profit >= 2.0:
                        bot.send_message(CHAT_ID, f"🔴 **إشارة بيع ذكية**\nالسعر: `{curr_price}`\nالربح: `%{profit:.2f}`")
                        state["position"] = None

            except Exception as e:
                print(f"⚠️ تنبيه: {e}")
        time.sleep(30)

if __name__ == "__main__":
    # تشغيل المحرك في الخلفية
    threading.Thread(target=trading_engine, daemon=True).start()
    print("🚀 البوت متصل الآن بتليجرام...")
    bot.infinity_polling()
