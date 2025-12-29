import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import sys

# Mock imports if Google libs are missing locally
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()
sys.modules['google.cloud.discoveryengine'] = MagicMock()

from logic.budget_engine import BudgetSimulator
from logic.vendor_quality import VendorScorecard
from logic.reg_monitor import RegulatoryRadar
from logic.meta_search import MetaSearch

class TestIntelligenceModules(unittest.TestCase):

    # --- TEST 1: BUDGET SIMULATOR (Math Check) ---
    def test_budget_simulator_logic(self):
        """
        Scenario: Input a mock "Schedule of Events" list: ['MRI', 'MRI', 'Blood Draw'].
        Mock Data: {'MRI': 1000, 'Blood Draw': 100}.
        Assertion: Verify total cost returns 2100.
        """
        sim = BudgetSimulator()
        # Override the DB for testing stability
        sim.CPT_COST_DB = {'MRI': 1000, 'Blood Draw': 100}
        
        procedures = ['MRI', 'MRI', 'Blood Draw']
        num_patients = 1
        
        res = sim.calculate_estimates(procedures, num_patients)
        
        # 1000 + 1000 + 100 = 2100
        self.assertEqual(res['per_patient'], 2100)
        self.assertEqual(res['total_study'], 2100 * num_patients)

    def test_budget_simulator_unknown_proc(self):
        """
        Failure Check: Verify it handles unknown procedures (default to $100) without crashing.
        """
        sim = BudgetSimulator()
        res = sim.calculate_estimates(["Alien Surgery"], 1)
        self.assertEqual(res['per_patient'], 100) # Default cost check

    # --- TEST 2: VENDOR SCORECARD (Quality Logic) ---
    @patch('logic.vendor_quality.firestore')
    def test_vendor_scorecard_calculation(self, mock_firestore):
        """
        Scenario: Input a Reconciliation Result with 10 Discrepancies out of 100 Rows.
        Assertion: Verify "Error Rate" calculation is exactly 10.0%.
        Database Check: Ensure the function tries to save record.
        """
        # Setup Mock DB
        mock_db_instance = MagicMock()
        mock_collection = MagicMock()
        mock_db_instance.collection.return_value = mock_collection
        mock_firestore.Client.return_value = mock_db_instance
        
        scorecard = VendorScorecard()
        # Force use_firestore to True to test that path if client init succeeded (mocked)
        scorecard.use_firestore = True 
        scorecard.db = mock_db_instance

        # Action: 10 errors, 100 rows
        scorecard.log_upload_quality("LabCorp", 100, 10)
        
        # Verify Calculation in the call args
        # Expected record: clean_rate should be 90.0
        args, _ = mock_collection.add.call_args
        record = args[0]
        
        self.assertEqual(record['vendor'], 'LabCorp')
        self.assertEqual(record['clean_rate'], 90.0) 
        self.assertEqual(record['error_count'], 10)

    # --- TEST 3: REGULATORY RADAR (Compliance Trigger) ---
    @patch('logic.reg_monitor.llm')
    def test_regulatory_radar_alert(self, mock_llm):
        """
        Scenario: Mock Regulation "Remote Consent". Protocol misses it.
        Assertion: Verify the check_compliance function returns a Warning Flag.
        """
        monitor = RegulatoryRadar()
        
        # Mock the Chain invoke response
        mock_response = MagicMock()
        mock_response.content = "Alert: Decentralized Trials - Protocol missing Remote Consent."
        
        # Mock the chain structure: chain.invoke(...) -> response
        # Since logic constructs chain = prompt | llm, mimicking exact behavior is complex with just patching llm.
        # However, typically the chain.invoke call eventually calls llm.invoke or similar.
        # A simpler way for testing purely the logic function's handling of output:
        # We can mock the `chain` object inside the method if correct, or simpler:
        # Patch the 'chain' creation or execution.
        
        # Let's try patching the `chain.invoke` if possible, but chain is local variable.
        # We'll rely on the fact that `prompt | llm` creates a RunnableSequence. 
        # When invoked, it calls `llm`. 
        # Actually, let's mock the `chain.invoke` by mocking the return of the pipe? 
        # Easier strategy: Mock `llm` and assume `chain.invoke` returns `llm` output for this test structure 
        # OR just mock the whole chain execution flow.
        
        with patch('logic.reg_monitor.PromptTemplate') as mock_pt:
             mock_chain = MagicMock()
             mock_chain.invoke.return_value = mock_response
             
             # When prompt | llm is called, return mock_chain? 
             # No, PromptTemplate | llm returns a Runnable.
             # We can patch the pipe operator `__or__`? No, too messy.
             
             # Better: Refactor or just patch `chain.invoke` isn't easy since it's local.
             # Strategy: Use `invoke` on the Mock LLM object itself if the code structure allows, 
             # BUT standard LC chain calls `llm.invoke` or `llm.generate`.
             # If we mock `llm`, the chain might fail if it expects a specific LC object.
             
             # ALTERNATIVE: Patch the `RegulatoryRadar.check_compliance` internal `chain`. 
             # Since we can't, let's just assume `llm` is used.
             # Actually, looking at `logic/reg_monitor.py`, it does: `response = chain.invoke({...}).content`.
             # If we mock `llm`, `prompt | llm` might result in a Mock object that we can configure `invoke` on.
             
             mock_pt.from_template.return_value = MagicMock() # The prompt
             # The result of prompt | llm
             mock_runnable = MagicMock()
             mock_runnable.invoke.return_value = mock_response
             
             # Configure the pipe result
             mock_pt.from_template.return_value.__or__.return_value = mock_runnable
             
             alerts = monitor.check_compliance("Patients will have home visits.")
             
             self.assertTrue(len(alerts) > 0)
             self.assertIn("Decentralized Trials", alerts[0])

    # --- TEST 4: META-SEARCH (Integration Check) ---
    def test_meta_search_stub(self):
        """
        Scenario: Call the search function.
        Assertion: Verify the function constructs query response correctly.
        """
        ms = MetaSearch()
        # "Inclusion" should trigger the stub logic to return rows
        res = ms.search_knowledge_graph("Inclusion criteria for Hypertension")
        
        self.assertFalse(res.empty)
        # Verify columns exist
        self.assertTrue("Study" in res.columns)
        self.assertTrue("Snippet" in res.columns)
        # Verify content
        row = res.iloc[0]
        self.assertIn("Inclusion", row['Section'])

if __name__ == '__main__':
    unittest.main()
