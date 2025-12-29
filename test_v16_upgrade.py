import pandas as pd
from logic.leevin_central import LeevinCentral
import traceback

print("🚀 Testing Antigravity Engine v1.6 (PD Edition)...")
central = LeevinCentral()

# 1. Test BRAIN CDM v1.6 (PD Recon)
print("\n--- 1. Testing BrainCDM v1.6 (PD Recon) ---")
try:
    df_pd = pd.DataFrame({
        'USUBJID': ['001', '002'],
        'Category': ['Missed Visit', 'Other'],
        'Visit': ['Visit 2', 'Visit 3']
    })
    df_edc = pd.DataFrame({
        'USUBJID': ['001'],
        'Folder': ['Visit 2'],
        'VisitDate': ['2025-01-01']
    })
    
    res, metrics = central.cdm.run_recon(df_pd, df_edc, "PD_Recon")
    
    print(f"Metrics: {metrics}")
    if any(res['Issue'] == 'Zombie Visit'):
        print("✅ Zombie Visit Detected successfully.")
    else:
        print("❌ Failed to detect Zombie Visit. Output:\n", res)

except Exception:
    print("❌ Critical Error in CDM:")
    with open("error_log.txt", "w") as f:
        traceback.print_exc(file=f)
    print("Traceback logged to error_log.txt")

# 2. Test BRAIN CRA v1.6 (Weighted Risk)
print("\n--- 2. Testing BrainCRA v1.6 (Weighted Risk) ---")
try:
    df_risk = pd.DataFrame({
        'SiteID': ['101'],
        'Queries': [1],      # 1
        'SAEs': [1],          # 5
        'PD_Major': [1],      # 3
        'PD_Minor': [1],      # 1
        'SubjCount': [1]
    })
    risk_res = central.cra.analyze_risk(df_risk, "Site")
    score = risk_res['Risk Score'].iloc[0]
    print(f"Calculated Score: {score}")

    if score == 10.0:
        print("✅ Weighted Scoring Logic Verified.")
    else:
        print(f"❌ Scoring Mismatch. Expected 10.0, got {score}")
except Exception:
    with open("error_log.txt", "a") as f:
        traceback.print_exc(file=f)

print("\n✅ Verification Script Done.")
