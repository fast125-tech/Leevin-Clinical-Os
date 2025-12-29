
import sys
import os
sys.path.append(os.getcwd())

from logic.digitizer_engine import ProtocolDigitizer

print("🚀 Testing Protocol Digitizer...")

try:
    engine = ProtocolDigitizer()
    if not engine.connected:
        print("⚠️ Engine not connected.")
        sys.exit(1)
        
    print("Reading test_protocol.pdf...")
    engine = ProtocolDigitizer()
    text = engine.extract_text("test_protocol.pdf")
    print(f"--- EXTRACTED TEXT ({len(text)} chars) ---")
    print(text)
    print("-------------------------------------------")

    res = engine.digitize_protocol("test_protocol.pdf")
    
    print("\n--- JSON OUTPUT ---")
    print(res)
    
    if "visit_schedule" in res and len(res["visit_schedule"]) > 0:
        print("\n✅ SUCCESS: Extracted Visits!")
        for v in res["visit_schedule"]:
            print(f"  - {v['visit_label']} (Week {v['week']})")
    else:
        print("\n❌ FAILURE: No visit schedule extracted.")

except Exception as e:
    print(f"❌ ERROR: {e}")
