import os
import time
import threading
import telebot
import ccxt # المكتبة العالمية القوية
import pandas as pd
import ta

# الإعدادات
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)

# إعداد الربط مع بينانس باستخدام CCXT لتجنب مشاكل الموقع
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {'adjustForTimeDifference': True}
})

def trading_engine():
    print("🚀 انطلاق المحرك المطور لتخطي الحظر...")
    while True:
        try:
            # جلب البيانات بطريقة CCXT المستقرة
            ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='15m', limit=100)
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            # حساب RSI
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)
            rsi = df['rsi'].iloc[-1]
            price = df['close'].iloc[-1]

            if rsi < 30:
                bot.send_message(CHAT_ID, f"🟢 **إشارة شراء**\nالسعر: `{price}`\nRSI: `{rsi:.2f}`")
            elif rsi > 70:
                bot.send_message(CHAT_ID, f"🔴 **إشارة بيع**\nالسعر: `{price}`")

        except Exception as e:
            print(f"⚠️ تنبيه الاتصال: {e}")
            # إذا استمر الحظر، سنخبرك فوراً
            if "restricted" in str(e).lower():
                 print("🚨 لا يزال بينانس يحظر هذا السيرفر.")
        
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=trading_engine, daemon=True).start()
    bot.infinity_polling()
