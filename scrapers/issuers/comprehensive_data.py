"""
Comprehensive card data for all major issuers.

This module contains manually curated, accurate data for all major credit cards
since most issuer websites are JavaScript-rendered and difficult to scrape reliably.
"""

from typing import Dict, List

import sys
from pathlib import Path

# Handle both package and flat structure imports
try:
    from ...models import (
        CardNetwork,
        Cap,
        RewardType,
    )
except ImportError:
    # Fallback for flat structure (Render): add root directory to path
    current_file = Path(__file__).resolve()
    # Go up 3 levels: scrapers/issuers/file.py -> root
    root_dir = current_file.parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    from models import (
        CardNetwork,
        Cap,
        RewardType,
    )

# Comprehensive card data structure
# Format: {issuer: {card_slug: {card_data}}}
COMPREHENSIVE_CARD_DATA: Dict[str, Dict] = {
    "chase": {
        "sapphire-preferred": {
            "name": "Chase Sapphire Preferred",
            "annual_fee": 95.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Travel purchased through Chase Ultimate Rewards",
                    "categories": ["travel"],
                    "merchant_names": ["Chase Ultimate Rewards", "Chase Travel Portal"],
                    "multiplier": 5.0,
                    "stacking_rules": "Must book through Chase Ultimate Rewards portal",
                },
                {
                    "description": "Dining purchases",
                    "categories": ["restaurants"],
                    "multiplier": 3.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "sapphire-reserve": {
            "name": "Chase Sapphire Reserve",
            "annual_fee": 550.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Travel and dining purchases",
                    "categories": ["travel", "restaurants"],
                    "multiplier": 3.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "freedom-flex": {
            "name": "Chase Freedom Flex",
            "annual_fee": 0.0,
            "network": CardNetwork.MASTERCARD,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.03,
            "earning_rules": [
                {
                    "description": "Rotating quarterly categories",
                    "categories": ["groceries", "gas", "wholesale"],
                    "multiplier": 5.0,
                    "caps": [{"amount": 1500.0, "period": "quarter"}],
                    "is_rotating": True,
                },
                {
                    "description": "Dining purchases",
                    "categories": ["restaurants"],
                    "multiplier": 3.0,
                },
                {
                    "description": "Drugstore purchases",
                    "categories": ["pharmacy"],
                    "multiplier": 3.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "freedom-unlimited": {
            "name": "Chase Freedom Unlimited",
            "annual_fee": 0.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.03,
            "earning_rules": [
                {
                    "description": "Dining purchases",
                    "categories": ["restaurants"],
                    "multiplier": 3.0,
                },
                {
                    "description": "Drugstore purchases",
                    "categories": ["pharmacy"],
                    "multiplier": 3.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.5,
                },
            ],
        },
    },
    "amex": {
        "gold-card": {
            "name": "American Express Gold Card",
            "annual_fee": 250.0,
            "network": CardNetwork.AMEX,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Dining at restaurants worldwide",
                    "categories": ["restaurants"],
                    "multiplier": 4.0,
                },
                {
                    "description": "U.S. supermarkets",
                    "categories": ["groceries"],
                    "multiplier": 4.0,
                    "caps": [{"amount": 25000.0, "period": "year"}],
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "platinum-card": {
            "name": "American Express Platinum Card",
            "annual_fee": 695.0,
            "network": CardNetwork.AMEX,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Flights booked directly with airlines",
                    "categories": ["travel", "airline"],
                    "multiplier": 5.0,
                },
                {
                    "description": "Flights booked through AmexTravel.com",
                    "categories": ["travel", "airline"],
                    "merchant_names": ["AmexTravel.com", "American Express Travel"],
                    "multiplier": 5.0,
                    "stacking_rules": "Must book through AmexTravel.com portal",
                },
                {
                    "description": "Prepaid hotels booked through AmexTravel.com",
                    "categories": ["travel", "hotel"],
                    "merchant_names": ["AmexTravel.com", "American Express Travel"],
                    "multiplier": 5.0,
                    "stacking_rules": "Must book through AmexTravel.com portal",
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "blue-cash-everyday": {
            "name": "Blue Cash Everyday",
            "annual_fee": 0.0,
            "network": CardNetwork.AMEX,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.027,
            "earning_rules": [
                {
                    "description": "U.S. supermarkets",
                    "categories": ["groceries"],
                    "multiplier": 3.0,
                    "caps": [{"amount": 6000.0, "period": "year"}],
                },
                {
                    "description": "U.S. gas stations",
                    "categories": ["gas"],
                    "multiplier": 3.0,
                },
                {
                    "description": "Online retail purchases",
                    "categories": ["online_shopping"],
                    "multiplier": 3.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "blue-cash-preferred": {
            "name": "Blue Cash Preferred",
            "annual_fee": 0.0,  # First year, then $95
            "network": CardNetwork.AMEX,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.027,
            "earning_rules": [
                {
                    "description": "U.S. supermarkets",
                    "categories": ["groceries"],
                    "multiplier": 6.0,
                    "caps": [{"amount": 6000.0, "period": "year"}],
                },
                {
                    "description": "Streaming services",
                    "categories": ["streaming"],
                    "multiplier": 6.0,
                },
                {
                    "description": "U.S. gas stations and transit",
                    "categories": ["gas", "transit"],
                    "multiplier": 3.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
    },
    "citi": {
        "premier-card": {
            "name": "Citi Premier Card",
            "annual_fee": 95.0,
            "network": CardNetwork.MASTERCARD,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Restaurants",
                    "categories": ["restaurants"],
                    "multiplier": 3.0,
                },
                {
                    "description": "Supermarkets",
                    "categories": ["groceries"],
                    "multiplier": 3.0,
                },
                {
                    "description": "Gas stations",
                    "categories": ["gas"],
                    "multiplier": 3.0,
                },
                {
                    "description": "Hotels and air travel",
                    "categories": ["travel"],
                    "multiplier": 3.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "double-cash": {
            "name": "Citi Double Cash",
            "annual_fee": 0.0,
            "network": CardNetwork.MASTERCARD,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.03,
            "earning_rules": [
                {
                    "description": "All purchases",
                    "categories": [],
                    "multiplier": 2.0,
                },
            ],
        },
        "custom-cash": {
            "name": "Citi Custom Cash",
            "annual_fee": 0.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.03,
            "earning_rules": [
                {
                    "description": "Top spending category each billing cycle",
                    "categories": ["groceries", "gas", "restaurants", "travel", "pharmacy"],
                    "multiplier": 5.0,
                    "caps": [{"amount": 500.0, "period": "month"}],
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
    },
    "capital_one": {
        "venture-x": {
            "name": "Capital One Venture X",
            "annual_fee": 395.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.MILES_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Hotels and rental cars booked through Capital One Travel",
                    "categories": ["travel"],
                    "merchant_names": ["Capital One Travel", "Capital One"],
                    "multiplier": 10.0,
                    "stacking_rules": "Must book through Capital One Travel portal",
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 2.0,
                },
            ],
        },
        "venture": {
            "name": "Capital One Venture",
            "annual_fee": 95.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.MILES_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "All purchases",
                    "categories": [],
                    "multiplier": 2.0,
                },
            ],
        },
        "savorone": {
            "name": "Capital One SavorOne",
            "annual_fee": 0.0,
            "network": CardNetwork.MASTERCARD,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Dining, entertainment, and streaming services",
                    "categories": ["restaurants", "entertainment", "streaming"],
                    "multiplier": 3.0,
                },
                {
                    "description": "Groceries (not including Walmart and Target)",
                    "categories": ["groceries"],
                    "multiplier": 3.0,
                },
                {
                    "description": "Hotels, vacation rentals and rental cars booked through Capital One Travel",
                    "categories": ["travel"],
                    "merchant_names": ["Capital One Travel"],
                    "multiplier": 5.0,
                    "stacking_rules": "Must book through Capital One Travel portal",
                },
                {
                    "description": "Capital One Entertainment purchases",
                    "merchant_names": ["Capital One Entertainment"],
                    "multiplier": 8.0,
                    "stacking_rules": "Only applies to purchases through Capital One Entertainment portal",
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "quicksilver": {
            "name": "Capital One Quicksilver",
            "annual_fee": 0.0,
            "network": CardNetwork.MASTERCARD,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "All purchases",
                    "categories": [],
                    "multiplier": 1.5,
                },
            ],
        },
    },
    "discover": {
        "it-cash-back": {
            "name": "Discover it Cash Back",
            "annual_fee": 0.0,
            "network": CardNetwork.DISCOVER,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Rotating quarterly categories",
                    "categories": ["groceries", "gas", "wholesale", "restaurants", "amazon", "target"],
                    "multiplier": 5.0,
                    "caps": [{"amount": 1500.0, "period": "quarter"}],
                    "is_rotating": True,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "it-miles": {
            "name": "Discover it Miles",
            "annual_fee": 0.0,
            "network": CardNetwork.DISCOVER,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "All purchases",
                    "categories": [],
                    "multiplier": 1.5,
                },
            ],
        },
    },
    "us_bank": {
        "altitude-reserve": {
            "name": "U.S. Bank Altitude Reserve Visa Infinite",
            "annual_fee": 400.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Mobile wallet purchases",
                    "categories": [],
                    "multiplier": 3.0,
                    "stacking_rules": "Must use mobile wallet (Apple Pay, Google Pay, Samsung Pay)",
                },
                {
                    "description": "Travel purchases",
                    "categories": ["travel"],
                    "multiplier": 3.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "cash-plus": {
            "name": "U.S. Bank Cash+ Visa",
            "annual_fee": 0.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.03,
            "earning_rules": [
                {
                    "description": "Two 5% categories of choice",
                    "categories": ["groceries", "gas", "restaurants", "department_store", "furniture", "gym", "movie_theater"],
                    "multiplier": 5.0,
                    "caps": [{"amount": 2000.0, "period": "quarter"}],
                },
                {
                    "description": "One 2% category of choice",
                    "categories": ["groceries", "gas", "restaurants"],
                    "multiplier": 2.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
    },
    "wells_fargo": {
        "active-cash": {
            "name": "Wells Fargo Active Cash",
            "annual_fee": 0.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.03,
            "earning_rules": [
                {
                    "description": "All purchases",
                    "categories": [],
                    "multiplier": 2.0,
                },
            ],
        },
        "autograph": {
            "name": "Wells Fargo Autograph",
            "annual_fee": 0.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Restaurants, travel, gas stations, transit, streaming, and phone plans",
                    "categories": ["restaurants", "travel", "gas", "transit", "streaming"],
                    "multiplier": 3.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
    },
    "barclays": {
        "avios": {
            "name": "Barclays AAdvantage Aviator Red World Elite Mastercard",
            "annual_fee": 99.0,
            "network": CardNetwork.MASTERCARD,
            "reward_type": RewardType.MILES_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "American Airlines purchases",
                    "categories": ["travel", "airline"],
                    "merchant_names": ["American Airlines", "aa.com"],
                    "multiplier": 2.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
    },
    "co_branded": {
        "amazon-prime-visa": {
            "name": "Amazon Prime Rewards Visa Signature",
            "annual_fee": 0.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.03,
            "earning_rules": [
                {
                    "description": "Amazon.com and Whole Foods Market",
                    "categories": ["online_shopping", "groceries"],
                    "merchant_names": ["Amazon", "Whole Foods", "Whole Foods Market"],
                    "multiplier": 5.0,
                },
                {
                    "description": "Restaurants, gas stations, and drugstores",
                    "categories": ["restaurants", "gas", "pharmacy"],
                    "multiplier": 2.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "amazon-visa": {
            "name": "Amazon Rewards Visa Signature",
            "annual_fee": 0.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.03,
            "earning_rules": [
                {
                    "description": "Amazon.com purchases",
                    "categories": ["online_shopping"],
                    "merchant_names": ["Amazon"],
                    "multiplier": 3.0,
                },
                {
                    "description": "Restaurants, gas stations, and drugstores",
                    "categories": ["restaurants", "gas", "pharmacy"],
                    "multiplier": 2.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "costco-anywhere": {
            "name": "Costco Anywhere Visa",
            "annual_fee": 0.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Costco and Costco.com",
                    "categories": ["wholesale", "groceries"],
                    "merchant_names": ["Costco"],
                    "multiplier": 2.0,
                },
                {
                    "description": "Restaurants and eligible travel",
                    "categories": ["restaurants", "travel"],
                    "multiplier": 3.0,
                },
                {
                    "description": "Gas stations (first $7,000 per year, then 1%)",
                    "categories": ["gas"],
                    "multiplier": 4.0,
                    "caps": [{"amount": 7000.0, "period": "year"}],
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "target-redcard": {
            "name": "Target RedCard",
            "annual_fee": 0.0,
            "network": CardNetwork.MASTERCARD,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.03,
            "earning_rules": [
                {
                    "description": "Target and Target.com purchases",
                    "categories": ["general_merchandise", "groceries"],
                    "merchant_names": ["Target"],
                    "multiplier": 5.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
    },
    "apple": {
        "apple-card": {
            "name": "Apple Card",
            "annual_fee": 0.0,
            "network": CardNetwork.MASTERCARD,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Apple purchases (Apple Store, apple.com, App Store, iTunes, Apple Music, iCloud)",
                    "categories": ["electronics", "shopping"],
                    "merchant_names": ["Apple", "Apple Store", "apple.com", "App Store", "iTunes", "Apple Music", "iCloud"],
                    "multiplier": 3.0,
                },
                {
                    "description": "Purchases made with Apple Pay",
                    "categories": [],
                    "multiplier": 2.0,
                    "stacking_rules": "Must use Apple Pay",
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
    },
    "airline_cards": {
        "united-explorer": {
            "name": "United Explorer Card",
            "annual_fee": 95.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.MILES_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "United purchases",
                    "categories": ["travel", "airline"],
                    "merchant_names": ["United Airlines", "united.com"],
                    "multiplier": 2.0,
                },
                {
                    "description": "Restaurants and hotel purchases",
                    "categories": ["restaurants", "travel", "hotel"],
                    "multiplier": 2.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "united-club-infinite": {
            "name": "United Club Infinite Card",
            "annual_fee": 525.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.MILES_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "United purchases",
                    "categories": ["travel", "airline"],
                    "merchant_names": ["United Airlines", "united.com"],
                    "multiplier": 4.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 2.0,
                },
            ],
        },
        "delta-gold": {
            "name": "Delta SkyMiles Gold American Express Card",
            "annual_fee": 99.0,
            "network": CardNetwork.AMEX,
            "reward_type": RewardType.MILES_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Delta purchases",
                    "categories": ["travel", "airline"],
                    "merchant_names": ["Delta", "delta.com", "Delta Air Lines"],
                    "multiplier": 2.0,
                },
                {
                    "description": "Restaurants and U.S. supermarkets",
                    "categories": ["restaurants", "groceries"],
                    "multiplier": 2.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "delta-platinum": {
            "name": "Delta SkyMiles Platinum American Express Card",
            "annual_fee": 250.0,
            "network": CardNetwork.AMEX,
            "reward_type": RewardType.MILES_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Delta purchases",
                    "categories": ["travel", "airline"],
                    "merchant_names": ["Delta", "delta.com", "Delta Air Lines"],
                    "multiplier": 3.0,
                },
                {
                    "description": "Restaurants and U.S. supermarkets",
                    "categories": ["restaurants", "groceries"],
                    "multiplier": 2.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "delta-reserve": {
            "name": "Delta SkyMiles Reserve American Express Card",
            "annual_fee": 550.0,
            "network": CardNetwork.AMEX,
            "reward_type": RewardType.MILES_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Delta purchases",
                    "categories": ["travel", "airline"],
                    "merchant_names": ["Delta", "delta.com", "Delta Air Lines"],
                    "multiplier": 3.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "southwest-plus": {
            "name": "Southwest Rapid Rewards Plus Credit Card",
            "annual_fee": 69.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.MILES_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Southwest purchases",
                    "categories": ["travel", "airline"],
                    "merchant_names": ["Southwest", "southwest.com", "Southwest Airlines"],
                    "multiplier": 2.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "southwest-priority": {
            "name": "Southwest Rapid Rewards Priority Credit Card",
            "annual_fee": 149.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.MILES_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Southwest purchases",
                    "categories": ["travel", "airline"],
                    "merchant_names": ["Southwest", "southwest.com", "Southwest Airlines"],
                    "multiplier": 2.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "american-airlines-platinum": {
            "name": "Citi AAdvantage Platinum Select World Elite Mastercard",
            "annual_fee": 99.0,
            "network": CardNetwork.MASTERCARD,
            "reward_type": RewardType.MILES_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "American Airlines purchases",
                    "categories": ["travel", "airline"],
                    "merchant_names": ["American Airlines", "aa.com"],
                    "multiplier": 2.0,
                },
                {
                    "description": "Restaurants and gas stations",
                    "categories": ["restaurants", "gas"],
                    "multiplier": 2.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
    },
    "premium_cards": {
        "chase-ink-business-unlimited": {
            "name": "Chase Ink Business Unlimited",
            "annual_fee": 0.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "All purchases",
                    "categories": [],
                    "multiplier": 1.5,
                },
            ],
        },
        "chase-ink-business-cash": {
            "name": "Chase Ink Business Cash",
            "annual_fee": 0.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Office supply stores, internet, cable, and phone services",
                    "categories": ["utilities", "shopping"],
                    "multiplier": 5.0,
                    "caps": [{"amount": 25000.0, "period": "year"}],
                },
                {
                    "description": "Gas stations and restaurants",
                    "categories": ["gas", "restaurants"],
                    "multiplier": 2.0,
                    "caps": [{"amount": 25000.0, "period": "year"}],
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "amex-business-gold": {
            "name": "American Express Business Gold Card",
            "annual_fee": 295.0,
            "network": CardNetwork.AMEX,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Top 2 spending categories each month (from airfare, advertising, gas stations, restaurants, shipping)",
                    "categories": ["travel", "gas", "restaurants"],
                    "multiplier": 4.0,
                    "caps": [{"amount": 150000.0, "period": "year"}],
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
        "citi-prestige": {
            "name": "Citi Prestige Card",
            "annual_fee": 495.0,
            "network": CardNetwork.MASTERCARD,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Restaurants and entertainment",
                    "categories": ["restaurants", "entertainment"],
                    "multiplier": 5.0,
                },
                {
                    "description": "Air travel and hotels",
                    "categories": ["travel", "airline", "hotel"],
                    "multiplier": 3.0,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                },
            ],
        },
    },
}


