"""
Co-branded credit card scraper.

Handles major co-branded cards (Amazon, Costco, Target, etc.) that are
issued by major banks but have specific merchant rewards.

This is a template/placeholder implementation. In production, you would
parse actual issuer websites to extract card details and earning rules.
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


class CoBrandedScraper(BaseScraper):
    """Scraper for co-branded credit cards."""
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False):
        super().__init__("Co-Branded Cards", use_cache=use_cache, offline_mode=offline_mode)
    
    def scrape_cards(self) -> List[CardProduct]:
        """
        Scrape co-branded cards.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        cards = [
            # Amazon cards (issued by Chase)
            CardProduct(
                id="amazon_prime_visa",
                issuer=CardIssuer(name="Chase", website_url="https://www.chase.com"),
                name="Amazon Prime Rewards Visa Signature",
                network=CardNetwork.VISA,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.03,
                reward_program=None,
                official_url="https://www.amazon.com/Amazon-Prime-Rewards-Visa-Signature-Card",
                metadata={"requires_prime": True}
            ),
            CardProduct(
                id="amazon_visa",
                issuer=CardIssuer(name="Chase", website_url="https://www.chase.com"),
                name="Amazon Rewards Visa Signature",
                network=CardNetwork.VISA,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.03,
                reward_program=None,
                official_url="https://www.amazon.com/Amazon-Rewards-Visa-Signature-Card",
            ),
            # Costco card (issued by Citi)
            CardProduct(
                id="costco_anywhere",
                issuer=CardIssuer(name="Citi", website_url="https://www.citi.com"),
                name="Costco Anywhere Visa",
                network=CardNetwork.VISA,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.0,
                reward_program=None,
                official_url="https://www.citi.com/credit-cards/costco-anywhere-visa-card",
                metadata={"requires_costco_membership": True}
            ),
            # Target card (issued by TD Bank)
            CardProduct(
                id="target_redcard",
                issuer=CardIssuer(name="TD Bank", website_url="https://www.td.com"),
                name="Target RedCard",
                network=CardNetwork.MASTERCARD,
                type=RewardType.CASHBACK_PERCENT,
                annual_fee=0.0,
                foreign_transaction_fee=0.03,
                reward_program=None,
                official_url="https://www.target.com/redcard",
            ),
        ]
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """
        Scrape earning rules for a co-branded card.
        
        NOTE: This is a mocked implementation. Replace with actual
        HTML parsing logic for production use.
        """
        rules = []
        
        if card.id == "amazon_prime_visa":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Amazon.com and Whole Foods Market",
                    merchant_names=["Amazon", "Whole Foods", "Whole Foods Market"],
                    merchant_categories=["online_shopping", "groceries"],
                    multiplier=5.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
                EarningRule(
                    card_id=card.id,
                    description="Restaurants, gas stations, and drugstores",
                    merchant_categories=["restaurants", "gas", "pharmacy"],
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
        elif card.id == "amazon_visa":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Amazon.com purchases",
                    merchant_names=["Amazon"],
                    merchant_categories=["online_shopping"],
                    multiplier=3.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
                EarningRule(
                    card_id=card.id,
                    description="Restaurants, gas stations, and drugstores",
                    merchant_categories=["restaurants", "gas", "pharmacy"],
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
        elif card.id == "costco_anywhere":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Costco and Costco.com",
                    merchant_names=["Costco"],
                    merchant_categories=["wholesale", "groceries"],
                    multiplier=2.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
                EarningRule(
                    card_id=card.id,
                    description="Restaurants and eligible travel",
                    merchant_categories=["restaurants", "travel"],
                    multiplier=3.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
                EarningRule(
                    card_id=card.id,
                    description="Gas stations (first $7,000 per year, then 1%)",
                    merchant_categories=["gas"],
                    multiplier=4.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                    caps=[Cap(amount_dollars=7000.0, period="year")],
                ),
                EarningRule(
                    card_id=card.id,
                    description="All other purchases",
                    merchant_categories=[],
                    multiplier=1.0,
                    reward_type=RewardType.CASHBACK_PERCENT,
                ),
            ]
        elif card.id == "target_redcard":
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="Target and Target.com purchases",
                    merchant_names=["Target"],
                    merchant_categories=["general_merchandise", "groceries"],
                    multiplier=5.0,
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

