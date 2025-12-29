from agents.antigravity_engine import AntigravityCore

print("🚀 Initializing Antigravity Engine v2.0...")
core = AntigravityCore()

print("\n--- Diagnostic Report ---")
print(f"Scanner (BioBERT) Loaded: {core.scanner.nlp is not None}")
if core.scanner.nlp is None:
    print("   -> Running in Mock Mode (ML Libraries missing or model load failed)")

print(f"Synthetic Lab Ready: {core.lab is not None}")
print(f"Graph Reasoner Nodes: {core.brain.get_protocol_graph().number_of_nodes()}")
print(f"Cloud Bridge Connected: {core.cloud.is_connected()}")

print("\n✅ Antigravity Core Test Complete.")
