#!/bin/bash

# Set the API token to the default value used in routes.py
export API_TOKEN="test_token"

echo "Testing API health endpoint..."
curl -X GET http://127.0.0.1:8000/api/health

echo -e "\n\nTesting price generation endpoint..."
curl -X POST http://127.0.0.1:8000/api/price \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{"asset_id": "digital_art_1", "current_price": 50000}'

echo -e "\n\nTesting data source update endpoint..."
curl -X POST http://127.0.0.1:8000/api/datasource/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token" \
  -d '{
    "source_name": "auction_data",
    "data": {
      "recent_sales": [
        {"item": "digital_art_new_piece", "price": 62000, "date": "2025-04-30"},
        {"item": "digital_art_trending", "price": 78000, "date": "2025-04-30"}
      ],
      "average_price": 70000,
      "price_trend": "+12.8%"
    },
    "timestamp": "2025-04-30T09:35:00.000000"
  }'

echo -e "\n\nTesting asset metadata endpoint..."
curl -X GET http://127.0.0.1:8000/api/assets/digital_art_1
