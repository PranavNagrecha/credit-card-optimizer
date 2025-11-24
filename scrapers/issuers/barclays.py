"""
Barclays credit card scraper.

This is a template/placeholder implementation. In production, you would
parse actual Barclays website HTML to extract card details and earning rules.
"""

from typing import List

from ...models import (
    CardIssuer,
    CardNetwork,
    CardProduct,
    EarningRule,
    RewardProgram,
    RewardType,
)
from ..base import BaseScraper


class BarclaysScraper(BaseScraper):
    """Scraper for Barclays credit cards."""
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False):
        super().__init__("Barclays", use_cache=use_cache, offline_mode=offline_mode)
        self.issuer = CardIssuer(
            name="Barclays",
            website_url="https://www.barclaysus.com",
            support_contact="1-866-928-8598"
        )
        self.reward_program = RewardProgram(
            id="BARCLAYS_POINTS",
            name="Barclays Rewards",
            base_point_value_cents=0.01,
            notes="Points redeemable for cash, travel, or gift cards"
        )
    
    def scrape_cards(self) -> List[CardProduct]:
        """
        Scrape Barclays cards.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        cards = [
            CardProduct(
                id="barclays_avios",
                issuer=self.issuer,
                name="Barclays AAdvantage Aviator Red World Elite Mastercard",
                network=CardNetwork.MASTERCARD,
                type=RewardType.MILES_PER_DOLLAR,
                annual_fee=99.0,
                foreign_transaction_fee=0.0,
                reward_program=RewardProgram(
                    id="AMERICAN_AIRLINES_MILES",
                    name="American Airlines AAdvantage Miles",
                    base_point_value_cents=0.014,
                    notes="American Airlines frequent flyer miles"
                ),
                official_url="https://www.barclaysus.com/credit-cards/american-airlines-aviator-red-world-elite-mastercard",
                metadata={"signup_bonus": "60000"}
            ),
        ]
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """
        Scrape earning rules for a Barclays card.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        rules = []
        
        if card.id == "barclays_avios":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="American Airlines purchases",
                    merchant_names=["American Airlines", "aa.com"],
                    merchant_categories=["travel", "airline"],
                    multiplier=2.0,
                    reward_type=RewardType.MILES_PER_DOLLAR,
                ),
                EarningRule(
                    card_id=card.id,
                    description="All other purchases",
                    merchant_categories=[],
                    multiplier=1.0,
                    reward_type=RewardType.MILES_PER_DOLLAR,
                ),
            ]
        
        return rules

