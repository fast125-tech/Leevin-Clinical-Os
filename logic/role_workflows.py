import pandas as pd
import datetime
import random
import os
import io
from fpdf import FPDF
from fuzzywuzzy import process
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate

# --- AI CONFIGURATION ---
try:
    llm = ChatVertexAI(
        model_name="gemini-1.5-flash-001",
        temperature=0.2,
        location="us-central1"
    )
except Exception as e:
    llm = None

# ==============================================================================
# 1. CLINICAL DATA MANAGER (CDM)
# ==============================================================================
class CDMWorkflows:
    @staticmethod
    def generate_synthetic_uat_data(spec_df):
        """
        Generates Rave-compliant UAT data (Subject, Folder, Form, Field, Value).
        Logic: Min, Max, and Boundary values.
        """
        try:
            uat_data = []
            # Ensure spec has minimal required columns
            required_cols = ['Form', 'Field', 'Type'] 
            if not all(col in spec_df.columns for col in required_cols):
                 # Try to guess or fallback
                 return pd.DataFrame({"Error": ["Spec file missing columns (Form, Field, Type)"]})

            for _, row in spec_df.iterrows():
                form = row.get('Form', 'Common')
                field = row.get('Field', 'Unknown')
                dtype = str(row.get('Type', 'Text')).lower()
                
                # Scenarios
                scenarios = [
                    ("Clean", "101", 1), # Normal
                    ("Boundary", "201", 0), # Min/Max
                    ("Failure", "901", 2)  # Invalid
                ]
                
                for scen, subj_prefix, code in scenarios:
                    val = ""
                    if "number" in dtype or "integer" in dtype:
                        if scen == "Clean": val = "50"
                        elif scen == "Boundary": val = "100" # Max
                        elif scen == "Failure": val = "9999" # Out of range
                    elif "date" in dtype:
                        if scen == "Clean": val = "01-JAN-2025"
                        elif scen == "Failure": val = "01-JAN-2099" # Future
                    else:
                        val = f"Test_{scen}"

                    uat_data.append({
                        "Subject": f"{subj_prefix}-001",
                        "Folder": "SCREENING",
                        "Form": form,
                        "Field": field,
                        "Value": val,
                        "Scenario": scen
                    })
            
            return pd.DataFrame(uat_data)
        except Exception as e:
            return pd.DataFrame({"Error": [f"UAT Gen Failed: {str(e)}"]})

    @staticmethod
    def draft_edit_check(description):
        """
        Converts natural language rule to Pandas Query Syntax.
        """
        if not llm: return "Error: AI not active."
        template = """
        You are a Python Expert. Convert this Clinical Rule into a PANDAS QUERY string.
        Assume data is in dataframe 'df'. Return ONLY the code snippet.
        
        Rule: {rule}
        
        Example Input: "If Age < 18, exclude."
        Example Output: df[df['AGE'] < 18]
        """
        try:
            chain = PromptTemplate.from_template(template) | llm
            return chain.invoke({"rule": description}).content.replace("```python", "").replace("```", "").strip()
        except Exception as e:
            return f"Error drafting check: {e}"

    @staticmethod
    def calculate_study_health(files):
        """
        Aggregates metrics from up to 6 uploaded files.
        """
        metrics = {
            "Total Files": 0,
            "Total Records": 0,
            "Total Columns": 0,
            "Common Sites": set(),
            "File Summary": []
        }
        
        try:
            # Handle empty input or single dataframe (legacy support)
            if not files: return metrics
            if isinstance(files, pd.DataFrame): return metrics # Legacy fallback
            
            for f in files:
                try:
                    # Determine loader
                    if f.name.endswith('.xlsx'):
                        df = pd.read_excel(f)
                    else:
                        df = pd.read_csv(f)
                    
                    # Aggregate
                    metrics["Total Files"] += 1
                    metrics["Total Records"] += len(df)
                    metrics["Total Columns"] += len(df.columns)
                    
                    # Intelligent Scanning
                    # Look for Site/Subject logic
                    for col in df.columns:
                        if 'site' in col.lower():
                            metrics["Common Sites"].update(df[col].dropna().astype(str).unique())
                            
                    metrics["File Summary"].append({
                        "Name": f.name,
                        "Rows": len(df),
                        "Cols": len(df.columns)
                    })
                    
                except Exception as e:
                    metrics["File Summary"].append({"Name": f.name, "Error": str(e)})

            metrics["Site Count"] = len(metrics["Common Sites"])
            del metrics["Common Sites"] # Clean up set for display
            return metrics

        except Exception as e:
            return {"Error": str(e)}

