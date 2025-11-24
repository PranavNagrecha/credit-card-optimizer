"""
Bank of America credit card scraper - Manual data extraction.

Since the pages are JavaScript-rendered and Selenium setup is complex,
this version uses known card data with improved parsing where possible.
"""

import json
import logging
import re
from typing import List, Optional

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

logger = logging.getLogger(__name__)


class BankOfAmericaScraper(BaseScraper):
    """Scraper for Bank of America credit cards."""
    
    # Known Bank of America card data (manually curated from their website)
    CARD_DATA = {
        "premium-rewards-credit-card": {
            "name": "Bank of America Premium Rewards",
            "annual_fee": 95.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "Travel and dining purchases",
                    "categories": ["travel", "restaurants"],
                    "multiplier": 2.0,
                    "reward_type": RewardType.POINTS_PER_DOLLAR,
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.5,
                    "reward_type": RewardType.POINTS_PER_DOLLAR,
                },
            ],
        },
        "cash-back-credit-card": {
            "name": "Bank of America Customized Cash Rewards",
            "annual_fee": 0.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.CASHBACK_PERCENT,
            "foreign_transaction_fee": 0.03,
            "earning_rules": [
                {
                    "description": "Choice category (gas, online shopping, dining, drug stores, home improvement, or travel)",
                    "categories": ["gas", "online_shopping", "restaurants", "pharmacy", "travel", "home_improvement"],
                    "multiplier": 3.0,
                    "reward_type": RewardType.CASHBACK_PERCENT,
                    "caps": [{"amount": 2500.0, "period": "quarter"}],
                    "activation_required": True,
                },
                {
                    "description": "Wholesale clubs",
                    "categories": ["wholesale"],
                    "multiplier": 2.0,
                    "reward_type": RewardType.CASHBACK_PERCENT,
                    "caps": [{"amount": 2500.0, "period": "quarter"}],
                },
                {
                    "description": "All other purchases",
                    "categories": [],
                    "multiplier": 1.0,
                    "reward_type": RewardType.CASHBACK_PERCENT,
                },
            ],
        },
        "travel-rewards-credit-card": {
            "name": "Bank of America Travel Rewards",
            "annual_fee": 0.0,
            "network": CardNetwork.VISA,
            "reward_type": RewardType.POINTS_PER_DOLLAR,
            "foreign_transaction_fee": 0.0,
            "earning_rules": [
                {
                    "description": "All purchases",
                    "categories": [],
                    "multiplier": 1.5,
                    "reward_type": RewardType.POINTS_PER_DOLLAR,
                },
            ],
        },
    }
    
    CARD_URLS = [
        "https://www.bankofamerica.com/credit-cards/products/premium-rewards-credit-card",
        "https://www.bankofamerica.com/credit-cards/products/cash-back-credit-card",
        "https://www.bankofamerica.com/credit-cards/products/travel-rewards-credit-card",
    ]
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False, use_selenium: bool = False):
        super().__init__("Bank of America", use_cache=use_cache, offline_mode=offline_mode, use_selenium=use_selenium)
        self.issuer = CardIssuer(
            name="Bank of America",
            website_url="https://www.bankofamerica.com",
            support_contact="1-800-732-9194"
        )
        self.reward_program = RewardProgram(
            id="BOA_POINTS",
            name="Bank of America Rewards",
            base_point_value_cents=0.01,
            notes="Points redeemable for cash, travel, or gift cards"
        )
    
    def _get_card_key_from_url(self, url: str) -> Optional[str]:
        """Extract card key from URL."""
        for key in self.CARD_DATA.keys():
            if key in url:
                return key
        return None
    
    def scrape_cards(self) -> List[CardProduct]:
        """
        Scrape Bank of America cards.
        
        Uses manually curated data since pages are JS-rendered.
        """
        cards = []
        
        for card_url in self.CARD_URLS:
            card_key = self._get_card_key_from_url(card_url)
            if not card_key or card_key not in self.CARD_DATA:
                logger.warning(f"No data available for {card_url}")
                continue
            
            data = self.CARD_DATA[card_key]
            
            # Generate card ID
            card_id = re.sub(r'[^a-z0-9]+', '_', data["name"].lower()).strip('_')
            card_id = f"boa_{card_id}"
            
            # Determine reward program
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
                metadata={"source": "manual_data"}
            )
            
            cards.append(card)
            logger.info(f"Loaded card: {data['name']} (fee: ${data['annual_fee']}, type: {data['reward_type'].value})")
        
        if not cards:
            raise ValueError("Bank of America scraper failed: No card data available.")
        
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """
        Scrape earning rules for a Bank of America card.
        
        Uses manually curated data.
        """
        card_key = self._get_card_key_from_url(card.official_url)
        if not card_key or card_key not in self.CARD_DATA:
            raise ValueError(f"No earning rules data available for {card.name}")
        
        data = self.CARD_DATA[card_key]
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
                multiplier=rule_data["multiplier"],
                reward_type=rule_data["reward_type"],
                caps=caps,
                is_rotating=rule_data.get("activation_required", False),
                stacking_rules="Activation/selection required" if rule_data.get("activation_required") else None,
            )
            rules.append(rule)
        
        logger.info(f"Loaded {len(rules)} earning rules for {card.name}")
        return rules

