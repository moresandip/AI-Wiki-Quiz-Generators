import sys
import os
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from main import get_quiz, delete_quiz, save_quiz_results
from schemas import SaveResultsRequest
from database import engine, SQL_AVAILABLE
from models import Base, Quiz

# Ensure database tables exist (important for serverless environments)
if SQL_AVAILABLE and engine:
    Base.metadata.create_all(bind=engine)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Extract quiz_id from path
            path_parts = self.path.split('/')
            quiz_id = int(path_parts[-1])

            # Set CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Call the get_quiz function
            result = get_quiz(quiz_id)

            # Return the result
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                "detail": f"Error fetching quiz: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def do_PUT(self):
        try:
            # Extract quiz_id from path
            path_parts = self.path.split('/')
            quiz_id = int(path_parts[-1])

            # Set CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))

            # Create SaveResultsRequest object
            save_request = SaveResultsRequest(user_answers=request_data.get('user_answers'))

            # Call the save_quiz_results function
            result = save_quiz_results(quiz_id, save_request)

            # Return the result
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                "detail": f"Error saving quiz results: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def do_DELETE(self):
        try:
            # Extract quiz_id from path
            path_parts = self.path.split('/')
            quiz_id = int(path_parts[-1])

            # Set CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Call the delete_quiz function
            result = delete_quiz(quiz_id)

            # Return the result
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                "detail": f"Error deleting quiz: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
