class RecistCalculator:
    def __init__(self):
        pass

    def validate_baseline(self, lesions):
        """
        Validates Baseline Lesions against RECIST 1.1.
        
        Rules:
        - Solid Tumor: Must be >= 10mm (Long Diameter).
        - Lymph Node: Must be >= 15mm (Short Axis).
        - Max Targets: 5 Total, 2 per Organ.
        """
        valid_lesions = []
        rejected_lesions = []
        organ_counter = {}
        
        for lesion in lesions:
            # Type Check
            l_type = lesion.get('type', 'Solid')
            size = float(lesion.get('size', 0))
            organ = lesion.get('organ', 'Unknown')
            
            # Size Check
            is_valid_size = False
            if l_type == 'Solid' and size >= 10:
                is_valid_size = True
            elif l_type == 'Node' and size >= 15:
                is_valid_size = True
            
            if not is_valid_size:
                rejected_lesions.append(f"{l_type} in {organ} too small ({size}mm)")
                continue
                
            # Organ Count Check
            if organ not in organ_counter:
                organ_counter[organ] = 0
            
            if organ_counter[organ] >= 2:
                rejected_lesions.append(f"Organ cap exceeded for {organ}")
                continue
                
            # Total Cap Check
            if len(valid_lesions) >= 5:
                rejected_lesions.append("Total Target Limit (5) exceeded")
                continue
                
            # Accept
            organ_counter[organ] += 1
            valid_lesions.append(lesion)
            
        return {
            "valid": valid_lesions,
            "rejected": rejected_lesions,
            "baseline_sum": sum([float(l['size']) for l in valid_lesions])
        }

    def calculate_target_response(self, baseline_sum, current_sum):
        """
        Determines Response for TARGET lesions.
        """
        if baseline_sum == 0:
            return "NE"
            
        diff = current_sum - baseline_sum
        pct_change = (diff / baseline_sum) * 100
        
        # CR: 0mm (Special handling for nodes <10mm needed in real life, assuming 0 for now)
        if current_sum == 0:
            return "CR"
            
        # PD: >= 20% increase AND >= 5mm absolute increase
        if pct_change >= 20 and diff >= 5:
            return "PD"
            
        # PR: >= 30% decrease
        if pct_change <= -30:
            return "PR"
            
        return "SD"

    def determine_overall_response(self, target_resp, non_target_resp, new_lesions):
        """
        The Master RECIST Matrix.
        """
        # 1. New Lesions kills everything
        if new_lesions:
            return "PD"
            
        # 2. Target Driven
        if target_resp == "PD":
            return "PD"
            
        if non_target_resp == "PD":
            return "PD"
            
        if target_resp == "CR":
            if non_target_resp == "CR":
                return "CR"
            else:
                # Non-Target is Non-CR/Non-PD or Not Evaluated
                return "PR"
                
        if target_resp == "PR":
            # Non-Target cannot be PD (already checked)
            return "PR"
            
        if target_resp == "SD":
            return "SD"
            
        # Fallback
        return "NE"
