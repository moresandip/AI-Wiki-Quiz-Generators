import sys
import os
from fastapi import FastAPI

# Add backend directory to sys.path to ensure imports in backend files work correctly
# This is necessary because Vercel runs from root, but backend code expects to be in backend dir
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from main import app as backend_app

app = FastAPI()
# Mount the backend app at /api path to handle Vercel's URL structure
app.mount("/api", backend_app)
