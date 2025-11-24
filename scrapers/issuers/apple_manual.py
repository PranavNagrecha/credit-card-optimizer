"""
Apple Card scraper - Manual data extraction.

Apple Card is issued by Goldman Sachs.
"""

import re
import sys
from pathlib import Path
from typing import List

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
    # Fallback for flat structure (Render): add parent directories to path
    current_file = Path(__file__).resolve()
    # Go up 3 levels: scrapers/issuers/ -> root
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


class AppleScraper(BaseScraper):
    """Scraper for Apple Card."""
    
    CARD_URLS = [
        "https://www.apple.com/apple-card/",
    ]
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False, use_selenium: bool = False):
        super().__init__("Apple", use_cache=use_cache, offline_mode=offline_mode, use_selenium=use_selenium)
        self.issuer = CardIssuer(
            name="Goldman Sachs",
            website_url="https://www.apple.com/apple-card/",
            support_contact="1-877-255-5923"
        )
    
    def _get_card_key_from_url(self, url: str) -> str:
        """Extract card key from URL."""
        if "apple-card" in url:
            return "apple-card"
        return ""
    
    def scrape_cards(self) -> List[CardProduct]:
        """Scrape Apple Card using comprehensive data."""
        cards = []
        apple_data = COMPREHENSIVE_CARD_DATA.get("apple", {})
        
        for card_url in self.CARD_URLS:
            card_key = self._get_card_key_from_url(card_url)
            if not card_key or card_key not in apple_data:
                continue
            
            data = apple_data[card_key]
            
            card_id = re.sub(r'[^a-z0-9]+', '_', data["name"].lower()).strip('_')
            card_id = f"apple_{card_id}"
            
            card = CardProduct(
                id=card_id,
                issuer=self.issuer,
                name=data["name"],
                network=data["network"],
                type=data["reward_type"],
                annual_fee=data["annual_fee"],
                foreign_transaction_fee=data["foreign_transaction_fee"],
                reward_program=None,  # Apple Card uses cashback, not points
                official_url=card_url,
                metadata={"source": "comprehensive_data"}
            )
            
            cards.append(card)
            logger.info(f"Loaded card: {data['name']} (fee: ${data['annual_fee']}, type: {data['reward_type'].value})")
        
        if not cards:
            raise ValueError("Apple scraper failed: No card data available.")
        
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """Scrape earning rules for Apple Card."""
        from .comprehensive_data import COMPREHENSIVE_CARD_DATA
        
        card_key = self._get_card_key_from_url(card.official_url)
        if not card_key:
            card_key = "apple-card"
        
        apple_data = COMPREHENSIVE_CARD_DATA.get("apple", {})
        if card_key not in apple_data:
            return []
        
        data = apple_data[card_key]
        rules = []
        
        for rule_data in data.get("earning_rules", []):
            rule = EarningRule(
                card_id=card.id,
                description=rule_data["description"],
                merchant_categories=rule_data.get("categories", []),
                merchant_names=rule_data.get("merchant_names", []),
                multiplier=rule_data["multiplier"],
                reward_type=card.type,
                caps=[Cap(amount_dollars=cap.get("amount", cap.get("amount_dollars", 0)), period=cap.get("period", "year")) for cap in rule_data.get("caps", [])],
                is_rotating=rule_data.get("is_rotating", False),
                stacking_rules=rule_data.get("stacking_rules"),
            )
            rules.append(rule)
            logger.info(f"Loaded earning rule: {rule.description}")
        
        return rules

