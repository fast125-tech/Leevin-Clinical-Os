import os
from langchain_community.chat_models import ChatOllama
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential

class HybridBrain:
    def __init__(self):
        # 1. Local Brain (The "Janitor" - Scrubs dirty data)
        # Assumes Ollama is running on localhost:11434
        try:
            self.local_brain = ChatOllama(model="medgemma", temperature=0) 
        except:
            print("WARNING: Local Ollama not found. Hybrid mode will fail.")
            self.local_brain = None

        # 2. Cloud Brain (The "Doctor" - Analyzes clean data)
        try:
            self.cloud_brain = ChatVertexAI(
                model_name="gemini-1.5-pro",
                temperature=0.0,
                location="us-central1"
            )
        except:
            self.cloud_brain = None

    def process_sensitive_patient_data(self, text_input):
        """
        Orchestrates the Clean -> Analyze pipeline.
        Returns: (redacted_text, analysis_result)
        """
        if not self.local_brain:
            return "Error: Local Brain (Ollama) not connected.", "N/A"
        
        # STEP 1: LOCAL SCRUB (On-Premise)
        scrub_template = """
        You are a HIPAA Compliance Officer.
        Task: Redact ALL PII (Names, DOBS, SSNs, MRNs, Phone Numbers) from the text below.
        Replace them with [REDACTED]. Do NOT change the clinical content.
        
        Input: {text}
        """
        scrub_prompt = PromptTemplate.from_template(scrub_template)
        scrub_chain = scrub_prompt | self.local_brain
        
        try:
            print("⏳ Local Brain scrubbing data...")
            redacted_text = scrub_chain.invoke({"text": text_input}).content
        except Exception as e:
            return f"Squawk 7700: Local Scrub Failed - {str(e)}", "Aborted"

        # STEP 2: CLOUD ANALYSIS (Secure)
        analyze_template = """
        You are a Senior Oncologist. Analyze this patient note.
        Note that PII has been redacted. Focus on the Clinical Narrative.
        
        1. Summarize the Diagnosis.
        2. Flag any potential risks or Adverse Events.
        
        Input: {text}
        """
        analyze_prompt = PromptTemplate.from_template(analyze_template)
        analyze_chain = analyze_prompt | self.cloud_brain
        
        try:
            print("🚀 Sending sanitized data to Cloud Brain...")
            analysis = analyze_chain.invoke({"text": redacted_text}).content
        except Exception as e:
            return redacted_text, f"Cloud Error: {str(e)}"
            
        return redacted_text, analysis
