"""
Reward valuation logic.

Converts all reward types (cashback, points, miles) to a standardized
"cents per dollar" value for comparison.
"""

from typing import Optional

from .config import POINT_VALUES
from .models import EarningRule, RewardProgram, RewardType


def get_point_value(reward_program: Optional[RewardProgram]) -> float:
    """
    Get the point value in cents for a reward program.
    
    Args:
        reward_program: RewardProgram object or None
        
    Returns:
        Cents per point/mile
    """
    if not reward_program:
        return POINT_VALUES["DEFAULT"]
    
    # Map program name to valuation
    program_id_upper = reward_program.id.upper()
    return POINT_VALUES.get(program_id_upper, reward_program.base_point_value_cents)


def compute_effective_rate(
    earning_rule: EarningRule,
    reward_program: Optional[RewardProgram]
) -> float:
    """
    Compute the effective reward rate in cents per dollar.
    
    Args:
        earning_rule: The earning rule to evaluate
        reward_program: Associated reward program (if applicable)
        
    Returns:
        Effective cents per dollar spent
    """
    if earning_rule.reward_type == RewardType.CASHBACK_PERCENT:
        # Cashback: multiplier is already a percentage
        return earning_rule.multiplier
    
    elif earning_rule.reward_type == RewardType.POINTS_PER_DOLLAR:
        # Points: multiplier points per dollar * point value
        point_value = get_point_value(reward_program)
        return earning_rule.multiplier * point_value
    
    elif earning_rule.reward_type == RewardType.MILES_PER_DOLLAR:
        # Miles: similar to points, but may have different valuation
        point_value = get_point_value(reward_program)
        return earning_rule.multiplier * point_value
    
    elif earning_rule.reward_type == RewardType.HYBRID:
        # Hybrid: use reward program valuation if available
        point_value = get_point_value(reward_program)
        return earning_rule.multiplier * point_value
    
    # Default fallback
    return earning_rule.multiplier * POINT_VALUES["DEFAULT"]


def apply_cap_penalty(
    effective_rate: float,
    caps: list,
    spending_amount: float = 0.0,
    base_rate: float = 1.0
) -> tuple[float, list[str]]:
    """
    Adjust effective rate based on spending caps.
    
    Computes a blended rate when caps apply: high rate up to cap, then base rate after.
    If spending_amount is 0, assumes user will hit cap and returns blended rate.
    
    Args:
        effective_rate: Base effective rate (cents per dollar, e.g., 5.0 = 5%)
        caps: List of Cap objects
        spending_amount: User's expected spending (0 = assume cap will be hit)
        base_rate: Rate after cap is exceeded (default 1.0 = 1%)
        
    Returns:
        Tuple of (adjusted_rate, notes)
    """
    notes = []
    
    if not caps:
        return effective_rate, notes
    
    # Use the first cap (most restrictive)
    cap = caps[0]
    cap_amount = cap.amount_dollars
    
    if spending_amount == 0.0:
        # Assume spending will exceed cap - compute blended rate
        # Assume user spends 2x the cap amount (half at high rate, half at base)
        assumed_spend = cap_amount * 2
        high_rate_earnings = cap_amount * effective_rate
        remaining_spend = assumed_spend - cap_amount
        base_rate_earnings = remaining_spend * base_rate
        blended_rate = (high_rate_earnings + base_rate_earnings) / assumed_spend
        
        notes.append(
            f"Spending cap: ${cap_amount:,.0f}/{cap.period}. "
            f"Blended rate: {blended_rate:.2f}% (assumes spending exceeds cap)"
        )
        return blended_rate, notes
    elif spending_amount > cap_amount:
        # User exceeds cap - compute actual blended rate
        high_rate_earnings = cap_amount * effective_rate
        remaining_spend = spending_amount - cap_amount
        base_rate_earnings = remaining_spend * base_rate
        blended_rate = (high_rate_earnings + base_rate_earnings) / spending_amount
        
        notes.append(
            f"Spending cap of ${cap_amount:,.0f}/{cap.period} exceeded. "
            f"Blended rate: {blended_rate:.2f}%"
        )
        return blended_rate, notes
    else:
        # User within cap - rate applies fully
        notes.append(
            f"Spending cap: ${cap_amount:,.0f}/{cap.period} (within limit)"
        )
        return effective_rate, notes

