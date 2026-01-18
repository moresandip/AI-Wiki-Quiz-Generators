import os
try:
    with open("diagnostic.txt", "w") as f:
        f.write("Python is working")
    print("Diagnostic wrote to file")
except Exception as e:
    print(f"Diagnostic failed: {e}")
