# TODO: Fix Quiz Generation Database Error

## Problem
- Error: "sqlite3.OperationalError) no such table: quizzes" when generating quiz on Vercel
- Issue: Database tables not being created properly in Vercel serverless environment

## Changes Made
- [x] Created `backend/create_tables.py` script to handle table creation
- [x] Modified `backend/database.py` to attempt engine creation even if connection test fails (for Vercel /tmp)
- [x] Updated `api/index.py` to call `create_tables()` at startup

## Next Steps
- [ ] Test locally to ensure quiz generation works
- [ ] Deploy to Vercel and test quiz generation
- [ ] If persistence is needed, consider migrating to a cloud database (PostgreSQL on Vercel)

## Notes
- On Vercel, database is ephemeral (/tmp/quiz.db), so quizzes won't persist across requests
- For production with persistence, recommend using Vercel Postgres or similar cloud database
