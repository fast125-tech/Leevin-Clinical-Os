import pandas as pd

class BrainCoder:
    def __init__(self):
        self.version = "CODER-1.6 (Dict Validator)"

    def draft_query(self, term):
        suggestions = {
            "BLUE SKIN": "Cyanosis", "HIGH BP": "Hypertension",
            "HEAD PAIN": "Headache", "BELLY ACHE": "Abdominal Pain",
            "SUGAR": "Diabetes Mellitus"
        }
        rec = suggestions.get(term.upper(), "[Insert MedDRA Term]")
        return f"Investigator,\n\nThe term '{term}' is ambiguous. Did you mean '{rec}'?\nPlease update or clarify source."

    def verify_coding_impact(self, df):
        # v1.5 Logic: Check Verbatim vs PT match
        issues = []
        col_verb = next((c for c in df.columns if "VERB" in c.upper()), "Verbatim")
        col_query = next((c for c in df.columns if "QUERY" in c.upper()), "QueryText")
        col_pt = next((c for c in df.columns if "PT" in c.upper()), "PT")

        for _, r in df.iterrows():
            verb, query, pt = str(r.get(col_verb,"")).upper(), str(r.get(col_query,"")).upper(), str(r.get(col_pt,"")).upper()
            imp_words = [w for w in query.split() if len(w) > 4]
            match = True if not imp_words else any(w in pt for w in imp_words)
            
            if not match and len(query) > 5:
                sugg = "Suggestion: Update Verbatim" if "CHANGE TERM" in query else "Suggestion: Recode"
                issues.append({"Verbatim": verb, "Query": query, "PT": pt, "Action": sugg})
        
        if not issues: return pd.DataFrame([["✅ Coding matches Query"]], columns=["Status"])
        return pd.DataFrame(issues)

    def validate_terms(self, df):
        # v1.6 Logic: Mock Dictionary validation
        # Checks if PT is in the 'Official' list
        valid_pts = {
            "HEADACHE", "NAUSEA", "VOMITING", "DIZZINESS", "FATIGUE", 
            "HYPERTENSION", "ANEMIA", "FEVER", "RASH", "DYSPNEA",
            "COVID-19", "PNEUMONIA", "DIARRHEA", "CONSTIPATION"
        }
        
        col_pt = next((c for c in df.columns if "PT" in c.upper() or "TERM" in c.upper()), "PT")
        issues = []
        
        for _, r in df.iterrows():
            pt = str(r.get(col_pt, "")).upper().strip()
            if pt not in valid_pts:
                issues.append({
                    "Term": pt,
                    "Status": "❌ Unknown/Deprecated",
                    "Action": "Check MedDRA Version"
                })
        
        if not issues: return pd.DataFrame([["✅ All Terms Valid"]], columns=["Status"])
        return pd.DataFrame(issues)
