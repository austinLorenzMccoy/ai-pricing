"""
API routes for the RWA AI Pricing Engine.
"""
import os
import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ai_pricing.models.schemas import (
    PriceSignal, AssetMetadata, PricingRequest, 
    DataSourceUpdate, HealthResponse
)
from ai_pricing.core.pricing_engine import AIPricingEngine
from ai_pricing.data.asset_db import get_asset_db
from ai_pricing import __version__

# Initialize logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Authentication with OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize pricing engine
pricing_engine = AIPricingEngine()

# Get asset database
asset_db = get_asset_db()

# Authentication middleware
def validate_token(token: str = Depends(oauth2_scheme)):
    """Validate the authentication token."""
    expected_token = os.getenv("API_TOKEN", "test_token")
    if token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@router.get("/", tags=["general"])
async def root():
    """Root endpoint with basic information."""
    return {
        "name": "RWA AI Pricing Engine",
        "version": __version__,
        "description": "AI engine for dynamic pricing of tokenized real-world assets"
    }

@router.post("/api/price", response_model=PriceSignal, tags=["pricing"])
async def generate_price(request: PricingRequest, token: str = Depends(validate_token)):
    """Generate AI price signal for a tokenized asset."""
    if request.asset_id not in asset_db:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset_metadata = asset_db[request.asset_id]
    if request.current_price:
        asset_metadata["current_price"] = request.current_price
    
    price_signal = await pricing_engine.get_asset_price(request.asset_id, asset_metadata)
    return price_signal

@router.post("/api/datasource/update", tags=["data"])
async def update_data_source(data: DataSourceUpdate, token: str = Depends(validate_token)):
    """Update a data source in the AI engine."""
    result = await pricing_engine.update_knowledge_base(data.dict())
    return result

@router.get("/api/assets/{asset_id}", response_model=Dict, tags=["assets"])
async def get_asset(asset_id: str):
    """Get asset metadata."""
    if asset_id not in asset_db:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset_db[asset_id]

@router.get("/api/health", response_model=HealthResponse, tags=["general"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version=__version__,
        last_model_update=pricing_engine.last_model_update.isoformat()
    )
