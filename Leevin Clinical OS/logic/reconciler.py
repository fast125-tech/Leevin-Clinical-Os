import pandas as pd

def reconcile_datasets(df1, df2, key_col):
    """
    Reconciles two dataframes based on a key column.
    """
    mismatches = []
    
    # Ensure key exists
    if key_col not in df1.columns or key_col not in df2.columns:
        return pd.DataFrame({"Error": ["Key column not found in both datasets"]})
        
    # Merge
    merged = pd.merge(df1, df2, on=key_col, suffixes=('_EDC', '_Ext'), how='outer')
    
    # Find mismatches in other columns
    # (Simplified: check all common columns)
    common_cols = [c for c in df1.columns if c in df2.columns and c != key_col]
    
    for index, row in merged.iterrows():
        for col in common_cols:
            val1 = row[f"{col}_EDC"]
            val2 = row[f"{col}_Ext"]
            
            # Simple inequality check (can be enhanced with fuzzy logic)
            if str(val1) != str(val2):
                mismatches.append({
                    "SubjectID": row[key_col],
                    "Variable": col,
                    "EDC Value": val1,
                    "External Value": val2,
                    "Discrepancy": "Value Mismatch"
                })
                
    return pd.DataFrame(mismatches)
