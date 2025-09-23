import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class RedditPostAnalyzer:
    """
    Analyzes Reddit posts using OpenAI to determine relevance for a data visualization software house.
    """
    
    def __init__(self, api_key: Optional[str] = None, business_context: Optional[Dict[str, Any]] = None):
        """
        Initialize the analyzer with OpenAI API key.
        
        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY from environment.
            business_context: Custom business context dictionary. If None, uses default.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Set business context (use provided or default)
        if business_context:
            self.business_context = business_context
        else:
            # Default business context for data visualization software house
            self.business_context = {
                "company_type": "software house",
                "specialty": "data visualization",
                "blog_focus": "data visualization topics",
                "target_audience": "data professionals, analysts, developers",
                "interests": [
                    "data visualization tools and techniques",
                    "business intelligence",
                    "dashboard design",
                    "data storytelling",
                    "analytics platforms",
                    "data science workflows",
                    "visualization libraries (D3.js, Plotly, etc.)",
                    "business data challenges",
                    "data-driven decision making",
                    "interactive dashboards",
                    "data visualization best practices",
                    "BI tools and platforms"
                ]
            }
    
    def analyze_post_relevance(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single Reddit post for relevance to the business.
        
        Args:
            post: Reddit post dictionary with title, selftext, subreddit, etc.
            
        Returns:
            Dictionary with relevance score, reasoning, and insights
        """
        try:
            # Prepare the content for analysis
            content = f"""
            Title: {post.get('title', '')}
            Subreddit: r/{post.get('subreddit', '')}
            Content: {post.get('selftext', '')[:1000]}  # Limit content to avoid token limits
            Score: {post.get('score', 0)}
            Comments: {post.get('num_comments', 0)}
            """
            
            # Create the analysis prompt
            prompt = self._create_analysis_prompt(content)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert business analyst specializing in identifying relevant opportunities for a data visualization software house."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content
            
            # Extract structured data from the response
            analysis = self._parse_analysis_response(analysis_text)
            
            return {
                "relevance_score": analysis.get("relevance_score", 0),
                "reasoning": analysis.get("reasoning", ""),
                "business_opportunity": analysis.get("business_opportunity", ""),
                "content_type": analysis.get("content_type", ""),
                "target_audience_match": analysis.get("target_audience_match", ""),
                "raw_analysis": analysis_text
            }
            
        except Exception as e:
            return {
                "relevance_score": 0,
                "reasoning": f"Analysis failed: {str(e)}",
                "business_opportunity": "",
                "content_type": "",
                "target_audience_match": "",
                "raw_analysis": f"Error: {str(e)}"
            }
    
    def analyze_posts_batch(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple Reddit posts for relevance.
        
        Args:
            posts: List of Reddit post dictionaries
            
        Returns:
            List of posts with added analysis data
        """
        analyzed_posts = []
        
        for i, post in enumerate(posts):
            # Add analysis to the post
            analysis = self.analyze_post_relevance(post)
            post_with_analysis = {**post, **analysis}
            analyzed_posts.append(post_with_analysis)
        
        # Sort by relevance score (highest first)
        analyzed_posts.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return analyzed_posts
    
    def _create_analysis_prompt(self, content: str) -> str:
        """Create the analysis prompt for OpenAI."""
        return f"""
        Analyze this Reddit post for relevance to the specified business:

        BUSINESS CONTEXT:
        - Company: {self.business_context.get('company_type', 'Unknown')} specializing in {self.business_context.get('specialty', 'Unknown')}
        - Blog focus: {self.business_context.get('blog_focus', 'Unknown')}
        - Target audience: {self.business_context.get('target_audience', 'Unknown')}
        - Interests: {', '.join(self.business_context.get('interests', []))}

        REDDIT POST:
        {content}

        Please analyze this post and provide:
        1. RELEVANCE_SCORE: A score from 0-100 indicating how relevant this post is to our business
        2. REASONING: Brief explanation of why this score was given
        3. BUSINESS_OPPORTUNITY: How this could be relevant for our business (content ideas, potential clients, industry insights)
        4. CONTENT_TYPE: What type of content this represents (question, discussion, showcase, news, etc.)
        5. TARGET_AUDIENCE_MATCH: How well this matches our target audience

        Format your response as:
        RELEVANCE_SCORE: [0-100]
        REASONING: [brief explanation]
        BUSINESS_OPPORTUNITY: [how this relates to our business]
        CONTENT_TYPE: [type of content]
        TARGET_AUDIENCE_MATCH: [audience relevance]
        """
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the OpenAI response into structured data."""
        analysis = {
            "relevance_score": 0,
            "reasoning": "",
            "business_opportunity": "",
            "content_type": "",
            "target_audience_match": ""
        }
        
        try:
            lines = response_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('RELEVANCE_SCORE:'):
                    score_text = line.replace('RELEVANCE_SCORE:', '').strip()
                    try:
                        analysis["relevance_score"] = int(score_text)
                    except ValueError:
                        analysis["relevance_score"] = 0
                elif line.startswith('REASONING:'):
                    analysis["reasoning"] = line.replace('REASONING:', '').strip()
                elif line.startswith('BUSINESS_OPPORTUNITY:'):
                    analysis["business_opportunity"] = line.replace('BUSINESS_OPPORTUNITY:', '').strip()
                elif line.startswith('CONTENT_TYPE:'):
                    analysis["content_type"] = line.replace('CONTENT_TYPE:', '').strip()
                elif line.startswith('TARGET_AUDIENCE_MATCH:'):
                    analysis["target_audience_match"] = line.replace('TARGET_AUDIENCE_MATCH:', '').strip()
        except Exception as e:
            print(f"Error parsing analysis response: {e}")
        
        return analysis
    
    def get_top_posts(self, analyzed_posts: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the top most relevant posts.
        
        Args:
            analyzed_posts: List of analyzed posts
            limit: Maximum number of posts to return
            
        Returns:
            List of top posts sorted by relevance score
        """
        # Filter posts with relevance score > 0 and sort by score
        relevant_posts = [post for post in analyzed_posts if post.get('relevance_score', 0) > 0]
        relevant_posts.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return relevant_posts[:limit]
    
    def get_analysis_summary(self, analyzed_posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of the analysis results.
        
        Args:
            analyzed_posts: List of analyzed posts
            
        Returns:
            Summary statistics and insights
        """
        if not analyzed_posts:
            return {"error": "No posts to analyze"}
        
        # Calculate statistics
        total_posts = len(analyzed_posts)
        relevant_posts = [p for p in analyzed_posts if p.get('relevance_score', 0) > 0]
        high_relevance_posts = [p for p in analyzed_posts if p.get('relevance_score', 0) >= 70]
        
        avg_score = sum(p.get('relevance_score', 0) for p in analyzed_posts) / total_posts if total_posts > 0 else 0
        
        # Get content type distribution
        content_types = {}
        for post in analyzed_posts:
            content_type = post.get('content_type', 'Unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        # Get top subreddits by relevance
        subreddit_scores = {}
        for post in analyzed_posts:
            subreddit = post.get('subreddit', 'Unknown')
            score = post.get('relevance_score', 0)
            if subreddit not in subreddit_scores:
                subreddit_scores[subreddit] = []
            subreddit_scores[subreddit].append(score)
        
        # Calculate average scores per subreddit
        subreddit_avg_scores = {
            sub: sum(scores) / len(scores) 
            for sub, scores in subreddit_scores.items()
        }
        top_subreddits = sorted(subreddit_avg_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_posts": total_posts,
            "relevant_posts": len(relevant_posts),
            "high_relevance_posts": len(high_relevance_posts),
            "average_relevance_score": round(avg_score, 2),
            "content_type_distribution": content_types,
            "top_subreddits_by_relevance": top_subreddits,
            "relevance_distribution": {
                "0-30": len([p for p in analyzed_posts if 0 <= p.get('relevance_score', 0) < 30]),
                "30-60": len([p for p in analyzed_posts if 30 <= p.get('relevance_score', 0) < 60]),
                "60-80": len([p for p in analyzed_posts if 60 <= p.get('relevance_score', 0) < 80]),
                "80-100": len([p for p in analyzed_posts if 80 <= p.get('relevance_score', 0) <= 100])
            }
        }
