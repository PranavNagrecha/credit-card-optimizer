"""
U.S. Bank credit card scraper.

This is a template/placeholder implementation. In production, you would
parse actual U.S. Bank website HTML to extract card details and earning rules.
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


class USBankScraper(BaseScraper):
    """Scraper for U.S. Bank credit cards."""
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False):
        super().__init__("U.S. Bank", use_cache=use_cache, offline_mode=offline_mode)
        self.issuer = CardIssuer(
            name="U.S. Bank",
            website_url="https://www.usbank.com",
            support_contact="1-800-872-2657"
        )
        self.reward_program = RewardProgram(
            id="USBANK_POINTS",
            name="U.S. Bank Points",
            base_point_value_cents=0.012,
            notes="Points redeemable for travel, cash, or gift cards"
        )
    
    def scrape_cards(self) -> List[CardProduct]:
        """
        Scrape U.S. Bank cards.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        cards = [
            CardProduct(
                id="usbank_altitude_reserve",
                issuer=self.issuer,
                name="U.S. Bank Altitude Reserve Visa Infinite",
                network=CardNetwork.VISA,
                type=RewardType.POINTS_PER_DOLLAR,
                annual_fee=400.0,
                foreign_transaction_fee=0.0,
                reward_program=self.reward_program,
                official_url="https://www.usbank.com/credit-cards/altitude-reserve-visa-infinite-card.html",
                metadata={"signup_bonus": "50000"}
            ),
            CardProduct(
                id="usbank_cash_plus",
                issuer=self.issuer,
                name="U.S. Bank Cash+ Visa",
                network=CardNetwork.VISA,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.03,
                reward_program=None,
                official_url="https://www.usbank.com/credit-cards/cash-plus-visa-signature.html",
            ),
        ]
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """
        Scrape earning rules for a U.S. Bank card.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        rules = []
        
        if card.id == "usbank_altitude_reserve":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Mobile wallet purchases",
                    merchant_categories=[],
                    multiplier=3.0,
                    reward_type=RewardType.POINTS_PER_DOLLAR,
                    stacking_rules="Must use mobile wallet (Apple Pay, Google Pay, Samsung Pay)",
                ),
                EarningRule(
                    card_id=card.id,
                    description="Travel purchases",
                    merchant_categories=["travel"],
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
        elif card.id == "usbank_cash_plus":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Two 5% categories of choice",
                    merchant_categories=["groceries", "gas", "restaurants", "department_store", "furniture", "gym", "movie_theater"],
                    multiplier=5.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                    caps=[Cap(amount_dollars=2000.0, period="quarter")],
                ),
                EarningRule(
                    card_id=card.id,
                    description="One 2% category of choice",
                    merchant_categories=["groceries", "gas", "restaurants"],
                    multiplier=2.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
                EarningRule(
                    card_id=card.id,
                    description="All other purchases",
                    merchant_categories=[],
                    multiplier=1.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
            ]
        
        return rules

