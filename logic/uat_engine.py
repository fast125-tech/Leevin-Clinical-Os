import pandas as pd
import random
import datetime

# --- SYNTHETIC DATA GENERATOR (ADVANCED) ---

def generate_synthetic_uat_data(spec_df):
    """
    Generates 'Medically Plausible' synthetic data for UAT.
    Creates 3 Datasets per Study:
    - Set A: Clean Path (Valid, Normal Range)
    - Set B: Boundary Path (Min/Max Edges)
    - Set C: Failure Path (Triggers Edit Checks)
    
    Output Format: Medidata Rave Loader (Subject, Folder, Form, Field, Value)
    """
    uat_data = []
    
    # Define Scenarios
    scenarios = [
        {"Type": "Set A (Clean)", "Count": 5, "Prefix": "100"},
        {"Type": "Set B (Boundary)", "Count": 3, "Prefix": "200"},
        {"Type": "Set C (Failure)", "Count": 3, "Prefix": "900"}
    ]
    
    for scen in scenarios:
        for i in range(1, scen["Count"] + 1):
            subj_id = f"{scen['Prefix']}-{i:03d}"
            
            # Store subject-level context (for BMI calc, BP logic)
            subj_context = {} 
            
            # 1. First Pass: Generate Context Values (Height/Weight/SYSBP)
            # We iterate spec to find these first
            for _, row in spec_df.iterrows():
                field = str(row.get('Field', '')).upper()
                if field in ['HEIGHT', 'WEIGHT', 'SYSBP']:
                    val = _generate_smart_value(row, scen['Type'], subj_context)
                    subj_context[field] = val
            
            # 2. Second Pass: Generate All Values
            for _, row in spec_df.iterrows():
                form = row.get('Form', 'Common')
                field = row.get('Field', 'Unknown')
                
                # Check if we already generated it in context
                if str(field).upper() in subj_context:
                    val = subj_context[str(field).upper()]
                else:
                    val = _generate_smart_value(row, scen['Type'], subj_context)
                
                uat_data.append({
                    "Subject": subj_id,
                    "Folder": "SCREENING", # Default folder
                    "Form": form,
                    "Field": field,
                    "Value": val,
                    "Scenario": scen['Type'] # Extra col for validation logic, remove for pure Rave export
                })
                
    return pd.DataFrame(uat_data)

def _generate_smart_value(row, scenario_type, context):
    """
    Generates value based on Field Name (Medical Logic) or Data Type.
    """
    field = str(row.get('Field', '')).upper()
    dtype = str(row.get('Type', 'Text')).lower()
    min_v = float(row.get('Min', 0))
    max_v = float(row.get('Max', 100))
    codelist = str(row.get('Codelist', '')).split(',')
    
    # --- MEDICAL LOGIC ---
    
    # 1. BMI Calculation
    if field == 'BMI':
        try:
            h = float(context.get('HEIGHT', 170))
            w = float(context.get('WEIGHT', 70))
            if h > 0:
                bmi = w / ((h/100)**2)
                return round(bmi, 1)
        except:
            return 24.5 # Fallback
            
    # 2. Diastolic BP (Must be < Systolic)
    if field == 'DIABP':
        try:
            sys = float(context.get('SYSBP', 120))
            if "Clean" in scenario_type:
                return int(sys - random.randint(30, 50))
            elif "Boundary" in scenario_type:
                return int(sys - 10) # Narrow pulse pressure
            else: # Failure
                return int(sys + 10) # IMPOSSIBLE (Diastolic > Systolic)
        except:
            return 80

    # --- STANDARD LOGIC ---
    
    if "Clean" in scenario_type:
        if "number" in dtype:
            # Safe middle range
            mid = (min_v + max_v) / 2
            return round(random.normalvariate(mid, (max_v-min_v)/6), 1)
        if "date" in dtype:
            return (datetime.date.today() - datetime.timedelta(days=random.randint(1, 30))).strftime("%d-%b-%Y").upper()
        if "codelist" in dtype and codelist:
            return random.choice(codelist).strip()
        return "Valid Data"
        
    elif "Boundary" in scenario_type:
        if "number" in dtype:
            return random.choice([min_v, max_v])
        if "date" in dtype:
            return datetime.date.today().strftime("%d-%b-%Y").upper() # Today
        return "Boundary_Text"
        
    else: # Failure
        if "number" in dtype:
            return max_v + random.randint(1, 100) # Exceed Max
        if "date" in dtype:
            return "01-JAN-2099" # Future date
        if "codelist" in dtype:
            return "INVALID_CODE"
        return "X" * 256 # Text overflow

