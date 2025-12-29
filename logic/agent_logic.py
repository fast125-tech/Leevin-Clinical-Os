import os
import io
import pandas as pd
import pdfplumber
from fuzzywuzzy import process
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ServiceUnavailable, ResourceExhausted
from logic.data_cleaner import DataCleaner
from logic.learning_engine import LearningEngine

# --- CONFIGURATION ---
try:
    # STABLE CONFIGURATION (Standardized)
    llm = ChatVertexAI(
        model_name="gemini-1.5-flash-001",
        temperature=0.3,
        location="us-central1",
        max_output_tokens=4096
    )
    print("✅ AI Brain: Connected (Standard Stable)")
except Exception as e:
    llm = None

# --- RETRY DECORATOR ---
ai_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((ServiceUnavailable, ResourceExhausted, Exception)),
    reraise=True
)

# --- UTILITY ---
def extract_text_from_pdf(pdf_file, extract_tables=False):
    text = ""
    tables = []
    try:
        # Check if file path or file-like
        if isinstance(pdf_file, str) and not os.path.exists(pdf_file):
             return "Error: File not found.", []
             
        pdf = pdfplumber.open(pdf_file)
        with pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: text += f"\n--- Page {page.page_number} ---\n{t}"
                
                if extract_tables:
                    for tbl in page.extract_tables():
                         tables.append(pd.DataFrame(tbl).to_markdown())
    except Exception as e:
        return f"Error reading PDF: {e}", []
    return text, tables

# --- MODULE 1: DESIGNER ---
@ai_retry
def analyze_protocol(pdf_file):
    """
    Performs 'Deep Operational Stress Test'.
    STRICT RULE: No Date Math. No Statistics.
    """
    if not llm: return "⚠️ AI Brain Disconnected. Check Internet/Credentials."
    
    raw_text, tables = extract_text_from_pdf(pdf_file, extract_tables=True)
    if "Error" in raw_text: return raw_text
    
    table_context = "\n".join(tables[:5])
    
    template = """
    You are a Senior Medical Monitor.
    TASK: Audit this Protocol.
    
    INPUT:
    {protocol_text_snippet}
    {table_context}
    
    RULES:
    1. **Text Extraction ONLY:** Identify discrepancies between Narrative vs Table.
    2. **NO MATH:** Do NOT calculate durations or sample sizes.
    3. **Standard of Care:** Flag impossible criteria.
    
    OUTPUT (Markdown):
    1. **Executive Summary**
    2. **Feasibility Score (Qualitative Only)**
    3. **Data Discrepancy Log**
    4. **Critical Risks**
    """
    
    try:
        chain = PromptTemplate.from_template(template) | llm
        return chain.invoke({
            "protocol_text_snippet": raw_text[:60000],
            "table_context": table_context
        }).content
    except Exception as e:
        return f"⚠️ AI Busy or Error: {e}"

