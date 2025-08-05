 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/database.py
index 0000000000000000000000000000000000000000..d790b01c0c58d48c32868692c6f6523be4645bf2 100644
--- a//dev/null
+++ b/database.py
@@ -0,0 +1,58 @@
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
+    with get_connection(db_path) as conn:
+        conn.execute(
+            """
+            CREATE TABLE IF NOT EXISTS vehicles (
+                id INTEGER PRIMARY KEY AUTOINCREMENT,
+                name TEXT NOT NULL,
+                plate_number TEXT NOT NULL UNIQUE,
+                registration_expiry DATE,
+                insurance_expiry DATE
+            )
+            """
+        )
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
+    with get_connection(db_path) as conn:
+        conn.execute(
+            """
+            INSERT INTO vehicles (name, plate_number, registration_expiry, insurance_expiry)
+            VALUES (?, ?, ?, ?)
+            """,
+            (name, plate_number, registration_expiry, insurance_expiry),
+        )
+
+
+def get_all_vehicles(db_path: Path = DEFAULT_DB_PATH) -> Iterable[Tuple[str, str, str, str]]:
+    """Return all vehicle records."""
+    with get_connection(db_path) as conn:
+        cur = conn.execute(
+            "SELECT name, plate_number, registration_expiry, insurance_expiry FROM vehicles"
+        )
+        rows = cur.fetchall()
+    return rows
+
+
+if __name__ == "__main__":
+    initialize()
 
EOF
)
