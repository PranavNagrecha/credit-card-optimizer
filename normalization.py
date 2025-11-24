"""
Category normalization and merchant mapping logic.

Converts user queries and merchant names into normalized categories
and MCC codes for matching against earning rules.
"""

import re
from typing import List, Optional

from config import CATEGORY_SYNONYMS
from models import MerchantCategoryMapping


# Known merchant mappings (can be expanded)
KNOWN_MERCHANTS: dict[str, MerchantCategoryMapping] = {
    "macy's": MerchantCategoryMapping(
        merchant_name="Macy's",
        mcc="5311",
        normalized_categories=["department_store"],
        aliases=["macys", "macy", "macy's"]
    ),
    "amazon": MerchantCategoryMapping(
        merchant_name="Amazon",
        mcc="5999",
        normalized_categories=["online_shopping", "general_merchandise"],
        aliases=["amazon.com", "amzn"]
    ),
    "costco": MerchantCategoryMapping(
        merchant_name="Costco",
        mcc="5300",
        normalized_categories=["wholesale", "groceries"],
        aliases=["costco wholesale"]
    ),
    "walmart": MerchantCategoryMapping(
        merchant_name="Walmart",
        mcc="5331",
        normalized_categories=["general_merchandise", "groceries"],
        aliases=["walmart supercenter", "walmart.com"]
    ),
    "target": MerchantCategoryMapping(
        merchant_name="Target",
        mcc="5331",
        normalized_categories=["general_merchandise", "groceries"],
        aliases=["target.com"]
    ),
    "kroger": MerchantCategoryMapping(
        merchant_name="Kroger",
        mcc="5411",
        normalized_categories=["groceries"],
        aliases=["kroger grocery", "kroger.com"]
    ),
    "whole foods": MerchantCategoryMapping(
        merchant_name="Whole Foods",
        mcc="5411",
        normalized_categories=["groceries"],
        aliases=["whole foods market", "wholefoods"]
    ),
    "delta": MerchantCategoryMapping(
        merchant_name="Delta Airlines",
        mcc="4511",
        normalized_categories=["travel", "airline"],
        aliases=["delta air lines", "delta.com"]
    ),
    "united": MerchantCategoryMapping(
        merchant_name="United Airlines",
        mcc="4511",
        normalized_categories=["travel", "airline"],
        aliases=["united airlines", "united.com"]
    ),
    "american airlines": MerchantCategoryMapping(
        merchant_name="American Airlines",
        mcc="4511",
        normalized_categories=["travel", "airline"],
        aliases=["aa.com", "american"]
    ),
}

# MCC to category mappings
MCC_TO_CATEGORY: dict[str, List[str]] = {
    "5411": ["groceries"],
    "5541": ["gas"],
    "5542": ["gas"],
    "5812": ["restaurants"],
    "5814": ["restaurants"],
    "5311": ["department_store"],
    "5331": ["general_merchandise"],
    "5300": ["wholesale"],
    "4511": ["travel", "airline"],
    "7011": ["travel", "hotel"],
    "5999": ["online_shopping"],
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
    
    Args:
        query: User query (e.g., "Macy's", "groceries", "gas")
        
    Returns:
        MerchantCategoryMapping with resolved categories and MCCs
    """
    query_lower = query.lower().strip()
    
    # Check known merchants first
    for key, mapping in KNOWN_MERCHANTS.items():
        if key in query_lower or any(alias in query_lower for alias in mapping.aliases):
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

