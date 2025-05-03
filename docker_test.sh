#!/bin/bash
# AI Pricing Engine Docker API - Production Testing
# This script demonstrates how to use the AI Pricing Engine API running in Docker with actual API keys

# Base URL for the Docker API
BASE_URL="http://localhost:8888"

echo "===== AI Pricing Engine Docker API Production Tests ====="

# 1. Health Check - Verify API is running
echo -e "\n1. Health Check:"
curl -s -X GET ${BASE_URL}/api/health | jq

# 2. Generate Price for an NFT with LLM-based valuation
echo -e "\n2. Generate Price for an NFT with LLM-based valuation:"
curl -s -X POST ${BASE_URL}/api/price \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "asset_id": "bored_ape_1234",
    "current_price": 120000,
    "use_llm": true
  }' | jq

# 3. Generate Price for a Real Estate Token with blockchain verification
echo -e "\n3. Generate Price for a Real Estate Token with blockchain verification:"
curl -s -X POST ${BASE_URL}/api/price \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "asset_id": "manhattan_property_token",
    "current_price": 2500000,
    "verify_on_chain": true
  }' | jq

# 4. Update Market Data Source with Alpha Vantage data
echo -e "\n4. Update Market Data Source with Alpha Vantage data:"
curl -s -X POST ${BASE_URL}/api/datasource/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "source_name": "alpha_vantage",
    "data": {
      "market_indices": {
        "sp500": 5120.45,
        "nasdaq": 16780.32,
        "bitcoin": 78500.21
      },
      "volatility_index": 18.5,
      "interest_rate": 3.75,
      "timestamp": "2025-04-30T09:45:00.000000"
    },
    "timestamp": "2025-04-30T09:45:00.000000"
  }' | jq

# 5. Update NFT Auction Data from OpenSea
echo -e "\n5. Update NFT Auction Data from OpenSea:"
curl -s -X POST ${BASE_URL}/api/datasource/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "source_name": "opensea",
    "data": {
      "recent_sales": [
        {"collection": "bored_ape", "token_id": 1234, "price": 125000, "date": "2025-04-29"},
        {"collection": "bored_ape", "token_id": 5678, "price": 118000, "date": "2025-04-28"},
        {"collection": "cryptopunks", "token_id": 9012, "price": 95000, "date": "2025-04-30"}
      ],
      "floor_prices": {
        "bored_ape": 110000,
        "cryptopunks": 90000,
        "art_blocks": 15000
      },
      "volume_24h": 3500000,
      "unique_buyers": 78
    },
    "timestamp": "2025-04-30T09:45:00.000000"
  }' | jq

# 6. Update Sentiment Analysis Data from NewsAPI
echo -e "\n6. Update Sentiment Analysis Data from NewsAPI:"
curl -s -X POST ${BASE_URL}/api/datasource/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "source_name": "newsapi",
    "data": {
      "social_media": {
        "twitter": 0.75,
        "reddit": 0.68,
        "discord": 0.82
      },
      "news_sentiment": 0.62,
      "search_trends": 1.25,
      "overall_score": 0.72
    },
    "timestamp": "2025-04-30T09:45:00.000000"
  }' | jq

# 7. Update Economic Indicators from FRED API
echo -e "\n7. Update Economic Indicators from FRED API:"
curl -s -X POST ${BASE_URL}/api/datasource/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "source_name": "fred",
    "data": {
      "gdp_growth": 3.2,
      "unemployment_rate": 3.8,
      "inflation_rate": 2.9,
      "housing_index": 285.4,
      "consumer_confidence": 108.7
    },
    "timestamp": "2025-04-30T09:45:00.000000"
  }' | jq

# 8. Get Asset Metadata (may return "not found" if asset doesn't exist)
echo -e "\n8. Get Asset Metadata:"
curl -s -X GET ${BASE_URL}/api/assets/bored_ape_1234 | jq

# 9. Test Blockchain Asset Verification
echo -e "\n9. Test Blockchain Asset Verification with Infura:"
curl -s -X POST ${BASE_URL}/api/price \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "asset_id": "ethereum_nft_12345",
    "current_price": 85000,
    "verify_on_chain": true,
    "contract_address": "0xd61E1Ccf90c293Ec1B02ad398626A3348Ef13A8a",
    "token_id": "12345"
  }' | jq

echo -e "\n===== End of Production Tests ====="
