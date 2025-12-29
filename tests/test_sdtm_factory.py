import pandas as pd
import os
import sys

# Add root to sys.path
sys.path.append(os.getcwd())

from logic.sdtm_engine import auto_map_to_sdtm, validate_sdtm_structure

def test_sdtm_engine():
    print("--- 🧪 TESTING SDTM FACTORY ---")
    
    # 1. Create Dummy Raw Data
    csv_name = "dummy_vitals.csv"
    df_raw = pd.DataFrame({
        "Patient": ["001", "002"],
        "Sys BP": [120, 130],
        "Dia BP": [80, 85],
        "Visit Date": ["2023-01-01", "2023-01-02"]
    })
    df_raw.to_csv(csv_name, index=False)
    
    # 2. Test Mapping
    print("Step 1: Running Auto-Map (Domain: VS)...")
    # Note: If offline, this will use fallback (no mapping usually, but let's see)
    # The prompt might fail if no creds, returning headers as is or empty mapping.
    df_sdtm, log = auto_map_to_sdtm(csv_name, "VS")
    
    print(f"Log: {log}")
    print("Mapped Columns:", df_sdtm.columns.tolist())
    
    # Check if DOMAIN column was added
    if "DOMAIN" in df_sdtm.columns and df_sdtm["DOMAIN"].iloc[0] == "VS":
        print("✅ DOMAIN Column Added correctly.")
    else:
        print("❌ DOMAIN Column missing or incorrect.")

    # 3. Test Validation
    print("\nStep 2: Validating Structure...")
    # Inject an invalid date to test validator
    df_sdtm["VSDTC"] = ["2023-01-01", "01/02/2023"] # Second is invalid ISO
    report = validate_sdtm_structure(df_sdtm, "VS")
    print("Validation Report:")
    print(report)
    
    if "Date Format Warning" in report:
        print("✅ Validator correctly caught invalid date format.")
    else:
        print("⚠️ Validator might have missed date check (or col name mismatch if AI didn't map 'Visit Date' to 'VSDTC').")

    # Cleanup
    if os.path.exists(csv_name):
        os.remove(csv_name)
    print("\n🏁 SDTM Test Finished.")

if __name__ == "__main__":
    test_sdtm_engine()
