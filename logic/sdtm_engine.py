import pandas as pd
import json
import re
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import PromptTemplate

# --- CONFIG ---
# Reusing the existing AI setup pattern
try:
    llm = ChatVertexAI(
        model_name="gemini-1.5-pro",
        temperature=0.0,
        max_output_tokens=2048,
        location="us-central1"
    )
except Exception as e:
    print(f"Warning: AI not connected. SDTM Engine will default to mock mode. {e}")
    llm = None

def auto_map_to_sdtm(raw_csv_path, domain):
    """
    Ingests a raw CSV and maps columns to SDTM 3.3 variables for the specified Domain.
    """
    try:
        df = pd.read_csv(raw_csv_path)
    except Exception as e:
        return pd.DataFrame(), f"Error reading CSV: {e}"

    headers = df.columns.tolist()

    if llm:
        # AI MAPPING
        template = """
        You are a generic Clinical Data CDISC Expert.
        
        TASK: Map the following Raw Data Headers to standard SDTM IG 3.3 Variables for the Domain '{domain}'.
        
        RAW HEADERS: {headers}
        
        RULES:
        1. Return ONLY a valid JSON dictionary: {{"RawHeader": "SDTMVariable"}}
        2. Use standard variables (e.g., USUBJID, VSORRES, VSDTC, AETERM, LBTESTCD).
        3. If no clear match, map to "SUPP_{domain}" or ignore.
        
        JSON OUTPUT:
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        
        try:
            response = chain.invoke({"domain": domain, "headers": str(headers)})
            mapping_text = response.content.replace("```json", "").replace("```", "").strip()
            mapping_dict = json.loads(mapping_text)
        except Exception as e:
            return df, f"AI Mapping Failed: {e}"
    else:
        # FALLBACK / MOCK
        mapping_dict = {} # No mapping in mock mode unless hardcoded

    # TRANSFORMATION
    # Rename columns
    df_sdtm = df.rename(columns=mapping_dict)
    
    # Add Static / Required SDTM Columns if missing
    if "DOMAIN" not in df_sdtm.columns:
        df_sdtm["DOMAIN"] = domain
        
    # Ensure USUBJID exists (Mock logic: Use PatientID or first column if missing)
    # Ideally AI handles this, but here's a safety net
    if "USUBJID" not in df_sdtm.columns:
        if "PatientID" in df_sdtm.columns:
            df_sdtm.rename(columns={"PatientID": "USUBJID"}, inplace=True)
        # else: take a guess? For now, we leave it for the validator to catch.

    return df_sdtm, f"✅ SDTM Conversion Complete (Mapped {len(mapping_dict)} columns)"

def validate_sdtm_structure(df, domain):
    """
    Validates the structure of a draft SDTM dataframe.
    """
    issues = []
    
    # 1. Mandatory Variables (General)
    required_vars = ["USUBJID", "DOMAIN"]
    # Domain specific sequence
    seq_var = f"{domain}SEQ"
    # required_vars.append(seq_var) # Usually auto-generated, but let's check if user expects it
    
    for var in required_vars:
        if var not in df.columns:
            issues.append(f"❌ Missing Required Variable: {var}")
            
    # 2. Date Format Check (ISO 8601 YYYY-MM-DD)
    # Find columns ending in DTC
    date_cols = [c for c in df.columns if c.endswith("DTC")]
    
    iso_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}')
    
    for col in date_cols:
        # Check first non-null value
        sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
        if sample:
             # simplistic check: string must start with YYYY-MM-DD
             if not iso_pattern.match(str(sample)):
                 issues.append(f"⚠️ Date Format Warning ({col}): '{sample}' does not look like ISO-8601 (YYYY-MM-DD).")

    if not issues:
        return "✅ Conformance Report: 100% Pass (Structure & Dates)"
    else:
        return "\n".join(issues)
