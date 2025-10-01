from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
import time
from datetime import datetime, timedelta, timezone
import asyncio
import httpx
import json
import base64
from app.models.reddit import SearchRequest, SearchResponse, RedditPost
from app.core.config import settings

router = APIRouter()

async def get_reddit_access_token() -> str:
    """Get Reddit OAuth2 access token."""
    if not settings.reddit_client_id or not settings.reddit_client_secret:
        raise HTTPException(
            status_code=500,
            detail="Reddit credentials not configured. Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET."
        )
    
    # Create basic auth header
    credentials = f"{settings.reddit_client_id}:{settings.reddit_client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.reddit.com/api/v1/access_token",
            headers={
                "Authorization": f"Basic {encoded_credentials}",
                "User-Agent": settings.reddit_user_agent or "RedditAgent/1.0 by /u/yourusername"
            },
            data={
                "grant_type": "client_credentials"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get Reddit access token: {response.text}"
            )
        
        token_data = response.json()
        return token_data["access_token"]

async def get_reddit_client(request: Request):
    """Return shared httpx client from app.state."""
    reddit_client = getattr(request.app.state, "reddit_client", None)
    if reddit_client is None:
        raise HTTPException(
            status_code=500,
            detail="Reddit client not initialized. Call /api/initialize or configure credentials.",
        )
    return reddit_client

def matches(text: str, keywords: List[str]) -> tuple[bool, List[str]]:
    """Check if text matches any keywords."""
    t = (text or "").lower()
    matched_keywords = [k for k in keywords if k.lower() in t]
    return bool(matched_keywords), matched_keywords

@router.post("/search", response_model=SearchResponse)
async def search_reddit(request: SearchRequest, req: Request):
    """Search Reddit for posts matching keywords."""
    try:
        # Get Reddit access token
        access_token = await get_reddit_access_token()
        
        # Create authenticated client
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": settings.reddit_user_agent or "RedditAgent/1.0 by /u/yourusername"
        }
        
        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            results = []
            start_time = time.time()
            
            # Calculate timestamp for specified days back
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=request.days_back)
            cutoff_timestamp = int(cutoff_time.timestamp())
            
            # Process each subreddit
            for subreddit_name in request.subreddits:
                try:
                    # Use Reddit's JSON API with authentication
                    url = f"https://oauth.reddit.com/r/{subreddit_name}/new"
                    params = {"limit": 100}
                    
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    for post_data in data.get("data", {}).get("children", []):
                        post = post_data.get("data", {})
                        
                        # Check if post is within time range
                        if post.get("created_utc", 0) < cutoff_timestamp:
                            break
                            
                        text = f"{post.get('title', '')}\n{post.get('selftext', '')}"
                        is_match, matched_keywords = matches(text, request.keywords)
                        
                        if is_match:
                            result = RedditPost(
                                title=post.get("title", ""),
                                subreddit=post.get("subreddit", subreddit_name),
                                url=f"https://reddit.com{post.get('permalink', '')}",
                                created=datetime.fromtimestamp(post.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M:%S"),
                                keywords=matched_keywords,
                                selftext=(post.get("selftext", "")[:200] + "...") if len(post.get("selftext", "")) > 200 else post.get("selftext", ""),
                                score=post.get("score", 0),
                                num_comments=post.get("num_comments", 0)
                            )
                            results.append(result)
                        
                        await asyncio.sleep(0.1)  # Rate limiting
                        
                except Exception as e:
                    print(f"Error searching r/{subreddit_name}: {e}")
                    continue
            
            search_time = time.time() - start_time
            unique_subreddits = len(set(r.subreddit for r in results))
            
            return SearchResponse(
                posts=results,
                total_posts=len(results),
                unique_subreddits=unique_subreddits,
                search_time=search_time
            )
        
    except HTTPException as e:
        # Preserve HTTPException details
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

@router.get("/health")
async def reddit_health(req: Request):
    """Check if Reddit client is working."""
    try:
        # Check if credentials are configured
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            return {
                "status": "warning", 
                "message": "Reddit credentials not configured - using mock data"
            }
        
        # Get access token and test connection
        access_token = await get_reddit_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": settings.reddit_user_agent or "RedditAgent/1.0 by /u/yourusername"
        }
        
        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            # Test connection with a simple Reddit API call
            response = await client.get("https://oauth.reddit.com/r/Python/hot", params={"limit": 1})
            response.raise_for_status()
            return {"status": "healthy", "message": "Reddit client is working"}
    except HTTPException as e:
        return {
            "status": "error", 
            "message": e.detail
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Reddit client error: {e}"
        }
