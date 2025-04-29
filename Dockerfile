# Use a stable Python image with minimal dependencies
FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install basic tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install core dependencies first
RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.27.0 \
    python-dotenv==1.0.0 \
    pydantic==2.6.1 \
    requests==2.31.0 \
    aiohttp==3.9.1

# Install ML dependencies with the lightweight TensorFlow alternative
# Note: TensorFlow 2.12.0 requires numpy<1.24
RUN pip install --no-cache-dir \
    numpy==1.23.5 \
    tensorflow-cpu==2.12.0 \
    tensorflow-hub==0.14.0 \
    faiss-cpu==1.7.4 \
    "pandas<2.0.0"

# Install API integrations
RUN pip install --no-cache-dir \
    langchain-groq==0.1.5 \
    langchain-community>=0.0.35 \
    groq==0.5.0 \
    web3==6.15.0 \
    textblob==0.17.1

# Copy application code
COPY . .

# Create necessary directories for data, models, and logs
RUN mkdir -p /app/data /app/models /app/logs && \
    # Create a non-root user and switch to it
    useradd -m appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set and expose API port
ENV PORT=8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Command to run the API server
CMD uvicorn ai_pricing.api.app:app --host 0.0.0.0 --port $PORT
