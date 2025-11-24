"""
Rule Engine for Credit Card Reward Rules

This module provides a rule-based system for parsing and evaluating
credit card earning rules. It uses structured patterns to extract
rules and a rule engine to evaluate which rule applies to a given
merchant/category query.
"""

import re
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass

from models import EarningRule, RewardType, CardProduct


@dataclass
class ParsedRewardRule:
    """A parsed reward rule with structured components."""
    multiplier: float
    category_keywords: List[str]
    merchant_keywords: List[str]
    description: str
    cap_amount: Optional[float] = None
    cap_period: Optional[str] = None
    is_rotating: bool = False
    priority: int = 0  # Higher priority = more specific rule


class RuleParser:
    """Parses reward rules from text using structured patterns."""
    
    # Common reward patterns in NerdWallet format
    REWARD_PATTERNS = [
        # Pattern: "6% cash back at U.S. supermarkets, on up to $6,000 in spending per year"
        r'(\d+(?:\.\d+)?)\s*%\s*cash\s*back\s+(?:at|on|for)\s+([^,]+?)(?:,\s*on\s+up\s+to\s+\$?(\d+(?:,\d+)?)\s*(?:in\s+spending\s+)?(?:per\s+)?(year|month|quarter))?',
        
        # Pattern: "6% cash back on select U.S. streaming subscriptions"
        r'(\d+(?:\.\d+)?)\s*%\s*cash\s*back\s+on\s+([^\.]+)',
        
        # Pattern: "3% cash back at U.S. gas stations"
        r'(\d+(?:\.\d+)?)\s*%\s*cash\s+back\s+at\s+([^\.]+)',
        
        # Pattern: "1% cash back on other purchases"
        r'(\d+(?:\.\d+)?)\s*%\s*cash\s+back\s+on\s+([^\.]+)',
        
        # Pattern: "3x points on travel"
        r'(\d+(?:\.\d+)?)\s*x\s+points?\s+(?:on|for|at)\s+([^\.]+)',
        
        # Pattern: "2 miles per dollar on dining"
        r'(\d+(?:\.\d+)?)\s*miles?\s+per\s+dollar\s+(?:on|for|at)\s+([^\.]+)',
    ]
    
    # Category mapping keywords
    CATEGORY_KEYWORDS = {
        'groceries': ['supermarket', 'supermarkets', 'grocery', 'grocery store', 'grocery stores', 'food store'],
        'restaurants': ['restaurant', 'dining', 'dine', 'food', 'fast food', 'cafe'],
        'travel': ['travel', 'trip', 'airline', 'hotel', 'flight', 'airport', 'lodging'],
        'gas': ['gas', 'gasoline', 'fuel', 'gas station', 'gas stations'],
        'streaming': ['streaming', 'netflix', 'spotify', 'hulu', 'disney', 'entertainment'],
        'utilities': ['utility', 'phone', 'internet', 'cable', 'electric', 'water'],
        'pharmacy': ['pharmacy', 'drugstore', 'cvs', 'walgreens', 'rite aid'],
        'entertainment': ['entertainment', 'movie', 'theater', 'cinema', 'concert'],
        'transit': ['transit', 'uber', 'lyft', 'taxi', 'public transportation'],
        'online_shopping': ['online', 'internet', 'e-commerce'],
        'department_store': ['department store', 'retail'],
        'wholesale': ['wholesale', 'warehouse', 'costco', "sam's club"],
    }
    
    @classmethod
    def parse_reward_text(cls, text: str, reward_type: RewardType) -> List[ParsedRewardRule]:
        """
        Parse reward rules from structured text.
        
        Example input:
        "6% cash back at U.S. supermarkets, on up to $6,000 in spending per year.
         6% cash back on select U.S. streaming subscriptions.
         3% cash back at U.S. gas stations.
         3% cash back on transit.
         1% cash back on other purchases."
        """
        rules = []
        text_lower = text.lower()
        
        # Split by sentences or bullet points
        sentences = re.split(r'[\.\n]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue
            
            # Skip marketing/comparison text
            if any(phrase in sentence.lower() for phrase in [
                'compare', 'vs', 'versus', 'better than', 'prominent brands', 
                'heard of', 'advertisement', 'sponsored'
            ]):
                continue
            
            # Try each pattern
            for pattern in cls.REWARD_PATTERNS:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    multiplier = float(match.group(1))
                    category_text = match.group(2).strip()
                    
                    # Extract cap if present
                    cap_amount = None
                    cap_period = None
                    if len(match.groups()) >= 4 and match.group(3):
                        try:
                            cap_amount = float(match.group(3).replace(',', ''))
                            cap_period = match.group(4) if len(match.groups()) >= 4 else 'year'
                        except (ValueError, IndexError):
                            pass
                    
                    # Map category text to normalized categories
                    categories = cls._extract_categories(category_text)
                    
                    # Determine priority (more specific = higher priority)
                    priority = len(categories) * 10 + (1 if cap_amount else 0)
                    
                    # Check if rotating
                    is_rotating = bool(re.search(r'rotating|quarterly|changes', sentence.lower()))
                    
                    rule = ParsedRewardRule(
                        multiplier=multiplier,
                        category_keywords=cls._extract_keywords(category_text),
                        merchant_keywords=[],
                        description=sentence,
                        cap_amount=cap_amount,
                        cap_period=cap_period,
                        is_rotating=is_rotating,
                        priority=priority
                    )
                    rules.append(rule)
                    break  # Found a match, move to next sentence
        
        return rules
    
    @classmethod
    def _extract_categories(cls, text: str) -> List[str]:
        """Extract normalized categories from text."""
        categories = []
        text_lower = text.lower()
        
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)
        
        return categories
    
    @classmethod
    def _extract_keywords(cls, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Remove common words
        stop_words = {'at', 'on', 'for', 'the', 'a', 'an', 'u.s.', 'us', 'select', 'other'}
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]


