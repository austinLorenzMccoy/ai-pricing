"""
Mock database for tokenized assets.
"""
from typing import Dict, List, Optional
from datetime import datetime

def get_asset_db() -> Dict:
    """
    Get the mock asset database.
    
    In a production environment, this would be replaced with a real database.
    """
    return {
        "asset1": {
            "asset_id": "asset1",
            "name": "Beeple Digital Collage",
            "category": "digital_art",
            "description": "Famous NFT artwork by digital artist Beeple",
            "initial_price": 50000.00,
            "created_at": "2025-01-15"
        },
        "asset2": {
            "asset_id": "asset2",
            "name": "Luxury Manhattan Apartment",
            "category": "real_estate",
            "description": "High-end apartment in downtown financial district, 2 bed, 2 bath, 1200 sq ft",
            "initial_price": 1200000.00,
            "created_at": "2025-02-10"
        },
        "asset3": {
            "asset_id": "asset3",
            "name": "Vintage Wine Collection",
            "category": "collectibles",
            "description": "Collection of rare vintage wines from renowned vineyards",
            "initial_price": 75000.00,
            "created_at": "2025-03-05"
        },
        "asset4": {
            "asset_id": "asset4",
            "name": "Commercial Office Space",
            "category": "real_estate",
            "description": "Prime commercial office space in tech hub area",
            "initial_price": 2500000.00,
            "created_at": "2025-01-20"
        },
        "asset5": {
            "asset_id": "asset5",
            "name": "Renewable Energy Farm",
            "category": "infrastructure",
            "description": "Solar farm with 50MW capacity and long-term energy contracts",
            "initial_price": 5000000.00,
            "created_at": "2025-02-28"
        }
    }
