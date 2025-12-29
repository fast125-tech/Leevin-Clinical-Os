import pandas as pd
from logic.leevin_central import LeevinCentral

print("🚀 Testing Antigravity Engine v1.6 (Full Suite)...")
central = LeevinCentral()

# 1. BRAIN SITE v1.6 (Burden Analysis)
print("\n--- 1. Testing BrainSite v1.6 (Burden) ---")
visits = [
    {'name':'V1', 'procedures':['MRI', 'ECG']}, # 5+2=7
    {'name':'V2', 'procedures':['Vitals']}      # 1
]
res_burden = central.site.analyze_burden(visits)
print(res_burden[['Visit', 'Burden Score', 'Status']].to_string(index=False))
if res_burden.iloc[0]['Burden Score'] == 7:
    print("✅ Burden Logic Checked.")
else:
    print("❌ Burden Logic Failed.")

# 2. BRAIN CODER v1.6 (Dictionary Validator)
print("\n--- 2. Testing BrainCoder v1.6 (Validator) ---")
df_terms = pd.DataFrame({'PT': ['HEADACHE', 'ALIEN VIRUS', 'COVID-19']})
res_val = central.coder.validate_terms(df_terms)
print(res_val.to_string(index=False))
if any(res_val['Status'].str.contains('Unknown')):
    print("✅ Unknown Term Flagged.")
else:
    print("❌ Validation Failed.")

# 3. BRAIN WRITER v1.6 (Narrative Generator)
print("\n--- 3. Testing BrainWriter v1.6 (Narrative) ---")
demo_data = {
    'SubjectID': 'TEST-001', 'Age': 50, 'Sex': 'F',
    'AEs': [{'Day': 1, 'Term': 'Nausea', 'Outcome': 'Recovered', 'Rel': 'Probable'}],
    'Labs': []
}
narrative = central.writer.write_patient_narrative(demo_data)
print(narrative)
if "Subject experienced 1 Adverse Event" in narrative or "TEST-001" in narrative:
    print("✅ Narrative Generated.")
else:
    print("❌ Narrative Generation Failed.")

print("\n✅ Full v1.6 Verification Complete.")
