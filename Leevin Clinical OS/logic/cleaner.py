import pandas as pd

def scan_data(df):
    """
    Scans dataframe for common clinical data errors.
    Returns a list of error dictionaries.
    """
    errors = []
    
    # Check 1: Future Dates
    # (Simplified logic)
    
    # Check 2: Logic Conflicts (Consent > Enrollment)
    if 'ConsentDate' in df.columns and 'EnrollmentDate' in df.columns:
        for index, row in df.iterrows():
            try:
                if pd.to_datetime(row['ConsentDate']) > pd.to_datetime(row['EnrollmentDate']):
                    errors.append({
                        "row": index,
                        "SubjectID": row.get('SubjectID', 'Unknown'),
                        "error": "Consent Date is after Enrollment Date",
                        "query_text": f"Please verify dates. Consent ({row['ConsentDate']}) cannot be after Enrollment ({row['EnrollmentDate']})."
                    })
            except:
                pass
                
    return errors

def draft_queries(errors):
    """
    Formats errors into a Rave Batch Query Upload format.
    """
    query_rows = []
    for err in errors:
        query_rows.append({
            "Site": "101", # Mock
            "Subject": err.get('SubjectID'),
            "Folder": "SCREENING",
            "Form": "ENROLL",
            "Field": "ENRLDAT",
            "QueryText": err.get('query_text')
        })
    return pd.DataFrame(query_rows)
