from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
from openai import OpenAI
from app.core.config import settings
from app.models.reddit import RedditPost, BusinessContext

router = APIRouter()

class AnalysisRequest(BaseModel):
    posts: List[RedditPost]
    business_context: BusinessContext

class AnalyzedPost(RedditPost):
    relevance_score: Optional[int] = None
    content_type: Optional[str] = None
    target_audience_match: Optional[str] = None
    reasoning: Optional[str] = None
    business_opportunity: Optional[str] = None

class AnalysisResponse(BaseModel):
    analyzed_posts: List[AnalyzedPost]
    total_analyzed: int
    high_relevance_count: int
    average_relevance: float

def get_openai_client():
    """Initialize OpenAI client."""
    if not settings.openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    return OpenAI(api_key=settings.openai_api_key)

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_posts(request: AnalysisRequest):
    """Analyze Reddit posts using OpenAI for relevance scoring."""
    try:
        client = get_openai_client()
        analyzed_posts = []
        
        # Convert business context to string
        context_str = f"""
        Company Type: {request.business_context.company_type}
        Specialty: {request.business_context.specialty}
        Blog Focus: {request.business_context.blog_focus}
        Target Audience: {request.business_context.target_audience}
        Interests: {', '.join(request.business_context.interests)}
        """
        
        for post in request.posts:
            try:
                # Create analysis prompt
                prompt = f"""
                Analyze this Reddit post for relevance to our business:
                
                BUSINESS CONTEXT:
                {context_str}
                
                REDDIT POST:
                Title: {post.title}
                Subreddit: r/{post.subreddit}
                Content: {post.selftext or 'No content'}
                Keywords: {', '.join(post.keywords)}
                
                Please provide a JSON response with:
                1. relevance_score: 0-100 (how relevant is this post to our business?)
                2. content_type: Type of content (question, discussion, news, etc.)
                3. target_audience_match: How well does this match our target audience?
                4. reasoning: Brief explanation of the relevance score
                5. business_opportunity: Potential business opportunity or content idea
                
                Respond ONLY with valid JSON, no other text.
                """
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a business intelligence analyst. Analyze Reddit posts for business relevance and provide structured JSON responses."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                # Parse JSON response
                analysis_data = json.loads(response.choices[0].message.content)
                
                # Create analyzed post
                analyzed_post = AnalyzedPost(
                    **post.dict(),
                    relevance_score=analysis_data.get('relevance_score'),
                    content_type=analysis_data.get('content_type'),
                    target_audience_match=analysis_data.get('target_audience_match'),
                    reasoning=analysis_data.get('reasoning'),
                    business_opportunity=analysis_data.get('business_opportunity')
                )
                
                analyzed_posts.append(analyzed_post)
                
            except Exception as e:
                print(f"Error analyzing post {post.title}: {e}")
                # Add post without analysis if analysis fails
                analyzed_post = AnalyzedPost(**post.dict())
                analyzed_posts.append(analyzed_post)
        
        # Calculate statistics
        relevant_posts = [p for p in analyzed_posts if p.relevance_score is not None]
        high_relevance_count = len([p for p in relevant_posts if p.relevance_score >= 70])
        average_relevance = sum(p.relevance_score for p in relevant_posts) / len(relevant_posts) if relevant_posts else 0
        
        return AnalysisResponse(
            analyzed_posts=analyzed_posts,
            total_analyzed=len(analyzed_posts),
            high_relevance_count=high_relevance_count,
            average_relevance=average_relevance
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

@router.get("/health")
async def analysis_health():
    """Check if OpenAI client is working."""
    try:
        client = get_openai_client()
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return {"status": "healthy", "message": "OpenAI client is working"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI client error: {e}")
