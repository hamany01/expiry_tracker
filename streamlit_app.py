
import streamlit as st
import pandas as pd
import datetime
from database import (initialize, get_all_vehicles, add_vehicle,
                      update_vehicle, delete_vehicle, search_vehicles,
                      get_vehicles_by_status, backup_data, restore_data)
from utils import (color_row, save_to_excel, VEHICLE_COLUMNS_AR,
                   get_expiry_notifications, create_status_chart,
                   create_expiry_timeline)



st.set_page_config(page_title="لوحة متابعة السيارات", layout="wide")
initialize()

st.sidebar.title("🚗 لوحة التحكم")
page = st.sidebar.radio("اختر الصفحة",
                        ["📊 لوحة التحكم", "📁 إدارة السيارات",
                         "📤 تصدير البيانات", "🔔 الإشعارات",
                         "💾 النسخ الاحتياطي"])

if page == "📊 لوحة التحكم":
    st.title("📊 لوحة تحكم السيارات")

    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 البحث عن سيارة (الاسم أو رقم اللوحة)")
    with col2:
        filter_status = st.selectbox("فلترة حسب الحالة",
                                     ["الكل", "منتهية", "قريبة من الانتهاء", "صالحة"])

    if search_term:
        try:
            vehicles_data = search_vehicles(search_term)
        except ValueError as e:
            st.error(str(e))
            vehicles_data = []
    elif filter_status == "منتهية":
        try:
            vehicles_data = get_vehicles_by_status("expired")
        except ValueError as e:
            st.error(str(e))
            vehicles_data = []
    elif filter_status == "قريبة من الانتهاء":
        try:
            vehicles_data = get_vehicles_by_status("near_expiry")
        except ValueError as e:
            st.error(str(e))
            vehicles_data = []
    else:
        vehicles_data = get_all_vehicles()
    
    df = pd.DataFrame(vehicles_data, columns=VEHICLE_COLUMNS_AR)
    if not df.empty:
        df["انتهاء الاستمارة"] = pd.to_datetime(df["انتهاء الاستمارة"])
        df["انتهاء التأمين"] = pd.to_datetime(df["انتهاء التأمين"])

    if df.empty:
        st.info("لا توجد بيانات لعرضها.")
    else:
        today = pd.Timestamp.now().normalize()
        df["انتهاء الاستمارة"] = pd.to_datetime(df["انتهاء الاستمارة"])
        df["انتهاء التأمين"] = pd.to_datetime(df["انتهاء التأمين"])

        expired = df[(df["انتهاء الاستمارة"] < today) |
                     (df["انتهاء التأمين"] < today)]
        near_expiry = df[
            (((df["انتهاء الاستمارة"] - today).dt.days <= 30) &
             ((df["انتهاء الاستمارة"] - today).dt.days >= 0)) |
            (((df["انتهاء التأمين"] - today).dt.days <= 30) &
             ((df["انتهاء التأمين"] - today).dt.days >= 0))
        ]
        valid = df[
            ((df["انتهاء الاستمارة"] - today).dt.days > 30) &
            ((df["انتهاء التأمين"] - today).dt.days > 30)
        ]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("إجمالي السيارات", len(df))
        with col2:
            st.metric("منتهية", len(expired),
                      delta=f"-{len(expired)}" if len(expired) > 0 else None)
        with col3:
            st.metric("قريبة من الانتهاء", len(near_expiry),
                      delta=f"⚠️ {len(near_expiry)}" if len(near_expiry) > 0 else None)
        with col4:
            st.metric("صالحة", len(valid),
                      delta=f"✅ {len(valid)}" if len(valid) > 0 else None)

        col1, col2 = st.columns(2)
        with col1:
            chart = create_status_chart(df)
            if chart:
                st.plotly_chart(chart, use_container_width=True)

        with col2:
            timeline = create_expiry_timeline(df)
            if timeline:
                st.plotly_chart(timeline, use_container_width=True)

        st.subheader("📋 جدول السيارات")
        styled_df = df.style.apply(color_row, axis=1)
        st.dataframe(styled_df, use_container_width=True)

