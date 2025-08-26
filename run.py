import uvicorn
import os
from dotenv import load_dotenv

# Loading environment variables
load_dotenv()

if __name__ == "__main__":
    # Getting port from environment or using default
    port = int(os.getenv("PORT", 8000))
    
    # Running the application
    uvicorn.run(
        "app.main:app",  # Path to my FastAPI app
        host="0.0.0.0",  # Listen on all interfaces
        port=port,       # Port number
        reload=True      # Auto-reload on code changes (development only)
    )