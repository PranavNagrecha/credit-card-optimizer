"""
Knowledge base for credit cards with rotating quarterly categories.

This module contains comprehensive information about cards that offer rotating
quarterly bonus categories, which require activation each quarter.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class RotatingCategoryCard:
    """Information about a card with rotating quarterly categories."""
    card_name: str
    issuer: str
    multiplier: float
    cap_amount: Optional[float] = None
    cap_period: str = "quarter"
    possible_categories: List[str] = None
    activation_required: bool = True
    activation_method: Optional[str] = None
    notes: Optional[str] = None

# Comprehensive list of cards with rotating quarterly categories
ROTATING_CATEGORY_CARDS: Dict[str, RotatingCategoryCard] = {
    # Discover Cards
    "discover_it_cash_back": RotatingCategoryCard(
        card_name="Discover it Cash Back",
        issuer="Discover",
        multiplier=5.0,
        cap_amount=1500.0,
        cap_period="quarter",
        possible_categories=[
            "groceries", "gas", "wholesale", "restaurants", "amazon", "target",
            "streaming", "home_improvement", "pharmacy", "gym", "fitness",
            "paypal", "walmart", "target", "amazon"
        ],
        activation_required=True,
        activation_method="Online or mobile app activation required each quarter",
        notes="5% cashback on rotating categories, 1% on everything else. First year cashback match."
    ),
    
    "discover_it_chrome": RotatingCategoryCard(
        card_name="Discover it Chrome",
        issuer="Discover",
        multiplier=2.0,
        cap_amount=1000.0,
        cap_period="quarter",
        possible_categories=["gas", "restaurants"],
        activation_required=True,
        notes="2% cashback on rotating gas/restaurant categories"
    ),
    
    # Chase Cards
    "chase_freedom_flex": RotatingCategoryCard(
        card_name="Chase Freedom Flex",
        issuer="Chase",
        multiplier=5.0,
        cap_amount=1500.0,
        cap_period="quarter",
        possible_categories=[
            "groceries", "gas", "wholesale", "restaurants", "streaming",
            "home_improvement", "pharmacy", "gym", "fitness", "amazon",
            "target", "walmart", "paypal", "internet", "cable", "phone"
        ],
        activation_required=True,
        activation_method="Activate online or via Chase mobile app each quarter",
        notes="5x Ultimate Rewards points on rotating categories. Also has fixed 3x on dining and drugstores."
    ),
    
    "chase_freedom": RotatingCategoryCard(
        card_name="Chase Freedom",
        issuer="Chase",
        multiplier=5.0,
        cap_amount=1500.0,
        cap_period="quarter",
        possible_categories=[
            "groceries", "gas", "wholesale", "restaurants", "streaming",
            "home_improvement", "pharmacy", "gym", "fitness", "amazon",
            "target", "walmart", "paypal", "internet", "cable", "phone"
        ],
        activation_required=True,
        notes="5x Ultimate Rewards points on rotating categories (legacy card, may be discontinued)"
    ),
    
    # Bank of America Cards
    "bank_of_america_cash_rewards": RotatingCategoryCard(
        card_name="Bank of America Cash Rewards",
        issuer="Bank of America",
        multiplier=3.0,
        cap_amount=2500.0,
        cap_period="quarter",
        possible_categories=[
            "gas", "online_shopping", "drugstores", "home_improvement",
            "furniture", "dining", "travel"
        ],
        activation_required=True,
        activation_method="Select category online or via mobile app each quarter",
        notes="3% cashback on one selected category per quarter from list of options"
    ),
    
    "bank_of_america_customized_cash": RotatingCategoryCard(
        card_name="Bank of America Customized Cash Rewards",
        issuer="Bank of America",
        multiplier=3.0,
        cap_amount=2500.0,
        cap_period="quarter",
        possible_categories=[
            "gas", "online_shopping", "drugstores", "home_improvement",
            "furniture", "dining", "travel"
        ],
        activation_required=True,
        notes="3% cashback on one selected category per quarter"
    ),
    
    # Citi Cards
    "citi_dividend": RotatingCategoryCard(
        card_name="Citi Dividend",
        issuer="Citi",
        multiplier=5.0,
        cap_amount=6000.0,
        cap_period="year",
        possible_categories=[
            "groceries", "gas", "restaurants", "amazon", "target", "walmart"
        ],
        activation_required=True,
        notes="5% cashback on rotating categories (annual cap, not quarterly)"
    ),
    
    # US Bank Cards
    "us_bank_cash_plus": RotatingCategoryCard(
        card_name="U.S. Bank Cash+ Visa Signature",
        issuer="U.S. Bank",
        multiplier=5.0,
        cap_amount=2000.0,
        cap_period="quarter",
        possible_categories=[
            "electronics", "furniture", "gym", "fitness", "cell_phone",
            "bookstores", "sporting_goods", "movie_theaters", "fast_food",
            "department_stores", "clothing_stores", "utilities", "internet",
            "cable", "phone", "streaming", "ground_transportation"
        ],
        activation_required=True,
        activation_method="Select two 5% categories and one 2% category each quarter",
        notes="5% cashback on two selected categories, 2% on one selected category per quarter"
    ),
    
    # Capital One Cards (some have rotating categories)
    "capital_one_savorone": RotatingCategoryCard(
        card_name="Capital One SavorOne Cash Rewards",
        issuer="Capital One",
        multiplier=5.0,
        cap_amount=None,
        cap_period="quarter",
        possible_categories=["entertainment"],
        activation_required=False,
        notes="5% cashback on entertainment (not rotating, but included for reference)"
    ),
}

# Keywords that indicate rotating categories in card descriptions
ROTATING_CATEGORY_KEYWORDS = [
    "rotating",
    "quarterly",
    "each quarter",
    "per quarter",
    "changes quarterly",
    "changes each quarter",
    "different categories",
    "different places",
    "select categories",
    "bonus categories",
    "activate",
    "activation required",
    "enrollment required",
    "choose your category",
    "pick your category",
    "select your category",
    "category selection",
    "rotating bonus",
    "quarterly bonus",
]

# Phrases that indicate fixed (non-rotating) categories
FIXED_CATEGORY_PHRASES = [
    "always earn",
    "every purchase",
    "all purchases",
    "permanent",
    "ongoing",
    "year-round",
    "no activation",
    "automatic",
]

def is_rotating_category_card(card_name: str, issuer: str) -> bool:
    """Check if a card is known to have rotating categories."""
    card_key = f"{issuer.lower()}_{card_name.lower().replace(' ', '_').replace('-', '_')}"
    
    # Try exact match
    for key, card_info in ROTATING_CATEGORY_CARDS.items():
        if card_key in key or key in card_key:
            return True
        if card_info.card_name.lower() == card_name.lower() and card_info.issuer.lower() == issuer.lower():
            return True
    
    return False

def get_rotating_category_info(card_name: str, issuer: str) -> Optional[RotatingCategoryCard]:
    """Get detailed information about a rotating category card."""
    card_key = f"{issuer.lower()}_{card_name.lower().replace(' ', '_').replace('-', '_')}"
    
    # Try exact match
    for key, card_info in ROTATING_CATEGORY_CARDS.items():
        if card_key in key or key in card_key:
            return card_info
        if card_info.card_name.lower() == card_name.lower() and card_info.issuer.lower() == issuer.lower():
            return card_info
    
    return None

def detect_rotating_category_from_text(text: str) -> bool:
    """Detect if text describes a rotating category based on keywords."""
    text_lower = text.lower()
    
    # Check for fixed category phrases first (these override rotating)
    if any(phrase in text_lower for phrase in FIXED_CATEGORY_PHRASES):
        return False
    
    # Check for rotating category keywords
    return any(keyword in text_lower for keyword in ROTATING_CATEGORY_KEYWORDS)

def get_all_rotating_category_cards() -> List[RotatingCategoryCard]:
    """Get a list of all known rotating category cards."""
    return list(ROTATING_CATEGORY_CARDS.values())

