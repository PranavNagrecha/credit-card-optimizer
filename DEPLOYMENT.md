# Deployment Guide

This guide covers deploying the Credit Card Optimizer as a web service.

## Quick Start

### Option 1: Docker Compose (Recommended)

1. **Clone and navigate to the project:**
```bash
cd credit_card_optimizer
```

2. **Start the service:**
```bash
docker-compose up -d
```

3. **Access the API:**
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

4. **View logs:**
```bash
docker-compose logs -f
```

5. **Stop the service:**
```bash
docker-compose down
```

### Option 2: Direct Python

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the API:**
```bash
python -m credit_card_optimizer.api
```

Or with uvicorn directly:
```bash
uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port 8000
```

### Option 3: Docker (Standalone)

1. **Build the image:**
```bash
docker build -t credit-card-optimizer .
```

2. **Run the container:**
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/cache:/app/.cache/scrapers \
  --name credit-card-optimizer \
  credit-card-optimizer
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Get Recommendations
```bash
GET /api/recommend?query=Amazon&max_results=5
```

### List All Cards
```bash
GET /api/cards
```

### Get Statistics
```bash
GET /api/stats
```

### Interactive API Documentation
Visit http://localhost:8000/docs for Swagger UI or http://localhost:8000/redoc for ReDoc.

## Example API Usage

### Using curl:
```bash
# Get recommendations for Amazon
curl "http://localhost:8000/api/recommend?query=Amazon"

# Get recommendations for groceries
curl "http://localhost:8000/api/recommend?query=groceries&max_results=3"
```

### Using Python:
```python
import requests

response = requests.get("http://localhost:8000/api/recommend", params={
    "query": "Amazon",
    "max_results": 5
})
data = response.json()
print(data["explanation"])
for card in data["candidate_cards"]:
    print(f"{card['card']['name']}: {card['effective_rate_cents_per_dollar']:.2f}%")
```

### Using JavaScript (fetch):
```javascript
const response = await fetch('http://localhost:8000/api/recommend?query=Amazon');
const data = await response.json();
console.log(data.explanation);
data.candidate_cards.forEach(card => {
    console.log(`${card.card.name}: ${card.effective_rate_cents_per_dollar}%`);
});
```

## Environment Variables

Create a `.env` file (or use environment variables):

```bash
USE_CACHE=true          # Enable response caching
OFFLINE_MODE=false      # Only use cached data (no network requests)
API_HOST=0.0.0.0        # API host (default: 0.0.0.0)
API_PORT=8000          # API port (default: 8000)
CORS_ORIGINS=*         # CORS allowed origins (comma-separated)
```

## Production Deployment

### Cloud Platforms

#### Heroku

1. **Create Procfile:**
```
web: uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port $PORT
```

2. **Deploy:**
```bash
heroku create your-app-name
git push heroku main
```

#### AWS (ECS/Fargate)

1. **Push Docker image to ECR:**
```bash
aws ecr create-repository --repository-name credit-card-optimizer
docker tag credit-card-optimizer:latest <account>.dkr.ecr.<region>.amazonaws.com/credit-card-optimizer:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/credit-card-optimizer:latest
```

2. **Create ECS task definition** (use the Docker image)
3. **Create ECS service** with Fargate launch type

#### Google Cloud Run

1. **Build and push:**
```bash
gcloud builds submit --tag gcr.io/<project-id>/credit-card-optimizer
```

2. **Deploy:**
```bash
gcloud run deploy credit-card-optimizer \
  --image gcr.io/<project-id>/credit-card-optimizer \
  --platform managed \
  --allow-unauthenticated \
  --port 8000
```

#### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name credit-card-optimizer \
  --image credit-card-optimizer:latest \
  --dns-name-label credit-card-optimizer \
  --ports 8000
```

### Using a Reverse Proxy (Nginx)

Create `/etc/nginx/sites-available/credit-card-optimizer`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/credit-card-optimizer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Using Systemd (Linux)

Create `/etc/systemd/system/credit-card-optimizer.service`:

```ini
[Unit]
Description=Credit Card Optimizer API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/credit_card_optimizer
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn credit_card_optimizer.api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable credit-card-optimizer
sudo systemctl start credit-card-optimizer
```

## Performance Considerations

1. **Caching**: Enable `USE_CACHE=true` to cache scraper responses
2. **Offline Mode**: Use `OFFLINE_MODE=true` for production if you pre-populate cache
3. **Load Balancing**: Use multiple instances behind a load balancer
4. **Database**: Consider persisting cards/rules in a database instead of scraping on startup
5. **Background Jobs**: Move scraping to background tasks (Celery, RQ, etc.)

## Monitoring

### Health Checks
Monitor `/health` endpoint:
```bash
curl http://localhost:8000/health
```

### Logging
Logs are output to stdout/stderr. In Docker:
```bash
docker-compose logs -f api
```

### Metrics
Consider adding Prometheus metrics or APM tools (Datadog, New Relic, etc.)

## Security

1. **CORS**: Update `CORS_ORIGINS` in production to specific domains
2. **Rate Limiting**: Add rate limiting middleware (e.g., `slowapi`)
3. **Authentication**: Add API keys or OAuth if needed
4. **HTTPS**: Use SSL/TLS in production (Let's Encrypt, Cloudflare, etc.)

## Troubleshooting

### Service won't start
- Check logs: `docker-compose logs api`
- Verify Python version (3.9+)
- Check port 8000 is available

### Slow responses
- Enable caching: `USE_CACHE=true`
- Pre-populate cache in offline mode
- Consider database storage instead of scraping

### Scraping failures
- Check network connectivity
- Verify target websites are accessible
- Review scraper logs for specific errors

## Support

For issues or questions, check:
- API documentation: http://localhost:8000/docs
- Project README.md
- Scraper logs in `.cache/scrapers/`

