## How to Run the Application and Verify the Fix

I have made several changes to the application to address the issues you were facing. Here's a summary of the changes and how to verify that they have fixed the problem.

### Summary of Changes

1.  **Database Initialization:** The application now correctly creates the database tables when it starts up on Vercel. This should resolve the `sqlite3.OperationalError: no such table: quizzes` error.
2.  **API Key:** The Google AI API key you provided has been added to the application, so it should now be able to generate new quizzes.
3.  **API Structure:** The API has been consolidated into a single entry point, which makes the application more robust and easier to maintain.

### How to Verify the Fix

1.  **Deploy to Vercel:** Deploy the latest version of your application to Vercel.
2.  **Generate a Quiz:** Open the deployed application in your browser and try to generate a new quiz by providing a Wikipedia URL.
3.  **Verify Quiz Generation:** The application should now generate a new quiz based on the provided URL. You should no longer see the default sample data.

If you continue to experience issues, please check the Vercel logs for any errors and provide them to me.