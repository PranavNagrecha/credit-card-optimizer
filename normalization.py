"""
Category normalization and merchant mapping logic.

Converts user queries and merchant names into normalized categories
and MCC codes for matching against earning rules.
"""

import re
from typing import List, Optional

from config import CATEGORY_SYNONYMS
from models import MerchantCategoryMapping


# Known merchant mappings - expanded to 100+ common merchants
KNOWN_MERCHANTS: dict[str, MerchantCategoryMapping] = {
    # Grocery Stores
    "walmart": MerchantCategoryMapping(
        merchant_name="Walmart",
        mcc="5331",
        normalized_categories=["general_merchandise", "groceries"],
        aliases=["walmart supercenter", "walmart.com", "walmart store", "walmart neighborhood market"]
    ),
    "target": MerchantCategoryMapping(
        merchant_name="Target",
        mcc="5331",
        normalized_categories=["general_merchandise", "groceries"],
        aliases=["target.com", "target store"]
    ),
    "kroger": MerchantCategoryMapping(
        merchant_name="Kroger",
        mcc="5411",
        normalized_categories=["groceries"],
        aliases=["kroger grocery", "kroger.com", "kroger store", "ralphs", "fred meyer", "food 4 less", "king soopers"]
    ),
    "whole foods": MerchantCategoryMapping(
        merchant_name="Whole Foods",
        mcc="5411",
        normalized_categories=["groceries"],
        aliases=["whole foods market", "wholefoods", "whole foods"]
    ),
    "safeway": MerchantCategoryMapping(
        merchant_name="Safeway",
        mcc="5411",
        normalized_categories=["groceries"],
        aliases=["safeway.com", "safeway store", "vons", "pavilions", "tom thumb"]
    ),
    "publix": MerchantCategoryMapping(
        merchant_name="Publix",
        mcc="5411",
        normalized_categories=["groceries"],
        aliases=["publix.com", "publix supermarket"]
    ),
    "wegmans": MerchantCategoryMapping(
        merchant_name="Wegmans",
        mcc="5411",
        normalized_categories=["groceries"],
        aliases=["wegmans.com", "wegmans food market"]
    ),
    "h-e-b": MerchantCategoryMapping(
        merchant_name="H-E-B",
        mcc="5411",
        normalized_categories=["groceries"],
        aliases=["heb", "h.e.b", "heb.com"]
    ),
    "albertsons": MerchantCategoryMapping(
        merchant_name="Albertsons",
        mcc="5411",
        normalized_categories=["groceries"],
        aliases=["albertsons.com", "acme", "jewel osco", "shaws", "star market"]
    ),
    "stop & shop": MerchantCategoryMapping(
        merchant_name="Stop & Shop",
        mcc="5411",
        normalized_categories=["groceries"],
        aliases=["stop and shop", "stopandshop", "stopandshop.com"]
    ),
    "giant": MerchantCategoryMapping(
        merchant_name="Giant",
        mcc="5411",
        normalized_categories=["groceries"],
        aliases=["giant food", "giant.com", "giant eagle", "giant martin"]
    ),
    "food lion": MerchantCategoryMapping(
        merchant_name="Food Lion",
        mcc="5411",
        normalized_categories=["groceries"],
        aliases=["foodlion.com", "food lion store"]
    ),
    "meijer": MerchantCategoryMapping(
        merchant_name="Meijer",
        mcc="5411",
        normalized_categories=["groceries", "general_merchandise"],
        aliases=["meijer.com", "meijer store"]
    ),
    "costco": MerchantCategoryMapping(
        merchant_name="Costco",
        mcc="5300",
        normalized_categories=["wholesale", "groceries"],
        aliases=["costco wholesale", "costco.com"]
    ),
    "sam's club": MerchantCategoryMapping(
        merchant_name="Sam's Club",
        mcc="5300",
        normalized_categories=["wholesale", "groceries"],
        aliases=["sams club", "samsclub", "samsclub.com"]
    ),
    "bj's": MerchantCategoryMapping(
        merchant_name="BJ's",
        mcc="5300",
        normalized_categories=["wholesale", "groceries"],
        aliases=["bjs", "bjs wholesale", "bjs.com"]
    ),
    
    # Retailers
    "amazon": MerchantCategoryMapping(
        merchant_name="Amazon",
        mcc="5999",
        normalized_categories=["online_shopping", "general_merchandise"],
        aliases=["amazon.com", "amzn", "amazon prime"]
    ),
    "macy's": MerchantCategoryMapping(
        merchant_name="Macy's",
        mcc="5311",
        normalized_categories=["department_store"],
        aliases=["macys", "macy", "macy's", "macys.com"]
    ),
    "best buy": MerchantCategoryMapping(
        merchant_name="Best Buy",
        mcc="5732",
        normalized_categories=["electronics", "shopping"],
        aliases=["bestbuy", "bestbuy.com", "best buy store"]
    ),
    "home depot": MerchantCategoryMapping(
        merchant_name="Home Depot",
        mcc="5200",
        normalized_categories=["home_improvement", "shopping"],
        aliases=["homedepot", "homedepot.com", "the home depot"]
    ),
    "lowe's": MerchantCategoryMapping(
        merchant_name="Lowe's",
        mcc="5200",
        normalized_categories=["home_improvement", "shopping"],
        aliases=["lowes", "lowes.com", "lowes store"]
    ),
    "nordstrom": MerchantCategoryMapping(
        merchant_name="Nordstrom",
        mcc="5311",
        normalized_categories=["department_store"],
        aliases=["nordstrom.com", "nordstrom rack"]
    ),
    "tj maxx": MerchantCategoryMapping(
        merchant_name="TJ Maxx",
        mcc="5311",
        normalized_categories=["department_store"],
        aliases=["tjmaxx", "tj maxx", "tjmaxx.com", "marshalls", "homegoods"]
    ),
    
    # Gas Stations
    "shell": MerchantCategoryMapping(
        merchant_name="Shell",
        mcc="5541",
        normalized_categories=["gas"],
        aliases=["shell gas", "shell station", "shell.com"]
    ),
    "chevron": MerchantCategoryMapping(
        merchant_name="Chevron",
        mcc="5541",
        normalized_categories=["gas"],
        aliases=["chevron gas", "chevron station", "chevron.com"]
    ),
    "bp": MerchantCategoryMapping(
        merchant_name="BP",
        mcc="5541",
        normalized_categories=["gas"],
        aliases=["bp gas", "bp station", "british petroleum", "bp.com"]
    ),
    "exxon": MerchantCategoryMapping(
        merchant_name="Exxon",
        mcc="5541",
        normalized_categories=["gas"],
        aliases=["exxon mobil", "exxonmobil", "exxon station", "exxon.com"]
    ),
    "mobil": MerchantCategoryMapping(
        merchant_name="Mobil",
        mcc="5541",
        normalized_categories=["gas"],
        aliases=["mobil gas", "mobil station", "mobil.com"]
    ),
    "speedway": MerchantCategoryMapping(
        merchant_name="Speedway",
        mcc="5541",
        normalized_categories=["gas"],
        aliases=["speedway gas", "speedway station"]
    ),
    "7-eleven": MerchantCategoryMapping(
        merchant_name="7-Eleven",
        mcc="5541",
        normalized_categories=["gas", "convenience"],
        aliases=["7eleven", "7-11", "seven eleven"]
    ),
    
    # Restaurants
    "mcdonald's": MerchantCategoryMapping(
        merchant_name="McDonald's",
        mcc="5814",
        normalized_categories=["restaurants", "fast food"],
        aliases=["mcdonalds", "mcd", "mcdonald", "mcdonalds.com"]
    ),
    "starbucks": MerchantCategoryMapping(
        merchant_name="Starbucks",
        mcc="5814",
        normalized_categories=["restaurants", "cafe"],
        aliases=["starbucks.com", "starbucks coffee"]
    ),
    "chipotle": MerchantCategoryMapping(
        merchant_name="Chipotle",
        mcc="5814",
        normalized_categories=["restaurants", "fast food"],
        aliases=["chipotle.com", "chipotle mexican grill"]
    ),
    "subway": MerchantCategoryMapping(
        merchant_name="Subway",
        mcc="5814",
        normalized_categories=["restaurants", "fast food"],
        aliases=["subway.com", "subway restaurant"]
    ),
    "pizza hut": MerchantCategoryMapping(
        merchant_name="Pizza Hut",
        mcc="5812",
        normalized_categories=["restaurants", "fast food"],
        aliases=["pizzahut", "pizza hut", "pizzahut.com"]
    ),
    "domino's": MerchantCategoryMapping(
        merchant_name="Domino's",
        mcc="5812",
        normalized_categories=["restaurants", "fast food"],
        aliases=["dominos", "domino's pizza", "dominos.com"]
    ),
    
    # Airlines
    "delta": MerchantCategoryMapping(
        merchant_name="Delta Airlines",
        mcc="4511",
        normalized_categories=["travel", "airline"],
        aliases=["delta air lines", "delta.com", "delta air"]
    ),
    "united": MerchantCategoryMapping(
        merchant_name="United Airlines",
        mcc="4511",
        normalized_categories=["travel", "airline"],
        aliases=["united airlines", "united.com", "united air"]
    ),
    "american airlines": MerchantCategoryMapping(
        merchant_name="American Airlines",
        mcc="4511",
        normalized_categories=["travel", "airline"],
        aliases=["aa.com", "american", "american air", "americanairlines"]
    ),
    "southwest": MerchantCategoryMapping(
        merchant_name="Southwest Airlines",
        mcc="4511",
        normalized_categories=["travel", "airline"],
        aliases=["southwest.com", "southwest air", "southwest airlines"]
    ),
    "jetblue": MerchantCategoryMapping(
        merchant_name="JetBlue",
        mcc="4511",
        normalized_categories=["travel", "airline"],
        aliases=["jetblue.com", "jet blue", "jetblue airways"]
    ),
    "alaska airlines": MerchantCategoryMapping(
        merchant_name="Alaska Airlines",
        mcc="4511",
        normalized_categories=["travel", "airline"],
        aliases=["alaskaair.com", "alaska air", "alaskaairlines"]
    ),
    
    # Transit/Rideshare
    "uber": MerchantCategoryMapping(
        merchant_name="Uber",
        mcc="4121",
        normalized_categories=["transit", "travel"],
        aliases=["uber.com", "uber ride", "uber eats"]
    ),
    "lyft": MerchantCategoryMapping(
        merchant_name="Lyft",
        mcc="4121",
        normalized_categories=["transit", "travel"],
        aliases=["lyft.com", "lyft ride"]
    ),
    
    # Streaming
    "netflix": MerchantCategoryMapping(
        merchant_name="Netflix",
        mcc="4899",
        normalized_categories=["streaming", "entertainment"],
        aliases=["netflix.com"]
    ),
    "spotify": MerchantCategoryMapping(
        merchant_name="Spotify",
        mcc="4899",
        normalized_categories=["streaming", "entertainment"],
        aliases=["spotify.com"]
    ),
    "hulu": MerchantCategoryMapping(
        merchant_name="Hulu",
        mcc="4899",
        normalized_categories=["streaming", "entertainment"],
        aliases=["hulu.com"]
    ),
    "disney+": MerchantCategoryMapping(
        merchant_name="Disney+",
        mcc="4899",
        normalized_categories=["streaming", "entertainment"],
        aliases=["disney plus", "disneyplus", "disneyplus.com"]
    ),
    
    # Pharmacy
    "cvs": MerchantCategoryMapping(
        merchant_name="CVS",
        mcc="5912",
        normalized_categories=["pharmacy", "groceries"],
        aliases=["cvs pharmacy", "cvs.com", "cvs store"]
    ),
    "walgreens": MerchantCategoryMapping(
        merchant_name="Walgreens",
        mcc="5912",
        normalized_categories=["pharmacy", "groceries"],
        aliases=["walgreens pharmacy", "walgreens.com", "walgreens store"]
    ),
    "rite aid": MerchantCategoryMapping(
        merchant_name="Rite Aid",
        mcc="5912",
        normalized_categories=["pharmacy", "groceries"],
        aliases=["riteaid", "rite aid pharmacy", "riteaid.com"]
    ),
}

