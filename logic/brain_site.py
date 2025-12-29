import pandas as pd
from datetime import datetime, timedelta

class BrainSite:
    def __init__(self):
        self.version = "SITE-1.6 (Burden Analysis)"

    def calculate_schedule(self, start_date, visits):
        if not start_date: return pd.DataFrame()
        anchor = start_date
        res = []
        for v in visits:
            target = anchor + timedelta(days=v['days'])
            window = v.get('window', 0)
            
            # Weekend Logic
            shifted = target
            note = "On Target"
            if target.weekday() == 5: # Sat
                shifted += timedelta(days=2) # Mon
                note = "Shifted (Sat->Mon)"
            elif target.weekday() == 6: # Sun
                shifted += timedelta(days=1) # Mon
                note = "Shifted (Sun->Mon)"
            
            # Window Check
            days_shifted = (shifted - target).days
            window_remaining = window - days_shifted
            
            status = "✅ OK"
            if window_remaining < 0:
                status = "❌ OUT OF WINDOW"
                note += " (Deviation!)"
            elif window_remaining == 0:
                status = "⚠️ CRITICAL"
                note += " (Last Day of Window)"
                
            res.append({
                "Visit": v['name'],
                "Target Date": target,
                "Adjusted Date": shifted,
                "Window End": target + timedelta(days=window),
                "Status": status,
                "Note": note
            })
        return pd.DataFrame(res)

    def analyze_burden(self, visits):
        # v1.6 Feature: Site Burden Analysis
        # Calculates complexity score based on procedures
        # Weights: MRI/CT=5, PK=3, Vitals=1, Lab=1, ECG=2
        weights = {"MRI": 5, "CT": 5, "PK": 3, "ECG": 2, "Vitals": 1, "Lab": 1, "Dispensing": 2}
        
        res = []
        for v in visits:
            procs = v.get('procedures', [])
            score = sum(weights.get(p, 1) for p in procs)
            
            status = "🟢 Low"
            if score > 10: status = "🔴 High"
            elif score > 5: status = "🟡 Medium"
            
            res.append({
                "Visit": v['name'],
                "Procedures": ", ".join(procs),
                "Burden Score": score,
                "Status": status
            })
        return pd.DataFrame(res)
