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

## Setting Up Supabase Database (Required for Vercel Deployment)

Since Vercel doesn't support persistent SQLite databases, we use Supabase (free PostgreSQL) for production.

### 1. Create a Supabase Account and Project

1. Go to [Supabase](https://supabase.com/)
2. Sign up or log in
3. Click "New project"
4. Choose your organization, enter project name (e.g., "ai-wiki-quiz")
5. Set database password (save this securely)
6. Choose region closest to you
7. Click "Create new project"

### 2. Get Your Database Connection String

1. In your Supabase dashboard, go to Settings > Database
2. Under "Connection string", select "URI" from the dropdown
3. Copy the connection string (it will look like: `postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres`)

### 3. Set Environment Variables in Vercel

1. Go to your Vercel project dashboard
2. Navigate to Settings > Environment Variables
3. Add these variables:
   - `DATABASE_URL`: Your Supabase connection string
   - `GOOGLE_API_KEY`: Your Google Gemini API key

### 4. Test Local Setup with PostgreSQL

For local development with PostgreSQL:

1. Install PostgreSQL locally or use a Docker container
2. Set `DATABASE_URL` in your `.env` file to your local PostgreSQL connection string
3. Run `python backend/create_tables.py` to create tables
4. Test the app locally

## Testing Your Setup

After setting up your API key and database, you can test it by:

1. Running the backend: `uvicorn main:app --reload`
2. Visiting `http://localhost:8000/api-status` to check if the API key is valid
3. The app will show available models and connection status

**Note:** Never commit your `.env` file to version control. It should be in `.gitignore`.

**Important:** The app now uses Google Gemini API directly. Make sure your API key has the necessary permissions for Gemini models.

