import sys
import os

# Adjust path to include the project root
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'Leevin Clinical OS')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'Leevin Clinical OS', 'leevin_os', 'services')))

try:
    from cdm_agent import CdmAgent
except ImportError:
    # Try alternate path if running from root
    sys.path.append(os.path.join(os.getcwd(), 'leevin_os', 'services'))
    from cdm_agent import CdmAgent

def test_reconciliation():
    print("Initializing CdmAgent...")
    agent = CdmAgent()
    
    if not agent.brain_3_active:
        print("⚠️ SKIPPING TEST: Brain 3 (LLM) is not active/configured.")
        return

    print("Brain 3 Active. Running Synthetic Test...")

    # Mock Data
    edc_data = """
    SubjectID, Visit, Date, Meds
    001, Visit 1, 2025-01-01, None
    001, Visit 2, 2025-01-15, None
    002, Visit 2, 2025-01-20, None  # Late (Should be ~Jan 15 +/- 2 days)
    003, Visit 1, 2025-01-01, NSAID (Ibuprofen)
    """

    cra_log = """
    SubjectID, Event, Description
    002, Visit Window, Visit 2 was late by 5 days.
    004, Missed Visit, Subject missed Visit 2.
    """

    print("\n--- Sending to Agent Epsilon ---")
    result = agent.run_reconciliation(edc_data, cra_log)
    
    print("\n--- RESULT ---")
    print(result)

    # Basic Assertions
    if "discrepancies" in result:
        discs = result["discrepancies"]
        print(f"\nFound {len(discs)} discrepancies.")
        
        # We expect:
        # 1. Subject 002: Matched? If it matched, it might NOT be a discrepancy depending on prompt logic (prompt says "discrepancies found"). 
        #    Actually, if it's in the log, it's NOT a discrepancy between EDC and Log. It's a deviation, but reconciled.
        #    Wait, step 3 says: 
        #    - UNREPORTED (In EDC, not in Log)
        #    - OVER-REPORTED (In Log, not in EDC)
        #    - MISMATCH (Details differ)
        #    So if it matches perfectly, it should NOT return as a discrepancy in the JSON list.
        #    
        # 2. Subject 003: UNREPORTED (NSAID in EDC, no Log).
        # 3. Subject 004: OVER-REPORTED (Log says missed, EDC doesn't say anything... wait EDC doesn't have 004, so maybe it IS missed? 
        #    If EDC is the TRUTH, and EDC doesn't have 004, then they missed the visit? If they missed the visit, and Log says "Missed Visit", then it Matches.
        #    Ah, but if EDC shows the visit HAPPENED (data exists) and Log says MISSED, that's Over-Reported. 
        #    In my mock, 004 is NOT in EDC. So presumably they missed it. Log says missed. That matches.
        
        found_unreported = any(d['issue_type'] == 'UNREPORTED' and '003' in str(d) for d in discs)
        print(f"Subject 003 UNREPORTED Found: {found_unreported}")

if __name__ == "__main__":
    test_reconciliation()
