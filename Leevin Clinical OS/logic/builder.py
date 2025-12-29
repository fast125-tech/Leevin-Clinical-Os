import pandas as pd

def generate_uat_script(spec_df):
    """
    Generates a UAT script based on the specification dataframe.
    """
    steps = []
    
    # Mock Logic: Iterate through spec rows and create test steps
    if isinstance(spec_df, pd.DataFrame):
        for index, row in spec_df.iterrows():
            field = row.get('FieldOID', 'Unknown')
            label = row.get('Label', 'Unknown')
            
            steps.append({
                "ScenarioID": f"UAT-{index+1:03d}",
                "Step Description": f"Navigate to form. Enter '{label}' ({field}).",
                "Expected Result": "Field accepts value. No error displayed.",
                "Pass/Fail": ""
            })
            
    return pd.DataFrame(steps)
