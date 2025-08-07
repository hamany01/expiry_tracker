
import sqlite3
from pathlib import Path

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
    with get_conn() as conn:
        conn.execute("""INSERT INTO vehicles (name, plate_number, registration_expiry, insurance_expiry)
                      VALUES (?, ?, ?, ?)""", (name, plate, reg_expiry, ins_expiry))

def get_all_vehicles():
    with get_conn() as conn:
        return conn.execute("""SELECT name, plate_number, registration_expiry, insurance_expiry FROM vehicles""").fetchall()

def update_vehicle(name, plate, reg_expiry, ins_expiry):
    with get_conn() as conn:
        conn.execute("""UPDATE vehicles SET name = ?, registration_expiry = ?, insurance_expiry = ? WHERE plate_number = ?""", (name, reg_expiry, ins_expiry, plate))

def delete_vehicle(plate):
    with get_conn() as conn:
        conn.execute("DELETE FROM vehicles WHERE plate_number = ?", (plate,))
