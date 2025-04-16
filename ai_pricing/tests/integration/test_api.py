"""
Integration tests for the API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from ai_pricing.api.app import app
from ai_pricing.models.schemas import PriceSignal, AssetMetadata, PricingRequest
import os
import json
from datetime import datetime

# Create a test client
client = TestClient(app=app)

# Mock token for testing
TEST_API_TOKEN = "test_token"

# Setup and teardown
@pytest.fixture(autouse=True)
def setup_environment():
    """Setup test environment variables."""
    original_token = os.environ.get("API_TOKEN")
    os.environ["API_TOKEN"] = TEST_API_TOKEN
    yield
    if original_token:
        os.environ["API_TOKEN"] = original_token
    else:
        del os.environ["API_TOKEN"]

class TestPricingAPI:
    """Test cases for the pricing API endpoints."""
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_generate_price_unauthorized(self):
        """Test price generation with invalid token."""
        request_data = {"asset_id": "asset1"}
        response = client.post(
            "/api/price",
            json=request_data,
            headers={"Authorization": f"Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_generate_price(self):
        """Test price generation with valid token."""
        request_data = {"asset_id": "asset1", "include_factors": True}
        response = client.post(
            "/api/price",
            json=request_data,
            headers={"Authorization": f"Bearer {TEST_API_TOKEN}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "asset_id" in data
        assert "price" in data
        assert "confidence_score" in data
        assert "timestamp" in data
        assert "factors" in data
    
    def test_get_asset_metadata(self):
        """Test retrieving asset metadata."""
        response = client.get(
            "/api/assets/asset1",
            headers={"Authorization": f"Bearer {TEST_API_TOKEN}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["asset_id"] == "asset1"
        assert "name" in data
        assert "category" in data
    
    def test_update_data_source(self):
        """Test updating a data source."""
        update_data = {
            "source_name": "auction_data",
            "data": {
                "recent_sales": [{"item": "test_item", "price": 50000}]
            },
            "timestamp": datetime.now().isoformat()
        }
        response = client.post(
            "/api/data-sources/update",
            json=update_data,
            headers={"Authorization": f"Bearer {TEST_API_TOKEN}"}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
