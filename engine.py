"""
Recommendation engine for credit card optimization.

Resolves merchant queries, matches earning rules, computes scores,
and generates recommendations.
"""

from typing import List

from models import (
    CardProduct,
    CardScore,
    ComputedRecommendation,
    EarningRule,
    RewardType,
)
from normalization import (
    get_categories_for_mcc,
    match_categories,
    resolve_merchant_query,
)
from valuation import apply_cap_penalty, compute_effective_rate, get_point_value


def find_best_cards_for_query(
    query: str,
    all_cards: List[CardProduct],
    all_rules: List[EarningRule],
    max_results: int = 5
) -> ComputedRecommendation:
    """
    Find the best credit cards for a given merchant/category query.
    
    Args:
        query: User query (merchant name or category)
        all_cards: List of all available cards
        all_rules: List of all earning rules
        max_results: Maximum number of recommendations to return
        
    Returns:
        ComputedRecommendation with ranked cards
    """
    # Resolve query to categories
    merchant_mapping = resolve_merchant_query(query)
    resolved_categories = merchant_mapping.normalized_categories
    
    # Add categories from MCC if available
    if merchant_mapping.mcc:
        mcc_categories = get_categories_for_mcc(merchant_mapping.mcc)
        resolved_categories.extend(mcc_categories)
    
    # Remove duplicates
    resolved_categories = list(set(resolved_categories))
    
    # Build card_id -> card mapping
    card_dict = {card.id: card for card in all_cards}
    
    # Find matching rules
    candidate_scores: List[CardScore] = []
    
    for rule in all_rules:
        # Skip if card not found
        if rule.card_id not in card_dict:
            continue
        
        card = card_dict[rule.card_id]
        
        # Skip business cards for now (unless explicitly requested)
        if card.is_business_card:
            continue
        
        # Check category match
        category_match = match_categories(rule.merchant_categories, resolved_categories)
        
        # Check MCC match
        mcc_match = (
            merchant_mapping.mcc and
            merchant_mapping.mcc in rule.mcc_list
        )
        
        # Check merchant name match
        merchant_match = (
            merchant_mapping.merchant_name and
            any(
                merchant.lower() in merchant_mapping.merchant_name.lower() or
                merchant_mapping.merchant_name.lower() in merchant.lower()
                for merchant in rule.merchant_names
            )
        )
        
        if not (category_match or mcc_match or merchant_match):
            continue
        
        # Compute effective rate
        effective_rate = compute_effective_rate(rule, card.reward_program)
        
        # Determine base rate after cap (usually 1% or 1x)
        base_rate = 1.0
        if card.reward_program:
            base_rate = get_point_value(card.reward_program)
        elif card.type == RewardType.CASHBACK_PERCENT:
            base_rate = 1.0  # 1% cashback after cap
        
        # Apply cap penalties - this now actually reduces the rate
        adjusted_rate, cap_notes = apply_cap_penalty(
            effective_rate, 
            rule.caps, 
            spending_amount=0.0,  # TODO: Allow user to specify expected spending
            base_rate=base_rate
        )
        
        # Build explanation
        reward_type_desc = {
            "cashback_percent": f"{rule.multiplier}% cashback",
            "points_per_dollar": f"{rule.multiplier}x points",
            "miles_per_dollar": f"{rule.multiplier}x miles",
            "hybrid": f"{rule.multiplier}x rewards",
        }.get(rule.reward_type.value, f"{rule.multiplier}x")
        
        # Convert cents per dollar to percentage for display
        effective_percent = adjusted_rate  # adjusted_rate is already in cents per dollar (e.g., 5.1 = 5.1%)
        
        explanation = (
            f"{card.name} offers {reward_type_desc} "
            f"({effective_percent:.2f}% effective value) for {rule.description}"
        )
        
        # Add notes
        notes = cap_notes.copy()
        if rule.is_rotating:
            notes.append("Rotating category - may require activation")
        if rule.is_intro_offer_only:
            notes.append("Introductory offer - limited time")
        if rule.stacking_rules:
            notes.append(f"Note: {rule.stacking_rules}")
        
        candidate_scores.append(
            CardScore(
                card=card,
                effective_rate_cents_per_dollar=adjusted_rate,
                matching_rule=rule,
                explanation=explanation,
                notes=notes
            )
        )
    
    # Sort by effective rate (descending)
    candidate_scores.sort(
        key=lambda x: x.effective_rate_cents_per_dollar,
        reverse=True
    )
    
    # Take top N
    top_cards = candidate_scores[:max_results]
    
    # Generate overall explanation
    if not top_cards:
        overall_explanation = (
            f"No specific rewards found for '{query}'. "
            f"Consider cards with flat-rate rewards."
        )
    else:
        best_card = top_cards[0]
        # effective_rate_cents_per_dollar is already in percentage (cents = percent)
        best_rate = best_card.effective_rate_cents_per_dollar
        overall_explanation = (
            f"For {query} ({', '.join(resolved_categories)}), "
            f"{best_card.card.name} offers the best value at "
            f"{best_rate:.2f}% effective return. "
        )
        if len(top_cards) > 1:
            second_rate = top_cards[1].effective_rate_cents_per_dollar
            overall_explanation += (
                f"Other options include {top_cards[1].card.name} "
                f"({second_rate:.2f}%)."
            )
    
    return ComputedRecommendation(
        merchant_query=query,
        resolved_categories=resolved_categories,
        candidate_cards=top_cards,
        explanation=overall_explanation
    )

