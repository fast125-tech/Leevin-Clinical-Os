import sys
import os
from io import BytesIO
from logic.role_workflows import QAWorkflows

sys.path.append(os.getcwd())

print("🔎 TESTING QA MIGRATION (eTMF)...")
print("-" * 60)

# Mock File
f = BytesIO(b"dummy")
f.name = "Site_101_Lab_Results.pdf"

# Test Filing
res = QAWorkflows.audit_and_file_document(f)

print(f"Input: {f.name}")
print(f"Result Status: {res['Status']}")
print(f"Filed Name: {res['NewName']}")
print(f"Zone: {res['Zone']}")

if res["Status"] == "Filed" and "ZONE_10_LABS" in res["Zone"]:
    print("\n✅ MIGRATION SUCCESS: QA Role is handling eTMF.")
else:
    print("\n❌ MIGRATION FAILED.")
