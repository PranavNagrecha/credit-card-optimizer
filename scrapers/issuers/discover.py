"""
Discover credit card scraper.

This is a template/placeholder implementation. In production, you would
parse actual Discover website HTML to extract card details and earning rules.
"""

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


class DiscoverScraper(BaseScraper):
    """Scraper for Discover credit cards."""
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False):
        super().__init__("Discover", use_cache=use_cache, offline_mode=offline_mode)
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
    
    def scrape_cards(self) -> List[CardProduct]:
        """
        Scrape Discover cards.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        cards = [
            CardProduct(
                id="discover_it_cashback",
                issuer=self.issuer,
                name="Discover it Cash Back",
                network=CardNetwork.DISCOVER,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.0,
                reward_program=None,
                official_url="https://www.discover.com/credit-cards/cash-back/it-card.html",
                metadata={"first_year_match": True}
            ),
            CardProduct(
                id="discover_it_miles",
                issuer=self.issuer,
                name="Discover it Miles",
                network=CardNetwork.DISCOVER,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.0,
                reward_program=None,
                official_url="https://www.discover.com/credit-cards/travel-rewards/miles-card.html",
            ),
        ]
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """
        Scrape earning rules for a Discover card.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        rules = []
        
        if card.id == "discover_it_cashback":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Rotating quarterly categories",
                    merchant_categories=["groceries", "gas", "wholesale", "restaurants", "amazon", "target"],
                    multiplier=5.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                    caps=[Cap(amount_dollars=1500.0, period="quarter")],
                    is_rotating=True,
                ),
                EarningRule(
                    card_id=card.id,
                    description="All other purchases",
                    merchant_categories=[],
                    multiplier=1.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
            ]
        elif card.id == "discover_it_miles":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="All purchases",
                    merchant_categories=[],
                    multiplier=1.5,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
            ]
        
        return rules

