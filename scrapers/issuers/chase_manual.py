"""
Chase credit card scraper - Manual data extraction.

Uses comprehensive, accurate data since pages are JavaScript-rendered.
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


class ChaseScraper(BaseScraper):
    """Scraper for Chase credit cards."""
    
    CARD_URLS = [
        "https://www.chase.com/credit-cards/sapphire-preferred",
        "https://www.chase.com/credit-cards/sapphire-reserve",
        "https://www.chase.com/credit-cards/freedom/flex",
        "https://www.chase.com/credit-cards/freedom/unlimited",
    ]
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False, use_selenium: bool = False):
        super().__init__("Chase", use_cache=use_cache, offline_mode=offline_mode, use_selenium=use_selenium)
        self.issuer = CardIssuer(
            name="Chase",
            website_url="https://www.chase.com",
            support_contact="1-800-935-9935"
        )
        self.reward_program = RewardProgram(
            id="CHASE_UR",
            name="Chase Ultimate Rewards",
            base_point_value_cents=0.017,
            notes="Transferable to travel partners"
        )
    
    def _get_card_key_from_url(self, url: str) -> str:
        """Extract card key from URL."""
        if "sapphire-preferred" in url:
            return "sapphire-preferred"
        elif "sapphire-reserve" in url:
            return "sapphire-reserve"
        elif "freedom-flex" in url or "freedom/flex" in url:
            return "freedom-flex"
        elif "freedom-unlimited" in url or "freedom/unlimited" in url:
            return "freedom-unlimited"
        return ""
    
    def scrape_cards(self) -> List[CardProduct]:
        """Scrape Chase cards using comprehensive data."""
        cards = []
        chase_data = COMPREHENSIVE_CARD_DATA.get("chase", {})
        
        for card_url in self.CARD_URLS:
            card_key = self._get_card_key_from_url(card_url)
            if not card_key or card_key not in chase_data:
                continue
            
            data = chase_data[card_key]
            
            # Generate card ID
            card_id = re.sub(r'[^a-z0-9]+', '_', data["name"].lower()).strip('_')
            card_id = f"chase_{card_id}"
            
            # Determine reward program
            reward_program = None
            if data["reward_type"] == RewardType.POINTS_PER_DOLLAR:
                reward_program = self.reward_program
            
            # Foreign transaction fee
            foreign_transaction_fee = 0.03
            if "sapphire" in card_key:
                foreign_transaction_fee = 0.0
            
            card = CardProduct(
                id=card_id,
                issuer=self.issuer,
                name=data["name"],
                network=data["network"],
                type=data["reward_type"],
                annual_fee=data["annual_fee"],
                foreign_transaction_fee=foreign_transaction_fee,
                reward_program=reward_program,
                official_url=card_url,
                metadata={"source": "comprehensive_data"}
            )
            
            cards.append(card)
            logger.info(f"Loaded card: {data['name']} (fee: ${data['annual_fee']}, type: {data['reward_type'].value})")
        
        if not cards:
            raise ValueError("Chase scraper failed: No card data available.")
        
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """Scrape earning rules using comprehensive data."""
        card_key = self._get_card_key_from_url(card.official_url)
        chase_data = COMPREHENSIVE_CARD_DATA.get("chase", {})
        
        if not card_key or card_key not in chase_data:
            raise ValueError(f"No earning rules data available for {card.name}")
        
        data = chase_data[card_key]
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

