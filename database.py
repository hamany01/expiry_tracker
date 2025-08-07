
import sqlite3
from pathlib import Path
import datetime
import pandas as pd

DB_FILE = Path("vehicle_expirations.db")


def get_conn():
    return sqlite3.connect(DB_FILE)


def initialize():
    with get_conn() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            plate_number TEXT UNIQUE,
            registration_expiry TEXT,
            insurance_expiry TEXT
        )""")


# Full vehicle table with detailed fields
FULL_VEHICLE_COLUMNS = [
    "plate_number",
    "registration_type",
    "branch",
    "brand",
    "model",
    "manufacture_year",
    "serial_number",
    "chassis_number",
    "base_color",
    "vehicle_status1",
    "ownership_date1",
    "license_expiry",
    "inspection_expiry",
    "actual_user_id",
    "actual_user_name",
    "inspection_status",
    "insurance_status",
    "custody_status",
    "ownership_date2",
    "vehicle_status2",
    "body_type",
]


def initialize_full():
    """Create detailed vehicle table if it does not exist."""
    with get_conn() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS vehicles_full (
            plate_number TEXT PRIMARY KEY,
            registration_type TEXT,
            branch TEXT,
            brand TEXT,
            model TEXT,
            manufacture_year INTEGER,
            serial_number TEXT,
            chassis_number TEXT,
            base_color TEXT,
            vehicle_status1 TEXT,
            ownership_date1 TEXT,
            license_expiry TEXT,
            inspection_expiry TEXT,
            actual_user_id TEXT,
            actual_user_name TEXT,
            inspection_status TEXT,
            insurance_status TEXT,
            custody_status TEXT,
            ownership_date2 TEXT,
            vehicle_status2 TEXT,
            body_type TEXT
        )"""
        )


def add_vehicle(name, plate, reg_expiry, ins_expiry):
    try:
        if not name or not plate:
            raise ValueError("اسم السيارة ورقم اللوحة مطلوبان")
        with get_conn() as conn:
            conn.execute("""INSERT INTO vehicles
                         (name, plate_number, registration_expiry, insurance_expiry)
                         VALUES (?, ?, ?, ?)""",
                         (name, plate, reg_expiry, ins_expiry))
            return True
    except sqlite3.IntegrityError:
        raise ValueError("رقم اللوحة موجود مسبقاً")
    except Exception as e:
        raise ValueError(f"خطأ في إضافة السيارة: {str(e)}")


def get_all_vehicles():
    try:
        with get_conn() as conn:
            return conn.execute("""SELECT name, plate_number,
                                 registration_expiry, insurance_expiry
                                 FROM vehicles""").fetchall()
    except Exception as e:
        raise ValueError(f"خطأ في جلب البيانات: {str(e)}")


def update_vehicle(name, plate, reg_expiry, ins_expiry):
    try:
        if not name or not plate:
            raise ValueError("اسم السيارة ورقم اللوحة مطلوبان")
        with get_conn() as conn:
            cursor = conn.execute("""UPDATE vehicles
                         SET name = ?, registration_expiry = ?, insurance_expiry = ?
                         WHERE plate_number = ?""",
                         (name, reg_expiry, ins_expiry, plate))
            if cursor.rowcount == 0:
                raise ValueError("السيارة غير موجودة")
            return True
    except Exception as e:
        raise ValueError(f"خطأ في تحديث السيارة: {str(e)}")


def delete_vehicle(plate):
    try:
        with get_conn() as conn:
            cursor = conn.execute("DELETE FROM vehicles WHERE plate_number = ?",
                                 (plate,))
            if cursor.rowcount == 0:
                raise ValueError("السيارة غير موجودة")
            return True
    except Exception as e:
        raise ValueError(f"خطأ في حذف السيارة: {str(e)}")


def search_vehicles(search_term):
    try:
        with get_conn() as conn:
            return conn.execute(
                """SELECT name, plate_number, registration_expiry, insurance_expiry
                   FROM vehicles WHERE name LIKE ? OR plate_number LIKE ?""",
                (f"%{search_term}%", f"%{search_term}%")
            ).fetchall()
    except Exception as e:
        raise ValueError(f"خطأ في البحث: {str(e)}")


