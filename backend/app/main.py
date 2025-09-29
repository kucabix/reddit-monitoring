from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.api import reddit, analysis, docs
from app.core.config import settings

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Reddit Agent API...")
    yield
    # Shutdown
    print("🛑 Shutting down Reddit Agent API...")

app = FastAPI(
    title="Reddit Agent API",
    description="Monitor Reddit for keywords, analyze with AI, and export results",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reddit.router, prefix="/api/reddit", tags=["reddit"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(docs.router, prefix="/api/docs", tags=["docs"])

@app.get("/")
async def root():
    return {"message": "Reddit Agent API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/initialize")
async def initialize_services():
    """Initialize and test all required services."""
    try:
        results = {
            "reddit": {"status": "error", "message": "Not configured"},
            "openai": {"status": "error", "message": "Not configured"},
            "google_docs": {"status": "error", "message": "Not configured"}
        }
        
        # Test Reddit API
        try:
            if settings.reddit_client_id and settings.reddit_client_secret:
                import praw
                reddit = praw.Reddit(
                    client_id=settings.reddit_client_id,
                    client_secret=settings.reddit_client_secret,
                    user_agent=settings.reddit_user_agent or "RedditAgent/1.0",
                    ratelimit_seconds=5,
                )
                # Test with a simple read-only operation
                reddit.subreddit("test").display_name
                results["reddit"] = {"status": "success", "message": "Reddit API connected"}
            else:
                results["reddit"] = {"status": "warning", "message": "Reddit credentials not configured"}
        except Exception as e:
            results["reddit"] = {"status": "error", "message": f"Reddit API error: {e}"}
        
        # Test OpenAI API
        try:
            if settings.openai_api_key:
                from openai import OpenAI
                client = OpenAI(api_key=settings.openai_api_key)
                # Test with a simple completion
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                results["openai"] = {"status": "success", "message": "OpenAI API connected"}
            else:
                results["openai"] = {"status": "warning", "message": "OpenAI API key not configured"}
        except Exception as e:
            results["openai"] = {"status": "error", "message": f"OpenAI API error: {e}"}
        
        # Test Google Docs API
        try:
            if settings.google_client_id and settings.google_client_secret:
                results["google_docs"] = {"status": "success", "message": "Google Docs credentials configured"}
            elif settings.google_credentials_file:
                import os
                if os.path.exists(settings.google_credentials_file):
                    results["google_docs"] = {"status": "success", "message": "Google Docs credentials file found"}
                else:
                    results["google_docs"] = {"status": "error", "message": "Google credentials file not found"}
            else:
                results["google_docs"] = {"status": "warning", "message": "Google credentials not configured"}
        except Exception as e:
            results["google_docs"] = {"status": "error", "message": f"Google Docs error: {e}"}
        
        # Determine overall status
        all_success = all(result["status"] == "success" for result in results.values())
        any_errors = any(result["status"] == "error" for result in results.values())
        
        if all_success:
            overall_status = "success"
            message = "All services initialized successfully"
        elif any_errors:
            overall_status = "error"
            message = "Some services failed to initialize"
        else:
            overall_status = "warning"
            message = "Services initialized with warnings"
        
        return {
            "status": overall_status,
            "message": message,
            "services": results,
            "timestamp": "2024-01-01T00:00:00Z"  # You might want to use actual timestamp
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {e}")
