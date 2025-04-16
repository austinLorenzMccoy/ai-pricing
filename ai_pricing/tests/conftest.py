"""
Common test fixtures and configurations for pytest.
"""
import pytest
import os
from datetime import datetime

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment with required environment variables."""
    # Store original environment variables
    original_env = {}
    for key in ["API_TOKEN", "GROQ_API_KEY", "ALPHA_VANTAGE_KEY", "FRED_API_KEY"]:
        original_env[key] = os.environ.get(key)
    
    # Set test environment variables
    os.environ["API_TOKEN"] = "test_api_token"
    os.environ["GROQ_API_KEY"] = "test_groq_api_key"
    os.environ["ALPHA_VANTAGE_KEY"] = "test_alpha_vantage_key"
    os.environ["FRED_API_KEY"] = "test_fred_api_key"
    
    yield
    
    # Restore original environment variables
    for key, value in original_env.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]

@pytest.fixture
def sample_asset_data():
    """Sample asset data for testing."""
    return {
        "asset_id": "asset1",
        "name": "Digital Art Piece",
        "category": "digital_art",
        "description": "A beautiful digital art piece",
        "initial_price": 50000.0,
        "created_at": datetime.now().isoformat()
    }

@pytest.fixture
def sample_price_signal_data():
    """Sample price signal data for testing."""
    return {
        "asset_id": "asset1",
        "price": 55000.0,
        "confidence_score": 0.85,
        "timestamp": datetime.now().isoformat(),
        "factors": {"market_data": 0.6, "sentiment": 0.4}
    }

@pytest.fixture
def sample_data_source_update():
    """Sample data source update for testing."""
    return {
        "source_name": "auction_data",
        "data": {
            "recent_sales": [
                {"item": "digital_art_piece", "price": 55000, "date": "2025-04-14"}
            ],
            "average_price": 55000,
            "price_trend": "+10.0%"
        },
        "timestamp": datetime.now().isoformat()
    }
