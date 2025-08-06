import sqlite3
from pathlib import Path
from typing import Iterable, Tuple

DEFAULT_DB_PATH = Path("vehicle_expirations.db")

def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    ...
