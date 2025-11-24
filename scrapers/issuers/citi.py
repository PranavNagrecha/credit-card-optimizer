"""
Citi credit card scraper.

This is a template/placeholder implementation. In production, you would
parse actual Citi website HTML to extract card details and earning rules.
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


class CitiScraper(BaseScraper):
    """Scraper for Citi credit cards."""
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False):
        super().__init__("Citi", use_cache=use_cache, offline_mode=offline_mode)
        self.issuer = CardIssuer(
            name="Citi",
            website_url="https://www.citi.com",
            support_contact="1-800-374-9700"
        )
        self.reward_program = RewardProgram(
            id="CITI_TY",
            name="ThankYou Points",
            base_point_value_cents=0.015,
            notes="Transferable to travel partners"
        )
    
    def scrape_cards(self) -> List[CardProduct]:
        """
        Scrape Citi cards.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        cards = [
            CardProduct(
                id="citi_premier",
                issuer=self.issuer,
                name="Citi Premier Card",
                network=CardNetwork.MASTERCARD,
                type=RewardType.POINTS_PER_DOLLAR,
                annual_fee=95.0,
                foreign_transaction_fee=0.0,
                reward_program=self.reward_program,
                official_url="https://www.citi.com/credit-cards/citi-premier-card",
                metadata={"signup_bonus": "60000"}
            ),
            CardProduct(
                id="citi_double_cash",
                issuer=self.issuer,
                name="Citi Double Cash",
                network=CardNetwork.MASTERCARD,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.03,
                reward_program=None,
                official_url="https://www.citi.com/credit-cards/citi-double-cash-card",
            ),
            CardProduct(
                id="citi_custom_cash",
                issuer=self.issuer,
                name="Citi Custom Cash",
                network=CardNetwork.VISA,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.03,
                reward_program=None,
                official_url="https://www.citi.com/credit-cards/citi-custom-cash-card",
            ),
        ]
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """
        Scrape earning rules for a Citi card.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        rules = []
        
        if card.id == "citi_premier":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Restaurants",
                    merchant_categories=["restaurants"],
                    multiplier=3.0,
                    reward_type=RewardType.POINTS_PER_DOLLAR,
                ),
                EarningRule(
                    card_id=card.id,
                    description="Supermarkets",
                    merchant_categories=["groceries"],
                    multiplier=3.0,
                    reward_type=RewardType.POINTS_PER_DOLLAR,
                ),
                EarningRule(
                    card_id=card.id,
                    description="Gas stations",
                    merchant_categories=["gas"],
                    multiplier=3.0,
                    reward_type=RewardType.POINTS_PER_DOLLAR,
                ),
                EarningRule(
                    card_id=card.id,
                    description="Hotels and air travel",
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
        elif card.id == "citi_double_cash":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="All purchases",
                    merchant_categories=[],
                    multiplier=2.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
            ]
        elif card.id == "citi_custom_cash":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Top spending category each billing cycle",
                    merchant_categories=["groceries", "gas", "restaurants", "travel", "drugstore"],
                    multiplier=5.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                    caps=[Cap(amount_dollars=500.0, period="month")],
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

