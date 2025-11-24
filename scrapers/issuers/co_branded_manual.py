"""
Co-branded credit card scraper - Manual data extraction.
"""

import re
from typing import List

import sys
from pathlib import Path

# Handle both package and flat structure imports
try:
    from ...models import (
        CardIssuer,
        CardNetwork,
        CardProduct,
        Cap,
        EarningRule,
        RewardProgram,
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


class CoBrandedScraper(BaseScraper):
    """Scraper for co-branded credit cards."""
    
    CARD_URLS = [
        "https://www.amazon.com/Amazon-Prime-Rewards-Visa-Signature-Card",
        "https://www.amazon.com/Amazon-Rewards-Visa-Signature-Card",
        "https://www.citi.com/credit-cards/costco-anywhere-visa-card",
        "https://www.target.com/redcard",
    ]
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False, use_selenium: bool = False):
        super().__init__("Co-Branded Cards", use_cache=use_cache, offline_mode=offline_mode, use_selenium=use_selenium)
    
    def _get_card_key_from_url(self, url: str) -> str:
        """Extract card key from URL."""
        if "amazon" in url and "prime" in url:
            return "amazon-prime-visa"
        elif "amazon" in url:
            return "amazon-visa"
        elif "costco" in url:
            return "costco-anywhere"
        elif "target" in url or "redcard" in url:
            return "target-redcard"
        return ""
    
    def scrape_cards(self) -> List[CardProduct]:
        """Scrape co-branded cards using comprehensive data."""
        cards = []
        cobranded_data = COMPREHENSIVE_CARD_DATA.get("co_branded", {})
        
        for card_url in self.CARD_URLS:
            card_key = self._get_card_key_from_url(card_url)
            if not card_key or card_key not in cobranded_data:
                continue
            
            data = cobranded_data[card_key]
            
            # Determine issuer based on card
            if "amazon" in card_key:
                issuer = CardIssuer(name="Chase", website_url="https://www.chase.com")
            elif "costco" in card_key:
                issuer = CardIssuer(name="Citi", website_url="https://www.citi.com")
            elif "target" in card_key:
                issuer = CardIssuer(name="TD Bank", website_url="https://www.td.com")
            else:
                issuer = CardIssuer(name="Various", website_url="")
            
            card_id = re.sub(r'[^a-z0-9]+', '_', data["name"].lower()).strip('_')
            card_id = f"cobranded_{card_id}"
            
            card = CardProduct(
                id=card_id,
                issuer=issuer,
                name=data["name"],
                network=data["network"],
                type=data["reward_type"],
                annual_fee=data["annual_fee"],
                foreign_transaction_fee=data["foreign_transaction_fee"],
                reward_program=None,  # Co-branded cards typically don't use transferable points
                official_url=card_url,
                metadata={"source": "comprehensive_data", "co_branded": True}
            )
            
            cards.append(card)
            logger.info(f"Loaded card: {data['name']} (fee: ${data['annual_fee']}, type: {data['reward_type'].value})")
        
        if not cards:
            raise ValueError("Co-branded scraper failed: No card data available.")
        
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """Scrape earning rules using comprehensive data."""
        card_key = self._get_card_key_from_url(card.official_url)
        cobranded_data = COMPREHENSIVE_CARD_DATA.get("co_branded", {})
        
        if not card_key or card_key not in cobranded_data:
            raise ValueError(f"No earning rules data available for {card.name}")
        
        data = cobranded_data[card_key]
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

