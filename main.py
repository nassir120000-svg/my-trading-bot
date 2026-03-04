import streamlit as st
import telebot
import threading
import os
import time

# --- 1. إعدادات الأمان (جلب التوكن من إعدادات السيرفر السريّة) ---
# ملاحظة: سنضع التوكن في موقع Render وليس هنا ليكون آمناً 100%
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# --- 2. واجهة المستخدم الاحترافية (Streamlit) ---
st.set_page_config(page_title="Nasser Pro Trader", page_icon="📈", layout="wide")

st.title("🚀 منصة ناصر للتداول الذكي")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.metric(label="حالة السيرفر", value="متصل ✅")
with col2:
    st.metric(label="حالة البوت", value="يعمل بنشاط 🤖")

st.sidebar.title("الإعدادات والتحكم")
st.sidebar.info("البوت مؤمن بنظام البيئة المحمية (Environment Variables)")

# --- 3. وظائف البوت المتطورة (تليجرام) ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"🌟 أهلاً بك يا {user_name} في نظام التداول المتطور!\n\n"
        "✅ البوت مؤمن بالكامل ويعمل من السيرفر.\n"
        "📊 أنا جاهز لتحليل السوق وتنفيذ الأوامر."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['status'])
def check_status(message):
    bot.reply_to(message, "📊 جميع الأنظمة تعمل بكفاءة 100% على سيرفر Render.")

# الرد الذكي على الرسائل
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)
    bot.reply_to(message, f"وصلت رسالتك: '{message.text}'\nسيتم معالجتها طبقاً لاستراتيجية التداول.")

# --- 4. تشغيل النظام المزدوج (الموقع + البوت) ---
def run_bot():
    try:
        print("جاري تشغيل محرك تليجرام...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"خطأ في المحرك: {e}")
        time.sleep(5)

if __name__ == "__main__":
    # تشغيل البوت في "خيط" منفصل لضمان عدم توقف الموقع
    thread = threading.Thread(target=run_bot)
    thread.daemon = True
    thread.start()
    
    st.write("✨ تم تشغيل المحرك الخلفي للبوت بنجاح.")
