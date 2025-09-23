# Reddit Agent MVP

A Streamlit web application that monitors Reddit for specific keywords, analyzes posts with AI for business relevance, and exports results to Google Docs.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root:
```env
# Reddit API Credentials (Required)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
USER_AGENT=reddit-agent-mvp/1.0

# Google Docs API Credentials (Optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_ACCESS_TOKEN=your_google_access_token
GOOGLE_REFRESH_TOKEN=your_google_refresh_token

# OpenAI API Credentials (Required for AI Analysis)
OPENAI_API_KEY=your_openai_api_key
```

### 3. Run the Application
```bash
python run_app.py
```
Or directly:
```bash
streamlit run streamlit_app.py
```

## Getting API Credentials

### Reddit API
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Copy the client ID and secret

### Google Docs API (Optional)
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Google Docs API and Google Drive API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` and place in project root
6. Run the app once to generate tokens, then add them to `.env`

### OpenAI API (Required for AI Analysis)
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add the key to your `.env` file as `OPENAI_API_KEY`

## Usage

1. Open the web interface
2. Click "Initialize Services" in the sidebar
3. Enter keywords and subreddits to monitor
4. Click "Start Search"
5. Click "Analyze with AI" to get relevance scores and business insights
6. Select posts and export to Google Docs (if configured)

## Features

- **Reddit Monitoring**: Search Reddit posts by keywords and subreddits
- **AI Analysis**: Use OpenAI to analyze post relevance for your business
- **Business Context**: Configured for data visualization software house
- **Relevance Scoring**: Posts are scored 0-100 based on business relevance
- **Export to Google Docs**: Export selected or all posts with AI insights
- **Statistics Dashboard**: View metrics and content type distribution

## Deployment

The app is configured for Azure Web App deployment with `startup.sh` and `.deployment` files.
