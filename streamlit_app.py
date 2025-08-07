
import streamlit as st
import pandas as pd
import datetime
from database import initialize, get_all_vehicles, add_vehicle, update_vehicle, delete_vehicle
from utils import color_row, save_to_excel, VEHICLE_COLUMNS_AR

st.set_page_config(page_title="لوحة متابعة السيارات", layout="wide")
initialize()

st.sidebar.title("🚗 لوحة التحكم")
page = st.sidebar.radio("اختر الصفحة", ["📊 لوحة التحكم", "📁 إدارة السيارات", "📤 تصدير البيانات"])

if page == "📊 لوحة التحكم":
    st.title("📊 لوحة تحكم السيارات")
    df = pd.DataFrame(get_all_vehicles(), columns=VEHICLE_COLUMNS_AR)

    if df.empty:
        st.info("لا توجد بيانات لعرضها.")
    else:
        today = datetime.date.today()
        df["انتهاء الاستمارة"] = pd.to_datetime(df["انتهاء الاستمارة"]).dt.date
        df["انتهاء التأمين"] = pd.to_datetime(df["انتهاء التأمين"]).dt.date

        expired = df[(df["انتهاء الاستمارة"] < today) | (df["انتهاء التأمين"] < today)]
        near_expiry = df[
            ((df["انتهاء الاستمارة"] - today).dt.days <= 30)
            | ((df["انتهاء التأمين"] - today).dt.days <= 30)
        ]

        st.metric("إجمالي السيارات", len(df))
        st.metric("منتهية", len(expired))
        st.metric("قريبة من الانتهاء", len(near_expiry))

        styled_df = df.style.apply(color_row, axis=1)
        st.dataframe(styled_df, use_container_width=True)

elif page == "📁 إدارة السيارات":
    st.title("📁 إدارة السيارات")
    df = pd.DataFrame(get_all_vehicles(), columns=VEHICLE_COLUMNS_AR)
    with st.expander("➕ إضافة سيارة جديدة"):
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("اسم السيارة")
            plate = st.text_input("رقم اللوحة")
            reg = st.date_input("تاريخ انتهاء الاستمارة")
            ins = st.date_input("تاريخ انتهاء التأمين")
            submitted = st.form_submit_button("إضافة")
            if submitted:
                add_vehicle(name, plate, str(reg), str(ins))
                st.success("✅ تم إضافة السيارة بنجاح.")
                st.rerun()

    if df.empty:
        st.warning("⚠️ لا توجد سيارات حالياً.")
    else:
        selected = st.selectbox("اختر السيارة للتعديل أو الحذف", df["رقم اللوحة"])
        selected_row = df[df["رقم اللوحة"] == selected].iloc[0]

        with st.form("edit_form"):
            new_name = st.text_input("اسم السيارة", value=selected_row["اسم السيارة"])
            new_reg = st.date_input("تاريخ الاستمارة", value=selected_row["انتهاء الاستمارة"])
            new_ins = st.date_input("تاريخ التأمين", value=selected_row["انتهاء التأمين"])
            updated = st.form_submit_button("💾 تحديث")
            if updated:
                update_vehicle(new_name, selected, str(new_reg), str(new_ins))
                st.success("✅ تم التحديث.")
                st.rerun()

        if st.button("🗑️ حذف السيارة"):
            delete_vehicle(selected)
            st.success("🚮 تم الحذف.")
            st.rerun()

        st.subheader("📋 جميع السيارات")
        st.dataframe(df, use_container_width=True)

elif page == "📤 تصدير البيانات":
    st.title("📤 تصدير البيانات إلى Excel")
    df = pd.DataFrame(get_all_vehicles(), columns=VEHICLE_COLUMNS_AR)
    if df.empty:
        st.warning("⚠️ لا توجد بيانات.")
    else:
        file = save_to_excel(df)
        with open(file, "rb") as f:
            st.download_button("⬇️ تحميل ملف Excel", f, file_name="vehicles.xlsx")
