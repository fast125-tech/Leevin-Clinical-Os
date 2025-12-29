
import streamlit as st
from sentence_transformers import SentenceTransformer, util
import torch

class ClinicalBertService:
    """
    BRAIN 2: PREMIUM SPECIALIST
    Model: emilyalsentzer/Bio_ClinicalBERT (via SentenceTransformer wrapper if available, else mini-lm for speed)
    Role: Medical Auto-Coding & Semantic Search.
    Constraint: 4GB Memory Optimized.
    """
    
    @staticmethod
    @st.cache_resource(show_spinner=True)
    def load_brain():
        """
        Loads the Model ONCE and persists it in memory.
        Uses 'all-MiniLM-L6-v2' for mock-up speed or a clinical specific model if requested.
        Note: True Bio_ClinicalBERT is heavy. Using a lighter clinical-tuned sentence transformer
        is better for Cloud Run unless 4GB is strictly guaranteed.
        
        Using: 'pritamdeka/S-PubMedBert-MS-MARCO' (High accuracy for medical, ~400MB)
        """
        try:
            device = 'cpu' # Cloud Run is CPU by default
            # Loading a robust medical sentence transformer
            model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO', device=device)
            return model
        except Exception as e:
            # Fallback
            return SentenceTransformer('all-MiniLM-L6-v2', device=device)

    def __init__(self):
        self.model = self.load_brain()
        
    def encode(self, text):
        return self.model.encode(text, convert_to_tensor=True)
        
    def compute_similarity(self, source_text, target_list):
        """
        Matrix Match: Finds best match for source_text in target_list.
        Returns: (Best Match String, Confidence Score float)
        """
        source_vec = self.encode(source_text)
        target_vecs = self.encode(target_list)
        
        # Cosine Similarity
        scores = util.cos_sim(source_vec, target_vecs)
        
        # Find max
        best_score_idx = torch.argmax(scores)
        best_score = scores[0][best_score_idx].item()
        best_match = target_list[best_score_idx]
        
        return best_match, best_score

    def auto_code_adverse_event(self, term, dictionary):
        """
        Brain 2 Logic: 
        If Conf > 0.85 -> Accept.
        Else -> Flag.
        """
        match, score = self.compute_similarity(term, dictionary)
        
        status = "Auto-Coded" if score > 0.85 else "Review Needed"
        return {
            "Term": term,
            "Match": match,
            "Confidence": round(score, 4),
            "Status": status
        }
