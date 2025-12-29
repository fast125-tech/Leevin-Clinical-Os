from logic.recist_engine import RecistCalculator

class OncologyEngine:
    def __init__(self):
        self.recist = RecistCalculator()

    def calculate_recist(self, baseline_sum, current_sum, new_lesions=False):
        """
        Legacy wrapper for simple checks, or could expose full object.
        For now, let's defer to the new class logic if we want strictness, 
        but the UI needs the full object for validation.
        """
        # We will expose the calculator class directly in the UI for advanced features
        pass 


    def check_survival_status(self, df_patients):
        """
        Flags patients potentially lost to follow-up (> 90 days since last contact).
        """
        issues = []
        today = datetime.now()
        
        if 'LastContactDate' not in df_patients.columns:
            return pd.DataFrame({"Error": ["Column 'LastContactDate' missing"]})
            
        for index, row in df_patients.iterrows():
            last_date = pd.to_datetime(row['LastContactDate'], errors='coerce')
            if pd.isna(last_date):
                continue
                
            delta = (today - last_date).days
            if delta > 90:
                issues.append({
                    "Subject": row.get('USUBJID', 'Unknown'),
                    "Last Contact": last_date.date(),
                    "Days Since": delta,
                    "Status": "Risk: Lost to Follow-up"
                })
                
        return pd.DataFrame(issues)

    def check_toxicity_vs_dose(self, df_lb, df_ex):
        """
        Cross-checks Grade 3+ Toxicities against Dose Reductions.
        If Lab Grade >= 3 AND Dose was NOT reduced -> Flag Issue.
        """
        # Simplified Mock Logic for MVP
        # In real life, we'd map Lab Value ranges to CTCAE Grades
        
        issues = []
        # Finding high grade toxicities (Mock column 'CTCAE_Grade')
        if 'CTCAE_Grade' in df_lb.columns and 'DoseReduced' in df_ex.columns:
             high_tox = df_lb[df_lb['CTCAE_Grade'] >= 3]
             
             for idx, row in high_tox.iterrows():
                 subj = row['USUBJID']
                 # Check if this subject had a dose reduction
                 patient_ex = df_ex[df_ex['USUBJID'] == subj]
                 # If no dose reduction recorded
                 if patient_ex[patient_ex['DoseReduced'] == 'Yes'].empty:
                     issues.append({
                         "Subject": subj,
                         "Toxicity": row.get('LBTEST', 'Lab'),
                         "Grade": row['CTCAE_Grade'],
                         "Issue": "Grade 3+ Toxicity but No Dose Reduction found."
                     })
                     
        return pd.DataFrame(issues)
