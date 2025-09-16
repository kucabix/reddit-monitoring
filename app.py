import os, time
from dotenv import load_dotenv
import praw
from datetime import datetime, timedelta, timezone
from google_docs_integration import GoogleDocsWriter

load_dotenv()

# Legacy support - can still be used as standalone script
def get_reddit_client():
    """Get Reddit client instance."""
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("USER_AGENT", "brand-listener-bot/1.0 (contact: you@example.com)"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        ratelimit_seconds=5,
    )

# Legacy environment variable support
KEYWORDS = [k.strip().lower() for k in os.getenv("KEYWORDS", "").split(",") if k.strip()]
SUBS = [s.strip() for s in os.getenv("SUBREDDITS", "all").split(",") if s.strip()]

# Removed seen.db concept - no longer tracking seen posts

def matches(text: str, keywords: list = None) -> tuple[bool, list]:
    if keywords is None:
        keywords = KEYWORDS
    t = (text or "").lower()
    matched_keywords = [k for k in keywords if k.lower() in t]
    return bool(matched_keywords), matched_keywords

def search_reddit_posts(keywords=None, subreddits=None, days_back=30, reddit_client=None):
    """
    Search Reddit for posts matching keywords.
    
    Args:
        keywords: List of keywords to search for
        subreddits: List of subreddit names to search in
        days_back: Number of days to search back
        reddit_client: Reddit client instance (optional)
    
    Returns:
        List of matching posts
    """
    # Use provided parameters or fall back to environment variables
    if keywords is None:
        keywords = KEYWORDS
    if subreddits is None:
        subreddits = SUBS if SUBS else ["all"]
    if reddit_client is None:
        reddit_client = get_reddit_client()
    
    results = []
    
    # Calculate timestamp for specified days back
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_back)
    cutoff_timestamp = int(cutoff_time.timestamp())
    
    # Get recent submissions from each subreddit
    for subreddit_name in subreddits:
        try:
            if subreddit_name == "all":
                current_sub = reddit_client.subreddit("all")
            else:
                current_sub = reddit_client.subreddit(subreddit_name)
            
            print(f"[info] searching r/{current_sub.display_name}...")
            
            # Get recent submissions (limit to 1000 to avoid rate limits)
            for post in current_sub.new(limit=1000):
                # Check if post is within specified time range
                if post.created_utc < cutoff_timestamp:
                    break  # Stop when we reach posts older than specified days
                    
                text = f"{post.title}\n{post.selftext or ''}"
                is_match, matched_keywords = matches(text, keywords)
                
                if is_match:
                    result = {
                        'title': post.title,
                        'subreddit': post.subreddit.display_name,
                        'url': f"https://reddit.com{post.permalink}",
                        'created': datetime.fromtimestamp(post.created_utc).strftime("%Y-%m-%d %H:%M:%S"),
                        'keywords': matched_keywords,
                        'selftext': post.selftext[:200] + "..." if len(post.selftext) > 200 else post.selftext,
                        'score': post.score,
                        'num_comments': post.num_comments
                    }
                    results.append(result)
                    
                    print(f"\nMATCH • r/{post.subreddit.display_name} • {post.permalink}")
                    print(f"Title: {post.title}")
                    print(f"Created: {result['created']}")
                    print(f"Keywords: {', '.join(matched_keywords)}")
                    # Later you can call: post.reply("Your helpful reply with disclosure")
                time.sleep(0.1)  # Rate limiting
                
        except Exception as e:
            print(f"[error] Error searching r/{subreddit_name}: {e}")
            continue
    
    return results

def main():
    """Legacy main function for standalone execution."""
    print(f"[ok] searching submissions from last month in: {', '.join(SUBS) if SUBS else 'all'}")
    print(f"[ok] keywords: {KEYWORDS}")
    
    # Initialize Google Docs integration
    docs_writer = None
    try:
        docs_writer = GoogleDocsWriter()
        print("[ok] Google Docs integration initialized")
    except Exception as e:
        print(f"[warning] Google Docs integration failed: {e}")
        print("[info] Results will only be printed to console")
    
    # Search for posts
    results = search_reddit_posts()
    
    print(f"[ok] finished searching posts from last month")
    print(f"[ok] found {len(results)} new matches")
    
    # Write results to Google Docs if available
    if docs_writer and results:
        try:
            docs_writer.write_results(results, f"Reddit Monitoring Results - {datetime.now().strftime('%Y-%m-%d')}")
            print(f"[ok] Results written to Google Docs successfully!")
        except Exception as e:
            print(f"[error] Failed to write to Google Docs: {e}")
    elif docs_writer and not results:
        print("[info] No new matches found, skipping Google Docs write")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nbye")
