import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

DB_PATH = os.path.join(os.getcwd(), "medical_knowledge_db")

class MedicalKnowledgeBase:
    def __init__(self):
        # Connect to the SAME database the Researcher updates
        try:
            self.chroma_client = chromadb.PersistentClient(path=DB_PATH)
            # Use get_or_create just in case, though get is safer if we expect it to exist.
            # But to avoid error if it doesn't exist yet, get_or_create is better for robustness.
            self.collection = self.chroma_client.get_or_create_collection(name="medical_papers")
            self.embedding_fn = HuggingFaceEmbeddings(model_name="pritamdeka/S-PubMedBert-MS-MARCO")
        except Exception as e:
            print(f"Knowledge Bridge Init Error: {e}")
            # Non-blocking init for UI safety, but methods will fail if this fails.

    def get_medical_context(self, condition, medication):
        """
        Asks: 'What does the latest research say about [Condition] and [Medication]?'
        Returns: A paragraph of evidence.
        """
        try:
            query_text = f"Interaction between {condition} and {medication} side effects contraindications"
            query_vec = self.embedding_fn.embed_query(query_text)
            
            results = self.collection.query(
                query_embeddings=[query_vec],
                n_results=1 # Just get the top most relevant fact
            )
            
            if results and results['documents'] and results['documents'][0]:
                return results['documents'][0][0] # Return the text snippet
            return "No specific recent research found."
        except Exception as e:
            return f"Error retrieving context: {e}"
