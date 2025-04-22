"""
Test script for verifying the new blockchain and API integrations.
"""
import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the services we want to test
from ai_pricing.services.data_sources import DataSourceAdapter
from ai_pricing.services.blockchain import BlockchainHelper

async def test_alpha_vantage():
    """Test Alpha Vantage API integration."""
    print("\n=== Testing Alpha Vantage API ===")
    try:
        result = await DataSourceAdapter.fetch_auction_data("tech")
        print(f"Success: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

async def test_news_api():
    """Test NewsAPI integration."""
    print("\n=== Testing NewsAPI Integration ===")
    try:
        result = await DataSourceAdapter.fetch_sentiment_analysis("bitcoin")
        print(f"Success: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

async def test_fred_api():
    """Test FRED API integration."""
    print("\n=== Testing FRED API Integration ===")
    try:
        result = await DataSourceAdapter.fetch_economic_indicators()
        print(f"Success: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

async def test_opensea_api():
    """Test OpenSea API integration."""
    print("\n=== Testing OpenSea API Integration ===")
    try:
        # Use a known NFT collection and token ID
        # Using Bored Ape Yacht Club as an example
        result = await DataSourceAdapter.fetch_nft_data("0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/1")
        print(f"Success: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_blockchain_connection():
    """Test blockchain connection via Infura."""
    print("\n=== Testing Blockchain Connection ===")
    try:
        blockchain = BlockchainHelper()
        if blockchain.w3 and blockchain.w3.is_connected():
            chain_id = blockchain.w3.eth.chain_id
            print(f"Successfully connected to Ethereum network (Chain ID: {chain_id})")
            
            # Test contract info - Bored Ape Yacht Club contract
            contract_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
            contract_info = blockchain.get_contract_info(contract_address)
            print(f"Contract info: {json.dumps(contract_info, indent=2)}")
            
            return True
        else:
            print("Failed to connect to Ethereum network")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

async def run_tests():
    """Run all integration tests."""
    print("Starting integration tests...")
    
    # Test blockchain connection
    blockchain_success = test_blockchain_connection()
    
    # Test API integrations
    alpha_vantage_success = await test_alpha_vantage()
    news_api_success = await test_news_api()
    fred_api_success = await test_fred_api()
    opensea_success = await test_opensea_api()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Blockchain Connection: {'✅' if blockchain_success else '❌'}")
    print(f"Alpha Vantage API: {'✅' if alpha_vantage_success else '❌'}")
    print(f"NewsAPI Integration: {'✅' if news_api_success else '❌'}")
    print(f"FRED API Integration: {'✅' if fred_api_success else '❌'}")
    print(f"OpenSea API Integration: {'✅' if opensea_success else '❌'}")

if __name__ == "__main__":
    asyncio.run(run_tests())
