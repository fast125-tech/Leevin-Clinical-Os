import streamlit as st
import chromadb
from Bio import Entrez
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
import pandas as pd
from datetime import datetime
import os

# CONFIGURATION
Entrez.email = "researcher@leevin.os"  # Required by PubMed
# Use absolute path or relative to CWD correctly. 
# Since app runs from root, "./medical_knowledge_db" works if run from root.
DB_PATH = os.path.join(os.getcwd(), "medical_knowledge_db")

class AsclepiusAgent:
    def __init__(self):
        # 1. Initialize Memory (Vector DB)
        try:
            self.chroma_client = chromadb.PersistentClient(path=DB_PATH)
            self.collection = self.chroma_client.get_or_create_collection(name="medical_papers")
        except Exception as e:
            st.error(f"Failed to initialize ChromaDB: {e}")
            raise e
        
        # 2. Initialize The Surgeon (Embedding Model)
        # Using a specialized medical model for better accuracy
        try:
            self.embedding_fn = HuggingFaceEmbeddings(model_name="pritamdeka/S-PubMedBert-MS-MARCO")
        except Exception as e:
            st.error(f"Failed to load Embedding Model: {e}")
            raise e

    def search_pubmed(self, query, max_results=5):
        """The Scout: Browses PubMed for new studies."""
        st.toast(f"🕵️ Scout is browsing PubMed for: {query}...")
        
        try:
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results, sort="date")
            record = Entrez.read(handle)
            id_list = record["IdList"]
            
            if not id_list:
                return ""
            
            # Fetch details
            handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="text")
            papers = handle.read()
            return papers
        except Exception as e:
            st.error(f"PubMed Search Failed: {e}")
            return ""

    def upgrade_knowledge(self, topic):
        """The Loop: Search -> Slice -> Inject."""
        raw_text = self.search_pubmed(topic)
        
        if not raw_text:
            return 0

        # Split text into digestible chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(raw_text)
        
        if not chunks:
            return 0
        
        # Embed and Store
        st.toast(f"🧠 Ingesting {len(chunks)} new knowledge chunks...")
        
        # Unique IDs based on timestamp
        ids = [f"{topic}_{datetime.now().isoformat()}_{i}" for i in range(len(chunks))]
        embeddings = self.embedding_fn.embed_documents(chunks)
        
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=[{"source": "PubMed", "topic": topic} for _ in chunks]
        )
        return len(chunks)

    def query_knowledge(self, question):
        """The Doctor: Answers based ONLY on upgraded knowledge."""
        try:
            query_vec = self.embedding_fn.embed_query(question)
            results = self.collection.query(query_embeddings=[query_vec], n_results=3)
            
            if results and results['documents'] and results['documents'][0]:
                context = "\n\n".join(results['documents'][0])
                return context
            else:
                return "No relevant knowledge found in local database."
        except Exception as e:
            return f"Error querying knowledge base: {e}"
