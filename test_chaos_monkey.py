import sys
import os
import pandas as pd
import datetime

# Add root to path
sys.path.append(os.getcwd())

from logic.agent_logic import generate_protocol_draft
from logic.role_workflows import CDMWorkflows, CRAWorkflows, CRCWorkflows, CoderWorkflows

print("🐒 STARTING CHAOS MONKEY TEST (Simulating 'Clumsy' User Input)...")
print("-" * 60)

# SCENARIO 1: The "Empty Input" Writer
print("\n[Case 1] Medical Writer submits empty title:")
try:
    # Logic file will call LLM, but we check if it handled args correctly even if "context" is just whitespace
    res = generate_protocol_draft("Phase 3", "Trial", "", "   ")
    print(f"✅ Result: {str(res)[:50]}... (Handled gracefully)")
except Exception as e:
    print(f"❌ CRASH: {e}")

# SCENARIO 2: The "Bad File" Data Manager
print("\n[Case 2] CDM uploads a Spec file with missing columns:")
try:
    # BAD input: DF missing 'Type' column
    bad_df = pd.DataFrame({"Form": ["F1"], "Field": ["Age"]}) 
    res = CDMWorkflows.generate_synthetic_uat_data(bad_df)
    if not res.empty and "Error" in res.columns:
        print(f"✅ Graceful Error Caught: '{res.iloc[0]['Error']}'")
    else:
        print(f"⚠️ Unexpected Success: {res.head()}")
except Exception as e:
    print(f"❌ CRASH: {e}")

# SCENARIO 3: The "Garbage Text" Coder
print("\n[Case 3] Coder pastes pure garbage/symbols:")
try:
    garbage_input = ["!@#$%^", "     ", "12345"]
    res = CoderWorkflows.auto_code_terms(garbage_input)
    if "No Match" in res['Match'].values:
        print("✅ Handled Garbage: 'No Match' returned correctly.")
    else:
        print(f"⚠️ Checks: {res}")
except Exception as e:
    print(f"❌ CRASH: {e}")

# SCENARIO 4: The "Non-Existent" File Upload (CRC)
print("\n[Case 4] CRC tries to file a weird object:")
try:
    class MockFile: name = "weird_file_no_extension"
    res = CRCWorkflows.auto_file_document(MockFile())
    print(f"✅ Result: {res}")
except Exception as e:
    print(f"❌ CRASH: {e}")

print("-" * 60)
print("🐒 CHAOS TEST COMPLETE.")
