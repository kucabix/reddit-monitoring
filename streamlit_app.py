import streamlit as st
import os
import time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import praw
from google_docs_integration import GoogleDocsWriter
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Reddit Agent MVP",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Material Design
st.markdown("""
<style>
    /* Material Design Color Palette */
    :root {
        --primary-color: #1976d2;
        --primary-dark: #1565c0;
        --secondary-color: #424242;
        --accent-color: #ff4081;
        --background-color: #fafafa;
        --surface-color: #ffffff;
        --text-primary: #212121;
        --text-secondary: #757575;
        --divider-color: #e0e0e0;
    }

    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Material Design Cards */
    .metric-card {
        background: var(--surface-color);
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
    }

    .result-card {
        display: flex;
        flex-direction: column;
        background: #2d2d2d;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        border: 1px solid #404040;
    }
    
    .result-card h4 {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .result-card h4 input {
        width: 20px;
        height: 20px;
        flex-shrink: 0;
    }

    /* Material Design Buttons */
    .stButton > button {
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: var(--primary-dark);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Material Design Input Fields */
    .stTextInput > div > div > input {
        border: 1px solid var(--divider-color);
        border-radius: 4px;
        padding: 0.75rem;
        font-size: 1rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.2);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: var(--surface-color);
    }

    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: var(--primary-color);
    }

    /* Success/Error messages */
    .success-message {
        background: #e8f5e8;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 4px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }

    .error-message {
        background: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 4px;
        border-left: 4px solid #f44336;
        margin: 1rem 0;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        color: white;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        text-align: center;
    }

    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 300;
    }

    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }

    /* Selection buttons */
    .selection-buttons {
        margin-bottom: 1rem;
    }

    .selection-buttons .stButton > button {
        font-size: 0.9rem;
        padding: 0.4rem 0.8rem;
        margin-right: 0.5rem;
    }

    .stCheckbox p {
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        line-height: 1.4 !important;
    }

    .stCheckbox span {
        width: 20px !important;
        height: 20px !important;
        min-width: 20px !important;
        min-height: 20px !important;
    }
    
    .stCheckbox {
      margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'reddit_client' not in st.session_state:
    st.session_state.reddit_client = None
if 'docs_writer' not in st.session_state:
    st.session_state.docs_writer = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'search_in_progress' not in st.session_state:
    st.session_state.search_in_progress = False
if 'selected_results' not in st.session_state:
    st.session_state.selected_results = []

def init_reddit_client():
    """Initialize Reddit client with environment variables."""
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("USER_AGENT", "brand-listener-bot/1.0 (contact: you@example.com)"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
            ratelimit_seconds=5,
        )
        return reddit
    except Exception as e:
        st.error(f"Failed to initialize Reddit client: {e}")
        return None

def init_google_docs():
    """Initialize Google Docs integration."""
    try:
        docs_writer = GoogleDocsWriter()
        return docs_writer
    except Exception as e:
        st.warning(f"Google Docs integration failed: {e}")
        return None

# Removed seen.db concept - no longer tracking seen posts

def matches(text: str, keywords: list) -> tuple[bool, list]:
    """Check if text matches any keywords."""
    t = (text or "").lower()
    matched_keywords = [k for k in keywords if k.lower() in t]
    return bool(matched_keywords), matched_keywords

def search_reddit(keywords: list, subreddits: list, days_back: int = 30):
    """Search Reddit for posts matching keywords."""
    if not st.session_state.reddit_client:
        st.error("Reddit client not initialized. Please check your environment variables.")
        return []
    
    results = []
    
    # Calculate timestamp for specified days back
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_back)
    cutoff_timestamp = int(cutoff_time.timestamp())
    
    # Process each subreddit
    for subreddit_name in subreddits:
        try:
            if subreddit_name == "all":
                current_sub = st.session_state.reddit_client.subreddit("all")
            else:
                current_sub = st.session_state.reddit_client.subreddit(subreddit_name)
            
            # Get recent submissions
            for post in current_sub.new(limit=1000):
                if post.created_utc < cutoff_timestamp:
                    break
                    
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
                
                time.sleep(0.1)  # Rate limiting
                
        except Exception as e:
            st.error(f"Error searching r/{subreddit_name}: {e}")
            continue
    
    return results

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Reddit Agent MVP</h1>
        <p>Monitor Reddit for keywords and export results to Google Docs</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Initialize clients
        if st.button("🔄 Initialize Services", type="primary"):
            with st.spinner("Initializing services..."):
                st.session_state.reddit_client = init_reddit_client()
                st.session_state.docs_writer = init_google_docs()
                
                if st.session_state.reddit_client:
                    st.success("✅ Reddit client initialized")
                else:
                    st.error("❌ Reddit client failed")
                    
                if st.session_state.docs_writer:
                    st.success("✅ Google Docs initialized")
                else:
                    st.warning("⚠️ Google Docs not available")

        # Keywords input
        st.markdown("### 🏷️ Keywords")
        keywords_input = st.text_area(
            "Enter keywords (one per line or comma-separated):",
            value="",
            height=100,
            help="Enter keywords to search for in Reddit posts"
        )
        
        # Process keywords
        keywords = []
        if keywords_input:
            # Split by newlines and commas, then clean
            raw_keywords = keywords_input.replace('\n', ',').split(',')
            keywords = [k.strip().lower() for k in raw_keywords if k.strip()]
        
        # Subreddits input
        st.markdown("### 📍 Subreddits")
        subreddits_input = st.text_area(
            "Enter subreddits (one per line or comma-separated):",
            value="all",
            height=100,
            help="Enter subreddit names (without r/) or 'all' for all subreddits"
        )
        
        # Process subreddits
        subreddits = []
        if subreddits_input:
            raw_subreddits = subreddits_input.replace('\n', ',').split(',')
            subreddits = [s.strip() for s in raw_subreddits if s.strip()]
        
        # Search parameters
        st.markdown("### 📅 Search Parameters")
        days_back = st.slider(
            "Days to search back:",
            min_value=1,
            max_value=90,
            value=30,
            help="How many days back to search for posts"
        )
        
        # Search button
        search_button = st.button(
            "🔍 Start Search",
            type="primary",
            disabled=not keywords or not subreddits or st.session_state.search_in_progress
        )

    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Search Results")
        
        if search_button and keywords and subreddits:
            st.session_state.search_in_progress = True
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Search Reddit
            status_text.text("🔍 Searching Reddit...")
            progress_bar.progress(0.3)
            
            results = search_reddit(keywords, subreddits, days_back)
            st.session_state.search_results = results
            
            progress_bar.progress(0.7)
            status_text.text("✅ Search completed!")
            progress_bar.progress(1.0)
            
            st.session_state.search_in_progress = False
            
            # Clear progress indicators
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
        
        # Display results
        if st.session_state.search_results:
            for i, result in enumerate(st.session_state.search_results):
                # Simple checkbox with title - let Streamlit manage the state
                st.checkbox(
                    f"📝 {result['title']}",
                    key=f"checkbox_{i}"
                )
                
                # Show post details
                st.markdown(f"""
                <div class="result-card">
                    <p><strong>Subreddit:</strong> r/{result['subreddit']}</p>
                    <p><strong>Created:</strong> {result['created']}</p>
                    <p><strong>Keywords:</strong> {', '.join(result['keywords'])}</p>
                    <p><strong>Score:</strong> {result['score']} | <strong>Comments:</strong> {result['num_comments']}</p>
                    <p><strong>URL:</strong> <a href="{result['url']}" target="_blank">{result['url']}</a></p>
                    {f"<p><strong>Preview:</strong> {result['selftext']}</p>" if result['selftext'] else ""}
                </div>
                """, unsafe_allow_html=True)
            
            # Build selected results list from checkbox states
            selected_indices = []
            for i in range(len(st.session_state.search_results)):
                if st.session_state.get(f"checkbox_{i}", False):
                    selected_indices.append(i)
            st.session_state.selected_results = selected_indices
                

        else:
            st.info("👆 Configure your search parameters in the sidebar and click 'Start Search' to begin monitoring Reddit.")
    
    with col2:
        st.markdown("### 📈 Statistics")
        
        if st.session_state.search_results:
            # Create summary metrics
            total_posts = len(st.session_state.search_results)
            selected_posts = len(st.session_state.selected_results)
            unique_subreddits = len(set(r['subreddit'] for r in st.session_state.search_results))
            avg_score = sum(r['score'] for r in st.session_state.search_results) / total_posts if total_posts > 0 else 0
            
            # Display metrics
            st.metric("Total Posts", total_posts)
            st.metric("Selected Posts", selected_posts)
            st.metric("Unique Subreddits", unique_subreddits)
            st.metric("Average Score", f"{avg_score:.1f}")
            
            # Subreddit distribution chart
            if unique_subreddits > 1:
                subreddit_counts = {}
                for result in st.session_state.search_results:
                    sub = result['subreddit']
                    subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
                
                fig = px.pie(
                    values=list(subreddit_counts.values()),
                    names=list(subreddit_counts.keys()),
                    title="Posts by Subreddit"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Export to Google Docs
            if st.session_state.docs_writer:
                # Show export options
                if selected_posts > 0:
                    export_option = st.radio(
                        "Export Options:",
                        ["Export Selected Posts Only", "Export All Posts"],
                        index=0
                    )
                else:
                    export_option = "Export All Posts"
                    st.info("💡 Select posts using checkboxes to export only chosen ones")
                
                if st.button("📄 Export to Google Docs", type="secondary"):
                    with st.spinner("Exporting to Google Docs..."):
                        try:
                            # Determine which results to export
                            if export_option == "Export Selected Posts Only" and selected_posts > 0:
                                results_to_export = [st.session_state.search_results[i] for i in st.session_state.selected_results]
                                title = f"Reddit Monitoring Results (Selected) - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                            else:
                                results_to_export = st.session_state.search_results
                                title = f"Reddit Monitoring Results (All) - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                            
                            st.session_state.docs_writer.write_results(results_to_export, title)
                            st.success(f"✅ {len(results_to_export)} results exported to Google Docs successfully!")
                        except Exception as e:
                            st.error(f"❌ Failed to export to Google Docs: {e}")
            else:
                st.warning("⚠️ Google Docs integration not available")
        else:
            st.info("No results to display yet.")

if __name__ == "__main__":
    main()
