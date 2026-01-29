# TODO: Remove OpenRouter and Use Only Google API

## Tasks
- [x] Update backend/llm.py: Remove generate_with_openrouter function
- [x] Update backend/llm.py: Update list_available_models to only include Google models
- [x] Update backend/llm.py: Update test_api_connection to only test Google API key
- [x] Update backend/llm.py: Update generate_quiz_data to only use Google API
- [x] Update backend/check_api_key.py: Remove OpenRouter key checking logic
- [x] Delete diagnose_setup.py file
- [x] Delete test_openrouter.py file
- [x] Test quiz generation with only Google API (OpenRouter successfully removed, Google API configured)
