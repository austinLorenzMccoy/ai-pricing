"""
Unit tests for schema models.
"""
import pytest
from datetime import datetime
from ai_pricing.models.schemas import PriceSignal, AssetMetadata, PricingRequest, DataSourceUpdate

def test_price_signal_schema():
    """Test the PriceSignal schema."""
    # Create a valid price signal
    price_signal = PriceSignal(
        asset_id="asset1",
        price=55000.0,
        confidence_score=0.85,
        timestamp=datetime.now().isoformat(),
        factors={"market_data": 0.6, "sentiment": 0.4}
    )
    
    # Check attributes
    assert price_signal.asset_id == "asset1"
    assert price_signal.price == 55000.0
    assert price_signal.confidence_score == 0.85
    assert isinstance(price_signal.timestamp, str)
    assert price_signal.factors["market_data"] == 0.6
    assert price_signal.factors["sentiment"] == 0.4
    
    # Test serialization
    serialized = price_signal.dict()
    assert serialized["asset_id"] == "asset1"
    assert serialized["price"] == 55000.0
    assert serialized["confidence_score"] == 0.85
    assert "timestamp" in serialized
    assert serialized["factors"]["market_data"] == 0.6

def test_asset_metadata_schema():
    """Test the AssetMetadata schema."""
    # Create a valid asset metadata
    asset = AssetMetadata(
        asset_id="asset1",
        name="Digital Art Piece",
        category="digital_art",
        description="A beautiful digital art piece",
        initial_price=50000.0,
        created_at=datetime.now().isoformat()
    )
    
    # Check attributes
    assert asset.asset_id == "asset1"
    assert asset.name == "Digital Art Piece"
    assert asset.category == "digital_art"
    assert asset.description == "A beautiful digital art piece"
    assert asset.initial_price == 50000.0
    assert isinstance(asset.created_at, str)
    
    # Test serialization
    serialized = asset.dict()
    assert serialized["asset_id"] == "asset1"
    assert serialized["name"] == "Digital Art Piece"
    assert serialized["initial_price"] == 50000.0

def test_pricing_request_schema():
    """Test the PricingRequest schema."""
    # Create a valid pricing request with defaults
    request = PricingRequest(asset_id="asset1")
    
    # Check attributes
    assert request.asset_id == "asset1"
    assert request.current_price is None
    assert request.include_factors is False
    
    # Create a request with all fields
    request_full = PricingRequest(
        asset_id="asset2",
        current_price=55000.0,
        include_factors=True
    )
    
    # Check attributes
    assert request_full.asset_id == "asset2"
    assert request_full.current_price == 55000.0
    assert request_full.include_factors is True
    
    # Test serialization
    serialized = request_full.dict()
    assert serialized["asset_id"] == "asset2"
    assert serialized["current_price"] == 55000.0
    assert serialized["include_factors"] is True

def test_data_source_update_schema():
    """Test the DataSourceUpdate schema."""
    # Create a valid data source update
    update = DataSourceUpdate(
        source_name="auction_data",
        data={"recent_sales": [{"item": "art1", "price": 50000}]},
        timestamp=datetime.now().isoformat()
    )
    
    # Check attributes
    assert update.source_name == "auction_data"
    assert isinstance(update.data, dict)
    assert "recent_sales" in update.data
    assert isinstance(update.timestamp, str)
    
    # Test serialization
    serialized = update.dict()
    assert serialized["source_name"] == "auction_data"
    assert serialized["data"]["recent_sales"][0]["price"] == 50000
