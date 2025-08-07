
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

DB_PATH = "vehicle_expirations.db"

# تحميل البيانات من SQLite
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT name, plate_number, registration_expiry, insurance_expiry FROM vehicles", conn)
    conn.close()
    df["registration_expiry"] = pd.to_datetime(df["registration_expiry"], errors="coerce")
    df["insurance_expiry"] = pd.to_datetime(df["insurance_expiry"], errors="coerce")
    return df

# واجهة التطبيق
st.set_page_config(page_title="لوحة تحكم السيارات", layout="wide")
st.sidebar.title("🚗 لوحة التحكم")
page = st.sidebar.radio("اختر الصفحة", ["📊 لوحة التحكم", "📁 إدارة السيارات", "📤 تصدير البيانات"])

df = load_data()
today = pd.to_datetime(datetime.today().date())

if page == "📊 لوحة التحكم":
    st.title("📊 لوحة تحكم السيارات")
    if df.empty:
        st.warning("لا توجد بيانات للعرض.")
    else:
        soon_expiring_reg = df[df["registration_expiry"].notna() & ((df["registration_expiry"] - today).dt.days <= 30)]
        soon_expiring_ins = df[df["insurance_expiry"].notna() & ((df["insurance_expiry"] - today).dt.days <= 30)]

        col1, col2 = st.columns(2)
        col1.metric("🚨 السيارات التي ستنتهي استمارتها خلال 30 يوم", len(soon_expiring_reg))
        col2.metric("🛡️ السيارات التي سينتهي تأمينها خلال 30 يوم", len(soon_expiring_ins))

        with st.expander("عرض تفاصيل السيارات التي ستنتهي قريباً"):
            st.subheader("استمارات ستنتهي قريباً")
            st.dataframe(soon_expiring_reg)

            st.subheader("تأمينات ستنتهي قريباً")
            st.dataframe(soon_expiring_ins)

elif page == "📁 إدارة السيارات":
    st.title("📁 إدارة السيارات")
    st.dataframe(df)

elif page == "📤 تصدير البيانات":
    st.title("📤 تصدير البيانات")
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 تحميل كملف CSV", data=csv, file_name="vehicles_export.csv", mime="text/csv")
