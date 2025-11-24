"""
Airline co-branded credit cards scraper - Manual data extraction.

Includes United, Delta, Southwest, and American Airlines cards.
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


class AirlineCardsScraper(BaseScraper):
    """Scraper for airline co-branded credit cards."""
    
    CARD_URLS = [
        "https://www.united.com/ual/en/us/credit-card",
        "https://www.delta.com/us/en/skymiles/credit-cards",
        "https://www.southwest.com/rapidrewards/credit-cards",
        "https://www.aa.com/aadvantage-program/credit-cards",
    ]
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False, use_selenium: bool = False):
        super().__init__("Airline Cards", use_cache=use_cache, offline_mode=offline_mode, use_selenium=use_selenium)
        self.issuer = CardIssuer(
            name="Various",
            website_url="",
            support_contact=""
        )
    
    def _get_card_key_from_url(self, url: str) -> str:
        """Extract card key from URL."""
        if "united" in url:
            return "united-explorer"  # Default to Explorer, can be expanded
        elif "delta" in url:
            return "delta-gold"  # Default to Gold, can be expanded
        elif "southwest" in url:
            return "southwest-plus"  # Default to Plus, can be expanded
        elif "aa.com" in url or "aadvantage" in url:
            return "american-airlines-platinum"  # Default to Platinum
        return ""
    
    def scrape_cards(self) -> List[CardProduct]:
        """Scrape airline cards using comprehensive data."""
        cards = []
        airline_data = COMPREHENSIVE_CARD_DATA.get("airline_cards", {})
        
        # Get all airline cards from data
        for card_key, data in airline_data.items():
            # Determine issuer based on card
            if "united" in card_key:
                issuer = CardIssuer(name="Chase", website_url="https://www.chase.com")
            elif "delta" in card_key:
                issuer = CardIssuer(name="American Express", website_url="https://www.americanexpress.com")
            elif "southwest" in card_key:
                issuer = CardIssuer(name="Chase", website_url="https://www.chase.com")
            elif "american" in card_key:
                issuer = CardIssuer(name="Citi", website_url="https://www.citi.com")
            else:
                issuer = self.issuer
            
            card_id = re.sub(r'[^a-z0-9]+', '_', data["name"].lower()).strip('_')
            card_id = f"airline_{card_id}"
            
            # Determine reward program
            reward_program = None
            if "united" in card_key:
                reward_program = RewardProgram(
                    id="UNITED_MILES",
                    name="United MileagePlus",
                    base_point_value_cents=0.014,
                    notes="United Airlines frequent flyer miles"
                )
            elif "delta" in card_key:
                reward_program = RewardProgram(
                    id="DELTA_MILES",
                    name="Delta SkyMiles",
                    base_point_value_cents=0.014,
                    notes="Delta Air Lines frequent flyer miles"
                )
            elif "southwest" in card_key:
                reward_program = RewardProgram(
                    id="SOUTHWEST_MILES",
                    name="Southwest Rapid Rewards",
                    base_point_value_cents=0.014,
                    notes="Southwest Airlines frequent flyer points"
                )
            elif "american" in card_key:
                reward_program = RewardProgram(
                    id="AMERICAN_AIRLINES_MILES",
                    name="American Airlines AAdvantage Miles",
                    base_point_value_cents=0.014,
                    notes="American Airlines frequent flyer miles"
                )
            
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
                metadata={"source": "comprehensive_data", "airline_card": True}
            )
            
            cards.append(card)
            logger.info(f"Loaded card: {data['name']} (fee: ${data['annual_fee']}, type: {data['reward_type'].value})")
        
        if not cards:
            raise ValueError("Airline cards scraper failed: No card data available.")
        
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """Scrape earning rules for airline cards."""
        from .comprehensive_data import COMPREHENSIVE_CARD_DATA
        
        airline_data = COMPREHENSIVE_CARD_DATA.get("airline_cards", {})
        
        # Find matching card by name
        card_key = None
        for key, data in airline_data.items():
            if data["name"] == card.name:
                card_key = key
                break
        
        if not card_key or card_key not in airline_data:
            return []
        
        data = airline_data[card_key]
        rules = []
        
        for rule_data in data.get("earning_rules", []):
            rule = EarningRule(
                description=rule_data["description"],
                categories=rule_data.get("categories", []),
                merchant_names=rule_data.get("merchant_names", []),
                multiplier=rule_data["multiplier"],
                caps=[Cap(**cap) for cap in rule_data.get("caps", [])],
                is_rotating=rule_data.get("is_rotating", False),
                stacking_rules=rule_data.get("stacking_rules"),
            )
            rules.append(rule)
            logger.info(f"Loaded earning rule: {rule.description}")
        
        return rules

