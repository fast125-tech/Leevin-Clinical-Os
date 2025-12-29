import sys
from unittest.mock import MagicMock

print("Mocking langchain_google_vertexai...")
sys.modules['langchain_google_vertexai'] = MagicMock()

try:
    print("Attempting import...")
    from langchain_google_vertexai import ChatVertexAI
    print(f"Imported ChatVertexAI: {ChatVertexAI}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
