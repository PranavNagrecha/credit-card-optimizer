"""
Discover credit card scraper - Manual data extraction.
"""

import re
from typing import List

from ...models import (
    CardIssuer,
    CardNetwork,
    CardProduct,
    Cap,
    EarningRule,
    RewardProgram,
    RewardType,
)
from ..base import BaseScraper
from .comprehensive_data import COMPREHENSIVE_CARD_DATA

logger = __import__('logging').getLogger(__name__)


class DiscoverScraper(BaseScraper):
    """Scraper for Discover credit cards."""
    
    CARD_URLS = [
        "https://www.discover.com/credit-cards/cash-back/it-card.html",
        "https://www.discover.com/credit-cards/travel-rewards/miles-card.html",
    ]
    
    # Map URLs to card keys (since both URLs might map to same key)
    URL_TO_KEY = {
        "https://www.discover.com/credit-cards/cash-back/it-card.html": "it-cash-back",
        "https://www.discover.com/credit-cards/travel-rewards/miles-card.html": "it-miles",
    }
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False, use_selenium: bool = False):
        super().__init__("Discover", use_cache=use_cache, offline_mode=offline_mode, use_selenium=use_selenium)
        self.issuer = CardIssuer(
            name="Discover",
            website_url="https://www.discover.com",
            support_contact="1-800-347-2683"
        )
        self.reward_program = RewardProgram(
            id="DISCOVER_CASHBACK",
            name="Discover Cashback",
            base_point_value_cents=0.01,
            notes="Cashback match for first year"
        )
    
    def _get_card_key_from_url(self, url: str) -> str:
        """Extract card key from URL."""
        return self.URL_TO_KEY.get(url, "")
    
    def scrape_cards(self) -> List[CardProduct]:
        """Scrape Discover cards using comprehensive data."""
        cards = []
        discover_data = COMPREHENSIVE_CARD_DATA.get("discover", {})
        seen_keys = set()  # Prevent duplicates
        
        for card_url in self.CARD_URLS:
            card_key = self._get_card_key_from_url(card_url)
            if not card_key or card_key not in discover_data or card_key in seen_keys:
                continue
            
            seen_keys.add(card_key)
            data = discover_data[card_key]
            
            card_id = re.sub(r'[^a-z0-9]+', '_', data["name"].lower()).strip('_')
            card_id = f"discover_{card_id}"
            
            reward_program = None
            if data["reward_type"] == RewardType.CASHBACK_PERCENT:
                reward_program = self.reward_program
            
            card = CardProduct(
                id=card_id,
                issuer=self.issuer,
                name=data["name"],
                network=data["network"],
                type=data["reward_type"],
                annual_fee=data["annual_fee"],
                foreign_transaction_fee=data["foreign_transaction_fee"],
                reward_program=reward_program,
                official_url=card_url,
                metadata={"source": "comprehensive_data"}
            )
            
            cards.append(card)
            logger.info(f"Loaded card: {data['name']} (fee: ${data['annual_fee']}, type: {data['reward_type'].value})")
        
        if not cards:
            raise ValueError("Discover scraper failed: No card data available.")
        
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """Scrape earning rules using comprehensive data."""
        card_key = self._get_card_key_from_url(card.official_url)
        discover_data = COMPREHENSIVE_CARD_DATA.get("discover", {})
        
        if not card_key or card_key not in discover_data:
            raise ValueError(f"No earning rules data available for {card.name}")
        
        data = discover_data[card_key]
        rules = []
        
        for rule_data in data["earning_rules"]:
            caps = []
            if "caps" in rule_data:
                for cap_data in rule_data["caps"]:
                    caps.append(Cap(
                        amount_dollars=cap_data["amount"],
                        period=cap_data["period"]
                    ))
            
            rule = EarningRule(
                card_id=card.id,
                description=rule_data["description"],
                merchant_categories=rule_data["categories"],
                merchant_names=rule_data.get("merchant_names", []),
                multiplier=rule_data["multiplier"],
                reward_type=data["reward_type"],
                caps=caps,
                is_rotating=rule_data.get("is_rotating", False),
                stacking_rules=rule_data.get("stacking_rules"),
            )
            rules.append(rule)
        
        logger.info(f"Loaded {len(rules)} earning rules for {card.name}")
        return rules

