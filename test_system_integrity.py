import sys
import os
import pandas as pd
import datetime

# Add root to path
sys.path.append(os.getcwd())

# 1. Test Agent Logic (Writer)
print("--- Testing Medical Writer Logic ---")
try:
    from logic.agent_logic import generate_protocol_draft
    # Mock LLM calls might fail if no creds, but we check if function runs
    # We expect a string or a handled error message, not a crash
    res = generate_protocol_draft("Phase 3", "Randomized", "Test Title", "Context")
    print(f"✅ Protocol Draft: Success (Length: {len(str(res))})")
except Exception as e:
    print(f"❌ Protocol Draft Failed: {e}")

# 2. Test Role Workflows
try:
    from logic.role_workflows import CDMWorkflows, CRAWorkflows, CRCWorkflows, CoderWorkflows
    
    # CDM: UAT Generation
    print("\n--- Testing CDM Logic ---")
    try:
        spec_df = pd.DataFrame({'Form': ['Demog'], 'Field': ['Age'], 'Type': ['Integer']})
        uat_res = CDMWorkflows.generate_synthetic_uat_data(spec_df)
        if "Subject" in uat_res.columns:
            print("✅ UAT Gen: Success")
        else:
            print(f"❌ UAT Gen Failed: {uat_res.iloc[0]['Error']}")
    except Exception as e: print(f"❌ UAT Gen Crash: {e}")

    # CDM: Edit Checks
    try:
        check = CDMWorkflows.draft_edit_check("If Age < 18 then Query")
        print(f"✅ Edit Check: Success ({check[:20]}...)")
    except Exception as e: print(f"❌ Edit Check Crash: {e}")

    # CRA: Trip Report
    print("\n--- Testing CRA Logic ---")
    try:
        pdf_path = CRAWorkflows.generate_trip_report("Site is good.")
        if ".pdf" in str(pdf_path):
            print(f"✅ Trip Report: Success ({pdf_path})")
            # Cleanup
            if os.path.exists(pdf_path): os.remove(pdf_path)
        else:
            print(f"⚠️ Trip Report Warning: {pdf_path}")
    except Exception as e: print(f"❌ Trip Report Crash: {e}")

    # CRC: Visit Calculator
    print("\n--- Testing CRC Logic ---")
    try:
        sched = CRCWorkflows.calculate_visit_schedule(datetime.date.today())
        if not sched.empty:
            print("✅ Visit Calc: Success")
        else:
            print("❌ Visit Calc Failed: Empty DF")
    except Exception as e: print(f"❌ Visit Calc Crash: {e}")

    # Coder: Auto-Coding
    print("\n--- Testing Coder Logic ---")
    try:
        codes = CoderWorkflows.auto_code_terms(["Headache", "Tylenol"])
        if not codes.empty and "Match" in codes.columns:
            print("✅ Auto-Coder: Success")
        else:
            print("❌ Auto-Coder Failed")
    except Exception as e: print(f"❌ Auto-Coder Crash: {e}")

except ImportError as e:
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
except Exception as e:
    print(f"❌ CRITICAL WORKFLOW ERROR: {e}")
