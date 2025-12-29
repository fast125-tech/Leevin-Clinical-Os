import unittest
from logic.recist_engine import RecistCalculator

class TestRecist(unittest.TestCase):
    def setUp(self):
        self.calc = RecistCalculator()

    def test_baseline_validation(self):
        lesions = [
            {"type": "Solid", "size": 5, "organ": "Liver"}, # Reject (<10)
            {"type": "Solid", "size": 20, "organ": "Lung"}, # Keep
            {"type": "Node", "size": 12, "organ": "Neck"}, # Reject (<15)
            {"type": "Node", "size": 16, "organ": "Neck"} # Keep
        ]
        res = self.calc.validate_baseline(lesions)
        self.assertEqual(len(res['valid']), 2)
        self.assertEqual(res['baseline_sum'], 36.0)

    def test_pd_logic(self):
        # 20% increase but < 5mm absolute -> SD
        # Base: 10, Curr: 13 (+30%, +3mm) -> Should be SD? Waaiit..
        # 30% is > 20%, but 3mm is < 5mm. Logic should allow this as SD.
        
        # NOTE: 20% of 10 is 2. So 13 is +3. +3 < 5. So SD.
        resp = self.calc.calculate_target_response(10, 13)
        self.assertEqual(resp, "SD")
        
        # 20% increase AND > 5mm -> PD
        # Base: 100, Curr: 121 (+21%, +21mm) -> PD
        resp2 = self.calc.calculate_target_response(100, 121)
        self.assertEqual(resp2, "PD")

    def test_matrix_logic(self):
        # T=CR, NT=Non-CR/Non-PD, New=No -> PR
        ovr = self.calc.determine_overall_response("CR", "Non-CR/Non-PD", False)
        self.assertEqual(ovr, "PR")
        
        # New Lesion -> PD
        ovr2 = self.calc.determine_overall_response("CR", "CR", True)
        self.assertEqual(ovr2, "PD")

if __name__ == '__main__':
    unittest.main()
