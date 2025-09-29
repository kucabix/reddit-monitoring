from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RedditPost(BaseModel):
    title: str
    subreddit: str
    url: str
    created: str
    keywords: List[str]
    selftext: Optional[str] = None
    score: int
    num_comments: int

class SearchRequest(BaseModel):
    keywords: List[str]
    subreddits: List[str]
    days_back: int = 30

class SearchResponse(BaseModel):
    posts: List[RedditPost]
    total_posts: int
    unique_subreddits: int
    search_time: float

class BusinessContext(BaseModel):
    company_type: str
    specialty: str
    blog_focus: str
    target_audience: str
    interests: List[str]
