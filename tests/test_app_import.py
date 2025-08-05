 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/tests/test_app_import.py
index 0000000000000000000000000000000000000000..90fe83a7cb59dc96ef079593f9317eec9950bc43 100644
--- a//dev/null
+++ b/tests/test_app_import.py
@@ -0,0 +1,9 @@
+from pathlib import Path
+import sys
+
+PROJECT_ROOT = Path(__file__).resolve().parents[1]
+if str(PROJECT_ROOT) not in sys.path:
+    sys.path.insert(0, str(PROJECT_ROOT))
+
+def test_app_module_importable():
+    import app  # noqa: F401
 
EOF
)
