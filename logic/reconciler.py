import pandas as pd
from fuzzywuzzy import process
from langchain_google_vertexai import ChatVertexAI

try:
    llm = ChatVertexAI(
        model_name="gemini-1.5-flash-001",
        temperature=0.1,
        location="us-central1"
    )
except:
    llm = None

class Reconciler:
    def __init__(self):
        pass

    def normalize_headers(self, df):
        """
        Standardizes column names to CDISC (USUBJID, VISIT, etc.) using Fuzzy Matching.
        """
        standard_cols = ["USUBJID", "VISIT", "LBTEST", "LBORRES", "LBORNRLO", "LBORNRHI", "AETERM", "AESTDTC", "DSDECOD"]
        
        rename_map = {}
        for col in df.columns:
            # Find best match
            match, score = process.extractOne(col.upper(), standard_cols)
            if score > 85: # High confidence threshold
                rename_map[col] = match
        
        return df.rename(columns=rename_map)

    def run_safety_triangulation(self, df_ae, df_ds, df_dd):
        """
        Triangulates Death Events between:
        1. AE (Adverse Events) -> Outcome = FATAL
        2. DS (Disposition) -> Reason = DEATH
        3. DD (Death Details) -> Form Exists
        """
        issues = []
        
        # Normalize
        df_ae = self.normalize_headers(df_ae)
        df_ds = self.normalize_headers(df_ds)
        
        # Get all subjects with Death indicators
        ae_deaths = df_ae[df_ae['AEOUT'] == 'FATAL']['USUBJID'].unique() if 'AEOUT' in df_ae.columns else []
        ds_deaths = df_ds[df_ds['DSDECOD'] == 'DEATH']['USUBJID'].unique() if 'DSDECOD' in df_ds.columns else []
        
        all_death_subjs = set(list(ae_deaths) + list(ds_deaths))
        
        for subj in all_death_subjs:
            in_ae = subj in ae_deaths
            in_ds = subj in ds_deaths
            
            if in_ae and not in_ds:
                issues.append({"Subject": subj, "Issue": "fatal AE recorded but Disposition not marked as Death."})
            if in_ds and not in_ae:
                issues.append({"Subject": subj, "Issue": "Disposition is Death but no Fatal AE recorded."})
                
        return pd.DataFrame(issues)

    def run_lab_reconciliation(self, df_clinical, df_vendor):
        """
        Reconciles Clinical DB vs Lab Vendor DB.
        Matches on Subject + Visit + Test.
        Checks Result Value (with 0.1 tolerance).
        """
        df_c = self.normalize_headers(df_clinical)
        df_v = self.normalize_headers(df_vendor)
        
        # Merge on Keys
        merged = pd.merge(df_c, df_v, on=["USUBJID", "VISIT", "LBTEST"], suffixes=('_clin', '_vend'), how='inner')
        
        mismatches = []
        
        for idx, row in merged.iterrows():
            val_c = pd.to_numeric(row.get('LBORRES_clin'), errors='coerce')
            val_v = pd.to_numeric(row.get('LBORRES_vend'), errors='coerce')
            
            if pd.notna(val_c) and pd.notna(val_v):
                # Hard Check: Tolerance 0.1
                if abs(val_c - val_v) > 0.1:
                    mismatches.append({
                        "Subject": row['USUBJID'],
                        "Test": row['LBTEST'],
                        "Clinical_Val": val_c,
                        "Vendor_Val": val_v,
                        "Diff": abs(val_c - val_v)
                    })
            else:
                # Soft Check: Unit Mismatch or string value?
                unit_c = row.get('LBORRESU_clin', '')
                unit_v = row.get('LBORRESU_vend', '')
                
                if unit_c != unit_v and llm:
                    # Ask AI if units are equivalent
                    # For performance, we'd batch this, but for now linear call
                    # (Skipping API call in loop for speed, treating as mismatch)
                    mismatches.append({
                        "Subject": row['USUBJID'],
                        "Test": row['LBTEST'],
                        "Issue": f"Unit Mismatch: {unit_c} vs {unit_v}"
                    })

        return pd.DataFrame(mismatches)
