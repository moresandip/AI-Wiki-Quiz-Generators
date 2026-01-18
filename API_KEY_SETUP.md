# API Key Setup Instructions

## Getting Your Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API key"
4. Copy your API key (it will start with "AIzaSy...")

## Setting Up the API Key

### Option 1: Using .env file (Recommended)

1. Create a file named `.env` in the `backend` folder
2. Add the following line to the file:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```
3. Replace `your_actual_api_key_here` with your actual API key

### Option 2: Using Environment Variable

Set the environment variable before running the backend:
- Windows: `set GOOGLE_API_KEY=your_actual_api_key_here`
- Linux/Mac: `export GOOGLE_API_KEY=your_actual_api_key_here`

## Example .env file

Create `backend/.env` with:
```
GOOGLE_API_KEY=AIzaSy...your_key_here
```

## Testing Your Setup

After setting up your API key, you can test it by:

1. Running the backend: `uvicorn main:app --reload`
2. Visiting `http://localhost:8000/api-status` to check if the API key is valid
3. The app will show available models and connection status

**Note:** Never commit your `.env` file to version control. It should be in `.gitignore`.

**Important:** The app now uses Google Gemini API directly. Make sure your API key has the necessary permissions for Gemini models.

