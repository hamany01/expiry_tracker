 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/database.py
index 0000000000000000000000000000000000000000..fd17f39215d906105abacb76bc5855c73dc63917 100644
--- a//dev/null
+++ b/database.py
@@ -0,0 +1,66 @@
+import sqlite3
+from pathlib import Path
+from typing import Iterable, Tuple
+
+DEFAULT_DB_PATH = Path("vehicle_expirations.db")
+
+
+def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
+    """Return a connection to the database located at ``db_path``."""
+    return sqlite3.connect(db_path)
+
+
+def initialize(db_path: Path = DEFAULT_DB_PATH) -> None:
+    """Create the vehicles table if it does not already exist."""
+    conn = get_connection(db_path)
+    cur = conn.cursor()
+    cur.execute(
+        """
+        CREATE TABLE IF NOT EXISTS vehicles (
+            id INTEGER PRIMARY KEY AUTOINCREMENT,
+            name TEXT NOT NULL,
+            plate_number TEXT NOT NULL UNIQUE,
+            registration_expiry DATE,
+            insurance_expiry DATE
+        )
+        """
+    )
+    conn.commit()
+    conn.close()
+
+
+def add_vehicle(
+    name: str,
+    plate_number: str,
+    registration_expiry: str,
+    insurance_expiry: str,
+    db_path: Path = DEFAULT_DB_PATH,
+) -> None:
+    """Insert a new vehicle record into the database."""
+    conn = get_connection(db_path)
+    cur = conn.cursor()
+    cur.execute(
+        """
+        INSERT INTO vehicles (name, plate_number, registration_expiry, insurance_expiry)
+        VALUES (?, ?, ?, ?)
+        """,
+        (name, plate_number, registration_expiry, insurance_expiry),
+    )
+    conn.commit()
+    conn.close()
+
+
+def get_all_vehicles(db_path: Path = DEFAULT_DB_PATH) -> Iterable[Tuple[str, str, str, str]]:
+    """Return all vehicle records."""
+    conn = get_connection(db_path)
+    cur = conn.cursor()
+    cur.execute(
+        "SELECT name, plate_number, registration_expiry, insurance_expiry FROM vehicles"
+    )
+    rows = cur.fetchall()
+    conn.close()
+    return rows
+
+
+if __name__ == "__main__":
+    initialize()
 
EOF
)
