# AI Pricing Engine - Docker Deployment Guide

This guide explains how to deploy the AI Pricing Engine using a standalone Docker container without Docker Compose.

## Prerequisites

- Docker installed on the deployment server
- All required API keys in a `.env` file (see `.env.template` for required variables)

## Deployment Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-pricing
   ```

2. **Create .env file**
   Make sure you have a `.env` file with all required API keys:
   ```
   GROQ_API_KEY=your_groq_api_key
   ALPHA_VANTAGE_KEY=your_alpha_vantage_key
   FRED_API_KEY=your_fred_api_key
   INFURA_ENDPOINT=your_infura_endpoint
   OPENSEA_API_KEY=your_opensea_api_key
   NEWSAPI_KEY=your_newsapi_key
   ```

3. **Build and run using the deployment script**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

   This script will:
   - Build the Docker image using `Dockerfile.deployment`
   - Stop and remove any existing container
   - Start a new container with all required volumes and environment variables

4. **Manual deployment (alternative to script)**
   If you prefer to run commands manually:
   ```bash
   # Build the Docker image
   docker build -t ai-pricing:latest -f Dockerfile.deployment .

   # Run the container
   docker run -d \
     --name ai-pricing-api \
     --restart unless-stopped \
     -p 9000:8000 \
     --env-file .env \
     -v "$(pwd)/data:/app/data" \
     -v "$(pwd)/logs:/app/logs" \
     -v "$(pwd)/faiss_index:/app/faiss_index" \
     ai-pricing:latest
   ```

## Container Management

- **Check container status**
  ```bash
  docker ps | grep ai-pricing-api
  ```

- **View logs**
  ```bash
  docker logs ai-pricing-api
  ```

- **Stop container**
  ```bash
  docker stop ai-pricing-api
  ```

- **Start container**
  ```bash
  docker start ai-pricing-api
  ```

## API Endpoints

The API will be available at `http://<server-ip>:9000` with the following endpoints:

- Health check: `GET /api/health`
- Generate price: `POST /api/price`
- Update data source: `POST /api/datasource/update`
- Get asset metadata: `GET /api/assets/{asset_id}`

See `example_usage.sh` for detailed API usage examples.

## Important Notes

1. The standalone Docker setup includes all necessary dependencies and doesn't require Redis or other external services.
2. Make sure your server has sufficient resources (at least 4GB RAM recommended).
3. The container uses a non-root user for security.
4. Data persistence is handled through volume mounts for `/app/data`, `/app/logs`, and `/app/faiss_index`.
