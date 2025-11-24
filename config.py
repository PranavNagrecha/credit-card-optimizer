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
    "groceries": [
        "grocery", "supermarket", "supermarkets", "grocery store", "grocery stores",
        "food store", "food stores", "market", "markets", "food market",
        "grocery shopping", "food shopping", "supermarket shopping"
    ],
    "gas": [
        "gas station", "gas stations", "fuel", "gasoline", "petrol", "petrol station",
        "filling station", "service station", "fuel station", "gas pump"
    ],
    "restaurants": [
        "restaurant", "dining", "dine", "food", "fast food", "fast-food", "fastfood",
        "cafe", "café", "coffee shop", "coffeehouse", "bistro", "eatery", "diner",
        "casual dining", "fine dining", "takeout", "take-out", "delivery"
    ],
    "travel": [
        "travel", "trip", "trips", "vacation", "vacations", "tourism", "tourist",
        "airline", "airlines", "flight", "flights", "airport", "hotel", "hotels",
        "lodging", "accommodation", "resort", "resorts", "cruise", "cruises",
        "car rental", "car rentals", "rental car", "train", "trains", "railway"
    ],
    "online_shopping": [
        "online", "e-commerce", "internet shopping", "online store", "online stores",
        "web shopping", "internet purchase", "online purchase", "ecommerce"
    ],
    "department_store": [
        "department store", "department stores", "retail store", "retail stores"
    ],
    "wholesale": [
        "wholesale club", "warehouse", "warehouse club", "warehouse store",
        "bulk store", "membership warehouse"
    ],
    "streaming": [
        "streaming", "streaming service", "streaming services", "netflix", "spotify",
        "hulu", "disney+", "disney plus", "apple music", "youtube premium",
        "prime video", "hbo", "hbo max", "paramount+", "paramount plus"
    ],
    "utilities": [
        "utility", "utilities", "phone", "internet", "cable", "electricity", "electric",
        "water", "gas utility", "internet service", "phone service", "cable service",
        "cell phone", "mobile phone", "wireless", "internet provider"
    ],
    "pharmacy": [
        "pharmacy", "pharmacies", "drugstore", "drug stores", "cvs", "walgreens",
        "rite aid", "prescription", "prescriptions", "medication", "medications"
    ],
    "entertainment": [
        "entertainment", "movies", "movie", "cinema", "theater", "theatre",
        "concert", "concerts", "sports", "sporting event", "sporting events",
        "amusement park", "theme park", "bowling", "golf", "sports bar"
    ],
    "shopping": [
        "shopping", "retail", "store", "stores", "merchant", "merchants",
        "purchase", "purchases", "buy", "buying"
    ],
    "transit": [
        "transit", "public transit", "public transportation", "metro", "subway",
        "bus", "buses", "uber", "lyft", "rideshare", "ride share", "taxi", "taxis"
    ],
}

