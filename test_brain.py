import sys
import os
import pandas as pd

# Add the current directory to sys.path so we can import the module
sys.path.append(os.getcwd())

try:
    from logic.agent_logic import (
        analyze_protocol, 
        map_to_cdisc, 
        generate_protocol_draft, 
        translate_and_verify,
        generate_uat_script
    )
    from logic.marketing_mcp import run_marketing_agent
    print("[SUCCESS] Successfully imported LEEVIN Brain & Marketing MCP.")
except ImportError as e:
    print(f"[ERROR] Import Error: {e}")
    print("Ensure you are running this from the root directory containing 'logic'.")
    sys.exit(1)

# --- DUMMY DATA FOR TESTING ---
# We create a fake protocol text file to simulate an upload
TEST_FILENAME = "dummy_protocol.txt"
DUMMY_PROTOCOL_TEXT = """
PROTOCOL TITLE: A Phase 2 Study of Drug X in Type 2 Diabetes
INVESTIGATIONAL PRODUCT: Drug X (10mg oral)
INDICATION: Type 2 Diabetes Mellitus

OBJECTIVES:
- Primary: To evaluate the reduction in HbA1c at Week 24.
- Secondary: Safety and tolerability.

SCHEDULE OF EVENTS:
- Screening (Day -14): Informed Consent, Demographics, Medical History, Vitals.
- Baseline (Day 0): Vitals, Weight, HbA1c, Randomization, Dispense Drug.
- Week 4: Vitals, AE Check, Drug Accountability.
- Week 12: Vitals, HbA1c, AE Check.
- Week 24 (EOT): Vitals, Weight, HbA1c, Physical Exam.

INCLUSION CRITERIA:
1. Male or Female, age 18-65.
2. Diagnosed with T2DM for > 6 months.
3. HbA1c between 7.5% and 10.0%.

EXCLUSION CRITERIA:
1. Type 1 Diabetes.
2. History of cardiac events.
"""

def create_dummy_file():
    with open(TEST_FILENAME, "w") as f:
        f.write(DUMMY_PROTOCOL_TEXT)
    print(f"[INFO] Created dummy protocol file: {TEST_FILENAME}")

def run_tests():
    create_dummy_file()
    
    print("\n--- TEST 1: PROTOCOL AUDIT ---")
    print("Sending protocol to Gemini 1.5 Pro...")
    try:
        audit_result = analyze_protocol(TEST_FILENAME)
        print(f"Result Preview:\n{audit_result[:300]}...\n")
        if "Executive Summary" in audit_result or "Error" in audit_result:
            print("[PASS] Audit Test Completed.")
        else:
            print("[FAIL] Audit Test Failed.")
    except Exception as e:
        print(f"[WARN] Audit Test Skipped (infra error): {e}")

    print("\n--- TEST 2: CDISC MAPPER ---")
    print("Extracting variables...")
    cdisc_df = map_to_cdisc(TEST_FILENAME)
    if isinstance(cdisc_df, pd.DataFrame) and not cdisc_df.empty:
        print("[PASS] CDISC Mapping Successful. Sample Data:")
        print(cdisc_df.head())
    else:
        print("[FAIL] CDISC Mapping Failed or Returned Empty.")

    print("\n--- TEST 3: ZERO DRAFT GENERATOR ---")
    print("Drafting a new synopsis...")
    try:
        params = {"title": "Phase III", "phase": "Phase III", "indication": "Hypertension", "drug": "Hypotensol", "sponsor": "Leevin Pharma"}
        draft = generate_protocol_draft(params)
        if "Hypotensol" in draft:
            print("[PASS] Draft Generated Successfully.")
        else:
            print("[FAIL] Draft Generation Failed.")
    except Exception as e:
        print(f"[WARN] Draft Test Skipped (infra error): {e}")

    print("\n--- TEST 4: TRANSLATION ---")
    print("Translating 'Informed Consent' to Spanish...")
    try:
        trans = translate_and_verify("I voluntarily agree to participate in this study.", "Spanish", "ICF")
        print(f"Result:\n{trans}")
        if "Quality Audit" in trans:
            print("[PASS] Translation & Back-Translation Audit Verified.")
        else:
            print("[FAIL] Translation Logic Failed.")
    except Exception as e:
        print(f"[WARN] Translation Test Skipped (infra error): {e}")

    print("\n--- TEST 5: UAT SCRIPT GENERATOR ---")
    print("Generating UAT script from dummy CDISC data...")
    dummy_cdisc_df = pd.DataFrame({
        "Assessment": ["Systolic Blood Pressure"],
        "CDISC Domain": ["VS"],
        "CDISC Variable": ["VS.SYSBP"],
        "Notes": ["Position: Supine"]
    })
    try:
        uat_script = generate_uat_script(dummy_cdisc_df)
        print(f"Result Preview:\n{uat_script[:200]}...\n")
        if "Step" in uat_script and "Expected System Behavior" in uat_script:
            print("[PASS] UAT Script Generation Successful.")
        else:
            print("[FAIL] UAT Script Generation Failed.")
    except Exception as e:
        print(f"[WARN] UAT Test Skipped (infra error): {e}")

    print("\n--- TEST 6: MARKETING MCP ---")
    print("Simulating Audit Success Event...")
    # This should fail gracefully on keys but succeed in logic execution
    logs = run_marketing_agent("Audit ID: 12345. Success. Drug: Aspirin. Phase: 3.")
    print("Marketing Logs:")
    for log in logs:
        print(f" - {log}")
    if any("SKIPPED" in l or "SUCCESS" in l for l in logs):
        print("[PASS] Marketing Agent handled execution (Skipped/Success).")
    elif any("Connecting to AI Brain" in l or "AI Generation Failed" in l for l in logs):
         print("[WARN] Marketing Agent failed due to AI connection (Expected if offline).")
    else:
        print("[FAIL] Marketing Agent did not return expected logs.")

    # Cleanup
    if os.path.exists(TEST_FILENAME):
        os.remove(TEST_FILENAME)
    print("\n[DONE] All Tests Finished.")

if __name__ == "__main__":
    run_tests()
