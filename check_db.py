import sqlite3
import os

# Try to find the db file
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "backend", "quiz.db")
output_file = os.path.join(base_dir, "db_check_result.txt")

with open(output_file, "w") as f:
    f.write(f"Checking DB at: {db_path}\n")

    if not os.path.exists(db_path):
        f.write("DB file not found!\n")
    else:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            f.write(f"Tables found: {tables}\n")
            conn.close()
        except Exception as e:
            f.write(f"Error: {e}\n")
