"""
Unit tests for the pricing engine.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from ai_pricing.core.pricing_engine import AIPricingEngine
from ai_pricing.models.schemas import DataSourceUpdate, PriceSignal
from datetime import datetime

@pytest.fixture
def pricing_engine():
    """Create a pricing engine instance for testing."""
    # Use a real environment variable or a default for testing
    engine = AIPricingEngine()
    return engine

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
def sample_data_source_update():
    """Sample data source update for testing."""
    return DataSourceUpdate(
        source_name="auction_data",
        data={
            "recent_sales": [
                {"item": "digital_art_piece", "price": 55000, "date": "2025-04-14"}
            ],
            "average_price": 55000,
            "price_trend": "+10.0%"
        },
        timestamp=datetime.now().isoformat()
    )

class TestPricingEngine:
    """Test cases for the pricing engine."""
    
    @pytest.mark.asyncio
    async def test_get_asset_price(self, pricing_engine, sample_asset_data):
        """Test getting an asset price."""
        # Mock the Groq API call
        with patch.object(pricing_engine, '_generate_price_with_llm') as mock_generate:
            mock_generate.return_value = {
                "price": 55000.0,
                "confidence_score": 0.85,
                "factors": {"market_data": 0.6, "sentiment": 0.4}
            }
            
            # Call the method
            result = await pricing_engine.get_asset_price("asset1", sample_asset_data)
            
            # Assertions
            assert isinstance(result, PriceSignal)
            assert result.asset_id == "asset1"
            assert result.price == 55000.0
            assert result.confidence_score == 0.85
            assert result.factors["market_data"] == 0.6
            assert result.factors["sentiment"] == 0.4
    
    @pytest.mark.asyncio
    async def test_update_knowledge_base(self, pricing_engine, sample_data_source_update):
        """Test updating the knowledge base."""
        # Call the method
        result = await pricing_engine.update_knowledge_base(sample_data_source_update.dict())
        
        # Assertions
        assert result["success"] is True
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_generate_price_with_llm(self, pricing_engine, sample_asset_data):
        """Test generating a price with the LLM."""
        # Mock the Groq client response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
        {
            "price": 55000.0,
            "confidence_score": 0.85,
            "factors": {
                "market_data": 0.6,
                "sentiment": 0.4
            }
        }
        """
        
        with patch('groq.AsyncClient') as MockClient:
            mock_client_instance = MagicMock()
            MockClient.return_value = mock_client_instance
            mock_client_instance.chat.completions.create = MagicMock(return_value=mock_response)
            
            # Call the method
            result = await pricing_engine._generate_price_with_llm(sample_asset_data)
            
            # Assertions
            assert result["price"] == 55000.0
            assert result["confidence_score"] == 0.85
            assert result["factors"]["market_data"] == 0.6
            assert result["factors"]["sentiment"] == 0.4
