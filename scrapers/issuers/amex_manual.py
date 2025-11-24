"""
American Express credit card scraper - Manual data extraction.
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


class AmexScraper(BaseScraper):
    """Scraper for American Express credit cards."""
    
    CARD_URLS = [
        "https://www.americanexpress.com/us/credit-cards/card/gold-card",
        "https://www.americanexpress.com/us/credit-cards/card/platinum-card",
        "https://www.americanexpress.com/us/credit-cards/card/blue-cash-everyday",
        "https://www.americanexpress.com/us/credit-cards/card/blue-cash-preferred",
    ]
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False, use_selenium: bool = False):
        super().__init__("American Express", use_cache=use_cache, offline_mode=offline_mode, use_selenium=use_selenium)
        self.issuer = CardIssuer(
            name="American Express",
            website_url="https://www.americanexpress.com",
            support_contact="1-800-528-4800"
        )
        self.reward_program = RewardProgram(
            id="AMEX_MR",
            name="Membership Rewards",
            base_point_value_cents=0.017,
            notes="Transferable to travel partners"
        )
    
    def _get_card_key_from_url(self, url: str) -> str:
        """Extract card key from URL."""
        if "gold-card" in url:
            return "gold-card"
        elif "platinum-card" in url:
            return "platinum-card"
        elif "blue-cash-everyday" in url:
            return "blue-cash-everyday"
        elif "blue-cash-preferred" in url:
            return "blue-cash-preferred"
        return ""
    
    def scrape_cards(self) -> List[CardProduct]:
        """Scrape Amex cards using comprehensive data."""
        cards = []
        amex_data = COMPREHENSIVE_CARD_DATA.get("amex", {})
        
        for card_url in self.CARD_URLS:
            card_key = self._get_card_key_from_url(card_url)
            if not card_key or card_key not in amex_data:
                continue
            
            data = amex_data[card_key]
            
            card_id = re.sub(r'[^a-z0-9]+', '_', data["name"].lower()).strip('_')
            card_id = f"amex_{card_id}"
            
            reward_program = None
            if data["reward_type"] == RewardType.POINTS_PER_DOLLAR:
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
            raise ValueError("Amex scraper failed: No card data available.")
        
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """Scrape earning rules using comprehensive data."""
        card_key = self._get_card_key_from_url(card.official_url)
        amex_data = COMPREHENSIVE_CARD_DATA.get("amex", {})
        
        if not card_key or card_key not in amex_data:
            raise ValueError(f"No earning rules data available for {card.name}")
        
        data = amex_data[card_key]
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

