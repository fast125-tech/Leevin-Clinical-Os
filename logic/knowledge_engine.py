import os
import json
import pdfplumber
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import PromptTemplate

class KnowledgeEngine:
    
    @staticmethod
    def train_on_pdf(pdf_path, output_name="master_template.json"):
        """
        Ingests a PDF, extracts style/structure DNA using Gemini, and saves a JSON template.
        """
        print(f"📖 Reading {pdf_path}...")
        
        # Configure Brain (using the same settings as other agents for consistency if needed, 
        # but user requested specific settings, so we adhere to those or safe defaults)
        try:
            llm = ChatVertexAI(
                model_name="gemini-1.5-pro", 
                temperature=0.0,
                max_output_tokens=8192
            )
        except Exception as e:
            return f"Error initializing AI: {e}"

        # 1. Extract Text
        full_text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Read first 50 pages (enough to get structure + boilerplate)
                for i, page in enumerate(pdf.pages[:50]): 
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
        except Exception as e:
            return f"Error reading PDF: {e}"

        if not full_text:
            return "Error: No text extracted from PDF."

        # 2. Extract The "DNA"
        print("🧠 Extracting Style DNA (Headers, Tone, Tables)...")
        
        template = """
        You are a Clinical Operations Architect. Analyze this Master Protocol.
        
        TASK: Extract the structural "Skeleton" so we can reuse it for future studies.
        
        OUTPUT JSON FORMAT:
        {{
            "headers": ["1. Introduction", "1.1 Background", "2. Objectives"...],
            "soe_columns": ["Visit", "Window", "Screening", "Baseline"...],
            "standard_text": {{
                "ethics": "Copy the standard Ethics text...",
                "data_management": "Copy the standard DM text..."
            }},
            "writing_style": "Formal, passive voice, specific verb usage..."
        }}
        
        PROTOCOL TEXT:
        {text}
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        
        try:
            result_json = chain.invoke({"text": full_text[:100000]}).content
            # Clean JSON
            clean_json = result_json.replace("```json", "").replace("```", "").strip()
            
            # Verify JSON validity
            try:
                json.loads(clean_json)
            except json.JSONDecodeError:
                return "Error: AI extracted invalid JSON."

            # 3. Save to Backend
            # Ensure directory exists
            output_dir = os.path.join("assets", "styles")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_name)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(clean_json)
                
            print(f"✅ Training Complete. Style saved to {output_path}")
            return f"Success: Trained on {os.path.basename(pdf_path)}. Style saved to {output_name}."
            
        except Exception as e:
            print(f"Training Failed: {e}")
            return f"Training Failed: {e}"
