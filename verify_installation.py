import sys
import os

print("🔍 VERIFICATION START: Checking imports...")

try:
    print("   - Importing networkx...", end=" ")
    import networkx
    print("OK")
    
    print("   - Importing spacy...", end=" ")
    import spacy
    print("OK")
    
    print("   - Importing selenium...", end=" ")
    from selenium import webdriver
    print("OK")
    
    print("   - Importing schedule...", end=" ")
    import schedule
    print("OK")

    print("\n🔍 VERIFICATION: Checking local modules...")
    
    print("   - services.medical_graph...", end=" ")
    from services.medical_graph import MedicalGraph
    mg = MedicalGraph()
    print("OK")
    
    print("   - agents.graph_learner...", end=" ")
    from agents.graph_learner import GraphLearner
    # We won't init GraphLearner as it launches Chrome which might fail in this headless verification without paths set up, 
    # but the import confirms the file is good.
    print("OK")
    
    print("   - agents.cdm_master_recon...", end=" ")
    from agents.cdm_master_recon import MasterCDM
    cdm = MasterCDM()
    print("OK")
    
    print("   - agents.marketing_agent...", end=" ")
    from agents.marketing_agent import GrowthAgent
    ga = GrowthAgent()
    print("OK")

    print("\n✅ VERIFICATION COMPLETE: All modules load correctly.")

except ImportError as e:
    print(f"\n❌ ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