# MCC to category mappings - expanded
MCC_TO_CATEGORY: dict[str, List[str]] = {
    # Groceries
    "5411": ["groceries"],
    "5422": ["groceries"],  # Freezer and locker meat provisioners
    "5441": ["groceries"],  # Candy, nut, confectionery stores
    "5451": ["groceries"],  # Dairy products stores
    "5462": ["groceries"],  # Bakeries
    "5499": ["groceries"],  # Miscellaneous food stores
    
    # Gas
    "5541": ["gas"],
    "5542": ["gas"],
    
    # Restaurants
    "5812": ["restaurants"],
    "5814": ["restaurants"],
    "5811": ["restaurants"],  # Caterers
    
    # Department/Retail
    "5311": ["department_store"],
    "5331": ["general_merchandise"],
    "5300": ["wholesale"],
    "5732": ["electronics", "shopping"],  # Electronics stores
    "5200": ["home_improvement", "shopping"],  # Home supply stores
    
    # Travel
    "4511": ["travel", "airline"],
    "7011": ["travel", "hotel"],
    "4111": ["transit"],  # Transportation
    "4121": ["transit"],  # Taxicabs and limousines
    "4112": ["transit"],  # Passenger railways
    "4119": ["transit"],  # Ambulance services
    "7512": ["travel"],  # Auto rental
    "7513": ["travel"],  # Truck rental
    "7519": ["travel"],  # Motor home rental
    
    # Online/Shopping
    "5999": ["online_shopping"],
    "5970": ["shopping"],  # Artist supply stores
    "5971": ["shopping"],  # Art dealers and galleries
    "5972": ["shopping"],  # Stamp and coin stores
    
    # Entertainment
    "7832": ["entertainment"],  # Motion picture theaters
    "7911": ["entertainment"],  # Dance halls, studios, schools
    "7922": ["entertainment"],  # Theatrical producers
    "7929": ["entertainment"],  # Bands, orchestras, entertainers
    "7932": ["entertainment"],  # Billiard and pool establishments
    "7933": ["entertainment"],  # Bowling alleys
    "7941": ["entertainment"],  # Commercial sports
    
    # Streaming/Utilities
    "4899": ["streaming", "utilities"],  # Cable and other pay TV
    "4814": ["utilities"],  # Telecommunications
    "4816": ["utilities"],  # Computer network/information services
    
    # Pharmacy
    "5912": ["pharmacy"],
    
    # Other
    "5995": ["shopping"],  # Pet shops
    "5998": ["shopping"],  # Tent and awning shops
}


