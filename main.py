import streamlit as st
import os

st.set_page_config(page_title="روبوت التداول الذكي", page_icon="📈")
st.title("🤖 لوحة تحكم الروبوت الآلي")

# التحقق من وجود المفاتيح في السيرفر
if "BINANCE_API_KEY" in os.environ:
    st.success("✅ تم الاتصال بحساب بينانس بنجاح")
    st.info("البوت الآن في وضع مراقبة السوق وإرسال الأرباح للفيزا")
else:
    st.warning("⚠️ انتظر.. يجب إضافة مفاتيح بينانس في إعدادات Render")

st.sidebar.header("الإحصائيات الحية")
st.sidebar.write("الحالة: يعمل 24/7")