@ai_retry
def generate_protocol_draft(phase, design, title, context):
    """
    Generates TransCelerate Protocol Draft.
    STRICT RULE: All Math are Placeholders.
    """
    if not llm: return "⚠️ AI Brain Disconnected."
    
    params = f"Phase: {phase}, Design: {design}, Title: {title}, Context: {context}"
    
    # Retrieve Learned Knowledge
    brain_context = LearningEngine.get_knowledge_context()

    # Retrieve Learned Style
    style_context = ""
    style_path = os.path.join("assets", "styles", "master_template.json")
    if os.path.exists(style_path):
        try:
            with open(style_path, "r", encoding="utf-8") as f:
                style_data = f.read()
                style_context = f"*** CORPORATE STYLE GUIDE (STRICT ADHERENCE REQUIRED) ***\nThe user has provided a 'Gold Standard' template. You MUST structure the protocol EXACTLY like this JSON schema:\n{style_data}\n"
        except Exception:
            pass
    
    template = """
    You are an Expert Medical Writer (PhD level) for a Top-Tier Biopharma.
    
    *** MISSION ***
    Generate a "Protocol Zero" (First Robust Draft) that is 80-90% complete.
    It must be ready for Medical Director review with minimal editing.
    
    *** INPUTS ***
    Study Title: {title}
    Phase: {phase}
    Design: {design}
    Context: {context}
    
    *** PRODUCT MEMORY (User Preferences) ***
    *** PRODUCT MEMORY (User Preferences) ***
    {brain_context}

    {style_context}
    
    *** REQUIRED SECTIONS & CONTENT (Adhere to TransCelerate) ***
    
    1. **PROTOCOL SYNOPSIS**
       - Rationale, Objectives, Endpoints, Population, Design, Duration.
       
    2. **SECTION 1: OBJECTIVES & ENDPOINTS**
       - **CRITICAL**: Create a Markdown Table with columns: | Objective Type | Objective | Endpoint |
       - Include Primary, Secondary, and Exploratory rows.
       
    3. **SECTION 2: STUDY DESIGN**
       - Scientific Rationale (Why this drug? Why this population?).
       - Overall Design (Randomization, Blinding, Control).
       - Justification of Dose.
       - End of Study Definition.
       
    4. **SECTION 3: STUDY POPULATION**
       - **Inclusion Criteria**: List at least 6 specific medical criteria (Age, Diagnosis, signatures).
       - **Exclusion Criteria**: List at least 6 specific criteria (Comorbidities, Meds, Labs).
       - Screen Failures & Rescreening logic.
       
    5. **SECTION 4: STUDY INTERVENTION**
       - Drug Description, Dosing Regimen, Packaging, Labeling.
       - Concomitant Therapy (Allowed/Prohibited).
       
    6. **SECTION 5: SCHEDULE OF ACTIVITIES (SoA)**
       - **CRITICAL**: Create a text-based grid/table showing Visits (V1, V2, V3...) vs Procedures (Consent, PE, Vitals, Dosing, PK, Safety Labs).
       - Use 'X' to mark required assessments.
       
    7. **SECTION 6: ADVERSE EVENTS & SAFETY**
       - Definition of AE/SAE.
       - Reporting Timelines (24h for SAE).
       - Pregnancy Reporting.
       
    8. **SECTION 7: STATISTICS**
       - Sample Size Calculation (Provide a realistic *hypothesis* and *N* calculation rationale).
       - Analysis Populations (ITT, PP, Safety).
       - Primary/Secondary Analysis Methods.
       
    *** TONE & STYLE ***
    - Use professional, regulatory-compliant language (ICH-GCP).
    - No "TBD" placeholders unless absolutely necessary. INVENT REALISTIC DATA based on the '{context}'.
    - Do not use markdown bolding (**) excessively, keep it clean for Word conversion.
    """
    

    
    try:
        if not llm: raise Exception("No LLM Configured")
        chain = PromptTemplate.from_template(template) | llm
        return chain.invoke({
            "params": str(params),
            "title": title,
            "phase": phase,
            "design": design,
            "context": context,
            "brain_context": brain_context,
            "style_context": style_context
        }).content
    except Exception as e:
        print(f"⚠️ AI Connection Failed ({e}). Using Fallback Generator.")
        # Fallback: Compliant Mock Draft
        return f"""
# Property of [SPONSOR] Confidential

**Protocol Title:** {title}
**Protocol Number:** [PROTOCOL_NO]
**Phase:** {phase}
**Sponsor:** [SPONSOR]

## Table of Contents
1. Introduction
2. Study Objectives
3. Investigational Plan
...

## 1. Introduction
### 1.1 Background
(AI Fallback) Detailed background on {context}...

### 1.2 Purpose
To evaluate safety and efficacy...

## 2. Study Objectives
### 2.1 Primary Objective
To demonstrate efficacy...

## 3. Investigational Plan
### 3.1 Study Design
{design}...

## 6. Visit Schedule and Assessments
### Table 6-1: Assessment Schedule
| Visit | Screening | Week 0 | Week 4 |
|-------|-----------|--------|--------|
| Vitals| X         | X      | X      |

## 12. References
1. Clinical Trial Protocol Template Version 03
"""

