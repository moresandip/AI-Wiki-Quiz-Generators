# AI Wiki Quiz Generator - How to Run

I have refactored the application to serve both the frontend and backend from a single server. This simplifies the process of running the application.

Due to security restrictions, I am unable to start the web server myself.

To run the application, please execute the following command in your terminal from the project's root directory (`c:\Users\mores\OneDrive\Desktop\AI Wiki Quiz Generator`):

```bash
c:\Users\mores\OneDrive\Desktop\AI Wiki Quiz Generator\backend\venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

After running this command, you can access the application by opening your web browser and navigating to `http://localhost:8000`.
