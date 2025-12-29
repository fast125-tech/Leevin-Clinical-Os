import sys
import os
import pandas as pd
from io import BytesIO
from logic.role_workflows import CDMWorkflows

# Add root
sys.path.append(os.getcwd())

print("📊 TESTING METRICS AGGREGATION LOGIC...")
print("-" * 60)

# Create Mock Files
def create_mock_csv(name, rows, sites):
    df = pd.DataFrame({
        "SubjectID": range(rows),
        "SiteID": [f"Site-{sites[i % len(sites)]}" for i in range(rows)],
        "Value": range(rows)
    })
    # Return as object with .name attribute (mocking Streamlit file buffer)
    buf = BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    buf.name = name
    return buf

try:
    # Scenario: Upload 3 files
    f1 = create_mock_csv("data1.csv", 10, ["101"])      # 10 rows, Site 101
    f2 = create_mock_csv("data2.csv", 20, ["102"])      # 20 rows, Site 102
    f3 = create_mock_csv("data3.csv", 5, ["101", "103"]) # 5 rows, Site 101, 103
    
    files = [f1, f2, f3]
    
    print(f"👉 Processing {len(files)} files...")
    metrics = CDMWorkflows.calculate_study_health(files)
    
    print("\n✅ RESULT:")
    for k, v in metrics.items():
        if k != "File Summary":
            print(f"  - {k}: {v}")
            
    # Visual Check
    expected_rows = 10 + 20 + 5 # 35
    expected_sites = 3 # 101, 102, 103
    
    if metrics["Total Records"] == expected_rows and metrics["Site Count"] == expected_sites:
         print("\n🎉 PASS: Aggregation Logic is Perfect.")
    else:
         print(f"\n❌ FAIL: Expected {expected_rows} rows, {expected_sites} sites.")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
