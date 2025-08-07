
import pandas as pd

VEHICLE_COLUMNS_AR = ["اسم السيارة", "رقم اللوحة", "انتهاء الاستمارة", "انتهاء التأمين"]

def color_row(row):
    today = pd.to_datetime("today").date()
    reg = pd.to_datetime(row["انتهاء الاستمارة"]).date()
    ins = pd.to_datetime(row["انتهاء التأمين"]).date()
    color = ""
    if reg < today or ins < today:
        color = "background-color: #ffcccc;"
    elif (reg - today).days <= 30 or (ins - today).days <= 30:
        color = "background-color: #fff3cd;"
    else:
        color = "background-color: #d4edda;"
    return [color] * len(row)

def save_to_excel(df):
    output = "/mnt/data/vehicles_export.xlsx"
    df.to_excel(output, index=False)
    return output
