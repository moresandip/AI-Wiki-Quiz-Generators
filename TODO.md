# TODO: Fix Quiz Generation Issues

## Problem
- App was always generating demo quiz instead of quiz based on wiki link
- Issue: LLM API calls were failing and falling back to sample data silently

## Changes Made
- [x] Fixed database column type issue (changed JSONType to Text for data/user_answers columns)
- [x] Removed silent fallback to sample data - now shows proper error when API keys are missing
- [x] Updated table creation script
- [x] Added better error logging for API failures

## Next Steps
- [ ] Set up API keys (GOOGLE_API_KEY or OPENROUTER_API_KEY) in .env file
- [ ] Test quiz generation with valid API keys
- [ ] Deploy to Vercel and test

## Notes
- App now requires valid API keys to generate quizzes
- No more silent fallback to demo data
- Database issues have been resolved
