
import sqlite3
from pathlib import Path
import datetime

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
