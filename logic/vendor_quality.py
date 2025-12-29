import pandas as pd
from datetime import datetime
try:
    from google.cloud import firestore
except:
    firestore = None

class VendorScorecard:
    def __init__(self):
        self.use_firestore = False
        self.db = None
        self.local_db = {} # Always init
        
        # Try connecting to Firestore
        try:
            self.db = firestore.Client()
            self.use_firestore = True
        except:
            # Fallback to local Session State in UI or just volatile memory for demo
            self.use_firestore = False

    def log_upload_quality(self, vendor_name, total_rows, error_count):
        """
        Logs an upload event and its quality metrics.
        """
        error_rate = (error_count / total_rows) * 100 if total_rows > 0 else 0
        clean_rate = 100 - error_rate
        
        record = {
            "timestamp": datetime.now(),
            "vendor": vendor_name,
            "total_rows": total_rows,
            "error_count": error_count,
            "clean_rate": round(clean_rate, 2)
        }
        
        # Dual Write or Fallback
        if self.use_firestore:
            try:
                # Add to 'vendor_uploads' collection
                self.db.collection("vendor_uploads").add(record)
            except Exception as e:
                print(f"Firestore Error: {e}")
                # Fallback write to local if firestore write fails
                if vendor_name not in self.local_db:
                    self.local_db[vendor_name] = []
                self.local_db[vendor_name].append(record)
        else:
            # Local Mock
            if vendor_name not in self.local_db:
                self.local_db[vendor_name] = []
            self.local_db[vendor_name].append(record)

    def get_leaderboard(self):
        """
        Returns a DataFrame of Vendor Performance.
        """
        all_records = []
        
        if self.use_firestore:
            try:
                docs = self.db.collection("vendor_uploads").stream()
                for doc in docs:
                    all_records.append(doc.to_dict())
            except:
                pass
        
        # If firestore empty or failed, use mock data/local db
        if not all_records:
             if self.local_db:
                 for v, recs in self.local_db.items():
                     all_records.extend(recs)
             else:
                 # Demo Data
                 all_records = [
                     {"vendor": "LabCorp", "clean_rate": 98.5, "total_rows": 5000},
                     {"vendor": "BioClinica", "clean_rate": 92.0, "total_rows": 3000},
                     {"vendor": "Local Labs", "clean_rate": 84.3, "total_rows": 1200}
                 ]

        if not all_records:
            return pd.DataFrame()

        df = pd.DataFrame(all_records)
        
        # Group by Vendor
        leaderboard = df.groupby("vendor").agg({
            "clean_rate": "mean",
            "total_rows": "sum"
        }).reset_index()
        
        leaderboard = leaderboard.sort_values(by="clean_rate", ascending=False)
        return leaderboard
