from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reddit_posts.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

class DisplayedPost(Base):
    """Model for tracking Reddit posts that have been displayed to users."""
    __tablename__ = "displayed_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    reddit_id = Column(String, unique=True, index=True, nullable=False)  # Reddit post ID
    title = Column(String, nullable=False)
    created_utc = Column(DateTime, nullable=False)
    displayed_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
