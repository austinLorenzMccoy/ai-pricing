"""
Unit tests for data source adapters.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from ai_pricing.services.data_sources import DataSourceAdapter
import os

@pytest.fixture(autouse=True)
def setup_environment():
    """Setup test environment variables."""
    os.environ["ALPHA_VANTAGE_KEY"] = "test_alpha_key"
    os.environ["FRED_API_KEY"] = "test_fred_key"
    yield
    del os.environ["ALPHA_VANTAGE_KEY"]
    del os.environ["FRED_API_KEY"]

class TestDataSourceAdapter:
    """Test cases for the data source adapter."""
    
    @pytest.mark.asyncio
    async def test_fetch_auction_data(self):
        """Test fetching auction data."""
        # Mock the aiohttp ClientSession
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json = MagicMock(return_value={"bestMatches": []})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Call the method
            result = await DataSourceAdapter.fetch_auction_data("digital_art")
            
            # Assertions
            assert "recent_sales" in result
            assert "average_price" in result
            assert "price_trend" in result
    
    @pytest.mark.asyncio
    async def test_fetch_sentiment_analysis(self):
        """Test fetching sentiment analysis."""
        # Call the method
        result = await DataSourceAdapter.fetch_sentiment_analysis("asset1")
        
        # Assertions
        assert "overall_sentiment" in result
        assert "mention_volume" in result
        assert "trending_keywords" in result
        assert "source_breakdown" in result
    
    @pytest.mark.asyncio
    async def test_fetch_economic_indicators(self):
        """Test fetching economic indicators."""
        # Mock the aiohttp ClientSession
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json = MagicMock(return_value={"observations": []})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Call the method
            result = await DataSourceAdapter.fetch_economic_indicators()
            
            # Assertions
            assert "inflation_rate" in result
            assert "interest_rate" in result
            assert "consumer_confidence" in result
            assert "gdp_growth" in result
    

