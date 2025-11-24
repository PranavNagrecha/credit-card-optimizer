"""
Premium and business credit cards scraper - Manual data extraction.

Includes premium cards and business cards from major issuers.
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


class PremiumCardsScraper(BaseScraper):
    """Scraper for premium and business credit cards."""
    
    CARD_URLS = [
        "https://www.chase.com/business/credit-cards",
        "https://www.americanexpress.com/us/business/credit-cards",
        "https://www.citi.com/credit-cards",
    ]
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False, use_selenium: bool = False):
        super().__init__("Premium Cards", use_cache=use_cache, offline_mode=offline_mode, use_selenium=use_selenium)
        self.issuer = CardIssuer(
            name="Various",
            website_url="",
            support_contact=""
        )
    
    def scrape_cards(self) -> List[CardProduct]:
        """Scrape premium/business cards using comprehensive data."""
        cards = []
        premium_data = COMPREHENSIVE_CARD_DATA.get("premium_cards", {})
        
        # Get all premium cards from data
        for card_key, data in premium_data.items():
            # Determine issuer based on card
            if "chase" in card_key:
                issuer = CardIssuer(name="Chase", website_url="https://www.chase.com")
                reward_program = RewardProgram(
                    id="CHASE_UR",
                    name="Chase Ultimate Rewards",
                    base_point_value_cents=0.017,
                    notes="Transferable to travel partners"
                )
            elif "amex" in card_key:
                issuer = CardIssuer(name="American Express", website_url="https://www.americanexpress.com")
                reward_program = RewardProgram(
                    id="AMEX_MR",
                    name="American Express Membership Rewards",
                    base_point_value_cents=0.017,
                    notes="Transferable to travel partners"
                )
            elif "citi" in card_key:
                issuer = CardIssuer(name="Citi", website_url="https://www.citi.com")
                reward_program = RewardProgram(
                    id="CITI_TY",
                    name="Citi ThankYou Points",
                    base_point_value_cents=0.015,
                    notes="Transferable to travel partners"
                )
            else:
                issuer = self.issuer
                reward_program = None
            
            card_id = re.sub(r'[^a-z0-9]+', '_', data["name"].lower()).strip('_')
            card_id = f"premium_{card_id}"
            
            card = CardProduct(
                id=card_id,
                issuer=issuer,
                name=data["name"],
                network=data["network"],
                type=data["reward_type"],
                annual_fee=data["annual_fee"],
                foreign_transaction_fee=data["foreign_transaction_fee"],
                reward_program=reward_program,
                official_url=self.CARD_URLS[0] if self.CARD_URLS else "",
                metadata={"source": "comprehensive_data", "premium_card": True, "business_card": "business" in card_key.lower()}
            )
            
            cards.append(card)
            logger.info(f"Loaded card: {data['name']} (fee: ${data['annual_fee']}, type: {data['reward_type'].value})")
        
        if not cards:
            raise ValueError("Premium cards scraper failed: No card data available.")
        
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """Scrape earning rules for premium/business cards."""
        from .comprehensive_data import COMPREHENSIVE_CARD_DATA
        
        premium_data = COMPREHENSIVE_CARD_DATA.get("premium_cards", {})
        
        # Find matching card by name
        card_key = None
        for key, data in premium_data.items():
            if data["name"] == card.name:
                card_key = key
                break
        
        if not card_key or card_key not in premium_data:
            return []
        
        data = premium_data[card_key]
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

