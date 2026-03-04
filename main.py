from binance.client import Client

# جلب مفاتيح بينانس من الإعدادات السرية في Render
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# الاتصال ببينانس
client = Client(api_key, api_secret)

# إضافة أمر تليجرام لمعرفة الرصيد
@bot.message_handler(commands=['balance'])
def get_balance(message):
    try:
        # جلب رصيد USDT كمثال
        balance = client.get_asset_balance(asset='USDT')
        free_amount = balance['free']
        bot.reply_to(message, f"💰 رصيدك الحالي في محفظة USDT هو: {free_amount}")
    except Exception as e:
        bot.reply_to(message, "❌ فشل الاتصال ببينانس. تأكد من صحة المفاتيح.")

# تحديث واجهة الموقع لعرض الرصيد أيضاً
st.sidebar.subheader("محفظة بينانس")
if api_key:
    try:
        res = client.get_asset_balance(asset='USDT')
        st.sidebar.metric("رصيد USDT", res['free'])
    except:
        st.sidebar.error("خطأ في الاتصال")
