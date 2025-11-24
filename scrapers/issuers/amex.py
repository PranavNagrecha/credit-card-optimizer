"""
American Express credit card scraper.

This is a template/placeholder implementation. In production, you would
parse actual Amex website HTML to extract card details and earning rules.
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


class AmexScraper(BaseScraper):
    """Scraper for American Express credit cards."""
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False):
        super().__init__("American Express", use_cache=use_cache, offline_mode=offline_mode)
        self.issuer = CardIssuer(
            name="American Express",
            website_url="https://www.americanexpress.com",
            support_contact="1-800-528-4800"
        )
        self.reward_program = RewardProgram(
            id="AMEX_MR",
            name="Membership Rewards",
            base_point_value_cents=0.017,
            notes="Transferable to travel partners"
        )
    
    def scrape_cards(self) -> List[CardProduct]:
        """
        Scrape American Express cards.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        cards = [
            CardProduct(
                id="amex_gold",
                issuer=self.issuer,
                name="American Express Gold Card",
                network=CardNetwork.AMEX,
                type=RewardType.POINTS_PER_DOLLAR,
                annual_fee=250.0,
                foreign_transaction_fee=0.0,
                reward_program=self.reward_program,
                official_url="https://www.americanexpress.com/us/credit-cards/card/gold-card",
                metadata={"signup_bonus": "60000"}
            ),
            CardProduct(
                id="amex_blue_cash_everyday",
                issuer=self.issuer,
                name="Blue Cash Everyday",
                network=CardNetwork.AMEX,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.027,
                reward_program=None,
                official_url="https://www.americanexpress.com/us/credit-cards/card/blue-cash-everyday",
            ),
        ]
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """
        Scrape earning rules for an Amex card.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        rules = []
        
        if card.id == "amex_gold":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Dining at restaurants worldwide",
                    merchant_categories=["restaurants"],
                    multiplier=4.0,
                    reward_type=RewardType.POINTS_PER_DOLLAR,
                ),
                EarningRule(
                    card_id=card.id,
                    description="U.S. supermarkets",
                    merchant_categories=["groceries"],
                    multiplier=4.0,
                    reward_type=RewardType.POINTS_PER_DOLLAR,
                    caps=[],
                ),
                EarningRule(
                    card_id=card.id,
                    description="All other purchases",
                    merchant_categories=[],
                    multiplier=1.0,
                    reward_type=RewardType.POINTS_PER_DOLLAR,
                ),
            ]
        elif card.id == "amex_blue_cash_everyday":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="U.S. supermarkets",
                    merchant_categories=["groceries"],
                    multiplier=3.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                    caps=[],
                ),
                EarningRule(
                    card_id=card.id,
                    description="U.S. gas stations",
                    merchant_categories=["gas"],
                    multiplier=3.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
                EarningRule(
                    card_id=card.id,
                    description="Online retail purchases",
                    merchant_categories=["online_shopping"],
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
        
        return rules