elif page == "📁 إدارة السيارات":
    st.title("📁 إدارة السيارات")
    df = pd.DataFrame(get_all_vehicles(), columns=VEHICLE_COLUMNS_AR)

    with st.expander("➕ إضافة سيارة جديدة", expanded=True):
        with st.form("add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("اسم السيارة *", placeholder="مثال: تويوتا كامري")
                reg = st.date_input("تاريخ انتهاء الاستمارة *")
            with col2:
                plate = st.text_input("رقم اللوحة *",
                                      placeholder="مثال: أ ب ج 123")
                ins = st.date_input("تاريخ انتهاء التأمين *")

            submitted = st.form_submit_button("➕ إضافة السيارة",
                                              use_container_width=True)
            if submitted:
                if not name or not plate:
                    st.error("⚠️ يرجى ملء جميع الحقول المطلوبة")
                else:
                    try:
                        add_vehicle(name.strip(), plate.strip(),
                                    str(reg), str(ins))
                        st.success("✅ تم إضافة السيارة بنجاح.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

    if df.empty:
        st.warning("⚠️ لا توجد سيارات حالياً.")
    else:
        st.subheader("✏️ تعديل أو حذف سيارة")
        selected = st.selectbox(
            "اختر السيارة للتعديل أو الحذف",
            df["رقم اللوحة"],
            format_func=lambda x: f"{df[df['رقم اللوحة'] == x]['اسم السيارة'].iloc[0]} - {x}"
        )
        selected_row = df[df["رقم اللوحة"] == selected].iloc[0]

        col1, col2 = st.columns([3, 1])
        with col1:
            with st.form("edit_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    new_name = st.text_input("اسم السيارة",
                                             value=selected_row["اسم السيارة"])
                    new_reg = st.date_input("تاريخ الاستمارة",
                                            value=selected_row["انتهاء الاستمارة"])
                with col_b:
                    st.text_input("رقم اللوحة", value=selected, disabled=True)
                    new_ins = st.date_input("تاريخ التأمين",
                                            value=selected_row["انتهاء التأمين"])

                updated = st.form_submit_button("💾 تحديث السيارة",
                                                use_container_width=True)
                if updated:
                    if not new_name:
                        st.error("⚠️ اسم السيارة مطلوب")
                    else:
                        try:
                            update_vehicle(new_name.strip(), selected,
                                           str(new_reg), str(new_ins))
                            st.success("✅ تم التحديث بنجاح.")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

        with col2:
            st.write("")
            st.write("")
            if st.button("🗑️ حذف السيارة", use_container_width=True,
                         type="secondary"):
                if st.session_state.get('confirm_delete') != selected:
                    st.session_state.confirm_delete = selected
                    st.warning("⚠️ انقر مرة أخرى للتأكيد")
                else:
                    try:
                        delete_vehicle(selected)
                        st.success("🚮 تم حذف السيارة بنجاح.")
                        if 'confirm_delete' in st.session_state:
                            del st.session_state.confirm_delete
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

        st.subheader("📋 جميع السيارات")
        styled_df = df.style.apply(color_row, axis=1)
        st.dataframe(styled_df, use_container_width=True)

elif page == "📤 تصدير البيانات":
    st.title("📤 تصدير البيانات")
    df = pd.DataFrame(get_all_vehicles(), columns=VEHICLE_COLUMNS_AR)

    if df.empty:
        st.warning("⚠️ لا توجد بيانات للتصدير.")
    else:
        st.subheader("📊 معاينة البيانات")
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📥 تصدير إلى Excel")
            st.write(f"📋 عدد السيارات: {len(df)}")

            try:
                file = save_to_excel(df)
                with open(file, "rb") as f:
                    st.download_button(
                        "⬇️ تحميل ملف Excel",
                        f,
                        file_name=f"vehicles_{datetime.date.today().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except ValueError as e:
                st.error(str(e))

        with col2:
            st.subheader("📤 استيراد من Excel")
            uploaded_file = st.file_uploader("اختر ملف Excel",
                                              type=['xlsx', 'xls'])

            if uploaded_file is not None:
                try:
                    import_df = pd.read_excel(uploaded_file)
                    st.write("📋 معاينة البيانات المستوردة:")
                    st.dataframe(import_df.head(), use_container_width=True)

                    if st.button("📥 استيراد البيانات",
                                 use_container_width=True):
                        imported_count = 0
                        errors = []

                        for _, row in import_df.iterrows():
                            try:
                                if len(row) >= 4:
                                    add_vehicle(str(row.iloc[0]), str(row.iloc[1]),
                                                str(row.iloc[2]), str(row.iloc[3]))
                                    imported_count += 1
                            except Exception as e:
                                errors.append(f"الصف {_ + 1}: {str(e)}")

                        if imported_count > 0:
                            st.success(f"✅ تم استيراد {imported_count} سيارة بنجاح.")
                        if errors:
                            st.warning(f"⚠️ {len(errors)} أخطاء في الاستيراد:")
                            for error in errors[:5]:
                                st.write(f"• {error}")

                        if imported_count > 0:
                            st.rerun()

                except Exception as e:
                    st.error(f"خطأ في قراءة الملف: {str(e)}")

elif page == "🔔 الإشعارات":
    st.title("🔔 إشعارات انتهاء الصلاحية")
    df = pd.DataFrame(get_all_vehicles(), columns=VEHICLE_COLUMNS_AR)

    if df.empty:
        st.info("لا توجد سيارات للتحقق من إشعاراتها.")
    else:
        notifications = get_expiry_notifications(df)

        if not notifications:
            st.success("🎉 لا توجد إشعارات! جميع السيارات في حالة جيدة.")
        else:
            expired_notifications = [n for n in notifications
                                      if n["type"] == "expired"]
            urgent_notifications = [n for n in notifications
                                    if n["type"] == "urgent"]
            warning_notifications = [n for n in notifications
                                     if n["type"] == "warning"]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔴 منتهية الصلاحية", len(expired_notifications))
            with col2:
                st.metric("🟠 عاجلة (أقل من 7 أيام)",
                          len(urgent_notifications))
            with col3:
                st.metric("🟡 تحذيرية (أقل من 30 يوم)",
                          len(warning_notifications))

            if expired_notifications:
                st.subheader("🔴 إشعارات منتهية الصلاحية")
                for notif in expired_notifications:
                    st.error(notif["message"])

            if urgent_notifications:
                st.subheader("🟠 إشعارات عاجلة")
                for notif in urgent_notifications:
                    st.warning(notif["message"])

            if warning_notifications:
                st.subheader("🟡 إشعارات تحذيرية")
                for notif in warning_notifications:
                    st.info(notif["message"])

elif page == "💾 النسخ الاحتياطي":
    st.title("💾 النسخ الاحتياطي واستعادة البيانات")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📤 إنشاء نسخة احتياطية")
        df = pd.DataFrame(get_all_vehicles(), columns=VEHICLE_COLUMNS_AR)
        st.write(f"📋 عدد السيارات الحالية: {len(df)}")

        if st.button("💾 إنشاء نسخة احتياطية", use_container_width=True):
            try:
                backup_file = backup_data()
                st.success(f"✅ تم إنشاء النسخة الاحتياطية: {backup_file}")

                with open(backup_file, "rb") as f:
                    st.download_button(
                        "⬇️ تحميل النسخة الاحتياطية",
                        f,
                        file_name=backup_file,
                        mime="application/json",
                        use_container_width=True
                    )
            except ValueError as e:
                st.error(str(e))

    with col2:
        st.subheader("📥 استعادة من نسخة احتياطية")
        uploaded_backup = st.file_uploader("اختر ملف النسخة الاحتياطية",
                                            type=['json'])

        if uploaded_backup is not None:
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False,
                                                 suffix='.json') as tmp_file:
                    tmp_file.write(uploaded_backup.getvalue())
                    tmp_file_path = tmp_file.name

                import json
                with open(tmp_file_path, 'r', encoding='utf-8') as f:
                    backup_data_content = json.load(f)

                st.write("📋 معلومات النسخة الاحتياطية:")
                st.write(f"• تاريخ النسخة: {backup_data_content.get('backup_date', 'غير محدد')}")
                st.write(f"• عدد السيارات: {len(backup_data_content.get('vehicles', []))}")

                if st.button("🔄 استعادة البيانات", use_container_width=True):
                    try:
                        restored_count = restore_data(tmp_file_path)
                        st.success(f"✅ تم استعادة {restored_count} سيارة بنجاح.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

            except Exception as e:
                st.error(f"خطأ في قراءة ملف النسخة الاحتياطية: {str(e)}")
