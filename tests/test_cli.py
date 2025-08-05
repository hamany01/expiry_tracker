 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/tests/test_cli.py
index 0000000000000000000000000000000000000000..f02da7526da0e354e688c09e2c1cc9e458bc5924 100644
--- a//dev/null
+++ b/tests/test_cli.py
@@ -0,0 +1,29 @@
+from pathlib import Path
+import sys
+
+# Ensure project root is on sys.path
+PROJECT_ROOT = Path(__file__).resolve().parents[1]
+if str(PROJECT_ROOT) not in sys.path:
+    sys.path.insert(0, str(PROJECT_ROOT))
+
+import cli
+
+
+def test_cli_add_and_list(tmp_path, capsys):
+    db_file = tmp_path / "vehicles.db"
+    cli.main(["init", "--db", str(db_file)])
+    cli.main(
+        [
+            "add",
+            "Car A",
+            "ABC123",
+            "2025-01-01",
+            "2025-06-01",
+            "--db",
+            str(db_file),
+        ]
+    )
+    cli.main(["list", "--db", str(db_file)])
+    captured = capsys.readouterr()
+    assert "Car A" in captured.out
+    assert "ABC123" in captured.out
 
EOF
)