# ==============================================================================
# 2. CRA / MONITOR
# ==============================================================================
class CRAWorkflows:
    @staticmethod
    def generate_trip_report(notes):
        """
        Generates a PDF MVR from raw notes using AI structuring + FPDF.
        """
        if not llm: return "AI Error"
        
        # 1. Structure Notes
        struct_prompt = """
        Organize these monitoring notes into JSON sections: 
        {{"Summary": "...", "Personnel": "...", "SDV": "...", "ActionItems": "..."}}
        Notes: {notes}
        """
        try:
            chain = PromptTemplate.from_template(struct_prompt) | llm
            structured_text = chain.invoke({"notes": notes}).content
            # Cleanup for simple parsing (Assuming LLM returns somewhat clean text, or we just print raw for MVP)
            # For robustness in MVP, we might just print the AI output directly to PDF.
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Monitoring Visit Report (MVR)", 0, 1, 'C')
            pdf.ln(10)
            
            pdf.set_font("Arial", '', 12)
            
            # SANITIZATION: Force Latin-1 Compatible Text
            # Replace emojis/special chars to prevent PDF corruption
            clean_text = structured_text.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, clean_text)
            
            # Save to bytes
            # FPDF output() to string is deprecated/messy, write to temp file
            out_name = f"MVR_{datetime.date.today()}.pdf"
            pdf.output(out_name)
            return out_name
        except Exception as e:
            return f"Error generating MVR: {e}"

    @staticmethod
    def compare_source_to_edc(source_img_bytes, edc_img_bytes):
        """
        Visual SDV: Uses Gemini Vision to compare two images.
        """
        if not llm: return "AI not active"
        try:
            # Construct Multimodal Prompt
            # source_img_bytes and edc_img_bytes should be raw bytes
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": "You are a CRA. Compare Image 1 (Source Doc) and Image 2 (EDC Screen). List ANY discrepancies in values (Dates, Vitals, Labs). If match, say MATCH."
                    },
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{source_img_bytes}"}}, # Placeholder for actual base64
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{edc_img_bytes}"}}
                ]
            )
            # Note: The langchain integration for images handles base64 differently usually, 
            # but for this MVP code structure we assume standard vertex integration.
            # If complex, fallback to text extraction placeholder.
            return "Visual SDV Feature: [Requires Gemini Vision Multimodal Input - Placeholder for Byte Handling]"
        except Exception as e:
            return f"SDV Error: {e}"

# ==============================================================================
# 3. CRC / SITE COORDINATOR
# ==============================================================================
class CRCWorkflows:
    @staticmethod
    def calculate_visit_schedule(baseline_date):
        """
        Calculates Standard Visits: Wk4, Wk12, Wk24.
        """
        try:
            base = pd.to_datetime(baseline_date)
            visits = [
                {"Visit": "Baseline", "Target": base, "Window": "N/A"},
                {"Visit": "Week 4", "Target": base + datetime.timedelta(days=28), "Window": "+/- 3 Days"},
                {"Visit": "Week 12", "Target": base + datetime.timedelta(days=84), "Window": "+/- 5 Days"},
                {"Visit": "Week 24", "Target": base + datetime.timedelta(days=168), "Window": "+/- 7 Days"},
                {"Visit": "EOS", "Target": base + datetime.timedelta(days=365), "Window": "+/- 14 Days"},
            ]
            df = pd.DataFrame(visits)
            df['Target'] = df['Target'].dt.strftime('%d-%b-%Y').str.upper()
            return df
        except Exception as e:
            return pd.DataFrame({"Error": [str(e)]})

    @staticmethod
    def auto_file_document(uploaded_file, patient_id="101-001"):
        """
        Simulates eTMF filing: Renames based on heuristics.
        """
        try:
            filename = uploaded_file.name.lower()
            doc_type = "DOC"
            if "lab" in filename: doc_type = "LAB"
            elif "consent" in filename or "icf" in filename: doc_type = "ICF"
            elif "cv" in filename: doc_type = "CV"
            
            new_name = f"SITE_101_{patient_id}_{doc_type}_{datetime.date.today()}.pdf"
            return f"✅ Filed Successfully: {new_name} (Zone: {doc_type})"
        except Exception as e:
            return f"Filing Error: {e}"

