"""
Configuration constants for the credit card optimization system.

Contains point valuations, timeouts, user-agent strings, and other
configurable parameters.
"""

import os

# Point/mile valuation assumptions (in cents per point/mile)
POINT_VALUES = {
    "CHASE_UR": 0.017,  # Chase Ultimate Rewards
    "AMEX_MR": 0.017,  # American Express Membership Rewards
    "CITI_TY": 0.015,  # Citi ThankYou Points
    "CAPITAL_ONE_MILES": 0.016,  # Capital One Miles
    "DISCOVER_CASHBACK": 0.01,  # Discover Cashback (1:1)
    "BOA_POINTS": 0.01,  # Bank of America Rewards
    "USBANK_POINTS": 0.012,  # U.S. Bank Points
    "WELLS_FARGO_POINTS": 0.01,  # Wells Fargo Rewards
    "BARCLAYS_POINTS": 0.01,  # Barclays Rewards
    "AMERICAN_AIRLINES_MILES": 0.014,  # American Airlines AAdvantage Miles
    "DEFAULT": 0.01,  # Default: 1 point = 1 cent
}

# HTTP request settings
REQUEST_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
RATE_LIMIT_DELAY = 1.0  # Seconds to wait between requests

# Recommendation settings
MAX_RECOMMENDATIONS = 5
DEFAULT_ANNUAL_FEE_WEIGHT = 0.0  # Set to > 0 to penalize annual fees in scoring

# Caching settings
USE_CACHE = True
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "false").lower() == "true"
CACHE_DIR = ".cache/scrapers"

# Category normalization patterns
CATEGORY_SYNONYMS = {
    "groceries": ["grocery", "supermarket", "supermarkets", "grocery store", "grocery stores"],
    "gas": ["gas station", "gas stations", "fuel", "gasoline"],
    "restaurants": ["restaurant", "dining", "dine", "food", "fast food"],
    "travel": ["travel", "trip", "trips"],
    "online_shopping": ["online", "e-commerce", "internet shopping"],
    "department_store": ["department store", "department stores"],
    "wholesale": ["wholesale club", "warehouse"],
}

