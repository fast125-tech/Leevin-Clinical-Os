from logic.cra_brain import BrainCRA

print("🧪 Testing BrainCRA (The Monitor)...")
monitor = BrainCRA()
print(f"✅ Loaded: {monitor.version}")

# Site 1: Low Risk (Clean)
metrics_101 = {'sdv': 100, 'queries': 0, 'saes': 0}
report_101 = monitor.generate_mvr("Site 101", metrics_101)
print(report_101)

# Site 102: Medium Risk (Messy but Safe)
metrics_102 = {'sdv': 85, 'queries': 8, 'saes': 0}
# Score: (8*2) + 0 = 16 -> Medium (>10)
report_102 = monitor.generate_mvr("Site 102", metrics_102)
print(report_102)

# Site 103: High Risk (Dangerous)
metrics_103 = {'sdv': 60, 'queries': 5, 'saes': 3}
# Score: (5*2) + (3*5) = 10 + 15 = 25 -> High (>20)
report_103 = monitor.generate_mvr("Site 103", metrics_103)
print(report_103)
