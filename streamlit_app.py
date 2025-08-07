
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

DB_PATH = "vehicle_expirations.db"

st.set_page_config(page_title="لوحة التحكم - السيارات", layout="wide")

# قراءة البيانات من SQLite
@st.cache_data
def load_data():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT name, plate_number, registration_expiry, insurance_expiry FROM vehicles", conn)
        df["registration_expiry"] = pd.to_datetime(df["registration_expiry"], errors="coerce")
        df["insurance_expiry"] = pd.to_datetime(df["insurance_expiry"], errors="coerce")
    return df

df = load_data()
today = pd.to_datetime(datetime.now().date())

# --- قائمة تنقل ---
st.sidebar.title("🚗 لوحة التحكم")
page = st.sidebar.radio("اختر الصفحة", ["📊 لوحة التحكم", "📁 إدارة السيارات", "📤 تصدير البيانات"])

# --- لوحة التحكم ---
if page == "📊 لوحة التحكم":
    st.header("📊 لوحة تحكم السيارات")
    col1, col2 = st.columns(2)

    with col1:
        reg_soon = df[df["registration_expiry"].notna() & ((df["registration_expiry"] - today).dt.days <= 30)]
        st.metric("🚨 سيارات تنتهي رخصتها خلال 30 يوم", len(reg_soon))

    with col2:
        ins_soon = df[df["insurance_expiry"].notna() & ((df["insurance_expiry"] - today).dt.days <= 30)]
        st.metric("📅 سيارات ينتهي تأمينها خلال 30 يوم", len(ins_soon))

    st.subheader("جميع السيارات القريبة من الانتهاء")
    st.dataframe(pd.concat([reg_soon, ins_soon]).drop_duplicates().reset_index(drop=True))

# --- إدارة السيارات ---
elif page == "📁 إدارة السيارات":
    st.header("📁 إدارة جميع السيارات")
    search = st.text_input("🔍 ابحث برقم اللوحة أو اسم المستخدم")
    filtered = df[df["plate_number"].str.contains(search, case=False, na=False) | df["name"].str.contains(search, case=False, na=False)]
    st.dataframe(filtered if search else df)

# --- تصدير البيانات ---
elif page == "📤 تصدير البيانات":
    st.header("📤 تصدير البيانات")
    export_df = df.copy()
    csv = export_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 تحميل ملف CSV", csv, "vehicles_export.csv", "text/csv")
