#!/usr/bin/env python3
"""
Startup script for the Reddit Agent MVP Streamlit app.
This script provides an easy way to launch the application.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    try:
        import streamlit
        import praw
        import plotly
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if environment variables are available (from .env file or Azure)."""
    # Try to load .env file if it exists (for local development)
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded .env file")
    else:
        print("ℹ️ No .env file found, checking Azure environment variables")
    
    # Check for required environment variables
    required_vars = [
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET", 
        "REDDIT_USERNAME",
        "REDDIT_PASSWORD"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        if not env_file.exists():
            print("Please add these to your Azure Web App configuration or create a .env file")
        else:
            print("Please add these to your .env file")
        return False
    
    print("✅ Environment variables configured")
    return True

def main():
    """Main function to start the Streamlit app."""
    print("🚀 Starting Reddit Agent MVP...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment configuration
    if not check_env_file():
        sys.exit(1)
    
    print("✅ All checks passed!")
    print("🌐 Launching Streamlit app...")
    print("=" * 50)
    
    # Launch Streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
