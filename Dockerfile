FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Update CA certificates
RUN update-ca-certificates

# Copy all application code
COPY . .

# Install pip with trusted host flags to avoid SSL issues
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir setuptools wheel

# Install Python dependencies with trusted hosts to avoid SSL issues
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org .

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "ai_pricing.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
