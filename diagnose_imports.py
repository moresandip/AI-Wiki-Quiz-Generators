
import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"Sys Path: {sys.path}")

try:
    from backend import main
    print("Successfully imported backend.main")
except Exception as e:
    print(f"Failed to import backend.main: {e}")
    import traceback
    traceback.print_exc()

try:
    import backend.models
    print("Successfully imported backend.models")
except Exception as e:
    print(f"Failed to import backend.models: {e}")
    import traceback
    traceback.print_exc()
