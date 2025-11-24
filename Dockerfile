FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directory
RUN mkdir -p .cache/scrapers

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OFFLINE_MODE=false
ENV USE_CACHE=true

# Run the API
CMD ["python", "-m", "uvicorn", "credit_card_optimizer.api:app", "--host", "0.0.0.0", "--port", "8000"]

