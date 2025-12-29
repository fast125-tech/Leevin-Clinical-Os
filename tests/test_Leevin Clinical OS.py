import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# --- PATH SETUP (Crucial for Import Errors) ---
# This tells Python: "Look for the 'logic' folder in the main project directory"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from logic.agent_logic import analyze_protocol
    from logic.marketing_mcp import run_marketing_agent
    print("✅ KAIROS Logic Modules Found.")
except ImportError as e:
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
    print("Make sure your folder structure is: KAIROS Clinical/logic/agent_logic.py")
    sys.exit(1)

class TestKairosCore(unittest.TestCase):

    @patch('logic.agent_logic.llm') # Mock the Brain so we don't pay for tokens
    def test_protocol_audit_flow(self, mock_llm):
        """Test if KAIROS can process a protocol without crashing."""
        print("\nTesting: KAIROS Protocol Auditor...")
        
        # 1. Simulate the AI's response
        mock_llm.invoke.return_value.content = "## Executive Summary\nStudy is feasible."
        
        # 2. Run the function with a dummy file path
        # (We use requirements.txt just because we know it exists)
        result = analyze_protocol("requirements.txt")
        
        # 3. Verify
        self.assertIn("Executive Summary", result)
        print("✅ PASS: Protocol Auditor returned analysis.")

    def test_marketing_agent(self):
        """Test if the Marketing Bot structure works."""
        print("\nTesting: KAIROS Marketing Engine...")
        # Simple check to ensure function exists
        self.assertTrue(callable(run_marketing_agent))
        print("✅ PASS: Marketing Agent is ready.")

if __name__ == '__main__':
    unittest.main()
```

### **Step 3: Run the Test**
Open your terminal and run this command:

```bash
python tests/test_kairos.py