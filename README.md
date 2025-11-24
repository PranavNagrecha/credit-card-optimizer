# Credit Card Rewards Optimizer

A Python system for optimizing credit card usage by recommending the best card for specific purchases based on rewards programs.

## Overview

This system answers the question: **"Which credit card should I use for this purchase to get the maximum value?"**

It does this by:
1. Collecting data on credit cards and their reward structures
2. Normalizing rewards across different programs (cashback, points, miles)
3. Matching merchant queries to earning categories
4. Computing effective reward rates
5. Ranking cards by value

## Project Structure

```
credit_card_optimizer/
├── __init__.py
├── __main__.py              # CLI entry point
├── models.py                # Data models (CardProduct, EarningRule, etc.)
├── config.py                # Configuration constants
├── normalization.py         # Category and merchant mapping
├── valuation.py             # Reward point/mile valuation
├── engine.py                # Recommendation engine
├── scrapers/
│   ├── __init__.py
│   ├── base.py              # Base scraper class
│   └── issuers/
│       ├── __init__.py
│       ├── chase.py        # Chase scraper (mocked)
│       └── amex.py         # Amex scraper (mocked)
└── README.md
```

## Usage

### CLI

```bash
# Query by merchant name
python -m credit_card_optimizer "Macy's"
python -m credit_card_optimizer "Amazon"

# Query by category
python -m credit_card_optimizer "groceries"
python -m credit_card_optimizer "gas"
python -m credit_card_optimizer "restaurants"
```

### Python API

```python
from credit_card_optimizer.engine import find_best_cards_for_query
from credit_card_optimizer.scrapers.issuers.chase import ChaseScraper
from credit_card_optimizer.scrapers.issuers.amex import AmexScraper

# Load cards and rules
chase = ChaseScraper()
amex = AmexScraper()

all_cards = chase.scrape_cards() + amex.scrape_cards()
all_rules = []
for card in all_cards:
    all_rules.extend(chase.scrape_earning_rules(card) if card.issuer.name == "Chase" else amex.scrape_earning_rules(card))

# Get recommendation
recommendation = find_best_cards_for_query("Macy's", all_cards, all_rules)
print(recommendation.explanation)
```

## Data Models

### CardProduct
Represents a credit card with issuer, network, fees, and reward program.

### EarningRule
Defines how rewards are earned: categories, multipliers, caps, and special conditions.

### MerchantCategoryMapping
Maps merchant names to normalized categories and MCC codes.

### ComputedRecommendation
Final output with ranked cards and explanations.

## Configuration

Edit `config.py` to adjust:
- Point/mile valuations (e.g., Chase UR = 1.7 cents)
- HTTP request settings
- Recommendation limits
- Category synonyms

## Extending the System

### Adding a New Issuer

1. Create a new scraper in `scrapers/issuers/`:

```python
from ..base import BaseScraper

class NewIssuerScraper(BaseScraper):
    def scrape_cards(self) -> List[CardProduct]:
        # Implement scraping logic
        pass
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        # Implement rule extraction
        pass
```

2. Register it in `__main__.py`:

```python
from .scrapers.issuers.new_issuer import NewIssuerScraper

scrapers = [
    ChaseScraper(),
    AmexScraper(),
    NewIssuerScraper(),  # Add here
]
```

### Adding Manual Data

Instead of scraping, you can load cards from JSON:

```python
import json
from credit_card_optimizer.models import CardProduct, EarningRule

# Load from JSON file
with open("data/cards.json") as f:
    card_data = json.load(f)
    # Convert to CardProduct objects
```

## Current Status

- ✅ Data models implemented
- ✅ Normalization and valuation logic
- ✅ Recommendation engine with cap enforcement
- ✅ CLI interface
- ✅ **Production Chase scraper** with structured DOM selectors and schema.org parsing
- ✅ Caching and offline mode support
- ✅ All fallback data removed (fails fast on errors)
- ⚠️ Other issuer scrapers still use mocked data (structure ready for production)

## Features

### Cap Enforcement
The system now properly enforces spending caps by computing blended rates:
- When spending exceeds cap: `(cap_amount × high_rate + remaining × base_rate) / total_spend`
- Example: 5% cashback with $1,500/quarter cap → ~3% blended rate if spending exceeds cap

### Caching & Offline Mode
- Responses are cached in `.cache/scrapers/` directory
- Offline mode: `OFFLINE_MODE=true python -m credit_card_optimizer "groceries"`
- Reduces API calls and enables offline testing

### Production Scraping
- Chase scraper uses structured DOM selectors and schema.org data
- No fallback data - fails fast on errors to prevent incorrect recommendations
- Proper error handling and logging

## Web API Deployment

The system includes a FastAPI web application for easy deployment as a web service.

### Quick Start

**Option 1: Docker Compose (Recommended)**
```bash
docker-compose up -d
```

**Option 2: Direct Python**
```bash
pip install -r requirements.txt
python -m credit_card_optimizer.api
```

**Option 3: Quick Start Script**
```bash
./run.sh
```

### Access Points

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Frontend**: http://localhost:8000/ (if static files are available)
- **Health Check**: http://localhost:8000/health

### API Endpoints

- `GET /api/recommend?query=Amazon&max_results=5` - Get recommendations
- `GET /api/cards` - List all cards
- `GET /api/stats` - Get statistics
- `GET /health` - Health check

## Deployment

- **Quick Start**: See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions
- **Free Hosting Options**: See [FREE_HOSTING.md](FREE_HOSTING.md) for free hosting platforms
- **Architecture**: See [HOW_IT_WORKS.md](HOW_IT_WORKS.md) for system architecture

## Next Steps

1. **Implement production scrapers for other issuers**: Amex, Citi, Capital One, etc.
2. **Add unit tests**: Cap enforcement, display formatting, scraper parsing
3. **Enhance category matching**: Improve merchant name resolution
4. **User spending input**: Allow users to specify expected spending for accurate cap calculations
5. **Database storage**: Persist cards and rules in a database for better performance
6. **Background jobs**: Move scraping to background tasks for faster API responses

## Legal & Ethical Considerations

- Respect `robots.txt` and website terms of service
- Use manual JSON ingestion for sites that prohibit scraping
- Rate limit requests to avoid overloading servers
- Do not hard-code proprietary content in the codebase

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install requests beautifulsoup4 lxml
```

## Dependencies

- Python 3.9+
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser (optional, but recommended for better performance)

## License

[Your license here]

