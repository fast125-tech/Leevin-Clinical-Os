"""
ANTIGRAVITY ENGINE v2.0 (Leevin Clinical OS)
------------------------------------------------
Consolidated Logic Kernel containing:
1. BioBERT Scanner (Medical NER)
2. Synthetic Data Lab (Digital Twins)
3. GraphOS (NetworkX Reasoning)
4. Cloud Bridge (Google Drive Sync)
"""

import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import random
from faker import Faker
from datetime import datetime, timedelta

# --- LIBRARY CHECKS (Graceful Degradation) ---
try:
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML Libraries not found. BioBERT will run in 'Mock Mode'.")

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    CLOUD_AVAILABLE = True
except ImportError:
    CLOUD_AVAILABLE = False

# ==========================================
# 1. THE BIOMEDICAL SCANNER (BioBERT)
# ==========================================
class BioMedicalScanner:
    def __init__(self):
        self.model_name = "alvaroalon2/biobert_chemical_ner"
        self.nlp = None
        if ML_AVAILABLE:
            print("🧠 Loading BioBERT (this may take a moment)...")
            try:
                tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                model = AutoModelForTokenClassification.from_pretrained(self.model_name)
                self.nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
                print("✅ BioBERT Loaded.")
            except Exception as e:
                print(f"❌ BioBERT Load Failed: {e}")

    def scan_text(self, text):
        """Returns list of medical entities (Drugs/Chemicals) found in text."""
        if not text: return []
        if not self.nlp: return [{"Term": "Mock Drug", "Type": "Chemical", "Confidence": 0.99}] # Fallback
        
        results = self.nlp(text)
        entities = []
        for r in results:
            if r['score'] > 0.85: # High confidence only
                entities.append({
                    "Term": r['word'],
                    "Type": r['entity_group'],
                    "Confidence": round(float(r['score']), 2)
                })
        return entities

# ==========================================
# 2. THE SYNTHETIC DATA LAB (Generator)
# ==========================================
class SyntheticLab:
    def __init__(self):
        self.fake = Faker()

    def generate_patients(self, n=10, error_rate=0.2):
        """Creates 'Digital Twin' patients with intentional protocol errors."""
        data = []
        for i in range(n):
            pat_id = f"SUB-{1000+i}"
            age = random.randint(18, 65)
            status = "Enrolled"
            
            # Inject Error
            if random.random() < error_rate:
                age = random.randint(10, 17) # Protocol Violation (Underage)
                status = "Screen Failure"
            
            data.append({
                "SubjectID": pat_id,
                "Age": age,
                "Gender": random.choice(["M", "F"]),
                "EnrollmentDate": self.fake.date_between(start_date='-1y', end_date='today'),
                "Status": status
            })
        return pd.DataFrame(data)

# ==========================================
# 3. GRAPH_OS (Reasoning Kernel)
# ==========================================
class GraphReasoningEngine:
    def __init__(self):
        self.G = nx.DiGraph()
        self._initialize_knowledge()

    def _initialize_knowledge(self):
        # Basic Medical Logic Graph
        self.G.add_edge("Ibuprofen", "NSAID", relation="is_a")
        self.G.add_edge("NSAID", "Kidney Failure", relation="risk_factor")
        self.G.add_edge("Visit 1", "Week 0", relation="timing")

    def trace_logic(self, drug, condition):
        """Walks the graph to find conflicts."""
        paths = []
        # Simple Mock Logic for Demo
        if drug == "Ibuprofen" and "Kidney" in condition:
            paths.append("⚠️ LOGIC TRAIL: Ibuprofen -> is NSAID -> Risk for Kidney Failure")
        return paths

    def get_protocol_graph(self):
        """Returns the graph object for visualization."""
        return self.G

# ==========================================
# 4. CLOUD BRIDGE (Google Drive)
# ==========================================
class CloudBridge:
    def __init__(self):
        self.key_path = "antigravity_files/service_account.json"
        self.service = None
        if CLOUD_AVAILABLE and os.path.exists(self.key_path):
            try:
                creds = service_account.Credentials.from_service_account_file(
                    self.key_path, scopes=['https://www.googleapis.com/auth/drive.file'])
                self.service = build('drive', 'v3', credentials=creds)
            except Exception: pass

    def is_connected(self):
        return self.service is not None

# ==========================================
# 5. THE MASTER CORE
# ==========================================
class AntigravityCore:
    def __init__(self):
        self.scanner = BioMedicalScanner()
        self.lab = SyntheticLab()
        self.brain = GraphReasoningEngine()
        self.cloud = CloudBridge()
