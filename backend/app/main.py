from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.api import reddit, analysis, docs
import certifi
from app.core.config import settings
import aiohttp
import ssl

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Reddit Agent API...")
    # Ensure SSL uses certifi CA bundle (fixes SSL CERTIFICATE_VERIFY_FAILED on some macOS setups)
    try:
        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    except Exception:
        pass

    # Create shared Reddit client if credentials are configured
    app.state.reddit_client = None
    try:
        if settings.reddit_client_id and settings.reddit_client_secret:
            import httpx
            
            # Create httpx client with SSL verification disabled
            app.state.reddit_client = httpx.AsyncClient(
                verify=False,
                timeout=30.0,
                headers={
                    "User-Agent": settings.reddit_user_agent or "RedditAgent/1.0"
                }
            )
    except Exception as e:
        print(f"Failed to initialize shared Reddit client: {e}")

    yield
    # Shutdown
    try:
        if getattr(app.state, "reddit_client", None) is not None:
            try:
                await app.state.reddit_client.aclose()
            except Exception:
                pass
    finally:
        print("🛑 Shutting down Reddit Agent API...")

app = FastAPI(
    title="Reddit Agent API",
    description="Monitor Reddit for keywords, analyze with AI, and export results",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://reddit-monitoring-app-b0cufgdzetc8b4ds.polandcentral-01.azurewebsites.net/"  # Add your Azure domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend build)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(reddit.router, prefix="/api/reddit", tags=["reddit"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(docs.router, prefix="/api/docs", tags=["docs"])

@app.get("/")
async def root():
    # Serve frontend index.html for root path
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Reddit Agent API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Catch-all route for frontend routing (must be last)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve frontend for all non-API routes"""
    # Don't interfere with API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    file_path = os.path.join(static_dir, full_path)
    
    # If it's a file that exists, serve it
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Otherwise serve index.html for client-side routing
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="Not found")

@app.post("/api/initialize")
async def initialize_services():
    """Initialize and test all required services."""
    try:
        results = {
            "reddit": {"status": "error", "message": "Not configured"},
            "openai": {"status": "error", "message": "Not configured"},
            "google_docs": {"status": "error", "message": "Not configured"},
        }

        # Test Reddit API
        try:
            if settings.reddit_client_id and settings.reddit_client_secret:
                import httpx
                # Test with a simple Reddit API call
                async with httpx.AsyncClient(verify=False) as client:
                    response = await client.get("https://www.reddit.com/r/Python/hot.json", params={"limit": 1})
                    response.raise_for_status()
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
                # minimal call to validate key without heavy usage
                client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=1,
                )
                results["openai"] = {"status": "success", "message": "OpenAI API connected"}
            else:
                results["openai"] = {"status": "warning", "message": "OpenAI API key not configured"}
        except Exception as e:
            results["openai"] = {"status": "error", "message": f"OpenAI API error: {e}"}

        # Test Google Docs configuration
        try:
            if settings.google_client_id and settings.google_client_secret:
                results["google_docs"] = {"status": "success", "message": "Google Docs credentials configured"}
            elif settings.google_credentials_file:
                if os.path.exists(settings.google_credentials_file):
                    results["google_docs"] = {"status": "success", "message": "Google credentials file found"}
                else:
                    results["google_docs"] = {"status": "error", "message": "Google credentials file not found"}
            else:
                results["google_docs"] = {"status": "warning", "message": "Google credentials not configured"}
        except Exception as e:
            results["google_docs"] = {"status": "error", "message": f"Google Docs error: {e}"}

        all_success = all(r["status"] == "success" for r in results.values())
        any_errors = any(r["status"] == "error" for r in results.values())

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
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {e}")
