"""
Data models and schemas for the RWA AI Pricing Engine.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class PriceSignal(BaseModel):
    """Price signal for a tokenized asset."""
    asset_id: str
    price: float
    confidence_score: float
    timestamp: str
    factors: Dict[str, float]
    explanation: Optional[str] = None
    trend: Optional[str] = None
    
class AssetMetadata(BaseModel):
    """Metadata for a tokenized asset."""
    asset_id: str
    name: str
    category: str
    description: str
    initial_price: float
    created_at: str
    
class PricingRequest(BaseModel):
    """Request for generating a price signal."""
    asset_id: str
    current_price: Optional[float] = None
    include_factors: bool = False

class DataSourceUpdate(BaseModel):
    """Update for a data source in the AI engine."""
    source_name: str
    data: Any
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    last_model_update: str
