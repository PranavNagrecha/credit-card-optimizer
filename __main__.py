"""
CLI entry point for credit card optimization.

Usage:
    python -m credit_card_optimizer "Macy's"
    python -m credit_card_optimizer "groceries"
    python -m credit_card_optimizer "Amazon"
"""

import logging
import sys
from typing import List

from .config import OFFLINE_MODE, USE_CACHE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from .config import MAX_RECOMMENDATIONS
from .engine import find_best_cards_for_query
from .models import CardProduct, EarningRule
from .scrapers.issuers.amex_manual import AmexScraper
from .scrapers.issuers.bank_of_america_manual import BankOfAmericaScraper
from .scrapers.issuers.barclays_manual import BarclaysScraper
from .scrapers.issuers.capital_one_manual import CapitalOneScraper
from .scrapers.issuers.chase_manual import ChaseScraper
from .scrapers.issuers.citi_manual import CitiScraper
from .scrapers.issuers.co_branded_manual import CoBrandedScraper
from .scrapers.issuers.discover_manual import DiscoverScraper
from .scrapers.issuers.us_bank_manual import USBankScraper
from .scrapers.issuers.wells_fargo_manual import WellsFargoScraper


def load_all_cards_and_rules() -> tuple[List[CardProduct], List[EarningRule]]:
    """
    Load all cards and earning rules from scrapers.
    
    Returns:
        Tuple of (all_cards, all_rules)
    """
    all_cards: List[CardProduct] = []
    all_rules: List[EarningRule] = []
    
    # Initialize all scrapers for major US issuers
    # Pass cache/offline settings to scrapers
    scrapers = [
        ChaseScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
        AmexScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
        CitiScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
        CapitalOneScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
        BankOfAmericaScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
        DiscoverScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
        USBankScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
        WellsFargoScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
        BarclaysScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
        CoBrandedScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
    ]
    
    # Scrape cards and rules
    for scraper in scrapers:
        try:
            cards = scraper.scrape_cards()
            all_cards.extend(cards)
            
            for card in cards:
                try:
                    rules = scraper.scrape_earning_rules(card)
                    all_rules.extend(rules)
                except Exception as e:
                    print(f"Warning: Failed to get rules for {card.name}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Failed to scrape {scraper.issuer_name}: {e}", file=sys.stderr)
    
    return all_cards, all_rules


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m credit_card_optimizer <merchant_or_category>")
        print("Examples:")
        print("  python -m credit_card_optimizer \"Macy's\"")
        print("  python -m credit_card_optimizer \"groceries\"")
        print("  python -m credit_card_optimizer \"Amazon\"")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    print(f"Loading cards and rules...")
    all_cards, all_rules = load_all_cards_and_rules()
    print(f"Loaded {len(all_cards)} cards with {len(all_rules)} earning rules\n")
    
    print(f"Finding best cards for: {query}\n")
    recommendation = find_best_cards_for_query(
        query=query,
        all_cards=all_cards,
        all_rules=all_rules,
        max_results=MAX_RECOMMENDATIONS
    )
    
    # Print results
    print("=" * 80)
    print(f"Query: {recommendation.merchant_query}")
    print(f"Resolved Categories: {', '.join(recommendation.resolved_categories)}")
    print("=" * 80)
    print()
    print(recommendation.explanation)
    print()
    
    if recommendation.candidate_cards:
        print("Top Recommendations:")
        print("-" * 80)
        for i, card_score in enumerate(recommendation.candidate_cards, 1):
            print(f"\n{i}. {card_score.card.name}")
            print(f"   Issuer: {card_score.card.issuer.name}")
            # effective_rate_cents_per_dollar is already in percentage
            effective_rate = card_score.effective_rate_cents_per_dollar
            print(f"   Effective Rate: {effective_rate:.2f}%")
            print(f"   Annual Fee: ${card_score.card.annual_fee:.2f}")
            print(f"   Explanation: {card_score.explanation}")
            if card_score.notes:
                print(f"   Notes:")
                for note in card_score.notes:
                    print(f"     - {note}")
            if card_score.card.official_url:
                print(f"   URL: {card_score.card.official_url}")
    else:
        print("No specific recommendations found.")
        print("Consider using a flat-rate cashback card (e.g., 2% on all purchases).")


if __name__ == "__main__":
    main()