# --- MODULE 6: FILER ---
def classify_tmf_doc(pdf_file):
    if not llm: return "⚠️ AI Brain Disconnected."
    
    raw_text, _ = extract_text_from_pdf(pdf_file)
    chain = PromptTemplate.from_template("Classify this TMF Doc (Zone/Section/Artifact): {text}") | llm
    
    try:
        return chain.invoke({"text": raw_text[:5000]}).content
    except Exception as e:
        return f"⚠️ Classification Error: {e}"

# --- MODULE 7: PLANNER ---
def generate_dmp(pdf_file):
    if not llm: return "⚠️ AI Brain Disconnected."
    
    raw_text, _ = extract_text_from_pdf(pdf_file)
    chain = PromptTemplate.from_template("Create Data Management Plan from Protocol: {text}") | llm
    
    try:
        return chain.invoke({"text": raw_text[:40000]}).content
    except Exception as e:
        return f"⚠️ DMP Error: {e}"

# --- MODULE 8: MAPPER ---
def generate_acrf_map(pdf_file):
    if not llm: return "⚠️ AI Brain Disconnected."
    
    raw_text, _ = extract_text_from_pdf(pdf_file)
    chain = PromptTemplate.from_template("Map CRF Fields to SDTM (IG 3.3). Return Table: {text}") | llm
    
    try:
        return chain.invoke({"text": raw_text[:30000]}).content
    except Exception as e:
        return f"⚠️ Mapping Error: {e}"

def generate_uat_script(cdisc_df):
    """
    Generates Excel UAT Script from CDISC DF.
    """
    if not llm: return "⚠️ AI Brain Disconnected."
    
    input_text = cdisc_df.to_markdown() if isinstance(cdisc_df, pd.DataFrame) else str(cdisc_df)
    
    template = """
    Create UAT Script (Step, Action, Expected, PassFail) for: {text}
    Return CSV format.
    """
    try:
        chain = PromptTemplate.from_template(template) | llm
        csv_text = chain.invoke({"text": input_text[:40000]}).content
        
        # Simple Parse
        rows = [line.split(',') for line in csv_text.split('\n') if ',' in line]
        df = pd.DataFrame(rows)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)
        return output.getvalue()
    except Exception:
        return None

def map_to_cdisc(pdf_file):
    """
    Extracts variables and maps to SDTM.
    """
    if not llm: return pd.DataFrame()
    raw_text, _ = extract_text_from_pdf(pdf_file)
    
    template = "Extract Clinical Assessments (Assessment|Domain|Variable) from: {text}"
    try:
        chain = PromptTemplate.from_template(template) | llm
        resp = chain.invoke({"text": raw_text[:40000]}).content
        
        data = []
        for line in resp.split('\n'):
             if "|" in line and "Assessment" not in line:
                 p = line.split('|')
                 if len(p) >= 3:
                     data.append({"Assessment": p[0], "Domain": p[1], "Variable": p[2]})
        return pd.DataFrame(data)
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()

def run_data_checks(csv_file):
    """
    Wrapper for DataCleaner hard checks.
    """
    try:
        # Reset file pointer if needed, but streamlit file buffers behave differently
        # Assuming csv_file is a file-like object from st.file_uploader
        df = pd.read_csv(csv_file)
        cleaner = DataCleaner()
        issues_df = cleaner.run_hard_checks(df)
        
        # Convert to list of strings or dicts for the UI to display cleanly
        if issues_df.empty: return []
        
        errors = []
        for _, row in issues_df.iterrows():
            errors.append(f"Row {row['Row']} | {row['Column']}: {row['Issue']} (Value: {row['Value']})")
        return errors
    except Exception as e:
        return [f"Error validating data: {str(e)}"]

def translate_and_verify(text, target_lang="es"):
    """
    Placeholder for Translation Logic.
    """
    return f"[MOCK] Translated '{text[:20]}...' to {target_lang}. Verified by AI."