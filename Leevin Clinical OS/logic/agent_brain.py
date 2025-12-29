import vertexai
from vertexai.generative_models import GenerativeModel
import os

# Initialize Vertex AI
# Ideally, project and location should be configurable
PROJECT_ID = os.getenv("GCP_PROJECT", "kairos-clinical-os")
LOCATION = "us-central1"

try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
except Exception:
    pass

def audit_protocol(text: str) -> str:
    """
    Uses Gemini 1.5 Pro to extract risks from protocol text.
    """
    try:
        model = GenerativeModel("gemini-1.5-pro-001")
        prompt = f"""
        Act as a Medical Director. Analyze the following Clinical Trial Protocol text.
        Identify top 3 Risks (Safety, Operational, or Regulatory).
        
        Protocol Text:
        {text[:30000]}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing protocol: {e}"
