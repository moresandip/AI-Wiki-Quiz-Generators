import os
import json
import logging
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

# Import backend modules
import sys
sys.path.append('./backend')

from backend import models, schemas, scraper, llm, database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure tables are created
if database.SQL_AVAILABLE and database.engine:
    models.Base.metadata.create_all(bind=database.engine)
    logger.info("Database tables created (if not existed).")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            path = self.path
            if path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "AI Wiki Quiz Generator API is running"}).encode())
            elif path == '/api/quizzes':
                self.handle_get_quizzes()
            elif path.startswith('/api/quiz/'):
                parts = path.split('/')
                if len(parts) == 4 and parts[3].isdigit():
                    quiz_id = int(parts[3])
                    self.handle_get_quiz(quiz_id)
                else:
                    self.send_error(404, "Not Found")
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"GET error: {e}")
            self.send_error(500, str(e))

    def do_POST(self):
        try:
            path = self.path
            if path == '/api/quiz':
                self.handle_generate_quiz()
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"POST error: {e}")
            self.send_error(500, str(e))

    def do_PUT(self):
        try:
            path = self.path
            if path.startswith('/api/quiz/') and path.endswith('/save-results'):
                parts = path.split('/')
                if len(parts) == 5 and parts[3].isdigit():
                    quiz_id = int(parts[3])
                    self.handle_save_results(quiz_id)
                else:
                    self.send_error(404, "Not Found")
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"PUT error: {e}")
            self.send_error(500, str(e))

    def do_DELETE(self):
        try:
            path = self.path
            if path.startswith('/api/quiz/'):
                parts = path.split('/')
                if len(parts) == 4 and parts[3].isdigit():
                    quiz_id = int(parts[3])
                    self.handle_delete_quiz(quiz_id)
                else:
                    self.send_error(404, "Not Found")
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"DELETE error: {e}")
            self.send_error(500, str(e))

    def get_db(self):
        if not database.SessionLocal:
            return None
        db = database.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def handle_generate_quiz(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        url = data.get('url')

        if not url:
            self.send_error(400, "URL required")
            return

        logger.info(f"Received quiz request for URL: {url}")

        try:
            # Scrape
            scraped_data = scraper.scrape_wikipedia(url)
            logger.info(f"Scraping successful. Title: {scraped_data.get('title')}")

            # Generate quiz
            quiz_data = llm.generate_quiz_data(scraped_data)
            logger.info("Quiz generation successful")

            # Save to DB
            db_quiz = None
            db_gen = self.get_db()
            db = next(db_gen, None)
            if db:
                try:
                    db_quiz = models.Quiz(
                        url=url,
                        title=quiz_data.get("title"),
                        summary=quiz_data.get("summary"),
                        data=quiz_data
                    )
                    db.add(db_quiz)
                    db.commit()
                    db.refresh(db_quiz)
                    logger.info(f"Saved quiz to database with ID: {db_quiz.id}")
                except Exception as e:
                    logger.error(f"Failed to save to database: {e}")

            response = {
                "id": db_quiz.id if db_quiz else None,
                "url": url,
                "title": quiz_data.get("title"),
                "summary": quiz_data.get("summary"),
                "data": quiz_data,
                "created_at": db_quiz.created_at.isoformat() if db_quiz else None
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except ValueError as ve:
            logger.error(f"ValueError: {ve}")
            self.send_error(400, str(ve))
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.send_error(500, str(e))

    def handle_get_quizzes(self):
        db_gen = self.get_db()
        db = next(db_gen, None)
        if not db:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps([]).encode())
            return

        quizzes = db.query(models.Quiz).order_by(models.Quiz.created_at.desc()).limit(10).all()
        result = []
        for q in quizzes:
            result.append({
                "id": q.id,
                "url": q.url,
                "title": q.title,
                "summary": q.summary,
                "data": q.data,
                "user_answers": q.user_answers,
                "created_at": q.created_at.isoformat()
            })

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def handle_get_quiz(self, quiz_id):
        db_gen = self.get_db()
        db = next(db_gen, None)
        if not db:
            self.send_error(503, "Database not available")
            return

        quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
        if not quiz:
            self.send_error(404, "Quiz not found")
            return

        result = {
            "id": quiz.id,
            "url": quiz.url,
            "title": quiz.title,
            "summary": quiz.summary,
            "data": quiz.data,
            "user_answers": quiz.user_answers,
            "created_at": quiz.created_at.isoformat()
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def handle_delete_quiz(self, quiz_id):
        db_gen = self.get_db()
        db = next(db_gen, None)
        if not db:
            self.send_error(503, "Database not available")
            return

        quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
        if not quiz:
            self.send_error(404, "Quiz not found")
            return

        db.delete(quiz)
        db.commit()
        logger.info(f"Deleted quiz with ID: {quiz_id}")

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Quiz deleted successfully"}).encode())

    def handle_save_results(self, quiz_id):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        user_answers = data.get("user_answers", {})

        db_gen = self.get_db()
        db = next(db_gen, None)
        if not db:
            self.send_error(503, "Database not available")
            return

        quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
        if not quiz:
            self.send_error(404, "Quiz not found")
            return

        if quiz.data:
            quiz.data["user_answers"] = user_answers
        else:
            quiz.data = {"user_answers": user_answers}

        db.commit()
        db.refresh(quiz)
        logger.info(f"Saved results for quiz ID: {quiz_id}")

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Results saved successfully", "quiz": {
            "id": quiz.id,
            "url": quiz.url,
            "title": quiz.title,
            "summary": quiz.summary,
            "data": quiz.data,
            "user_answers": quiz.user_answers,
            "created_at": quiz.created_at.isoformat()
        }}).encode())
