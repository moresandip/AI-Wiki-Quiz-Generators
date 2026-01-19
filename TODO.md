# Fix Vercel Database Table Issue

## Problem
In Vercel's serverless environment, SQLite database is stored in /tmp which is ephemeral. Each function invocation runs in isolation, so database tables are not persisted across calls. API handlers need to create tables on every invocation.

## Tasks
- [ ] Modify api/generate-quiz.py to create database tables before operations
- [ ] Modify api/quizzes.py to create database tables and fix function name (get_quizzes -> get_recent_quizzes)
- [ ] Modify api/quiz/[quiz_id].py to create database tables before operations
- [x] Test the changes to ensure database tables are created properly in Vercel
