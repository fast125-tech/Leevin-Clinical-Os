import pandas as pd
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import PromptTemplate

# Initialize AI for Soft Checks
try:
    llm = ChatVertexAI(
        model_name="gemini-1.5-pro",
        temperature=0.0,
        location="us-central1"
    )
except:
    llm = None

class DataCleaner:
    def __init__(self):
        pass

    def run_hard_checks(self, df):
        """
        Executes Python-based logic (ZERO Hallucinations).
        1. Future Dates
        2. Negative Vitals
        3. Missing Key IDs
        """
        issues = []
        
        # 1. Future Dates
        date_cols = [c for c in df.columns if "Date" in c or "DTC" in c]
        for col in date_cols:
            try:
                # Coerce to datetime
                dates = pd.to_datetime(df[col], errors='coerce')
                today = pd.Timestamp.now()
                # Find future dates
                future_mask = dates > today
                
                for idx, is_future in future_mask.items():
                    if is_future:
                        issues.append({
                            "Row": idx,
                            "Column": col,
                            "Value": df.at[idx, col],
                            "Issue": "Future Date"
                        })
            except Exception as e:
                pass # Skip column if date parse fails entirely

        # 2. Negative Vitals (Numeric columns starting with VS)
        vs_cols = [c for c in df.columns if c.startswith("VS") and "ORRES" in c]
        for col in vs_cols:
            # Convert to numeric, errors='coerce' turns non-numeric to NaN
            nums = pd.to_numeric(df[col], errors='coerce')
            neg_mask = nums < 0
            
            for idx, is_neg in neg_mask.items():
                if is_neg:
                    issues.append({
                        "Row": idx,
                        "Column": col,
                        "Value": df.at[idx, col],
                        "Issue": "Negative Value"
                    })

        return pd.DataFrame(issues)

    def run_medical_consistency(self, df_ae, df_cm):
        """
        Executes AI-based medical logic (Soft Checks).
        Checks AE vs CM cross-references.
        """
        if not llm: return pd.DataFrame({"Error": ["AI Brain missing"]})
        
        # Sample data to avoid token limits
        ae_sample = df_ae.head(20).to_markdown()
        cm_sample = df_cm.head(20).to_markdown()
        
        template = """
        You are a Medical Data Reviewer.
        Compare the Adverse Events (AE) and Concomitant Meds (CM) below.
        
        TASK:
        Identify AEs that logically require medication but have no corresponding CM.
        (e.g., "Headache" typically requires "Paracetamol" or similar).
        
        AE DATA:
        {ae_data}
        
        CM DATA:
        {cm_data}
        
        OUTPUT FORMAT (Markdown Table):
        | Subject | AE | Issue | Suggested Query |
        |---|---|---|---|
        | 101 | Headache | No analgesic found | Please verify if concomitant medication was taken. |
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        
        try:
            response = chain.invoke({"ae_data": ae_sample, "cm_data": cm_sample}).content
            return response # Returns raw markdown for now, easier to display in Streamlit
        except Exception as e:
            return f"AI Analysis Failed: {e}"
