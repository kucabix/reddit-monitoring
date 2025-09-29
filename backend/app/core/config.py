from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Reddit API
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_user_agent: Optional[str] = None
    reddit_username: Optional[str] = None
    reddit_password: Optional[str] = None
    
    # OpenAI API
    openai_api_key: Optional[str] = None
    
    # Google Docs API
    google_credentials_file: Optional[str] = None
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_access_token: Optional[str] = None
    google_refresh_token: Optional[str] = None
    
    # App settings
    debug: bool = False
    user_agent: Optional[str] = None
    keywords: Optional[str] = None
    subreddits: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()
