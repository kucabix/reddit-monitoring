from fastapi import APIRouter, HTTPException, Depends
from typing import List
import time
from datetime import datetime, timedelta, timezone
import praw
from app.models.reddit import SearchRequest, SearchResponse, RedditPost
from app.core.config import settings

router = APIRouter()

def get_reddit_client():
    """Initialize Reddit client."""
    try:
        reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
            username=settings.reddit_username,
            password=settings.reddit_password,
            ratelimit_seconds=5,
        )
        return reddit
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Reddit client: {e}")

def matches(text: str, keywords: List[str]) -> tuple[bool, List[str]]:
    """Check if text matches any keywords."""
    t = (text or "").lower()
    matched_keywords = [k for k in keywords if k.lower() in t]
    return bool(matched_keywords), matched_keywords

@router.post("/search", response_model=SearchResponse)
async def search_reddit(request: SearchRequest):
    """Search Reddit for posts matching keywords."""
    try:
        reddit_client = get_reddit_client()
        results = []
        start_time = time.time()
        
        # Calculate timestamp for specified days back
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=request.days_back)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        # Process each subreddit
        for subreddit_name in request.subreddits:
            try:
                if subreddit_name == "all":
                    current_sub = reddit_client.subreddit("all")
                else:
                    current_sub = reddit_client.subreddit(subreddit_name)
                
                # Get recent submissions
                for post in current_sub.new(limit=1000):
                    if post.created_utc < cutoff_timestamp:
                        break
                        
                    text = f"{post.title}\n{post.selftext or ''}"
                    is_match, matched_keywords = matches(text, request.keywords)
                    
                    if is_match:
                        result = RedditPost(
                            title=post.title,
                            subreddit=post.subreddit.display_name,
                            url=f"https://reddit.com{post.permalink}",
                            created=datetime.fromtimestamp(post.created_utc).strftime("%Y-%m-%d %H:%M:%S"),
                            keywords=matched_keywords,
                            selftext=post.selftext[:200] + "..." if len(post.selftext) > 200 else post.selftext,
                            score=post.score,
                            num_comments=post.num_comments
                        )
                        results.append(result)
                    
                    time.sleep(0.1)  # Rate limiting
                    
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

@router.get("/health")
async def reddit_health():
    """Check if Reddit client is working."""
    try:
        reddit_client = get_reddit_client()
        # Test connection
        reddit_client.user.me()
        return {"status": "healthy", "message": "Reddit client is working"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reddit client error: {e}")
