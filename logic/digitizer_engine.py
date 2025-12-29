
import os
import json
import pdfplumber
import pandas as pd
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential

class ProtocolDigitizer:
    """
    The 'Veridix Killer': Converts PDF Protocols into structured JSON data.
    """
    
    def __init__(self):
        try:
            self.llm = ChatVertexAI(
                model_name="gemini-1.5-flash-001",
                temperature=0.0, # Zero temp for strict JSON
                location="us-central1",
                max_output_tokens=8192
            )
            self.connected = True
        except Exception as e:
            print(f"Digitizer Init Error: {e}")
            self.llm = None
            self.connected = False

    def extract_text(self, pdf_file):
        """Extracts text from PDF/Docx."""
        text = ""
        try:
            if hasattr(pdf_file, 'read'): # Streamlit Buffer
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
            else: # Path
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
        except Exception as e:
            return f"Error reading file: {e}"
        return text

    def digitize_protocol(self, pdf_file):
        """
        Main Pipeline: PDF -> Text -> Gemini -> JSON
        """
        if not self.connected:
            return {"Error": "AI Brain Disconnected"}

        raw_text = self.extract_text(pdf_file)
        if "Error" in raw_text:
            return {"Error": raw_text}

        # Truncate for token limits if massive (approx 30k words)
        safe_text = raw_text[:100000]

        prompt_template = """
        You are a Clinical Data Architect.
        TASK: Digitize this Clinical Trial Protocol into a strict JSON structure.
        
        INPUT TEXT:
        {text}

        REQUIRED JSON OUTPUT FORMAT:
        {{
          "metadata": {{
            "protocol_title": "string",
            "protocol_number": "string",
            "phase": "string",
            "sponsor": "string"
          }},
          "arms": [
            {{ "name": "Arm A", "description": "..." }}
          ],
          "visit_schedule": [
             {{ "visit_label": "Screening", "week": -1, "day": -7 }},
             {{ "visit_label": "Baseline", "week": 0, "day": 1 }},
             {{ "visit_label": "Visit 1", "week": 4, "day": 28 }}
          ],
          "cohorts": [
             {{ "name": "Inclusion Criteria", "criteria": ["list", "of", "items"] }},
             {{ "name": "Exclusion Criteria", "criteria": ["list", "of", "items"] }}
          ],
          "endpoints": {{
             "primary": "string",
             "secondary": ["list"]
          }}
        }}

        RULES:
        1. Return ONLY valid JSON. No markdown fencing (```json).
        2. Infer missing fields as null.
        3. Do not hallucinate. If not found, leave empty.
        """

        try:
            chain = PromptTemplate.from_template(prompt_template) | self.llm
            response = chain.invoke({"text": safe_text})
            
            # Clean response
            json_str = response.content.replace("```json", "").replace("```", "").strip()
            
            return json.loads(json_str)
        except Exception as e:
            return {"Error": f"Digitization Failed: {str(e)}"}

    def generate_schema_visualization(self, digital_protocol):
        """Generates a Pandas DF for the Visit Schedule."""
        if "visit_schedule" in digital_protocol:
            return pd.DataFrame(digital_protocol["visit_schedule"])
        return pd.DataFrame()
