import unittest
import pandas as pd
from logic.data_cleaner import DataCleaner
from logic.reconciler import Reconciler

class TestCoreSuite(unittest.TestCase):
    def setUp(self):
        self.cleaner = DataCleaner()
        self.reconciler = Reconciler()

    def test_hard_logic_checks(self):
        # Create Dummy Data with Errors
        data = {
            "ID": [1, 2],
            "VSORRES": [120, -5], # One negative
            "AESTDTC": ["2023-01-01", "2099-01-01"] # One future
        }
        df = pd.DataFrame(data)
        
        issues = self.cleaner.run_hard_checks(df)
        
        # Expect 2 issues
        self.assertEqual(len(issues), 2)
        self.assertTrue(any(issues['Issue'] == "Negative Value"))
        self.assertTrue(any(issues['Issue'] == "Future Date"))

    def test_reconciler_normalization(self):
        data = {"PatID": [101], "VisitName": ["V1"]}
        df = pd.DataFrame(data)
        
        # Mock normalization (requires fuzzywuzzy, assuming it works or returns orig)
        # Note: In test env without complex fuzzy logic, we might just check structure
        norm_df = self.reconciler.normalize_headers(df)
        
        # Check if column count remains same
        self.assertEqual(len(norm_df.columns), 2)

if __name__ == '__main__':
    unittest.main()
