
import sys
import os

# Ensure backend can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.llm import test_api_connection, list_available_models
    
    print("Import successful.")
    
    success, message = test_api_connection()
    
    with open("verification_result.txt", "w") as f:
        f.write(f"Success: {success}\n")
        f.write(f"Message: {message}\n")
        
        models = list_available_models()
        f.write(f"Available Models: {models}\n")
        
except Exception as e:
    with open("verification_result.txt", "w") as f:
        f.write(f"Error: {str(e)}\n")
