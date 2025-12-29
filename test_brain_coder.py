from logic.coder_brain import BrainCoder

print("🧪 Testing BrainCoder (The Translator)...")
coder = BrainCoder()
print(f"✅ Loaded: {coder.version}")

# Test Cases
terms = ["BLUE SKIN", "HIGH BP", "SUGAR", "UNKNOWN TERM"]

print("\n--- Drafting Queries ---")
for term in terms:
    print(f"\n[Input]: {term}")
    print(f"[Query]:\n{coder.draft_query(term)}")
    print("-" * 30)
