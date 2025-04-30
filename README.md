# 🚀 RWA AI Pricing Engine

![RWA AI Pricing](https://img.shields.io/badge/RWA-AI%20Pricing-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-teal)
![Web3](https://img.shields.io/badge/Web3-6.15.0-purple)
![License](https://img.shields.io/badge/License-MIT-orange)

A sophisticated AI-powered engine for dynamic pricing of tokenized real-world assets (RWAs). This system leverages large language models, blockchain data, market data, sentiment analysis, and economic indicators to generate accurate price signals for tokenized assets.

## ✨ Features

- **AI-Powered Pricing**: Uses Groq's LLM models (Mixtral-8x7b) to analyze multiple data sources and generate price signals
- **Blockchain Integration**: Connects to Ethereum via Infura to verify asset ownership and metadata
- **Multi-Source Analysis**: Combines NFT data, auction data, sentiment analysis, and economic indicators
- **Real API Integrations**: Connects to Alpha Vantage, FRED, NewsAPI, and OpenSea APIs
- **Vector Knowledge Base**: Maintains an evolving knowledge base of market trends and asset information
- **Lightweight Embedding Model**: Uses TensorFlow Hub's Universal Sentence Encoder Lite (18.8 MB) for efficient text embeddings
- **RESTful API**: Clean, well-documented API built with FastAPI
- **Modular Architecture**: Organized, maintainable codebase with clear separation of concerns
- **Docker Support**: Easy deployment with containerization
- **Comprehensive Testing**: Pytest-based test suite for reliability

## 🏗️ Architecture

The RWA AI Pricing Engine follows a modular architecture:

```
ai_pricing/
├── api/            # API endpoints and FastAPI application
├── core/           # Core pricing engine and business logic
├── data/           # Data access and storage
├── models/         # Data models and schemas
├── services/       # External service integrations
│   ├── blockchain.py  # Blockchain integration with Web3
│   └── data_sources.py # API integrations for market data
├── tests/          # Test suite
└── utils/          # Utility functions and helpers
```

## 🛠️ Installation

### Using pip

```bash
# Clone the repository
git clone https://github.com/thebulls/ai_pricing.git
cd ai_pricing

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package with development dependencies
pip install -e ".[dev]"
```

### Using Docker

```bash
# Build the Docker image
docker build -t rwa-ai-pricing .

# Run the container
docker run -p 8000:8000 --env-file .env rwa-ai-pricing
```

### Production Deployment with Docker Compose

For production deployment, we provide optimized Docker configurations that handle dependency conflicts and ensure robust operation:

```bash
# Build and start the production services
docker-compose -f docker-compose.production.yml up -d

# Check logs
docker logs ai-pricing-api

# Stop the services
docker-compose -f docker-compose.production.yml down
```

The production setup includes:

- Patched embedding model that works without TensorFlow dependencies
- Robust error handling for API integrations
- Health checks to ensure service availability
- Automatic asset database initialization
- Proper network isolation for security

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables (or use the provided `.env.template`):

```
# API Keys
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
FRED_API_KEY=your_fred_api_key
INFURA_ENDPOINT=https://mainnet.infura.io/v3/your_infura_key
OPENSEA_API_KEY=your_opensea_api_key
NEWSAPI_KEY=your_newsapi_key
GROQ_API_KEY=your_groq_key
API_TOKEN=your_secure_token

# App Config
REFRESH_INTERVAL=300  # 5 minutes

# API Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=False
ENVIRONMENT=development
```

## 🚀 Usage

### Running the API Server

```bash
# Start the API server
python main.py

# With auto-reload for development
python main.py --reload
```

### Running the Example

```bash
# Run the example usage
python main.py --example
```

### API Endpoints

- `GET /`: Root endpoint with basic information
- `POST /api/price`: Generate price signal for an asset
- `POST /api/datasource/update`: Update a data source
- `GET /api/assets/{asset_id}`: Get asset metadata
- `GET /api/health`: Health check endpoint

### Using curl

```bash
# Health check endpoint (no authentication required)
curl http://localhost:8000/api/health

# Generate price signal (requires authentication)
curl -X POST "http://localhost:8000/api/price" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_token" \
  -d '{"asset_id": "bitcoin", "current_price": 55000, "include_factors": true}'

# Update data source (requires authentication)
curl -X POST "http://localhost:8000/api/datasource/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_token" \
  -d '{"source_name": "market_data", "data": {"price": 55000}, "timestamp": "2025-04-28T16:00:00.000000"}'
```

### FastAPI Use Cases

#### 1. Asset Price Generation

```python
# Request
POST /api/price

{
  "asset_id": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/1",
  "metadata": {
    "name": "Bored Ape #1",
    "category": "nft",
    "description": "Bored Ape Yacht Club NFT",
    "initial_price": 100000.0
  }
}

# Response
{
  "asset_id": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/1",
  "price": 125000.0,
  "confidence_score": 0.85,
  "timestamp": "2025-04-22T16:50:00.000000",
  "factors": {
    "recent_market_data": 0.4,
    "sentiment_analysis": 0.2,
    "economic_indicators": 0.1,
    "blockchain_data": 0.2,
    "asset_intrinsic_value": 0.1
  },
  "explanation": "Price based on recent sales, market sentiment, and blockchain verification",
  "trend": "up"
}
```

#### 2. Data Source Update

```python
# Request
POST /api/datasource/update

{
  "source_name": "auction_data",
  "data": {
    "recent_sales": [
      {"item": "digital_art_new_piece", "price": 62000, "date": "2025-04-22"},
      {"item": "digital_art_trending", "price": 78000, "date": "2025-04-21"}
    ],
    "average_price": 70000,
    "price_trend": "+12.8%"
  },
  "timestamp": "2025-04-22T16:50:00.000000"
}

# Response
{
  "status": "success",
  "timestamp": "2025-04-22T16:50:01.123456"
}
```

#### 3. Blockchain Asset Verification

```python
# Request
GET /api/assets/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/1

# Response
{
  "asset_id": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/1",
  "name": "Bored Ape #1",
  "contract": {
    "name": "BoredApeYachtClub",
    "symbol": "BAYC",
    "address": "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
  },
  "owner": "0x8e04e63f69b4be0fd27a659933c203df2d5e2df5",
  "metadata": {
    "image_url": "https://ipfs.io/ipfs/QmeSjSinHpPnmXmspMjwiXyN6zS4E9zccariGR3jxcaWtq/1",
    "traits": [...],
    "last_sale": {
      "price": 100.5,
      "timestamp": "2025-03-15T12:30:45.000000"
    }
  },
  "verified": true
}
```

## 🧪 Testing

```bash
# Run the test suite
pytest

# Run with coverage report
pytest --cov=ai_pricing
```

## 💡 Embedding Model

The RWA AI Pricing Engine uses a lightweight embedding model for efficient text vectorization and semantic search:

- **TensorFlow Hub's Universal Sentence Encoder Lite**: A compact 18.8 MB model that generates 512-dimensional embeddings
- **Efficient Containerization**: Significantly smaller footprint compared to traditional embedding models (which can be several GB)
- **Compatibility**: Maintains the same vector dimension (512) for compatibility with the FAISS vector store
- **Batch Processing**: Implements efficient batch processing to handle large volumes of text
- **Error Handling**: Includes robust error handling with fallback to zero vectors

## 🔄 Workflow

1. **Data Collection**: The system collects data from various sources including OpenSea, Alpha Vantage, NewsAPI, FRED, and Ethereum blockchain.
2. **Blockchain Verification**: Asset ownership and metadata are verified through Ethereum using Infura.
3. **AI Analysis**: The Groq LLM (Mixtral-8x7b) analyzes the collected data to determine a fair market price.
4. **Price Signal Generation**: A price signal is generated with confidence score and influencing factors.
5. **Knowledge Base Update**: The system's knowledge base is continuously updated with new market data.

## 🔌 Integration

The RWA AI Pricing Engine can be integrated with:

- **Tokenization Platforms**: Provide real-time pricing for newly minted RWA tokens
- **Trading Platforms**: Support dynamic pricing for secondary market trading
- **DeFi Protocols**: Enable accurate collateral valuation for RWA-backed loans
- **Oracle Networks**: Feed price data to on-chain applications
- **NFT Marketplaces**: Provide accurate pricing for NFT assets
- **Blockchain Applications**: Connect directly with smart contracts for on-chain pricing

## 🛣️ Roadmap

- [x] Blockchain integration with Web3 and Infura
- [x] Integration with real-world APIs (Alpha Vantage, FRED, NewsAPI, OpenSea)
- [x] Upgraded LLM to Mixtral-8x7b for better analysis
- [x] Implemented lightweight embedding model for efficient containerization
- [ ] Multi-chain support (Ethereum, Polygon, Solana)
- [ ] Enhanced sentiment analysis with specialized models
- [ ] Advanced anomaly detection for price manipulation
- [ ] Time-series forecasting for price trends
- [ ] Governance mechanism for pricing disputes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ by TheBulls Team
