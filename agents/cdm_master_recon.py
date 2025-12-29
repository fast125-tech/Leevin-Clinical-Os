import pandas as pd
from services.medical_graph import MedicalGraph
import spacy

nlp = spacy.load("en_core_web_sm")

class MasterCDM:
    def __init__(self):
        self.graph = MedicalGraph()
        self.issues = []

    # MODULE A: NLP SAFETY SCAN
    def scan_narratives(self, df, col_name="Comments"):
        print("👁️ CDM: Scanning unstructured comments...")
        results = []
        for i, row in df.iterrows():
            doc = nlp(str(row[col_name]).lower())
            if "severe" in doc.text or "hospital" in doc.text:
                results.append({"Row": i, "Signal": "Potential SAE", "Text": row[col_name]})
        return pd.DataFrame(results)

    # MODULE B: LAB RECONCILIATION
    def reconcile_labs(self, df_edc, df_vendor):
        print("🧪 CDM: Reconciling Labs...")
        # Mock logic
        return pd.DataFrame([{"Issue": "Sample Mismatch", "Subject": "101"}])

    # MODULE C: GRAPH-BASED SAFETY CHECK
    def check_contraindications(self, meds, conditions):
        print("🧠 CDM: Checking Drug-Disease Graph...")
        risks = []
        for med in meds:
            for cond in conditions:
                trace = self.graph.find_connection(med, cond)
                if trace:
                    risks.append(f"RISK: {trace}")
        return risks
