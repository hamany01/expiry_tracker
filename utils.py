
import pandas as pd
import plotly.express as px

VEHICLE_COLUMNS_AR = ["اسم السيارة", "رقم اللوحة", "انتهاء الاستمارة", "انتهاء التأمين"]


def color_row(row):
    today = pd.Timestamp.now().normalize()
    reg = pd.to_datetime(row["انتهاء الاستمارة"])
    ins = pd.to_datetime(row["انتهاء التأمين"])
    color = ""
    if reg < today or ins < today:
        color = "background-color: #ffcccc;"
    elif (reg - today).days <= 30 or (ins - today).days <= 30:
        color = "background-color: #fff3cd;"
    else:
        color = "background-color: #d4edda;"
    return [color] * len(row)


def save_to_excel(df):
    try:
        output = "vehicles_export.xlsx"
        df.to_excel(output, index=False)
        return output
    except Exception as e:
        raise ValueError(f"خطأ في تصدير البيانات: {str(e)}")


def get_expiry_notifications(df):
    if df.empty:
        return []

    today = pd.Timestamp.now().normalize()
    notifications = []

    for _, row in df.iterrows():
        reg_expiry = pd.to_datetime(row["انتهاء الاستمارة"])
        ins_expiry = pd.to_datetime(row["انتهاء التأمين"])

        reg_days = (reg_expiry - today).days
        ins_days = (ins_expiry - today).days

        if reg_days < 0:
            notifications.append({
                "type": "expired",
                "message": f"🔴 السيارة {row['اسم السيارة']} - "
                           f"انتهت الاستمارة منذ {abs(reg_days)} يوم",
                "vehicle": row['اسم السيارة'],
                "plate": row['رقم اللوحة']
            })
        elif reg_days <= 7:
            notifications.append({
                "type": "urgent",
                "message": f"🟠 السيارة {row['اسم السيارة']} - "
                           f"تنتهي الاستمارة خلال {reg_days} يوم",
                "vehicle": row['اسم السيارة'],
                "plate": row['رقم اللوحة']
            })
        elif reg_days <= 30:
            notifications.append({
                "type": "warning",
                "message": f"🟡 السيارة {row['اسم السيارة']} - "
                           f"تنتهي الاستمارة خلال {reg_days} يوم",
                "vehicle": row['اسم السيارة'],
                "plate": row['رقم اللوحة']
            })

        if ins_days < 0:
            notifications.append({
                "type": "expired",
                "message": f"🔴 السيارة {row['اسم السيارة']} - "
                           f"انتهى التأمين منذ {abs(ins_days)} يوم",
                "vehicle": row['اسم السيارة'],
                "plate": row['رقم اللوحة']
            })
        elif ins_days <= 7:
            notifications.append({
                "type": "urgent",
                "message": f"🟠 السيارة {row['اسم السيارة']} - "
                           f"ينتهي التأمين خلال {ins_days} يوم",
                "vehicle": row['اسم السيارة'],
                "plate": row['رقم اللوحة']
            })
        elif ins_days <= 30:
            notifications.append({
                "type": "warning",
                "message": f"🟡 السيارة {row['اسم السيارة']} - "
                           f"ينتهي التأمين خلال {ins_days} يوم",
                "vehicle": row['اسم السيارة'],
                "plate": row['رقم اللوحة']
            })

    return notifications


def create_status_chart(df):
    if df.empty:
        return None

    today = pd.Timestamp.now().normalize()
    expired_count = 0
    near_expiry_count = 0
    valid_count = 0

    for _, row in df.iterrows():
        reg_expiry = pd.to_datetime(row["انتهاء الاستمارة"])
        ins_expiry = pd.to_datetime(row["انتهاء التأمين"])

        if reg_expiry < today or ins_expiry < today:
            expired_count += 1
        elif ((reg_expiry - today).days <= 30 or
              (ins_expiry - today).days <= 30):
            near_expiry_count += 1
        else:
            valid_count += 1

    fig = px.pie(
        values=[expired_count, near_expiry_count, valid_count],
        names=["منتهية", "قريبة من الانتهاء", "صالحة"],
        color_discrete_map={
            "منتهية": "#ff6b6b",
            "قريبة من الانتهاء": "#ffd93d",
            "صالحة": "#6bcf7f"
        },
        title="توزيع حالة السيارات"
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        font=dict(size=14),
        showlegend=True,
        height=400
    )

    return fig


def create_expiry_timeline(df):
    if df.empty:
        return None

    timeline_data = []
    today = pd.Timestamp.now().normalize()

    for _, row in df.iterrows():
        reg_expiry = pd.to_datetime(row["انتهاء الاستمارة"])
        ins_expiry = pd.to_datetime(row["انتهاء التأمين"])

        timeline_data.append({
            "السيارة": row['اسم السيارة'],
            "النوع": "استمارة",
            "تاريخ الانتهاء": reg_expiry,
            "الأيام المتبقية": (reg_expiry - today).days
        })

        timeline_data.append({
            "السيارة": row['اسم السيارة'],
            "النوع": "تأمين",
            "تاريخ الانتهاء": ins_expiry,
            "الأيام المتبقية": (ins_expiry - today).days
        })

    timeline_df = pd.DataFrame(timeline_data)
    timeline_df = timeline_df.sort_values("تاريخ الانتهاء")

    fig = px.scatter(
        timeline_df,
        x="تاريخ الانتهاء",
        y="السيارة",
        color="النوع",
        size="الأيام المتبقية",
        hover_data=["الأيام المتبقية"],
        title="الجدول الزمني لانتهاء الصلاحيات"
    )

    fig.update_layout(
        font=dict(size=12),
        height=500,
        xaxis_title="تاريخ الانتهاء",
        yaxis_title="السيارة"
    )

    return fig
