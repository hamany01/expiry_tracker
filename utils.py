
import pandas as pd
import tempfile
import os

VEHICLE_COLUMNS_AR = ["اسم السيارة", "رقم اللوحة", "انتهاء الاستمارة", "انتهاء التأمين"]

def color_row(row):
    today = pd.to_datetime("today").date()
    reg = row["انتهاء الاستمارة"]
    ins = row["انتهاء التأمين"]
    
    if isinstance(reg, str):
        reg = pd.to_datetime(reg).date()
    if isinstance(ins, str):
        ins = pd.to_datetime(ins).date()
    
    color = ""
    if reg < today or ins < today:
        color = "background-color: #ffcccc;"
    elif (reg - today).days <= 30 or (ins - today).days <= 30:
        color = "background-color: #fff3cd;"
    else:
        color = "background-color: #d4edda;"
    return [color] * len(row)

def save_to_excel(df):
    temp_dir = tempfile.gettempdir()
    output = os.path.join(temp_dir, "vehicles_export.xlsx")
    df.to_excel(output, index=False)
    return output
