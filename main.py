import os
import time
import threading
import telebot
from telebot import types
from binance.client import Client
import pandas as pd
import ta  # المكتبة الخفيفة والبديلة

# --- الإعدادات ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)
client = Client(API_KEY, API_SECRET)

state = {"is_trading": True, "symbol": "BTCUSDT", "amount_usd": 15.0, "position": None, "buy_price": 0.0, "qty": 0.0}

def trading_engine():
    while True:
        if state["is_trading"]:
            try:
                bars = client.get_klines(symbol=state["symbol"], interval=Client.KLINE_INTERVAL_15MINUTE, limit=100)
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'ct', 'qv', 'nt', 'tb', 'tv', 'i'])
                df['close'] = df['close'].astype(float)
                
                # حساب RSI باستخدام المكتبة الخفيفة ta
                df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
                
                curr_rsi = df['rsi'].iloc[-1]
                curr_price = df['close'].iloc[-1]

                if state["position"] is None and curr_rsi < 30:
                    # تنفيذ شراء حقيقي (بعد التأكد من الصلاحيات)
                    bot.send_message(CHAT_ID, f"🟢 شراء عند سعر: {curr_price}")
                    state["position"] = "BUY"
                    state["buy_price"] = curr_price

                elif state["position"] == "BUY" and curr_rsi > 70:
                    bot.send_message(CHAT_ID, f"🔴 بيع عند سعر: {curr_price}")
                    state["position"] = None

            except Exception as e:
                print(f"Error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=trading_engine, daemon=True).start()
    bot.infinity_polling()
