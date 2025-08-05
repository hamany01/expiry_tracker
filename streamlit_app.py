 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/app.py
index 0000000000000000000000000000000000000000..100c65b7171565a8f1eda94c8595b54c7f759249 100644
--- a//dev/null
+++ b/app.py
@@ -0,0 +1,42 @@
+import streamlit as st
+import database
+
+def main() -> None:
+    """Streamlit interface for vehicle expiration tracking."""
+    database.initialize()
+
+    st.title("Vehicle Expiration Tracker")
+
+    with st.form("add_vehicle"):
+        name = st.text_input("Vehicle Name")
+        plate = st.text_input("Plate Number")
+        registration = st.date_input("Registration Expiry")
+        insurance = st.date_input("Insurance Expiry")
+        submitted = st.form_submit_button("Add Vehicle")
+
+        if submitted:
+            database.add_vehicle(
+                name,
+                plate,
+                registration.isoformat(),
+                insurance.isoformat(),
+            )
+            st.success("Vehicle added")
+
+    st.header("Registered Vehicles")
+    vehicles = database.get_all_vehicles()
+    if vehicles:
+        st.table(
+            {
+                "Name": [v[0] for v in vehicles],
+                "Plate": [v[1] for v in vehicles],
+                "Registration": [v[2] for v in vehicles],
+                "Insurance": [v[3] for v in vehicles],
+            }
+        )
+    else:
+        st.info("No vehicles available")
+
+
+if __name__ == "__main__":
+    main()
 
EOF
)
