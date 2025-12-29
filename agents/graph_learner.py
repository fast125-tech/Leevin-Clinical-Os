import time
import spacy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from services.medical_graph import MedicalGraph

nlp = spacy.load("en_core_web_sm")

class GraphLearner:
    def __init__(self):
        self.graph = MedicalGraph()
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

    def learn_topic(self, term):
        print(f"🕵️ LEARNER: Extracting Graph Triples for '{term}'...")
        # Mocking a web read for demo speed (Replace with real scraper)
        text = f"{term} is a drug that treats severe pain. It belongs to the Opioid class."
        
        doc = nlp(text)
        for sent in doc.sents:
            if term in sent.text:
                root = sent.root
                for child in root.children:
                    if child.dep_ in ("attr", "dobj"):
                        print(f"   -> New Edge: ({term}) --[{root.lemma_}]--> ({child.text})")
                        self.graph.add_relationship(term, root.lemma_, child.text)
    
    def close(self):
        self.driver.quit()
