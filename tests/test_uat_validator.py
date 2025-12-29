import pandas as pd
import os
import sys

# Add root to sys.path
sys.path.append(os.getcwd())

from logic.uat_validator import validate_uat_results, generate_validation_pdf

def test_pdf_validator():
    print("--- 🧪 TESTING PDF VALIDATOR ---")
    
    # 1. Create Mock Data
    expected = pd.DataFrame([
        {"Subject": "101", "Field": "AGE", "Value": "25", "Scenario": "Set A (Clean)"},
        {"Subject": "102", "Field": "AGE", "Value": "300", "Scenario": "Set C (Failure)"} # Expecting Error
    ])
    
    actual = pd.DataFrame([
        {"Subject": "101", "Field": "AGE", "Value": "25"}, # Match
        {"Subject": "102", "Field": "AGE", "Value": ""}   # Empty (Blocked by Edit Check) -> Should PASS
    ])
    
    # 2. Run Logic
    print("Running Validation Logic...")
    res_df = validate_uat_results(expected, actual)
    print(res_df[['Subject', 'Status', 'Notes']])
    
    # Verify Status
    if res_df.iloc[0]['Status'] == 'PASS' and res_df.iloc[1]['Status'] == 'PASS':
        print("✅ Negative Test Logic Verified (Pass/Pass).")
    else:
        print("❌ Logic Failed.")
        
    # 3. Generate PDF
    print("Generating PDF...")
    pdf_path = generate_validation_pdf(res_df)
    
    if os.path.exists(pdf_path):
        print(f"✅ PDF Created: {pdf_path}")
        print(f"Size: {os.path.getsize(pdf_path)} bytes")
    else:
        print("❌ PDF Generation Failed.")

if __name__ == "__main__":
    test_pdf_validator()
