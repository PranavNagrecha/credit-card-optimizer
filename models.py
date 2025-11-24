"""
Data models for credit card rewards optimization system.

Defines the core data structures for cards, issuers, reward programs,
earning rules, and recommendations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class RewardType(str, Enum):
    """Types of reward structures."""
    CASHBACK_PERCENT = "cashback_percent"
    POINTS_PER_DOLLAR = "points_per_dollar"
    MILES_PER_DOLLAR = "miles_per_dollar"
    HYBRID = "hybrid"


class CardNetwork(str, Enum):
    """Credit card networks."""
    VISA = "visa"
    MASTERCARD = "mastercard"
    AMEX = "amex"
    DISCOVER = "discover"


@dataclass
class CardIssuer:
    """Represents a credit card issuer."""
    name: str
    website_url: str
    support_contact: Optional[str] = None


@dataclass
class RewardProgram:
    """Represents a reward program (points/miles system)."""
    id: str
    name: str
    base_point_value_cents: float
    notes: Optional[str] = None


@dataclass
class Cap:
    """Represents a spending cap or limit on rewards."""
    amount_dollars: float
    period: str  # e.g., "year", "quarter", "month", "lifetime"
    description: Optional[str] = None


@dataclass
class EarningRule:
    """Represents a rule for earning rewards on a card."""
    card_id: str
    description: str
    merchant_categories: List[str] = field(default_factory=list)
    mcc_list: List[str] = field(default_factory=list)
    merchant_names: List[str] = field(default_factory=list)
    multiplier: float = 1.0
    reward_type: RewardType = RewardType.CASHBACK_PERCENT
    caps: List[Cap] = field(default_factory=list)
    stacking_rules: Optional[str] = None
    is_rotating: bool = False
    is_intro_offer_only: bool = False
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


@dataclass
class CardProduct:
    """Represents a credit card product."""
    id: str
    issuer: CardIssuer
    name: str
    network: CardNetwork
    type: RewardType
    annual_fee: float
    foreign_transaction_fee: float
    reward_program: Optional[RewardProgram] = None
    is_business_card: bool = False
    official_url: Optional[str] = None
    terms_url: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class MerchantCategoryMapping:
    """Maps merchant names to normalized categories and MCCs."""
    merchant_name: str
    mcc: Optional[str] = None
    normalized_categories: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)


@dataclass
class CardScore:
    """Computed score for a card recommendation."""
    card: CardProduct
    effective_rate_cents_per_dollar: float
    matching_rule: EarningRule
    explanation: str
    notes: List[str] = field(default_factory=list)


@dataclass
class ComputedRecommendation:
    """Final recommendation result for a merchant query."""
    merchant_query: str
    resolved_categories: List[str]
    candidate_cards: List[CardScore]
    explanation: str

