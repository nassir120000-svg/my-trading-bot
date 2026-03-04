import streamlit as st
import telebot
import threading
import os

# --- 1. الجزء الخاص بواجهة الموقع (ليقبله Render) ---
st.set_page_config(page_title="لوحة تحكم ناصر")
st.title("🤖 لوحة تحكم الروبوت الآلي")
st.sidebar.header("الإحصائيات الحية")
st.write("✅ السيرفر يعمل الآن بنجاح وبانتظار أوامرك على تليجرام.")

# --- 2. الجزء الخاص بمحرك تليجرام (الذي يجعله يرد عليك) ---
TOKEN = "8606223838:AAHhk18b8F_u-jjRi6RxqMAuB3ob08IP18M"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "أهلاً ناصر! تم تشغيل البوت بنجاح من داخل السيرفر وهو مستعد الآن.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"وصلت رسالتك: {message.text}")

# دالة تشغيل البوت في الخلفية
def run_bot():
    bot.infinity_polling()

# --- 3. تشغيل الاثنين معاً في نفس الوقت ---
if __name__ == "__main__":
    # تشغيل محرك تليجرام في "خلفية" البرنامج
    thread = threading.Thread(target=run_bot)
    thread.daemon = True
    thread.start()
    
    # رسالة تأكيد في السجلات
    print("البوت بدأ العمل في الخلفية...")
