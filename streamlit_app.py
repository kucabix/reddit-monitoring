import streamlit as st
import os
import time
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import praw
from google_docs_integration import GoogleDocsWriter
from openai_analysis import RedditPostAnalyzer
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
if 'openai_analyzer' not in st.session_state:
    st.session_state.openai_analyzer = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'analyzed_results' not in st.session_state:
    st.session_state.analyzed_results = []
if 'search_in_progress' not in st.session_state:
    st.session_state.search_in_progress = False
if 'analysis_in_progress' not in st.session_state:
    st.session_state.analysis_in_progress = False
if 'selected_results' not in st.session_state:
    st.session_state.selected_results = []
if 'keywords_placeholder' not in st.session_state:
    st.session_state.keywords_placeholder = ""
if 'subreddits_placeholder' not in st.session_state:
    st.session_state.subreddits_placeholder = "all"

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

def init_openai_analyzer(business_context=None):
    """Initialize OpenAI analyzer."""
    try:
        analyzer = RedditPostAnalyzer(business_context=business_context)
        return analyzer
    except Exception as e:
        st.warning(f"OpenAI analyzer initialization failed: {e}")
        return None

def generate_placeholders_with_openai(company_type, specialty, blog_focus, target_audience, interests):
    """Generate keywords and subreddits using OpenAI based on business context."""
    try:
        # Create temporary OpenAI client
        from openai import OpenAI
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found")
        
        client = OpenAI(api_key=api_key)
        
        # Create prompt for OpenAI
        prompt = f"""
        Based on this business context, generate relevant keywords and subreddits for Reddit monitoring:

        BUSINESS CONTEXT:
        - Company Type: {company_type}
        - Specialty: {specialty}
        - Blog Focus: {blog_focus}
        - Target Audience: {target_audience}
        - Interests: {', '.join(interests) if interests else 'Not specified'}

        Please generate:
        1. 10-15 relevant keywords that people might use when discussing topics related to this business
        2. 8-10 relevant subreddits where this business might find relevant discussions

        IMPORTANT: You MUST format your response EXACTLY as follows:

        KEYWORDS:
        keyword1
        keyword2
        keyword3
        [continue with more keywords, one per line]

        SUBREDDITS:
        subreddit1
        subreddit2
        subreddit3
        [continue with more subreddits, one per line, without r/ prefix]

        Do not include any other text, explanations, or formatting. Just the keywords and subreddits in the exact format above.
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in business intelligence and social media monitoring. Generate relevant keywords and subreddits for Reddit monitoring based on business context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Parse the response
        response_text = response.choices[0].message.content
        
        # Extract keywords and subreddits with improved parsing
        keywords = []
        subreddits = []
        
        lines = response_text.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Check for section headers (case insensitive)
            if line.upper().startswith('KEYWORDS'):
                current_section = 'keywords'
                # Remove the header text and get any keyword on the same line
                remaining = line.split(':', 1)[-1].strip()
                if remaining:
                    keywords.append(remaining)
                continue
            elif line.upper().startswith('SUBREDDITS'):
                current_section = 'subreddits'
                # Remove the header text and get any subreddit on the same line
                remaining = line.split(':', 1)[-1].strip()
                if remaining:
                    subreddits.append(remaining)
                continue
            
            # Add items to current section
            if line and current_section == 'keywords':
                # Clean up the keyword (remove bullets, dashes, numbers)
                clean_keyword = line.lstrip('•-*123456789. ').strip()
                if clean_keyword and len(clean_keyword) > 1:
                    keywords.append(clean_keyword)
            elif line and current_section == 'subreddits':
                # Clean up the subreddit (remove bullets, dashes, numbers, r/ prefix)
                clean_subreddit = line.lstrip('•-*123456789. ').strip()
                if clean_subreddit.startswith('r/'):
                    clean_subreddit = clean_subreddit[2:]
                if clean_subreddit and len(clean_subreddit) > 1:
                    subreddits.append(clean_subreddit)
        
        # Remove duplicates while preserving order
        keywords = list(dict.fromkeys(keywords))
        subreddits = list(dict.fromkeys(subreddits))
        
        # Ensure we have some results
        if not keywords and not subreddits:
            raise ValueError("No keywords or subreddits found in response")
        
        return keywords, subreddits
        
    except Exception as e:
        st.warning(f"Failed to generate placeholders with OpenAI: {e}")
        # Return empty placeholders if OpenAI fails
        return [], []

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

def analyze_posts_with_ai(posts: list):
    """Analyze posts using OpenAI for relevance scoring."""
    if not st.session_state.openai_analyzer:
        st.error("OpenAI analyzer not initialized. Please check your OpenAI API key.")
        return []
    
    if not posts:
        return []
    
    st.session_state.analysis_in_progress = True
    
    try:
        # Analyze posts in batches to avoid overwhelming the API
        analyzed_posts = st.session_state.openai_analyzer.analyze_posts_batch(posts)
        return analyzed_posts
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return posts  # Return original posts if analysis fails
    finally:
        st.session_state.analysis_in_progress = False

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Reddit Agent MVP</h1>
        <p>Monitor Reddit for keywords, analyze with AI, and export results to Google Docs</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Business Context Accordion
        with st.expander("🏢 Business Context", expanded=False):
            st.markdown("Customize the business context for AI analysis:")
            
            # Company Type
            company_type = st.text_input(
                "Company Type:",
                value="software house",
                help="Type of company (e.g., software house, e-commerce platform, SaaS startup)"
            )
            
            # Specialty
            specialty = st.text_input(
                "Specialty:",
                value="data visualization",
                help="Company's main specialty or focus area"
            )
            
            # Blog Focus
            blog_focus = st.text_input(
                "Blog Focus:",
                value="data visualization topics",
                help="Main topics for blog content"
            )
            
            # Target Audience
            target_audience = st.text_input(
                "Target Audience:",
                value="data professionals, analysts, developers",
                help="Primary target audience for content"
            )
            
            # Interests
            interests_input = st.text_area(
                "Interests (one per line or comma-separated):",
                value="data visualization tools and techniques\nbusiness intelligence\ndashboard design\ndata storytelling\nanalytics platforms\ndata science workflows\nvisualization libraries (D3.js, Plotly, etc.)\nbusiness data challenges\ndata-driven decision making\ninteractive dashboards\ndata visualization best practices\nBI tools and platforms",
                height=120,
                help="Company interests and focus areas (one per line or comma-separated)"
            )
        
        # Initialize clients
        if st.button("🔄 Initialize Services", type="primary"):
            with st.spinner("Initializing services..."):
                st.session_state.reddit_client = init_reddit_client()
                st.session_state.docs_writer = init_google_docs()
                
                # Process interests input (same as keywords)
                interests = []
                if interests_input:
                    # Split by newlines and commas, then clean
                    raw_interests = interests_input.replace('\n', ',').split(',')
                    interests = [i.strip() for i in raw_interests if i.strip()]
                else:
                    # Default interests if none provided
                    interests = [
                        f"{specialty} tools and techniques",
                        "business intelligence",
                        "dashboard design",
                        "data storytelling",
                        "analytics platforms",
                        "data science workflows",
                        "visualization libraries (D3.js, Plotly, etc.)",
                        "business data challenges",
                        "data-driven decision making",
                        "interactive dashboards",
                        f"{specialty} best practices",
                        "BI tools and platforms"
                    ]
                
                # Create custom business context from user inputs
                custom_business_context = {
                    "company_type": company_type,
                    "specialty": specialty,
                    "blog_focus": blog_focus,
                    "target_audience": target_audience,
                    "interests": interests
                }
                
                # Generate placeholders using OpenAI
                with st.spinner("🤖 Generating smart keywords and subreddits with AI..."):
                    keywords_placeholder, subreddits_placeholder = generate_placeholders_with_openai(
                        company_type, specialty, blog_focus, target_audience, interests
                    )
                
                # Store placeholders in session state
                st.session_state.keywords_placeholder = "\n".join(keywords_placeholder)
                st.session_state.subreddits_placeholder = "\n".join(subreddits_placeholder)
                
                st.session_state.openai_analyzer = init_openai_analyzer(business_context=custom_business_context)
                
                if st.session_state.reddit_client:
                    st.success("✅ Reddit client initialized")
                else:
                    st.error("❌ Reddit client failed")
                    
                if st.session_state.docs_writer:
                    st.success("✅ Google Docs initialized")
                else:
                    st.warning("⚠️ Google Docs not available")
                
                if st.session_state.openai_analyzer:
                    st.success("✅ OpenAI analyzer initialized")
                else:
                    st.warning("⚠️ OpenAI analyzer not available")

        # Keywords input
        st.markdown("### 🏷️ Keywords")
        keywords_input = st.text_area(
            "Enter keywords (one per line or comma-separated):",
            value=st.session_state.keywords_placeholder,
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
            value=st.session_state.subreddits_placeholder,
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
        
        # AI Analysis button moved to main content area
        analyze_button = False

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
            progress_bar.progress(0.2)
            
            results = search_reddit(keywords, subreddits, days_back)
            st.session_state.search_results = results
            
            progress_bar.progress(0.4)
            status_text.text("🧠 Analyzing posts with AI...")
            
            # Analyze posts with AI if analyzer is available
            if st.session_state.openai_analyzer and results:
                analyzed_results = analyze_posts_with_ai(results)
                st.session_state.analyzed_results = analyzed_results
                progress_bar.progress(0.8)
                status_text.text("✅ Search and AI Analysis completed!")
            else:
                if not st.session_state.openai_analyzer:
                    st.warning("⚠️ OpenAI analyzer not initialized. Results will be displayed without AI analysis.")
                progress_bar.progress(0.8)
                status_text.text("✅ Search completed!")
            
            progress_bar.progress(1.0)
            st.session_state.search_in_progress = False
            
            # Clear progress indicators
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
        
        
        # Display results
        if st.session_state.search_results:
            # Use analyzed results if available, otherwise use search results
            display_results = st.session_state.analyzed_results if st.session_state.analyzed_results else st.session_state.search_results
            
            # Show analysis status
            if st.session_state.analyzed_results:
                st.success("🤖 AI Analysis Complete - Posts are sorted by relevance score!")
            else:
                st.info("💡 Results displayed without AI analysis. Initialize OpenAI analyzer for relevance scoring.")
            
            for i, result in enumerate(display_results):
                # Show relevance score if available
                relevance_score = result.get('relevance_score', None)
                score_display = f" (Relevance: {relevance_score}/100)" if relevance_score is not None else ""
                
                # Simple checkbox with title - let Streamlit manage the state
                st.checkbox(
                    f"📝 {result['title']}{score_display}",
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
                
                # Show AI insights using Streamlit components
                if relevance_score is not None:
                    with st.expander("🤖 AI Analysis", expanded=False):
                        ai_col1, ai_col2 = st.columns(2)
                        
                        with ai_col1:
                            st.metric("Relevance Score", f"{relevance_score}/100")
                            st.write("**Content Type:**", result.get('content_type', 'N/A'))
                            st.write("**Target Audience Match:**", result.get('target_audience_match', 'N/A'))
                        
                        with ai_col2:
                            st.write("**Reasoning:**")
                            st.write(result.get('reasoning', 'N/A'))
                        
                        st.write("**Business Opportunity:**")
                        st.write(result.get('business_opportunity', 'N/A'))
            
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
            
            # Display basic metrics
            st.metric("Total Posts", total_posts)
            st.metric("Selected Posts", selected_posts)
            st.metric("Unique Subreddits", unique_subreddits)
            st.metric("Average Score", f"{avg_score:.1f}")
            
            # Show AI analysis metrics if available
            if st.session_state.analyzed_results:
                st.markdown("### 🤖 AI Analysis Insights")
                
                # Calculate AI metrics
                relevant_posts = [r for r in st.session_state.analyzed_results if r.get('relevance_score', 0) > 0]
                high_relevance_posts = [r for r in st.session_state.analyzed_results if r.get('relevance_score', 0) >= 70]
                avg_relevance = sum(r.get('relevance_score', 0) for r in st.session_state.analyzed_results) / len(st.session_state.analyzed_results)
                
                st.metric("Relevant Posts", len(relevant_posts))
                st.metric("High Relevance (70+)", len(high_relevance_posts))
                st.metric("Avg Relevance Score", f"{avg_relevance:.1f}")
                
                # Show content type distribution
                content_types = {}
                for result in st.session_state.analyzed_results:
                    content_type = result.get('content_type', 'Unknown')
                    content_types[content_type] = content_types.get(content_type, 0) + 1
                
                if content_types:
                    st.markdown("**Content Types:**")
                    for content_type, count in content_types.items():
                        st.write(f"• {content_type}: {count}")
            
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
                            # Use analyzed results if available, otherwise use search results
                            export_results = st.session_state.analyzed_results if st.session_state.analyzed_results else st.session_state.search_results
                            
                            # Determine which results to export
                            if export_option == "Export Selected Posts Only" and selected_posts > 0:
                                results_to_export = [export_results[i] for i in st.session_state.selected_results]
                                analysis_suffix = " (AI Analyzed)" if st.session_state.analyzed_results else ""
                                title = f"Reddit Monitoring Results (Selected{analysis_suffix}) - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                            else:
                                results_to_export = export_results
                                analysis_suffix = " (AI Analyzed)" if st.session_state.analyzed_results else ""
                                title = f"Reddit Monitoring Results (All{analysis_suffix}) - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                            
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
