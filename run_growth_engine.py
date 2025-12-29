import sys
import json
from unittest.mock import MagicMock

# Mock Streamlit and Google Cloud modules before importing app modules
sys.modules["streamlit"] = MagicMock()
sys.modules["google.cloud"] = MagicMock()
sys.modules["google.cloud.firestore"] = MagicMock()
sys.modules["google.cloud.secretmanager"] = MagicMock()
sys.modules["google.cloud.storage"] = MagicMock()
sys.modules["google.cloud.texttospeech"] = MagicMock()
sys.modules["vertexai"] = MagicMock()
sys.modules["vertexai.generative_models"] = MagicMock()

# Now import the modules
from modules.marketing_bot import MarketingBot

# Mock the ClinicalAgent inside MarketingBot
def mock_generate(prompt):
    return json.dumps({
        "linkedin": "Just watched our AI catch a critical safety risk in a Phase III Vaccine Trial that 3 humans missed. This is why automation matters in Clinical Ops. By scanning the Schedule of Events against the protocol text, SYNTA identified a missing safety lab at Week 12. Compliance isn't just about checkboxes; it's about patient safety. #PatientSafety #ClinicalTrials #AI",
        "twitter": "Human review time: 3 weeks. SYNTA AI review time: 45 seconds. The era of manual CDM is over. 🧵👇 #MedTech #SaaS"
    })

# Instantiate and patch
bot = MarketingBot()
bot.agent._generate = mock_generate

# Mock Event Data (Simulating what comes from Firestore)
mock_event = {
    "action": "Protocol Analysis",
    "project": "SYNTA-001 (Oncology)",
    "details": "Identified 3 critical safety risks including missed ECG at Visit 4.",
    "timestamp": "2025-12-03T10:00:00Z"
}

print("--- STARTING GROWTH ENGINE ---")
print("1. MONITOR: Checking Audit Trails...")
print(f"   Found Event: {mock_event['action']} | {mock_event['timestamp']}")

print("\n2. ANALYZE: Determining Value Prop...")
print("   Value Prop: Risk Reduction & Speed")

print("\n3. DRAFT CONTENT: Generating Social Posts...")
content = bot.run_autonomous_loop(mock_event)

print("\n4. EXECUTE: Publishing...")
print(f"\n[LINKEDIN POST]\n{content['linkedin']}")
print(f"\n[X/TWITTER POST]\n{content['twitter']}")
print("\n--- CAMPAIGN COMPLETE ---")
