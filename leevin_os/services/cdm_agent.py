
import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import PromptTemplate

class CdmAgent:
    """
    BRAIN 1 (The Enforcer) + BRAIN 3 (The Doctor)
    Hybrid Intelligence for Data Management.
    """
    
    def __init__(self):
        # Brain 3: The Doctor (Cognitive)
        # Initialize lazily or checking connection
        try:
            self.llm = ChatVertexAI(
                model_name="gemini-1.5-flash-001",
                temperature=0.2,
                location="us-central1"
            )
            self.brain_3_active = True
        except:
            self.brain_3_active = False

    # --- BRAIN 1: THE ENFORCER (Deterministic Math) ---
    def run_hard_checks(self, df):
        """
        Cost: Free. Speed: Instant.
        Checks: Dates, Duplicates, Negative Vitals.
        """
        report = []
        
        # 1. Duplicates
        if df.duplicated().any():
            count = df.duplicated().sum()
            report.append(f"🔴 HARD CHECK FAIL: Found {count} duplicate rows.")

        # 2. Future Dates
        date_cols = [c for c in df.columns if 'date' in c.lower() or 'dtc' in c.lower()]
        for col in date_cols:
            try:
                # Coerce to datetime
                temp_series = pd.to_datetime(df[col], errors='coerce')
                future_mask = temp_series > datetime.now()
                if future_mask.any():
                    ct = future_mask.sum()
                    report.append(f"🔴 HARD CHECK FAIL: {ct} dates are in the future ({col}).")
            except:
                pass # Not a date column despite name
                
        # 3. Impossible Vitals (Negative)
        # Looking for generic numeric columns that should be positive
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if (df[col] < 0).any():
                # Check if it's not a change score (which can be negative)
                if "change" not in col.lower() and "diff" not in col.lower():
                    report.append(f"🔴 HARD CHECK FAIL: Negative values found in {col}.")
                    
        if not report:
            report.append("🟢 HARD CHECKS PASSED: No deterministic errors found.")
            
        return report

    # --- BRAIN 3: THE DOCTOR (Cognitive) ---
    def run_soft_checks(self, df):
        """
        Cost: Paid. Speed: Slower.
        Checks: Free text logic, Comment analysis.
        """
        if not self.brain_3_active:
            return ["⚠️ BRAIN 3 OFFLINE: Cannot perform cognitive checks."]
            
        report = []
        
        # Identify "Comment" or "Note" columns
        text_cols = [c for c in df.columns if 'comment' in c.lower() or 'reason' in c.lower() or 'desc' in c.lower()]
        
        if not text_cols:
            return ["🟢 SOFT CHECKS: No free-text columns identified for review."]

        # Batch Logic: Sample top 5 suspicious rows or just first 5 for speed
        # For production: Logic filters 'suspicious' rows first using Brain 1
        
        sample_size = min(len(df), 5)
        for col in text_cols:
            # Extract non-empty text
            sample_texts = df[col].dropna().head(sample_size).tolist()
            if not sample_texts: continue
            
            prompt = f"""
            You are a Senior Clinical Data Manager.
            Review these clinical comments for logical inconsistencies or PII risks.
            COMMENTS: {sample_texts}
            
            OUTPUT:
            - List issues only. If OK, say "Clear".
            """
            
            try:
                response = self.llm.invoke(prompt).content
                if "Clear" not in response:
                    report.append(f"🟡 SOFT CHECK WARN ({col}): {response}")
            except Exception as e:
                report.append(f"⚠️ AI ERROR: {str(e)}")
                
        if not report:
            report.append("🟢 SOFT CHECKS PASSED: AI found no obvious logic gaps.")
            
        return report

    # --- AGENT EPSILON: RECONCILIATION ---
    def run_reconciliation(self, edc_data: str, cra_log: str) -> dict:
        """
        Agent Epsilon: Pre-Lock Reconciliation.
        Compares EDC Data (The Truth) vs CRA Deviation Log (The Human Report).
        Returns JSON summary.
        """
        if not self.brain_3_active:
            return {"error": "⚠️ BRAIN 3 OFFLINE: Cannot perform reconciliation."}

        prompt = ANTIGRAVITY_PD_PROMPT.replace("[EDC_DATA]", edc_data[:20000]).replace("[CRA_LOG]", cra_log[:10000])
        # Note: Truncation added for safety, though Gemini 1.5 has large context.

        try:
            response_content = self.llm.invoke(prompt).content
            
            # Clean Markdown wrappers if present
            cleaned_json = response_content.replace("```json", "").replace("```", "").strip()
            
            return json.loads(cleaned_json)
        except Exception as e:
            return {"error": f"⚠️ AI RECONCILIATION FAILED: {str(e)}", "raw_response": response_content if 'response_content' in locals() else "None"}

