FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    HOST=0.0.0.0 \
    PORT=8000

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install basic tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.production.txt ./requirements.txt

# Install dependencies in stages to handle conflicts
# Stage 1: Core dependencies
RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.27.0 \
    python-dotenv==1.0.0 \
    pydantic==2.6.1 \
    requests==2.31.0 \
    aiohttp==3.9.1

# Stage 2: ML dependencies
RUN pip install --no-cache-dir \
    numpy==1.23.5 \
    "pandas<2.0.0" \
    faiss-cpu

# Stage 3: API integrations and remaining dependencies
RUN pip install --no-cache-dir \
    groq>=0.4.1 \
    web3==6.15.0 \
    python-jose==3.3.0 \
    passlib==1.7.4 \
    python-multipart==0.0.6 \
    python-dateutil==2.9.0 \
    textblob==0.17.1 \
    redis

# Create necessary directories for data, models, and logs
RUN mkdir -p /app/data /app/models /app/logs /app/faiss_index

# Copy application code
COPY . .

# Apply patched files to fix known issues (if they exist)
RUN if [ -f pricing_engine_patched.py ]; then cp pricing_engine_patched.py ai_pricing/core/pricing_engine.py; fi && \
    if [ -f embedding_model_patched.py ]; then cp embedding_model_patched.py ai_pricing/core/embedding_model.py; fi && \
    if [ -f routes_patched.py ]; then cp routes_patched.py ai_pricing/api/routes.py; fi

# Create a non-root user and switch to it
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Command to run the API server
# First run the load_assets.py script if it exists, then start the application
CMD if [ -f /app/load_assets.py ]; then python /app/load_assets.py; fi && \
    uvicorn ai_pricing.api.app:app --host 0.0.0.0 --port $PORT
