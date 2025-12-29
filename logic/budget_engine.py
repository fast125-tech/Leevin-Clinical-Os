class BudgetSimulator:
    def __init__(self):
        # Mock CPT Cost Database (USD)
        self.CPT_COST_DB = {
            "MRI": 800,
            "CT Scan": 600,
            "PET Scan": 1200,
            "Blood Draw": 50,
            "CBC": 20,
            "Chem Panel": 30,
            "PK Sample": 100,
            "Biopsy": 1500,
            "ECG": 100,
            "Physical Exam": 150,
            "Vitals": 20,
            "Informed Consent": 100, # Admin cost
            "Dispensing": 50,
            "Standard Visit": 500 # Overhead
        }

    def calculate_estimates(self, procedures_list: list, num_patients: int):
        """
        Calculates budget estimates based on list of procedures derived from SoA.
        """
        total_per_patient = 0
        breakdown = {}
        
        # Add basic visit overhead for each procedure 'event' assumption 
        # (simplified: assuming list implies unique visits or events)
        # Better: User inputs "Number of Visits".
        # For MVP, we'll assume procedures_list comes from extracting the SoA, 
        # so it represents ONE patient's journey.
        
        for proc in procedures_list:
            # Fuzzy match or direct lookup
            cost = 0
            matched_key = "Misc"
            
            # Simple keyword matching
            for key, val in self.CPT_COST_DB.items():
                if key.lower() in proc.lower():
                    cost = val
                    matched_key = key
                    break
            
            if cost == 0:
                # Default for unknown procedure
                cost = 100 
                matched_key = "Unspecified Procedure"
                
            total_per_patient += cost
            
            if matched_key in breakdown:
                breakdown[matched_key] += cost
            else:
                breakdown[matched_key] = cost
                
        total_study = total_per_patient * num_patients
        
        return {
            "per_patient": total_per_patient,
            "total_study": total_study,
            "breakdown": breakdown
        }