class RuleEngine:
    """Evaluates which reward rule applies to a given merchant/category."""
    
    def __init__(self, rules: List[EarningRule], card: CardProduct):
        self.rules = rules
        self.card = card
        self._sorted_rules = sorted(
            rules,
            key=lambda r: self._rule_priority(r),
            reverse=True
        )
    
    def _rule_priority(self, rule: EarningRule) -> int:
        """Calculate priority for a rule (higher = more specific)."""
        priority = 0
        
        # More categories = more specific
        priority += len(rule.merchant_categories) * 10
        
        # Merchant names = very specific
        priority += len(rule.merchant_names) * 20
        
        # MCC codes = specific
        priority += len(rule.mcc_list) * 15
        
        # Has cap = more specific
        if rule.caps:
            priority += 5
        
        # Rotating = less priority (may not be active)
        if rule.is_rotating:
            priority -= 10
        
        return priority
    
    def find_applicable_rule(
        self,
        categories: List[str],
        merchant_name: Optional[str] = None,
        mcc: Optional[str] = None
    ) -> Optional[Tuple[EarningRule, float]]:
        """
        Find the best matching rule for given criteria.
        
        Returns:
            Tuple of (rule, effective_rate) or None if no match
        """
        from valuation import compute_effective_rate
        
        # Try rules in priority order (most specific first)
        for rule in self._sorted_rules:
            # Check category match
            category_match = bool(set(rule.merchant_categories) & set(categories))
            
            # Check merchant name match
            merchant_match = False
            if merchant_name and rule.merchant_names:
                merchant_lower = merchant_name.lower()
                merchant_match = any(
                    m.lower() in merchant_lower or merchant_lower in m.lower()
                    for m in rule.merchant_names
                )
            
            # Check MCC match
            mcc_match = mcc and mcc in rule.mcc_list
            
            # Rule applies if any match
            if category_match or merchant_match or mcc_match:
                effective_rate = compute_effective_rate(rule, self.card.reward_program)
                return (rule, effective_rate)
        
        # No specific rule found - return default (1% or 1x)
        return None
    
    def get_all_applicable_rules(
        self,
        categories: List[str],
        merchant_name: Optional[str] = None,
        mcc: Optional[str] = None
    ) -> List[Tuple[EarningRule, float]]:
        """Get all applicable rules (not just the best one)."""
        from valuation import compute_effective_rate
        
        applicable = []
        
        for rule in self._sorted_rules:
            category_match = bool(set(rule.merchant_categories) & set(categories))
            merchant_match = (
                merchant_name and rule.merchant_names and
                any(m.lower() in merchant_name.lower() for m in rule.merchant_names)
            )
            mcc_match = mcc and mcc in rule.mcc_list
            
            if category_match or merchant_match or mcc_match:
                effective_rate = compute_effective_rate(rule, self.card.reward_program)
                applicable.append((rule, effective_rate))
        
        # Sort by effective rate (descending)
        applicable.sort(key=lambda x: x[1], reverse=True)
        return applicable

