import pandas as pd
from logic.leevin_central import LeevinCentral
from datetime import date

print("🚀 Testing Antigravity Engine v1.5 Upgrade...")
hub = LeevinCentral()

# 1. BRAIN CDM v1.5 (Visualization Check)
print("\n--- 1. Testing CDM v1.5 (Viz) ---")
issues = pd.DataFrame({'Subject': ['001', '001', '002'], 'Issue': ['SAE Error', 'Lab Error', 'SAE Error']})
try:
    charts = hub.cdm.visualize_metrics(issues, "Test Mode")
    if 'pie' in charts and 'bar' in charts:
        print("✅ Visualization Engine: Online")
    else:
        print("❌ Visualization Failed")
except Exception as e:
    print(f"❌ Viz Error: {e}")

# 2. BRAIN CRA v1.5 (Risk Analysis)
print("\n--- 2. Testing CRA v1.5 (Risk) ---")
metrics = pd.DataFrame({
    'SiteID': ['101', '102'],
    'Queries': [5, 20],
    'SAEs': [1, 5], 
    'SubjCount': [10, 10]
})
risk_df = hub.cra.analyze_risk(metrics, "Site")
print(risk_df[['SiteID', 'Risk Score', 'Risk Status']].to_string(index=False))

# 3. BRAIN SITE v1.5 (Deviation Logic)
print("\n--- 3. Testing Site v1.5 (Deviations) ---")
start = date(2025, 1, 1)
# 4 Jan (Sat) -> Shift to 6 Jan (Mon). Window=1. 6-4=2 days shift. Window remaining = 1-2 = -1 (OUT)
visits = [{'name': 'V2', 'days': 3, 'window': 1}] 
sch = hub.site.calculate_schedule(start, visits)
print(sch[['Visit', 'Adjusted Date', 'Status']].to_string(index=False))

# 4. BRAIN CODER v1.5 (Coding QC)
print("\n--- 4. Testing Coder v1.5 (QC) ---")
coding_data = pd.DataFrame({
    'Verbatim': ['High Blood Pressure'],
    'QueryText': ['Please recode to Hypertension'],
    'PT': ['Nausea'] # Mismatch: Hypertension not in Nausea
})
qc_res = hub.coder.verify_coding_impact(coding_data)
print(qc_res.to_string(index=False))

# 5. BRAIN WRITER v1.5 (Protocol)
print("\n--- 5. Testing Writer v1.5 (Protocol) ---")
res = hub.writer.analyze_protocol_file(None)
print("Analysis Generated" if "PROTOCOL ANALYSIS" in res else "Analysis Failed")
