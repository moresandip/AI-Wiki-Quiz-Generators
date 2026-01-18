import sys
import os
from fastapi import FastAPI

# Import the backend app
from main import app as backend_app

app = FastAPI()

# Mount the backend app to handle all API routes
app.mount("/api", backend_app)