def get_vehicles_by_status(status):
    try:
        today = datetime.date.today().strftime('%Y-%m-%d')
        with get_conn() as conn:
            if status == "expired":
                return conn.execute("""SELECT name, plate_number,
                                     registration_expiry, insurance_expiry
                                     FROM vehicles
                                     WHERE registration_expiry < ? OR
                                     insurance_expiry < ?""",
                                     (today, today)).fetchall()
            elif status == "near_expiry":
                future_date = (datetime.date.today() +
                               datetime.timedelta(days=30)).strftime('%Y-%m-%d')
                return conn.execute("""SELECT name, plate_number,
                                     registration_expiry, insurance_expiry
                                     FROM vehicles
                                     WHERE (registration_expiry BETWEEN ? AND ?)
                                     OR (insurance_expiry BETWEEN ? AND ?)""",
                                     (today, future_date, today,
                                      future_date)).fetchall()
            else:
                return get_all_vehicles()
    except Exception as e:
        raise ValueError(f"خطأ في فلترة السيارات: {str(e)}")


# ------- Extended table helpers -------


def add_vehicle_full(data):
    """Insert a detailed vehicle record into vehicles_full."""
    try:
        plate = data.get("plate_number")
        if not plate:
            raise ValueError("رقم اللوحة مطلوب")
        columns = ", ".join(FULL_VEHICLE_COLUMNS)
        placeholders = ", ".join(["?"] * len(FULL_VEHICLE_COLUMNS))
        values = [data.get(col) for col in FULL_VEHICLE_COLUMNS]
        with get_conn() as conn:
            conn.execute(
                f"INSERT INTO vehicles_full ({columns}) VALUES ({placeholders})",
                values,
            )
        return True
    except sqlite3.IntegrityError:
        raise ValueError("رقم اللوحة موجود مسبقاً")
    except Exception as e:
        raise ValueError(f"خطأ في إضافة السيارة: {str(e)}")


def update_vehicle_full(plate, data):
    """Update fields for a detailed vehicle."""
    try:
        if not plate:
            raise ValueError("رقم اللوحة مطلوب")
        updates = []
        values = []
        for col in FULL_VEHICLE_COLUMNS:
            if col in data:
                updates.append(f"{col} = ?")
                values.append(data[col])
        if not updates:
            raise ValueError("لا توجد بيانات للتحديث")
        values.append(plate)
        with get_conn() as conn:
            cursor = conn.execute(
                f"UPDATE vehicles_full SET {', '.join(updates)} WHERE plate_number = ?",
                values,
            )
            if cursor.rowcount == 0:
                raise ValueError("السيارة غير موجودة")
        return True
    except Exception as e:
        raise ValueError(f"خطأ في تحديث السيارة: {str(e)}")


def export_full_to_csv(csv_file="vehicles_full_export.csv"):
    """Export the detailed vehicle table to a CSV file."""
    try:
        with get_conn() as conn:
            df = pd.read_sql_query("SELECT * FROM vehicles_full", conn)
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")
        return csv_file
    except Exception as e:
        raise ValueError(f"خطأ في تصدير البيانات: {str(e)}")


def import_full_from_csv(csv_file):
    """Import vehicle records from a CSV file into vehicles_full."""
    try:
        df = pd.read_csv(csv_file)
        imported = 0
        for _, row in df.iterrows():
            data = {col: row.get(col) for col in FULL_VEHICLE_COLUMNS}
            try:
                add_vehicle_full(data)
                imported += 1
            except Exception:
                continue
        return imported
    except Exception as e:
        raise ValueError(f"خطأ في استيراد البيانات: {str(e)}")


def backup_data():
    try:
        import json
        vehicles = get_all_vehicles()
        backup_data = {
            "backup_date": datetime.datetime.now().isoformat(),
            "vehicles": vehicles
        }
        backup_file = f"backup_{datetime.date.today().strftime('%Y%m%d')}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        return backup_file
    except Exception as e:
        raise ValueError(f"خطأ في النسخ الاحتياطي: {str(e)}")


def restore_data(backup_file):
    try:
        import json
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        vehicles = backup_data.get("vehicles", [])
        restored_count = 0
        for vehicle in vehicles:
            try:
                add_vehicle(vehicle[0], vehicle[1], vehicle[2], vehicle[3])
                restored_count += 1
            except Exception:
                continue
        return restored_count
    except Exception as e:
        raise ValueError(f"خطأ في استعادة البيانات: {str(e)}")
