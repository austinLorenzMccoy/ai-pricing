"""
Main entry point for the RWA AI Pricing Engine.
"""
import uvicorn
import asyncio
import logging
from ai_pricing.utils.config import get_config
from ai_pricing.api.app import app

# Get configuration
config = get_config()

# Example usage function
async def run_example():
    """Run an example of the pricing engine functionality."""
    from ai_pricing.core.pricing_engine import AIPricingEngine
    from ai_pricing.data.asset_db import get_asset_db
    from ai_pricing.models.schemas import DataSourceUpdate
    import json
    from datetime import datetime
    
    print("=== RWA AI Pricing Engine Example Usage ===")
    
    # Initialize components
    pricing_engine = AIPricingEngine()
    asset_db = get_asset_db()
    
    # 1. Get sample asset data
    asset_id = "asset1"
    print(f"\n1. Using sample asset {asset_id}...")
    asset_data = asset_db.get(asset_id)
    print(f"Asset data: {json.dumps(asset_data, indent=2)}")
    
    # 2. Generate a price for the asset
    print(f"\n2. Generating price for {asset_id}...")
    try:
        price_signal = await pricing_engine.get_asset_price(asset_id, asset_data)
        print(f"Price signal: {json.dumps(price_signal.__dict__, indent=2)}")
        
        # Example of factors breakdown
        print("\nFactors influencing the price:")
        for factor, weight in price_signal.factors.items():
            print(f"- {factor}: {weight:.2f}")
            
    except Exception as e:
        print(f"Error generating price: {e}")
    
    # 3. Update a data source
    print("\n3. Updating a data source...")
    new_auction_data = {
        "source_name": "auction_data",
        "data": {
            "recent_sales": [
                {"item": "digital_art_new_piece", "price": 62000, "date": "2025-04-14"},
                {"item": "digital_art_trending", "price": 78000, "date": "2025-04-13"}
            ],
            "average_price": 70000,
            "price_trend": "+12.8%"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Call the update_knowledge_base method directly
        data_source_update = DataSourceUpdate(
            source_name=new_auction_data["source_name"],
            data=new_auction_data["data"],
            timestamp=new_auction_data["timestamp"]
        )
        update_result = await pricing_engine.update_knowledge_base(data_source_update.dict())
        print(f"Data source update result: {update_result}")
        
    except Exception as e:
        print(f"Error updating data source: {e}")
    
    # 4. Generate a new price after data update
    print(f"\n4. Generating updated price for {asset_id} after new data...")
    try:
        updated_price_signal = await pricing_engine.get_asset_price(asset_id, asset_data)
        print(f"Updated price signal: {json.dumps(updated_price_signal.__dict__, indent=2)}")
        
        # Check if price changed from first pricing
        if 'price_signal' in locals():
            price_diff = updated_price_signal.price - price_signal.price
            percent_change = (price_diff / price_signal.price) * 100
            print(f"\nPrice changed by ${price_diff:.2f} ({percent_change:.2f}%)")
            print(f"This demonstrates how new market data influences the AI pricing model")
            
    except Exception as e:
        print(f"Error generating updated price: {e}")
        
    print("\n=== Example completed ===")
    print("In a production environment, you would:")
    print("1. Run the API server with 'uvicorn main:app --reload'")
    print("2. Connect to the API from your frontend")
    print("3. Set up Pharos oracle integration for on-chain price updates")
    print("4. Configure real data sources for auction data, sentiment, etc.")

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="RWA AI Pricing Engine")
    parser.add_argument("--example", action="store_true", help="Run example usage")
    parser.add_argument("--host", type=str, default=config["host"], help="Host to run the server on")
    parser.add_argument("--port", type=int, default=config["port"], help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()
    
    if args.example:
        # Run example usage
        asyncio.run(run_example())
    else:
        # Run the API server
        print(f"Starting RWA AI Pricing Engine v{app.version} on http://{args.host}:{args.port}")
        uvicorn.run(
            "ai_pricing.api.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )
