"""
Configuration utilities for the RWA AI Pricing Engine.
"""
import os
import logging
from typing import Dict, Any
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

# Get configuration
def get_config() -> Dict[str, Any]:
    """Get application configuration from environment variables."""
    return {
        "api_token": os.getenv("API_TOKEN", "test_token"),
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "alpha_vantage_key": os.getenv("ALPHA_VANTAGE_KEY"),
        "fred_api_key": os.getenv("FRED_API_KEY"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "False").lower() == "true",
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8000")),
    }

# Project paths
def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent

def get_data_dir() -> Path:
    """Get the data directory."""
    data_dir = get_project_root() / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir
