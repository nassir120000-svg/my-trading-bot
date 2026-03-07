import os
import time
import threading
import telebot
from binance.client import Client
import pandas as pd
import ta 

# جلب بياناتك من إعدادات رندر
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)
client = Client(API_KEY, API_SECRET)

# حالة البوت
state = {"active": True, "pos": None, "buy_p": 0.0}

def trading_brain():
    while True:
        if state["active"]:
            try:
                # تحليل السوق (بيتكوين مقابل دولار)
                bars = client.get_klines(symbol="BTCUSDT", interval="15m", limit=100)
                df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'n', 'tb', 'tv', 'i'])
                df['c'] = df['c'].astype(float)
                
                # حساب مؤشر RSI (العقل التحليلي)
                rsi = ta.momentum.rsi(df['c'], window=14).iloc[-1]
                price = df['c'].iloc[-1]

                # قرار الشراء (إذا السعر رخيص RSI < 30)
                if state["pos"] is None and rsi < 30:
                    bot.send_message(CHAT_ID, f"🟢 **شراء آلي الآن**\nالسعر: {price}\nRSI: {rsi:.2f}")
                    state["pos"] = "BUY"
                    state["buy_p"] = price

                # قرار البيع (إذا السعر غالي RSI > 70)
                elif state["pos"] == "BUY" and rsi > 70:
                    profit = ((price - state["buy_p"]) / state["buy_p"]) * 100
                    bot.send_message(CHAT_ID, f"🔴 **بيع آلي الآن**\nالسعر: {price}\nالربح: %{profit:.2f}")
                    state["pos"] = None
            except: pass
        time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=trading_brain, daemon=True).start()
    bot.infinity_polling()
