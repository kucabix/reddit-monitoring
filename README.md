# Reddit Agent MVP

A Streamlit web application that monitors Reddit for specific keywords and exports results to Google Docs.

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

## Usage

1. Open the web interface
2. Click "Initialize Services" in the sidebar
3. Enter keywords and subreddits to monitor
4. Click "Start Search"
5. Select posts and export to Google Docs (if configured)

## Deployment

The app is configured for Azure Web App deployment with `startup.sh` and `.deployment` files.
