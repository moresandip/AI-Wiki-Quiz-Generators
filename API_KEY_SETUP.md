# API Key Setup Instructions

## Getting Your Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey) or [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new API key for Gemini
3. Copy your API key

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

**Note:** Never commit your `.env` file to version control. It should be in `.gitignore`.

