import streamlit as st
import pandas as pd
from database import initialize, add_vehicle, get_all_vehicles

# --- تهيئة قاعدة البيانات ---
initialize()

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
if vehicles:
    df = pd.DataFrame(
        vehicles,
        columns=["اسم السيارة", "رقم اللوحة", "انتهاء الاستمارة", "انتهاء التأمين"]
    )
    st.dataframe(df)
else:
    st.info("لا توجد بيانات سيارات حتى الآن.")
