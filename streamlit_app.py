import streamlit as st
import pandas as pd
from datetime import datetime
from database import initialize, add_vehicle, get_all_vehicles

# --- تهيئة قاعدة البيانات ---
initialize()

# --- دالة لحساب الفرق بالأيام ---
def days_until(date_str):
    if not date_str or date_str.strip() == "":
        return None
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return (date - datetime.today()).days
    except Exception:
        return None

st.title("متابعة تواريخ انتهاء السيارات")

# --- نموذج إضافة سيارة جديدة ---
st.header("إضافة سيارة جديدة")
with st.form("add_vehicle_form"):
    name = st.text_input("اسم السيارة / المالك")
    plate_number = st.text_input("رقم اللوحة")
    registration_expiry = st.date_input("تاريخ انتهاء الاستمارة")
    insurance_expiry = st.date_input("تاريخ انتهاء التأمين")
    submitted = st.form_submit_button("إضافة")
    if submitted:
        if name and plate_number:
            add_vehicle(
                name,
                plate_number,
                str(registration_expiry),
                str(insurance_expiry)
            )
            st.success("تمت إضافة السيارة بنجاح!")
        else:
            st.error("يجب إدخال اسم السيارة ورقم اللوحة على الأقل")

# --- عرض جميع السيارات ---
st.header("قائمة السيارات")
vehicles = get_all_vehicles()
if vehicles and len(vehicles) > 0:
    try:
        df = pd.DataFrame(
            vehicles,
            columns=["اسم السيارة", "رقم اللوحة", "انتهاء الاستمارة", "انتهاء التأمين"]
        )

        # --- إضافة عمودين لعدد الأيام المتبقية ---
        df["أيام متبقية للاستمار"] = df["انتهاء الاستمارة"].apply(days_until)
        df["أيام متبقية للتأمين"] = df["انتهاء التأمين"].apply(days_until)

        # --- تلوين الخلايا التي أقل من 30 يوم ---
        def highlight_expiry(val):
            if val is None:
                return ""
            if isinstance(val, int) and val <= 30:
                return "background-color: red; color: white;"
            return ""

        styled_df = df.style.applymap(highlight_expiry, subset=["أيام متبقية للاستمار", "أيام متبقية للتأمين"])
        st.dataframe(styled_df, use_container_width=True)
    except Exception as e:
        st.error(f"خطأ في إنشاء الجدول: {e}")
else:
    st.info("لا توجد بيانات سيارات حتى الآن.")
