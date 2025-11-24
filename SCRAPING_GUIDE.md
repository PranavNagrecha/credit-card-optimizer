# Production Scraping Guide

## Status

✅ **Chase scraper is now production-ready** with real HTML parsing
- Fetches actual card pages from chase.com
- Extracts card names, annual fees, networks, reward types
- Parses earning rules from HTML content
- Includes fallback data if scraping fails

## How It Works

### Chase Scraper Implementation

1. **Card Discovery**: Scrapes known Chase card URLs:
   - Sapphire Preferred
   - Sapphire Reserve
   - Freedom Flex
   - Freedom Unlimited
   - Slate
   - Freedom Rise

2. **Data Extraction**:
   - Card name from `<h1>` or `<title>` tags
   - Annual fee via regex patterns
   - Network (Visa/Mastercard) from page content
   - Reward type (points/cashback) from content analysis

3. **Earning Rules Parsing**:
   - Searches for reward sections in HTML
   - Extracts multipliers (e.g., "3x points", "5% cashback")
   - Identifies categories (dining, groceries, travel, etc.)
   - Detects spending caps and rotating categories

4. **Error Handling**:
   - Falls back to known data if scraping fails
   - Logs all errors for debugging
   - Continues processing other cards if one fails

## Running Production Scraping

```bash
# Install dependencies first
pip install -r requirements.txt

# Run the scraper
python -m credit_card_optimizer "groceries"
```

The system will:
1. Scrape all Chase cards from their website
2. Extract earning rules for each card
3. Use the data for recommendations

## Next Steps: Expand to All Issuers

The same pattern can be applied to all other issuers:

### Amex Scraper
- URL: https://www.americanexpress.com/us/credit-cards/
- Cards: Gold, Platinum, Blue Cash, etc.
- Pattern: Similar HTML structure to Chase

### Citi Scraper
- URL: https://www.citi.com/credit-cards/
- Cards: Premier, Double Cash, Custom Cash, etc.

### Capital One Scraper
- URL: https://www.capitalone.com/credit-cards/
- Cards: Venture X, Venture, SavorOne, Quicksilver

### Bank of America
- URL: https://www.bankofamerica.com/credit-cards/
- Cards: Premium Rewards, Customized Cash

### Discover
- URL: https://www.discover.com/credit-cards/
- Cards: it Cash Back, it Miles

### U.S. Bank
- URL: https://www.usbank.com/credit-cards/
- Cards: Altitude Reserve, Cash+

### Wells Fargo
- URL: https://www.wellsfargo.com/credit-cards/
- Cards: Active Cash, Autograph

### Co-Branded Cards
- Amazon: https://www.amazon.com/credit-cards/
- Costco: https://www.citi.com/credit-cards/costco-anywhere-visa-card
- Target: https://www.target.com/redcard

## Scraping Strategy

### 1. Identify Card URLs
Each issuer has a main credit cards page. Extract all card links from there.

### 2. Parse Card Details
For each card page:
- Extract card name
- Find annual fee
- Determine network (Visa/Mastercard/Amex/Discover)
- Identify reward type (points/cashback/miles)

### 3. Extract Earning Rules
Look for sections containing:
- Multiplier patterns: "3x", "5%", "2 points per dollar"
- Category mentions: "dining", "groceries", "travel"
- Cap information: "up to $1,500 per quarter"
- Special conditions: "rotating", "through portal"

### 4. Normalize Data
- Convert all rewards to standard format
- Map categories to normalized list
- Extract MCC codes if available

## Rate Limiting & Ethics

- **Rate Limiting**: 1 second delay between requests (configurable)
- **User Agent**: Realistic browser user agent
- **Retry Logic**: 3 retries with exponential backoff
- **Error Handling**: Graceful degradation to fallback data

## Testing

Test each scraper individually:

```python
from credit_card_optimizer.scrapers.issuers.chase import ChaseScraper

scraper = ChaseScraper()
cards = scraper.scrape_cards()
print(f"Found {len(cards)} cards")

for card in cards:
    rules = scraper.scrape_earning_rules(card)
    print(f"{card.name}: {len(rules)} earning rules")
```

## Monitoring

All scrapers log:
- Successful card scrapes
- Failed requests
- Parsing errors
- Fallback activations

Check logs to monitor scraping health.

