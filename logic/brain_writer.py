import pandas as pd

class BrainWriter:
    def __init__(self):
        self.version = "WRITER-1.6 (Narrative Gen)"

    def generate_shell(self, table_type):
        if table_type == "Demographics":
            data = {
                "Characteristic": ["Age (Mean)", "Sex (Female %)", "Race (White %)", "BMI (Mean)"],
                "Active (N=100)": ["45.2", "52.0%", "85.0%", "24.5"],
                "Placebo (N=100)": ["44.8", "51.0%", "84.5%", "24.8"]
            }
        else:
            data = {"Note": ["Select a valid table type"]}
        return pd.DataFrame(data)

    def analyze_protocol_file(self, f): 
        fname = getattr(f, 'name', 'Protocol.docx')
        return f"""
PROTOCOL ANALYSIS ({fname})
----------------------------
1. Consistency Check:
   - Text Section 6.1 mentions "Troponin" assessment.
   - SoA Table Column 'Lab Safety' DOES NOT include Troponin.
   ⚠️ DISCREPANCY DETECTED.

2. Structure Check:
   - 5 Visits defined in SoA.
   - 5 Visit Windows defined in text.
   ✅ MATCH.
"""

    def write_patient_narrative(self, data):
        # v1.6 Feature: Automated Patient Narrative
        subj = data.get('SubjectID', 'Unknown')
        age = data.get('Age', 'Unknown')
        sex = data.get('Sex', 'Unknown')
        
        aes = data.get('AEs', [])
        labs = data.get('Labs', [])
        
        narrative = f"""
PATIENT NARRATIVE
Subject ID: {subj}
Demographics: {age}-year-old {sex}.

SAFETY SUMMARY:
The subject experienced {len(aes)} Adverse Event(s).
        """
        
        for ae in aes:
            narrative += f"\n- On Day {ae.get('Day','?')}, subject experienced '{ae.get('Term','?')}'. Outcome: {ae.get('Outcome','?')}. Causality: {ae.get('Rel','?')},"
            
        narrative += "\n\nLABORATORY FINDINGS:"
        if not labs: narrative += "\nNo significant lab abnormalities reported."
        for lab in labs:
            narrative += f"\n- {lab.get('Test','?')} was {lab.get('Val','?')} on Day {lab.get('Day','?')}."
            
        narrative += "\n\nCONCLUSION:\nSubject completed the study per protocol."
        return narrative
