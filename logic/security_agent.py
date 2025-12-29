import pandas as pd
import re
from services.security_log import log_security_event

class SecuritySentinel:
    def __init__(self):
        # Regex Patterns for PHI
        self.patterns = {
            "Email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "Phone": r'(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}',
            "SSN": r'\d{3}-\d{2}-\d{4}',
            # "MRN": r'MRN\d+' # Example custom pattern
        }
        
        self.high_risk_headers = ["name", "ssn", "social", "dob", "birth", "address", "phone", "email"]

    def scan_dataframe(self, df, filename, user="Unknown"):
        """
        Scans a DataFrame for PHI.
        Returns: (is_safe: bool, message: str)
        """
        issues = []
        
        # 1. Header Scan (Heuristic)
        for col in df.columns:
            if any(risk in col.lower() for risk in self.high_risk_headers):
                issues.append(f"High Risk Column Header found: '{col}'")
                
        # 2. Data Scan (Content)
        # Check first 50 rows for speed
        subset = df.head(50)
        
        # Convert all to string for regex matching
        text_data = subset.to_string()
        
        for p_name, pattern in self.patterns.items():
            if re.search(pattern, text_data):
                issues.append(f"Pattern Match Detected: {p_name}")
                
        if issues:
            # LOG THE INCIDENT
            details = "; ".join(issues)
            log_security_event(user, "SECURITY_BLOCK", details, filename)
            return False, f"🚨 SECURITY BLOCK: PHI Detected ({details}). Remove this data before processing."
            
        return True, "✅ File Scan Passed."
