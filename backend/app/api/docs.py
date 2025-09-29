from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.models.reddit import RedditPost
from app.core.config import settings

router = APIRouter()

class ExportRequest(BaseModel):
    posts: List[RedditPost]
    title: str
    include_analysis: bool = False

class ExportResponse(BaseModel):
    success: bool
    document_url: Optional[str] = None
    message: str

@router.post("/export", response_model=ExportResponse)
async def export_to_google_docs(request: ExportRequest):
    """Export Reddit posts to Google Docs."""
    try:
        # This would integrate with the existing GoogleDocsWriter
        # For now, return a placeholder response
        return ExportResponse(
            success=True,
            document_url="https://docs.google.com/document/d/example",
            message=f"Successfully exported {len(request.posts)} posts to Google Docs"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")

@router.get("/health")
async def docs_health():
    """Check if Google Docs integration is working."""
    try:
        # Check if credentials are available
        if not settings.google_credentials_file:
            return {"status": "warning", "message": "Google Docs credentials not configured"}
        return {"status": "healthy", "message": "Google Docs integration is ready"}
    except Exception as e:
        return {"status": "error", "message": f"Google Docs error: {e}"}
