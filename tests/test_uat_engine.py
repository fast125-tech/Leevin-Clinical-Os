import pandas as pd
import os
import sys

# Add root to sys.path
sys.path.append(os.getcwd())

from logic.uat_engine import generate_synthetic_uat_data

def test_uat_engine():
    print("--- 🧪 TESTING ADVANCED UAT ENGINE ---")
    
    # 1. Create Mock Spec
    df_spec = pd.DataFrame([
        {"Form": "Demography", "Field": "AGE", "Type": "Number", "Min": 18, "Max": 65},
        {"Form": "Vitals", "Field": "SYSBP", "Type": "Number", "Min": 90, "Max": 140},
        {"Form": "Vitals", "Field": "DIABP", "Type": "Number", "Min": 60, "Max": 90}, 
        {"Form": "Vitals", "Field": "HEIGHT", "Type": "Number", "Min": 150, "Max": 200},
        {"Form": "Vitals", "Field": "WEIGHT", "Type": "Number", "Min": 50, "Max": 100},
        {"Form": "Vitals", "Field": "BMI", "Type": "Number"}, # Derived
    ])
    
    # 2. Run Generator
    print("\nGenerating Synthetic Data...")
    df_result = generate_synthetic_uat_data(df_spec)
    
    print(f"Generated {len(df_result)} records.")
    print(df_result.head(10))
    
    # 3. Validations
    col_check = "Subject" in df_result.columns and "Scenario" in df_result.columns
    print(f"Columns Correct (Subject, Scenario): {col_check}")
    
    scenarios = list(df_result['Scenario'].unique())
    print(f"Scenarios: {scenarios}")
    
    has_clean = any("Clean" in s for s in scenarios)
    has_fail = any("Failure" in s for s in scenarios)
    
    if has_clean and has_fail:
        print("✅ Scenario Coverage Verified.")
    else:
        print("❌ Scenarios Missing.")
        
    # 4. Check Context Logic (BMI)
    # Check if BMI exists and is roughly valid in Clean set
    clean_bmi = df_result[(df_result['Field']=='BMI') & (df_result['Scenario'].str.contains("Clean"))]
    if not clean_bmi.empty:
        val = float(clean_bmi.iloc[0]['Value'])
        print(f"Sample Clean BMI: {val}")
        if 15 < val < 40:
            print("✅ BMI looks medically plausible.")
        else:
            print(f"⚠️ BMI {val} suspicious.")
            
    print("\n🏁 Engine Test Complete.")

if __name__ == "__main__":
    test_uat_engine()
