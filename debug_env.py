
import os
from dotenv import load_dotenv

print(f"Current working directory: {os.getcwd()}")

# Attempt 1: Default load
load_dotenv()
key = os.getenv("GOOGLE_API_KEY")
print(f"Attempt 1 (Default): GOOGLE_API_KEY found? {'Yes' if key else 'No'}")
if key:
    print(f"Key preview: {key[:5]}...")

# Attempt 2: Explicit path
env_path = os.path.join(os.getcwd(), '.env')
print(f"Checking for .env at: {env_path}")
if os.path.exists(env_path):
    print(".env file exists.")
    load_dotenv(env_path, override=True)
    key2 = os.getenv("GOOGLE_API_KEY")
    print(f"Attempt 2 (Explicit Path): GOOGLE_API_KEY found? {'Yes' if key2 else 'No'}")
else:
    print(".env file NOT found at expected path.")

# Attempt 3: Check backend directory relative path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
print(f"Script location: {PROJECT_ROOT}")
