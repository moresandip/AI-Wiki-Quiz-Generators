## Backend Fixes
- [ ] Fix LLM API integration (currently using OpenRouter but instructions say Google Gemini)
- [ ] Update API key validation and error handling
- [ ] Ensure proper CORS configuration for both localhost and production

## Frontend Fixes  
- [ ] Fix "Failed to fetch" error on localhost
- [ ] Fix "Failed to generate quiz" error on Vercel deployment

## Deployment Fixes
- [ ] Fix Vercel deployment configuration (currently not supporting Python functions properly)
- [ ] Ensure database works in serverless environment
- [ ] Test API endpoints work correctly

## Testing
- [ ] Test quiz generation with valid Wikipedia URLs
- [ ] Test error handling with invalid URLs
- [ ] Test database operations (save/load quizzes)
- [ ] Test both localhost and Vercel deployments
=======
# TODO List for AI Wiki Quiz Generator

## Backend Fixes
- [x] Fix LLM API integration (switched from OpenRouter to Google Gemini API)
- [x] Update API key validation and error handling
- [x] Ensure proper CORS configuration for both localhost and production

## Frontend Fixes
- [x] Fix "Failed to fetch" error on localhost (CORS and API routing)
- [x] Fix "Failed to generate quiz" error on Vercel deployment (API structure)

## Deployment Fixes
- [x] Fix Vercel deployment configuration (created proper serverless API structure)
- [x] Ensure database works in serverless environment
- [x] Test API endpoints work correctly

## Testing
- [ ] Test quiz generation with valid Wikipedia URLs
- [ ] Test error handling with invalid URLs
- [ ] Test database operations (save/load quizzes)
- [ ] Test both localhost and Vercel deployments
