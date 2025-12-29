import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"Sys Path: {sys.path}")

try:
    import logic
    print(f"Logic module: {logic}")
    print(f"Logic file: {logic.__file__}")
    print(f"Logic path: {logic.__path__}")
except ImportError as e:
    print(f"Import logic failed: {e}")

try:
    import logic.agent_logic
    print("Import logic.agent_logic success")
except Exception as e:
    print(f"Import logic.agent_logic failed: {e}")
