import sys
import os
from logic.role_workflows import OncologyWorkflows

sys.path.append(os.getcwd())

print("🩺 TESTING ONCOLOGY LOGIC (RECIST 1.1)...")
print("-" * 60)

scenarios = [
    # (Base, Nadir, Curr, NewLesions, Expected)
    (100, 100, 0, False, "CR"),         # Complete Response
    (100, 100, 65, False, "PR"),        # -35% (Target > -30%)
    (100, 100, 80, False, "SD"),        # -20% (Not PR, Not PD)
    (100, 60, 75, False, "PD"),         # +15mm and +25% from Nadir (PD)
    (50, 50, 52, False, "SD"),          # +4% (Not PD)
    (100, 50, 52, True, "PD"),          # New Lesions = PD always
]

failures = 0

for i, (b, n, c, nl, exp) in enumerate(scenarios):
    res = OncologyWorkflows.calculate_recist(b, n, c, nl)
    outcome = res["Response"]
    
    print(f"Test {i+1}: B={b}, N={n}, C={c}, New={nl} -> Got: {outcome.split(' ')[0]}")
    
    if not outcome.startswith(exp):
        print(f"❌ FAIL: Expected {exp}, Got {outcome}")
        failures += 1

if failures == 0:
    print("\n✅ RECIST CALCULATOR: ALL PASS")
else:
    print(f"\n❌ FAILED {failures} TESTS")
