from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from app.routers import auth
from app.core.database import engine, Base

# Creating all database tables
Base.metadata.create_all(bind=engine)

# Creating my FastAPI app
app = FastAPI(
    title="AI Expense Tracker",
    description="My intelligent expense tracking application with AI categorization",
    version="1.0.0"
)

# Setting up CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # I'll restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mounting static files for CSS and JavaScript
app.mount("/static", StaticFiles(directory="static"), name="static")

# Including my routers
app.include_router(auth.router)

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    I'm serving a simple welcome page at the root.
    The actual app will be served from here later.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Expense Tracker</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            h1 { text-align: center; }
            .info {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
            }
            a {
                color: #ffd700;
                text-decoration: none;
            }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Welcome to AI Expense Tracker</h1>
        <div class="info">
            <h2>API Documentation</h2>
            <p>Visit <a href="/docs">/docs</a> for interactive API documentation</p>
            <p>Visit <a href="/redoc">/redoc</a> for alternative documentation</p>
        </div>
        <div class="info">
            <h2>Available Endpoints</h2>
            <ul>
                <li>POST /api/auth/register - Register new user</li>
                <li>POST /api/auth/login - Login user</li>
                <li>GET /api/auth/me - Get current user profile</li>
                <li>PUT /api/auth/me - Update profile</li>
                <li>DELETE /api/auth/me - Delete account</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """
    I'm providing a health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "AI Expense Tracker",
        "version": "1.0.0"
    }

@app.on_event("startup")
async def startup_event():
    """
    I'm running this when the application starts.
    Good place for initialization tasks.
    """
    print("AI Expense Tracker is starting up...")
    print("Database tables created/verified")
    print("Ready to track expenses!")

@app.on_event("shutdown")
async def shutdown_event():
    """
    I'm running this when the application shuts down.
    Good place for cleanup tasks.
    """
    print("Shutting down AI Expense Tracker...")