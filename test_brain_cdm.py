import pandas as pd
import sys
from logic.cdm_brain import BrainCDM

print("🧪 Testing BrainCDM (The Enforcer)...")
brain = BrainCDM()
print(f"✅ Loaded: {brain.version}")

# --- Test 1: SAE Logic ---
print("\n--- 1. Testing SAE Logic ---")
df_sae_clin = pd.DataFrame({
    'USUBJID': ['001', '002', '003'],
    'AESER': ['Y', 'N', 'Y'],
    'AEREL': ['RELATED', 'NONE', 'POSSIBLE'] 
})
df_sae_safe = pd.DataFrame({
    'USUBJID': ['001', '002', '003'],
    'AEREL': ['RELATED', 'NONE', 'UNLIKELY'] # 003 Mismatch
})
# Simulate Clean/Dirty
res = brain.run_recon(df_sae_clin, df_sae_safe, mode="SAE")
print(res)

# --- Test 2: Lab Logic ---
print("\n--- 2. Testing Lab Logic ---")
df_lab_edc = pd.DataFrame({
    'USUBJID': ['001', '002'],
    'VISITDAT': ['2025-01-01', '2025-01-01']
})
df_lab_ext = pd.DataFrame({
    'USUBJID': ['001', '002'],
    'LBDAT': ['2025-01-02', '2025-01-10'], # 002 Late (>2 days)
    'LBORRES': [10, None], # 002 Missing
    'LBCOMM': ['OK', 'sample QNS'] # 002 QNS
})
res = brain.run_recon(df_lab_edc, df_lab_ext, mode="Labs")
print(res)

# --- Test 3: Death Logic ---
print("\n--- 3. Testing Death Logic ---")
df_ae = pd.DataFrame({
    'USUBJID': ['001', '002'],
    'AEOUT': ['RECOVERED', 'FATAL']
})
df_ds = pd.DataFrame({
    'USUBJID': ['001', '002'],
    'DSDECOD': ['DEATH', 'COMPLETED'] 
})
# 001: Dispo Death, AE Recovered (Ghost Record)
# 002: AE Fatal, Dispo Completed (Zombie Record)
res = brain.run_recon(df_ae, df_ds, mode="Death")
print(res)

# --- Test 4: Coding Homogeneity ---
print("\n--- 4. Testing Coding Logic ---")
df_coding = pd.DataFrame({
    'USUBJID': ['001', '002', '003'],
    'AETERM': ['HEADACHE', 'HEADACHE', 'HEADACHE'],
    'AELLT': ['Headache', 'Headache', 'Migraine'] # Split Coding
})
# Need dummy df2 for coding (it only uses df1 but function requires 2 args)
res = brain.run_recon(df_coding, df_coding, mode="Coding")
print(res)

# --- Test 5: ConMed Orphans ---
print("\n--- 5. Testing ConMed Orphans ---")
df_ae_cm = pd.DataFrame({
    'USUBJID': ['001'],
    'AETERM': ['NAUSEA']
})
df_cm = pd.DataFrame({
    'USUBJID': ['001', '001'],
    'CMINDC': ['NAUSEA', 'HEADACHE'] # Headache is orphan (no AE)
})
res = brain.run_recon(df_ae_cm, df_cm, mode="AE_ConMed")
print(res)
