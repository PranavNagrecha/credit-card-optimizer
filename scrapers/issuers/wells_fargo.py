"""
Wells Fargo credit card scraper.

This is a template/placeholder implementation. In production, you would
parse actual Wells Fargo website HTML to extract card details and earning rules.
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


class WellsFargoScraper(BaseScraper):
    """Scraper for Wells Fargo credit cards."""
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False):
        super().__init__("Wells Fargo", use_cache=use_cache, offline_mode=offline_mode)
        self.issuer = CardIssuer(
            name="Wells Fargo",
            website_url="https://www.wellsfargo.com",
            support_contact="1-800-869-3557"
        )
        self.reward_program = RewardProgram(
            id="WELLS_FARGO_POINTS",
            name="Wells Fargo Rewards",
            base_point_value_cents=0.01,
            notes="Points redeemable for cash, travel, or gift cards"
        )
    
    def scrape_cards(self) -> List[CardProduct]:
        """
        Scrape Wells Fargo cards.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        cards = [
            CardProduct(
                id="wells_fargo_active_cash",
                issuer=self.issuer,
                name="Wells Fargo Active Cash",
                network=CardNetwork.VISA,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.03,
                reward_program=None,
                official_url="https://www.wellsfargo.com/credit-cards/active-cash",
            ),
            CardProduct(
                id="wells_fargo_autograph",
                issuer=self.issuer,
                name="Wells Fargo Autograph",
                network=CardNetwork.VISA,
                type=RewardType.POINTS_PER_DOLLAR,
                annual_fee=0.0,
                foreign_transaction_fee=0.0,
                reward_program=self.reward_program,
                official_url="https://www.wellsfargo.com/credit-cards/autograph",
            ),
        ]
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """
        Scrape earning rules for a Wells Fargo card.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        rules = []
        
        if card.id == "wells_fargo_active_cash":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="All purchases",
                    merchant_categories=[],
                    multiplier=2.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
            ]
        elif card.id == "wells_fargo_autograph":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Restaurants, travel, gas stations, transit, streaming, and phone plans",
                    merchant_categories=["restaurants", "travel", "gas", "transit", "streaming"],
                    multiplier=3.0,
                    reward_type=RewardType.POINTS_PER_DOLLAR,
                ),
                EarningRule(
                    card_id=card.id,
                    description="All other purchases",
                    merchant_categories=[],
                    multiplier=1.0,
                    reward_type=RewardType.POINTS_PER_DOLLAR,
                ),
            ]
        
        return rules