ANTIGRAVITY_PD_PROMPT = """
### ROLE
You are "Agent Epsilon," a Senior Clinical Data Manager and Auditor for the Leevin Clinical OS. 
Your goal is to perform a "Pre-Lock Reconciliation" to ensure 100% consistency between the EDC Data (The Truth) and the CRA Deviation Log (The Human Report).

### THE STAKES
The study is approaching Database Lock. Any discrepancy found here will block the lock. Precision is critical. 
- False Positives waste the team's time.
- False Negatives result in audit findings.

### INPUTS
You will receive two datasets in text/JSON format:
1. [EDC_DATA]: The clinical data entered by the site (Subject IDs, Visit Dates, Lab Values).
2. [CRA_LOG]: The manual list of deviations reported by the Monitor.

### PROTOCOL RULES (CONTEXT)
Use these constraints to determine if a deviation occurred in the [EDC_DATA]:
1. Visit Window: +/- 2 days from Scheduled Date.
2. Prohibited Meds: No NSAIDs allowed 24 hours pre-dose.
3. Informed Consent: Must be signed BEFORE Screen Visit.
4. Labs: Hematology must be collected at Visit 1 and Visit 4.

### YOUR TASK: RECONCILIATION LOGIC
Perform a 3-step cognitive pass on every subject:

Step 1: DETECT (The Machine Check)
Scan [EDC_DATA] against the Protocol Rules.
- Did Subject X miss a visit? 
- Is the date out of window? 
- Is there a prohibited med?
> *If a rule is broken, this is a "Potential Deviation".*

Step 2: MATCH (The Reconciliation)
For every "Potential Deviation" found in Step 1, search the [CRA_LOG].
- Look for a matching Subject ID and Event Type.
- *Fuzzy Match Logic:* Treat "Visit 3", "V3", and "Month 1 Visit" as the same.

Step 3: CLASSIFY (The Output)
Classify the finding into one of these strict categories:
- [TYPE A] UNREPORTED: The data shows a deviation, but the CRA Log is empty. (Critical Action: "Query Site to add to Log").
- [TYPE B] OVER-REPORTED: The CRA Log lists a deviation (e.g., "Missed Visit"), but the EDC Data shows the visit actually happened. (Critical Action: "Ask CRA to void deviation").
- [TYPE C] MISMATCH: Both exist, but details differ (e.g., EDC says "Jan 12", Log says "Jan 14").

### OUTPUT FORMAT
Return the result ONLY as a JSON object with this structure. Do not output markdown or conversational text.

{
  "summary": {
    "total_checked": <int>,
    "discrepancies_found": <int>
  },
  "discrepancies": [
    {
      "subject_id": "string",
      "issue_type": "UNREPORTED" | "OVER-REPORTED" | "MISMATCH",
      "description": "string (e.g. 'Visit 2 date is 14-Jan, which is 4 days late. No deviation found in Log.')",
      "action_item": "string (e.g. 'Post query on Vis_2 form')"
    }
  ]
}

DATA TO ANALYZE:
---
EDC DATA:
[EDC_DATA]
---
CRA DEVIATION LOG:
[CRA_LOG]
---
"""