def normalize_category_name(category: str) -> str:
    """
    Normalize a category name to a standard form.
    
    Args:
        category: Raw category string (e.g., "US Supermarkets", "grocery stores")
        
    Returns:
        Normalized category name (e.g., "groceries")
    """
    category_lower = category.lower().strip()
    
    # Check direct synonyms
    for normalized, synonyms in CATEGORY_SYNONYMS.items():
        if category_lower in synonyms or category_lower == normalized:
            return normalized
    
    # Check if category contains any synonym
    for normalized, synonyms in CATEGORY_SYNONYMS.items():
        for synonym in synonyms:
            if synonym in category_lower:
                return normalized
    
    # Return as-is if no match (could be a valid category)
    return category_lower.replace(" ", "_")


def resolve_merchant_query(query: str) -> MerchantCategoryMapping:
    """
    Resolve a user query to a merchant category mapping.
    
    Handles both specific merchant names and generic categories.
    Supports partial matches and common variations.
    
    Args:
        query: User query (e.g., "Macy's", "groceries", "gas", "walmart supercenter")
        
    Returns:
        MerchantCategoryMapping with resolved categories and MCCs
    """
    query_lower = query.lower().strip()
    
    # Remove common suffixes/prefixes that don't affect matching
    query_clean = re.sub(r'\s+(store|shop|market|supercenter|super market|grocery|gas station|station|restaurant|cafe|pharmacy|com|\.com)\b', '', query_lower)
    query_clean = query_clean.strip()
    
    # Check known merchants first - exact match
    for key, mapping in KNOWN_MERCHANTS.items():
        if key == query_lower or key == query_clean:
            return mapping
    
    # Check known merchants - partial match (merchant name in query)
    for key, mapping in KNOWN_MERCHANTS.items():
        if key in query_lower or key in query_clean:
            return mapping
    
    # Check aliases - exact match
    for key, mapping in KNOWN_MERCHANTS.items():
        if query_lower in mapping.aliases or query_clean in mapping.aliases:
            return mapping
    
    # Check aliases - partial match
    for key, mapping in KNOWN_MERCHANTS.items():
        for alias in mapping.aliases:
            if alias in query_lower or alias in query_clean:
                return mapping
    
    # Check if it's a generic category
    normalized = normalize_category_name(query_lower)
    
    # If it matches a known category, return a mapping for it
    if normalized in CATEGORY_SYNONYMS or normalized in [cat for cats in CATEGORY_SYNONYMS.values() for cat in cats]:
        return MerchantCategoryMapping(
            merchant_name=query,
            normalized_categories=[normalized]
        )
    
    # Default: return as generic query
    return MerchantCategoryMapping(
        merchant_name=query,
        normalized_categories=[normalized]
    )


def get_categories_for_mcc(mcc: str) -> List[str]:
    """
    Get normalized categories for a given MCC code.
    
    Args:
        mcc: Merchant Category Code (e.g., "5411")
        
    Returns:
        List of normalized category names
    """
    return MCC_TO_CATEGORY.get(mcc, [])


def match_categories(rule_categories: List[str], query_categories: List[str]) -> bool:
    """
    Check if rule categories match query categories.
    
    Args:
        rule_categories: Categories from an earning rule
        query_categories: Categories from the user query
        
    Returns:
        True if there's any overlap
    """
    rule_set = set(rule_categories)
    query_set = set(query_categories)
    return bool(rule_set & query_set)

