# NerdWallet Scraper - Primary Data Source

## Overview

The NerdWallet scraper is now the **primary data source** for credit card information. Instead of scraping individual issuer websites (which often have broken URLs and inconsistent structures), we scrape from NerdWallet, which aggregates and normalizes data from all major issuers.

## Why NerdWallet?

1. **Single Source**: One place to scrape instead of 10+ issuer sites
2. **Normalized Data**: Consistent structure across all cards
3. **More Reliable**: Fewer broken URLs and 404 errors
4. **Comprehensive**: Includes cards from all major issuers
5. **Up-to-date**: NerdWallet keeps their data current

## How It Works

### 1. URL Discovery

The scraper discovers card URLs by:
- Scraping the main credit cards listing page: `https://www.nerdwallet.com/credit-cards`
- Finding all links matching the pattern `/reviews/credit-cards/card-name`
- Filtering out comparison pages and other non-card pages

### 2. Card Parsing

For each card page, the scraper extracts:
- **Card Name**: From H1, title tag, or JSON-LD structured data
- **Annual Fee**: Parsed from text using regex patterns
- **Issuer**: Extracted from card name, URL, or page content
- **Network**: Visa, Mastercard, Amex, or Discover (from page content)
- **Reward Type**: Points, miles, or cashback (from page content)
- **Reward Program**: Automatically assigned based on issuer (Chase UR, Amex MR, etc.)

### 3. Earning Rules Parsing

The scraper extracts earning rules by:
- Finding reward/earning sections in the HTML
- Parsing multipliers (e.g., "3x", "5%", "2 points per dollar")
- Extracting categories (groceries, restaurants, travel, etc.)
- Detecting spending caps (e.g., "up to $1,500 per quarter")
- Identifying rotating categories

### 4. Data Normalization

All extracted data is normalized to match our internal data models:
- Categories are mapped to our standard category names
- Multipliers are converted to numeric values
- Caps are parsed with amounts and periods
- Reward types are mapped to our enum values

## Usage

The NerdWallet scraper is automatically used as the primary source in `scraper_job.py`:

```python
from scrapers.issuers.nerdwallet_scraper import NerdWalletScraper

scraper = NerdWalletScraper(use_cache=True, offline_mode=False)
cards = scraper.scrape_cards()

for card in cards:
    rules = scraper.scrape_earning_rules(card)
    # Process card and rules...
```

## Fallback

If the NerdWallet scraper is unavailable, the system falls back to individual issuer scrapers (Chase, Amex, Citi, etc.) for backward compatibility.

## Features

- **Rate Limiting**: Built-in delays to respect NerdWallet's servers
- **Caching**: Responses are cached to avoid re-scraping
- **Error Handling**: Continues processing other cards if one fails
- **Retry Logic**: Automatic retries for failed requests
- **Offline Mode**: Can work with cached data only

## Limitations

- **Parsing Accuracy**: Some data may need manual verification (annual fees, networks)
- **Earning Rules**: Complex rules may not be fully captured
- **Rate Limits**: Must respect NerdWallet's rate limits (built-in delays help)
- **Structure Changes**: If NerdWallet changes their HTML structure, parsing may break

## Future Improvements

1. **Better Parsing**: Improve regex patterns and HTML structure detection
2. **Structured Data**: Better use of JSON-LD and other structured data
3. **Validation**: Cross-reference with issuer sites for accuracy
4. **Monitoring**: Alert when parsing fails or data seems incorrect
