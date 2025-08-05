 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/tests/test_database.py
index 0000000000000000000000000000000000000000..061b2e5467b1dac9d8ae2fd4395f8fe0a9e4aa6b 100644
--- a//dev/null
+++ b/tests/test_database.py
@@ -0,0 +1,28 @@
+from pathlib import Path
+import sys
+
+# Ensure the project root is on sys.path for module imports
+PROJECT_ROOT = Path(__file__).resolve().parents[1]
+if str(PROJECT_ROOT) not in sys.path:
+    sys.path.insert(0, str(PROJECT_ROOT))
+
+import database
+
+
+def test_initialize_creates_db(tmp_path):
+    db_file = tmp_path / "vehicles.db"
+    database.initialize(db_file)
+    assert db_file.exists(), "Database file should be created"
+
+
+def test_add_and_retrieve_vehicle(tmp_path):
+    db_file = tmp_path / "vehicles.db"
+    database.initialize(db_file)
+    database.add_vehicle("Car A", "ABC123", "2025-01-01", "2025-06-01", db_path=db_file)
+    vehicles = list(database.get_all_vehicles(db_path=db_file))
+    assert len(vehicles) == 1
+    name, plate, registration_expiry, insurance_expiry = vehicles[0]
+    assert name == "Car A"
+    assert plate == "ABC123"
+    assert registration_expiry == "2025-01-01"
+    assert insurance_expiry == "2025-06-01"
 
EOF
)
