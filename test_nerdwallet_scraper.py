"""
Test script for NerdWallet scraper.
Tests card discovery, parsing, and earning rules extraction.
"""

import logging
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from scrapers.issuers.nerdwallet_scraper import NerdWalletScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_single_card(url: str):
    """Test parsing a single card page."""
    print(f"\n{'='*60}")
    print(f"Testing: {url}")
    print(f"{'='*60}")
    
    scraper = NerdWalletScraper(use_cache=True, offline_mode=False)
    
    try:
        # Parse card
        card = scraper._parse_card_page(url)
        if not card:
            print("❌ Failed to parse card")
            return False
        
        print(f"✅ Card Name: {card.name}")
        print(f"   Annual Fee: ${card.annual_fee}")
        print(f"   Issuer: {card.issuer.name}")
        print(f"   Network: {card.network.value}")
        print(f"   Reward Type: {card.type.value}")
        if card.reward_program:
            print(f"   Reward Program: {card.reward_program.name}")
        
        # Parse earning rules
        rules = scraper._parse_earning_rules(url, card)
        print(f"\n   Earning Rules: {len(rules)}")
        for i, rule in enumerate(rules[:5], 1):
            categories = rule.merchant_categories if rule.merchant_categories else ["all purchases"]
            caps_str = f" (cap: ${rule.caps[0].amount_dollars}/{rule.caps[0].period})" if rule.caps else ""
            rotating = " [ROTATING]" if rule.is_rotating else ""
            print(f"   {i}. {rule.multiplier}x on {', '.join(categories)}{caps_str}{rotating}")
            if rule.description:
                desc = rule.description[:80].replace('\n', ' ')
                print(f"      {desc}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_cards():
    """Test parsing multiple popular cards."""
    test_cards = [
        "https://www.nerdwallet.com/reviews/credit-cards/chase-sapphire-preferred",
        "https://www.nerdwallet.com/reviews/credit-cards/chase-sapphire-reserve",
        "https://www.nerdwallet.com/reviews/credit-cards/american-express-gold-card",
        "https://www.nerdwallet.com/reviews/credit-cards/citi-premier-card",
        "https://www.nerdwallet.com/reviews/credit-cards/capital-one-venture-x",
    ]
    
    print(f"\n{'='*60}")
    print(f"Testing {len(test_cards)} Popular Cards")
    print(f"{'='*60}\n")
    
    results = []
    for url in test_cards:
        success = test_single_card(url)
        results.append((url, success))
        print()  # Blank line between cards
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    successful = sum(1 for _, success in results if success)
    print(f"✅ Successfully parsed: {successful}/{len(results)} cards")
    if successful < len(results):
        print("\nFailed cards:")
        for url, success in results:
            if not success:
                print(f"  ❌ {url}")

def test_url_discovery():
    """Test URL discovery."""
    print(f"\n{'='*60}")
    print("Testing URL Discovery")
    print(f"{'='*60}\n")
    
    scraper = NerdWalletScraper(use_cache=True, offline_mode=False)
    
    try:
        urls = scraper._discover_card_urls()
        print(f"✅ Discovered {len(urls)} card URLs")
        
        if urls:
            print(f"\nSample URLs (first 10):")
            for i, url in enumerate(urls[:10], 1):
                print(f"  {i}. {url}")
        else:
            print("⚠️  No URLs discovered - will use fallback list")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_full_scrape():
    """Test the full scrape_cards() method."""
    print(f"\n{'='*60}")
    print("Testing Full Scrape (Limited to 3 cards for testing)")
    print(f"{'='*60}\n")
    
    scraper = NerdWalletScraper(use_cache=True, offline_mode=False)
    
    # Override _discover_card_urls to limit for testing
    original_discover = scraper._discover_card_urls
    def limited_discover():
        urls = original_discover()
        if not urls:
            # Use fallback URLs
            return [
                "https://www.nerdwallet.com/reviews/credit-cards/chase-sapphire-preferred",
                "https://www.nerdwallet.com/reviews/credit-cards/american-express-gold-card",
                "https://www.nerdwallet.com/reviews/credit-cards/citi-premier-card",
            ]
        return urls[:3]  # Limit to 3 for testing
    
    scraper._discover_card_urls = limited_discover
    
    try:
        cards = scraper.scrape_cards()
        print(f"✅ Scraped {len(cards)} cards\n")
        
        for card in cards:
            print(f"  - {card.name} (${card.annual_fee}, {card.issuer.name})")
            rules = scraper.scrape_earning_rules(card)
            print(f"    Rules: {len(rules)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("NerdWallet Scraper Test Suite")
    print("=" * 60)
    
    # Test 1: Single card parsing
    test_single_card("https://www.nerdwallet.com/reviews/credit-cards/chase-sapphire-preferred")
    
    # Test 2: Multiple cards
    test_multiple_cards()
    
    # Test 3: URL discovery
    test_url_discovery()
    
    # Test 4: Full scrape (limited)
    test_full_scrape()
    
    print(f"\n{'='*60}")
    print("Test Suite Complete")
    print(f"{'='*60}")