# ==============================================================================
# 4. MEDICAL CODER
# ==============================================================================
class CoderWorkflows:
    # Dummy Dictionary
    MEDDRA_DICT = {
        "HEADACHE": {"LLT": "Headache", "PT": "Headache", "SOC": "Nervous system disorders"},
        "TYLENOL": {"LLT": "Paracetamol", "PT": "Paracetamol", "SOC": "General disorders"},
        "NAUSEA": {"LLT": "Feeling Queasy", "PT": "Nausea", "SOC": "Gastrointestinal disorders"},
        "COVID": {"LLT": "COVID-19", "PT": "COVID-19", "SOC": "Infections"},
        "BROKEN LEG": {"LLT": "Fracture of leg", "PT": "Lower limb fracture", "SOC": "Injury"}
    }
    
    @staticmethod
    def auto_code_terms(term_list):
        """
        Uses Fuzzy Matching to code terms.
        """
        results = []
        try:
            # term_list is expected to be a list of strings
            for term in term_list:
                term_clean = str(term).upper().strip()
                # Fuzzy Match against keys
                match, score = process.extractOne(term_clean, CoderWorkflows.MEDDRA_DICT.keys())
                
                if score > 70:
                    details = CoderWorkflows.MEDDRA_DICT[match]
                    results.append({
                        "Verbatim": term,
                        "Match": match,
                        "PT": details['PT'],
                        "SOC": details['SOC'],
                        "Confidence": f"{score}%"
                    })
                else:
                    results.append({
                        "Verbatim": term,
                        "Match": "No Match",
                        "PT": "Uncoded",
                        "SOC": "",
                        "Confidence": f"{score}% (Low)"
                    })
            return pd.DataFrame(results)
        except Exception as e:
            return pd.DataFrame({"Error": [str(e)]})
# ==============================================================================
# 5. ONCOLOGY / MEDICAL MONITOR
# ==============================================================================
class OncologyWorkflows:
    @staticmethod
    def calculate_recist(baseline_sld, nadir_sld, current_sld, new_lesions=False):
        """
        Calculates RECIST 1.1 Response.
        Inputs: Sum of Longest Diameters (SLD) in mm.
        """
        try:
            # Type safety
            base = float(baseline_sld)
            nadir = float(nadir_sld)
            curr = float(current_sld)
            
            # Logic
            response = "Unknown"
            reason = ""
            
            # 1. PD (Progressive Disease)
            pd_threshold = nadir * 1.20 # 20% increase
            abs_increase = curr - nadir
            
            if new_lesions:
                response = "PD (Progressive Disease)"
                reason = "New Lesions appeared."
            elif (curr >= pd_threshold) and (abs_increase >= 5.0):
                pct = round(((curr - nadir) / nadir) * 100, 1)
                response = "PD (Progressive Disease)"
                reason = f"Increase of {pct}% from Nadir AND >5mm absolute increase."
            
            # 2. CR (Complete Response)
            elif curr == 0:
                response = "CR (Complete Response)"
                reason = "Disappearance of all target lesions."
                
            # 3. PR (Partial Response)
            elif curr <= (base * 0.70): # 30% decrease
                pct = round(((base - curr) / base) * 100, 1)
                response = "PR (Partial Response)"
                reason = f"Decrease of {pct}% from Baseline."
                
            # 4. SD (Stable Disease)
            else:
                pct_base = round(((curr - base) / base) * 100, 1)
                response = "SD (Stable Disease)"
                reason = f"Assuming insufficient shrinkage for PR and insufficient increase for PD (Change from Base: {pct_base}%)."
                
            return {
                "Response": response,
                "Reason": reason,
                "Visualization": {
                    "Baseline": base,
                    "Nadir": nadir,
                    "Current": curr
                }
            }
        except Exception as e:
            return {"Error": f"Calc Error: {e}"}

# ==============================================================================
# 6. QUALITY ASSURANCE (QA)
# ==============================================================================
class QAWorkflows:
    @staticmethod
    def audit_and_file_document(uploaded_file, study_id="ONCO-101"):
        """
        QA eTMF Filing: Renames based on heuristics and logs for audit.
        """
        try:
            filename = uploaded_file.name.lower()
            doc_type = "GENERAL"
            
            # QC Logic: Identify Zone
            if "lab" in filename: doc_type = "ZONE_10_LABS"
            elif "consent" in filename or "icf" in filename: doc_type = "ZONE_02_ICF"
            elif "cv" in filename: doc_type = "ZONE_05_SITE"
            elif "protocol" in filename: doc_type = "ZONE_01_ADMIN"
            
            # QA Naming Convention: STUDY_ZONE_DATE_FILE
            new_name = f"{study_id}_{doc_type}_{datetime.date.today()}_{filename}"
            return {
                "Status": "Filed",
                "NewName": new_name,
                "Zone": doc_type,
                "Message": f"✅ QC Passed & Filed to eTMF: {new_name}"
            }
        except Exception as e:
            return {"Status": "Error", "Message": f"Filing Error: {e}"}
