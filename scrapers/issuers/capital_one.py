"""
Capital One credit card scraper.

This is a template/placeholder implementation. In production, you would
parse actual Capital One website HTML to extract card details and earning rules.
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


class CapitalOneScraper(BaseScraper):
    """Scraper for Capital One credit cards."""
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False):
        super().__init__("Capital One", use_cache=use_cache, offline_mode=offline_mode)
        self.issuer = CardIssuer(
            name="Capital One",
            website_url="https://www.capitalone.com",
            support_contact="1-800-955-7070"
        )
        self.reward_program = RewardProgram(
            id="CAPITAL_ONE_MILES",
            name="Capital One Miles",
            base_point_value_cents=0.016,
            notes="Transferable to travel partners or redeemable at 1 cent each"
        )
    
    def scrape_cards(self) -> List[CardProduct]:
        """
        Scrape Capital One cards.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        cards = [
            CardProduct(
                id="capital_one_venture_x",
                issuer=self.issuer,
                name="Capital One Venture X",
                network=CardNetwork.VISA,
                type=RewardType.MILES_PER_DOLLAR,
                annual_fee=395.0,
                foreign_transaction_fee=0.0,
                reward_program=self.reward_program,
                official_url="https://www.capitalone.com/credit-cards/venture-x",
                metadata={"signup_bonus": "75000"}
            ),
            CardProduct(
                id="capital_one_venture",
                issuer=self.issuer,
                name="Capital One Venture",
                network=CardNetwork.VISA,
                type=RewardType.MILES_PER_DOLLAR,
                annual_fee=95.0,
                foreign_transaction_fee=0.0,
                reward_program=self.reward_program,
                official_url="https://www.capitalone.com/credit-cards/venture",
                metadata={"signup_bonus": "60000"}
            ),
            CardProduct(
                id="capital_one_savor_one",
                issuer=self.issuer,
                name="Capital One SavorOne",
                network=CardNetwork.MASTERCARD,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.0,
                reward_program=None,
                official_url="https://www.capitalone.com/credit-cards/savorone",
            ),
            CardProduct(
                id="capital_one_quicksilver",
                issuer=self.issuer,
                name="Capital One Quicksilver",
                network=CardNetwork.MASTERCARD,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.0,
                reward_program=None,
                official_url="https://www.capitalone.com/credit-cards/quicksilver",
            ),
        ]
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """
        Scrape earning rules for a Capital One card.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        rules = []
        
        if card.id == "capital_one_venture_x":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Travel purchases",
                    merchant_categories=["travel"],
                    multiplier=10.0,
                    reward_type=RewardType.MILES_PER_DOLLAR,
                ),
                EarningRule(
                    card_id=card.id,
                    description="Hotels and rental cars booked through Capital One",
                    merchant_categories=["travel"],
                    multiplier=10.0,
                    reward_type=RewardType.MILES_PER_DOLLAR,
                    stacking_rules="Must book through Capital One portal",
                ),
                EarningRule(
                    card_id=card.id,
                    description="All other purchases",
                    merchant_categories=[],
                    multiplier=2.0,
                    reward_type=RewardType.MILES_PER_DOLLAR,
                ),
            ]
        elif card.id == "capital_one_venture":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="All purchases",
                    merchant_categories=[],
                    multiplier=2.0,
                    reward_type=RewardType.MILES_PER_DOLLAR,
                ),
            ]
        elif card.id == "capital_one_savor_one":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Dining, entertainment, and streaming",
                    merchant_categories=["restaurants", "entertainment"],
                    multiplier=3.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
                EarningRule(
                    card_id=card.id,
                    description="Groceries",
                    merchant_categories=["groceries"],
                    multiplier=3.0,
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
        elif card.id == "capital_one_quicksilver":
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

