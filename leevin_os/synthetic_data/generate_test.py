
import pandas as pd
import random
from datetime import datetime, timedelta

def generate_stress_test_data(rows=50):
    """
    Generates a 'Dirty' dataset to prove the Cleaner works.
    Includes:
    1. Duplicates
    2. Future Dates
    3. Impossible Vitals (Negative BP)
    4. Logical Fallacies (Male + Pregnancy)
    """
    
    data = []
    base_date = datetime.now()
    
    for i in range(rows):
        # Default Clean Row
        row = {
            "SubjectID": f"101-{i:03d}",
            "VisitDate": (base_date - timedelta(days=i)).strftime("%Y-%m-%d"),
            "Sex": random.choice(["M", "F"]),
            "Age": random.randint(18, 85),
            "SysBP": random.randint(110, 140),
            "DiaBP": random.randint(70, 90),
            "Comment": "Routine visit."
        }
        
        # Inject TRAPS (every 10th row)
        if i % 10 == 0:
            trap_type = random.choice(["FUTURE_DATE", "NEGATIVE_BP", "LOGIC_FAIL"])
            
            if trap_type == "FUTURE_DATE":
                row["VisitDate"] = (base_date + timedelta(days=365)).strftime("%Y-%m-%d")
                row["Comment"] = "Patient scheduled for next year? (Trap)"
                
            elif trap_type == "NEGATIVE_BP":
                row["SysBP"] = -120
                row["Comment"] = "Typo in BP. (Trap)"
                
            elif trap_type == "LOGIC_FAIL":
                row["Sex"] = "M"
                row["Comment"] = "Patient is pregnant." # AI should catch this context if sophisticated
        
        data.append(row)
        
    # Inject Duplicate
    data.append(data[0]) 
    
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = generate_stress_test_data()
    df.to_csv("stress_test_data.csv", index=False)
    print("✅ Stress Data Generated.")
