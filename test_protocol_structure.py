import sys
import os
from logic.agent_logic import generate_protocol_draft

sys.path.append(os.getcwd())

print("📜 TESTING PROTOCOL STRUCTURE GENERATION...")
print("-" * 60)

# Dummy Input
title = "A Phase IV Study of Secukinumab in Psoriatic Arthritis"
context = "Focus on long-term safety and ACR20 response."

print("👉 Generating Draft (This may take 30s)...")
draft = generate_protocol_draft("Phase IV", "Randomized", title, context)

print("\n✅ GENERATION COMPLETE. SCANNING FOR MANDATORY HEADERS...")

required_headers = [
    "Property of [SPONSOR] Confidential",
    "1. Introduction",
    "1.1 Background",
    "2. Study Objectives",
    "3. Investigational Plan",
    "3.3 Rationale for Dose",
    "4. Population",
    "6. Visit Schedule and Assessments",
    "Table 6-1",
    "12.1 Appendix 1"
]

missing = []
for h in required_headers:
    if h in draft:
        print(f"  [OK] Found: '{h}'")
    else:
        print(f"  [MISSING] '{h}'")
        missing.append(h)

if not missing:
    print("\n🎉 SUCCESS: All Novartis Protocol Sections Present.")
else:
    print(f"\n❌ FAIL: Missing {len(missing)} Sections.")
