from logic.site_brain import BrainSite
from datetime import datetime, timedelta

print("🧪 Testing BrainSite (The Coordinator)...")
coordinator = BrainSite()
print(f"✅ Loaded: {coordinator.version}")

# Setup: Start on a Monday (Jan 1, 2024 was a Monday)
start_date = datetime(2024, 1, 1).date()

# Scenario:
# Visit 1: Day 4 (Friday, Jan 5) -> No Shift
# Visit 2: Day 5 (Saturday, Jan 6) -> Shift to Mon, Jan 8 (+2)
# Visit 3: Day 6 (Sunday, Jan 7) -> Shift to Mon, Jan 8 (+1)
# Visit 4: Day 13 (Sunday, Jan 14) -> Shift to Mon, Jan 15 (+1)

visits = [
    {'name': 'Visit 1', 'days': 4},
    {'name': 'Visit 2', 'days': 5},
    {'name': 'Visit 3', 'days': 6},
    {'name': 'Visit 4', 'days': 13}
]

print("\n--- Calculating Schedule ---")
df = coordinator.calculate_schedule(start_date, visits)

print(df)

# Assertions
print("\n--- Verifying Logic ---")
v2 = df[df['Visit'] == 'Visit 2'].iloc[0]
v3 = df[df['Visit'] == 'Visit 3'].iloc[0]

if v2['Adjusted'].weekday() == 0 and "Shifted" in v2['Note']:
    print(f"✅ Visit 2 (Sat) correctly shifted to {v2['Adjusted']} ({v2['Note']})")
else:
    print(f"❌ Visit 2 logic FAILED: {v2['Adjusted']} ({v2['Note']})")

if v3['Adjusted'].weekday() == 0 and "Shifted" in v3['Note']:
    print(f"✅ Visit 3 (Sun) correctly shifted to {v3['Adjusted']} ({v3['Note']})")
else:
    print(f"❌ Visit 3 logic FAILED: {v3['Adjusted']} ({v3['Note']})")
