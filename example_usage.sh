#!/bin/bash
# AI Pricing Engine API - Example Usage
# This script demonstrates how to use the AI Pricing Engine API with curl

# Set the API token
export API_TOKEN="test_token"

# Base URL for the API
BASE_URL="http://127.0.0.1:8000"

echo "===== AI Pricing Engine API Examples ====="

# 1. Health Check - Verify API is running
echo -e "\n1. Health Check:"
curl -s -X GET ${BASE_URL}/api/health | jq

# 2. Generate Price for an NFT
echo -e "\n2. Generate Price for an NFT:"
curl -s -X POST ${BASE_URL}/api/price \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "asset_id": "bored_ape_1234",
    "current_price": 120000
  }' | jq

# 3. Generate Price for a Real Estate Token
echo -e "\n3. Generate Price for a Real Estate Token:"
curl -s -X POST ${BASE_URL}/api/price \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "asset_id": "manhattan_property_token",
    "current_price": 2500000
  }' | jq

# 4. Update Market Data Source
echo -e "\n4. Update Market Data Source:"
curl -s -X POST ${BASE_URL}/api/datasource/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "source_name": "market_data",
    "data": {
      "market_indices": {
        "sp500": 5120.45,
        "nasdaq": 16780.32,
        "bitcoin": 78500.21
      },
      "volatility_index": 18.5,
      "interest_rate": 3.75,
      "timestamp": "2025-04-30T09:38:00.000000"
    },
    "timestamp": "2025-04-30T09:38:00.000000"
  }' | jq

# 5. Update NFT Auction Data
echo -e "\n5. Update NFT Auction Data:"
curl -s -X POST ${BASE_URL}/api/datasource/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "source_name": "nft_auction_data",
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
    "timestamp": "2025-04-30T09:38:00.000000"
  }' | jq

# 6. Update Sentiment Analysis Data
echo -e "\n6. Update Sentiment Analysis Data:"
curl -s -X POST ${BASE_URL}/api/datasource/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "source_name": "sentiment_data",
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
    "timestamp": "2025-04-30T09:38:00.000000"
  }' | jq

# 7. Get Asset Metadata (may return "not found" if asset doesn't exist)
echo -e "\n7. Get Asset Metadata:"
curl -s -X GET ${BASE_URL}/api/assets/bored_ape_1234 | jq

echo -e "\n===== End of Examples ====="
