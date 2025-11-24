"""
Background scraper job that runs periodically to refresh card data.

This should be run as a scheduled task (cron, systemd timer, etc.) or
as a background service.
"""

import logging
import sys
from pathlib import Path

# Import helper to setup paths correctly
try:
    import import_helper
except ImportError:
    # If import_helper doesn't exist, setup manually
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    current_dir = str(Path(__file__).parent)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

# Setup for relative imports to work
# We need to ensure the current directory is treated as a package root
# This allows scrapers to use "from ...models" successfully
import os
current_package_root = os.path.dirname(os.path.abspath(__file__))
if current_package_root not in sys.path:
    sys.path.insert(0, current_package_root)

# Try package imports first (for local development)
try:
    from credit_card_optimizer.config import OFFLINE_MODE, USE_CACHE
    from credit_card_optimizer.data_manager import DataManager
    from credit_card_optimizer.scrapers.issuers.amex_manual import AmexScraper
    from credit_card_optimizer.scrapers.issuers.bank_of_america_manual import BankOfAmericaScraper
    from credit_card_optimizer.scrapers.issuers.barclays_manual import BarclaysScraper
    from credit_card_optimizer.scrapers.issuers.capital_one_manual import CapitalOneScraper
    from credit_card_optimizer.scrapers.issuers.chase_manual import ChaseScraper
    from credit_card_optimizer.scrapers.issuers.citi_manual import CitiScraper
    from credit_card_optimizer.scrapers.issuers.co_branded_manual import CoBrandedScraper
    from credit_card_optimizer.scrapers.issuers.discover_manual import DiscoverScraper
    from credit_card_optimizer.scrapers.issuers.us_bank_manual import USBankScraper
    from credit_card_optimizer.scrapers.issuers.wells_fargo_manual import WellsFargoScraper
    from credit_card_optimizer.scrapers.issuers.apple_manual import AppleScraper
    from credit_card_optimizer.scrapers.issuers.airline_cards_manual import AirlineCardsScraper
    from credit_card_optimizer.scrapers.issuers.premium_cards_manual import PremiumCardsScraper
except ImportError:
    # Fallback: direct imports (for Render's flat structure)
    # The scrapers will use relative imports (from ...models) which should work
    # because we've set up sys.path correctly above
    from config import OFFLINE_MODE, USE_CACHE
    from data_manager import DataManager
    from scrapers.issuers.amex_manual import AmexScraper
    from scrapers.issuers.bank_of_america_manual import BankOfAmericaScraper
    from scrapers.issuers.barclays_manual import BarclaysScraper
    from scrapers.issuers.capital_one_manual import CapitalOneScraper
    from scrapers.issuers.chase_manual import ChaseScraper
    from scrapers.issuers.citi_manual import CitiScraper
    from scrapers.issuers.co_branded_manual import CoBrandedScraper
    from scrapers.issuers.discover_manual import DiscoverScraper
    from scrapers.issuers.us_bank_manual import USBankScraper
    from scrapers.issuers.wells_fargo_manual import WellsFargoScraper
    from scrapers.issuers.apple_manual import AppleScraper
    from scrapers.issuers.airline_cards_manual import AirlineCardsScraper
    from scrapers.issuers.premium_cards_manual import PremiumCardsScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_all_cards_and_rules():
    """
    Scrape all cards and rules from all issuers and save to disk.
    
    This function should be called periodically (e.g., once per day)
    to refresh the card data.
    """
    logger.info("Starting card and rule scraping job...")
    
    data_manager = DataManager()
    all_cards = []
    all_rules = []
    
    # Primary scraper: NerdWallet (aggregates all cards)
    # Fallback scrapers: Individual issuer scrapers (for cards not on NerdWallet)
    scrapers = []
    
    # Use NerdWallet as primary source (scrapes all cards from one place)
    try:
        from credit_card_optimizer.scrapers.issuers.nerdwallet_scraper import NerdWalletScraper
        scrapers.append(NerdWalletScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE))
        logger.info("✅ Using NerdWallet as primary data source (scrapes all cards)")
    except ImportError:
        try:
            from scrapers.issuers.nerdwallet_scraper import NerdWalletScraper
            scrapers.append(NerdWalletScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE))
            logger.info("✅ Using NerdWallet as primary data source (scrapes all cards)")
        except ImportError as e:
            logger.warning(f"NerdWallet scraper not available ({e}), using individual scrapers as fallback")
            # Fallback to individual scrapers
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
                AppleScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
                AirlineCardsScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
                PremiumCardsScraper(use_cache=USE_CACHE, offline_mode=OFFLINE_MODE),
            ]
    
    for scraper in scrapers:
        try:
            logger.info(f"Scraping {scraper.issuer_name}...")
            cards = scraper.scrape_cards()
            all_cards.extend(cards)
            logger.info(f"  Found {len(cards)} cards")
            
            for card in cards:
                try:
                    rules = scraper.scrape_earning_rules(card)
                    all_rules.extend(rules)
                except Exception as e:
                    logger.warning(f"  Failed to get rules for {card.name}: {e}")
        except Exception as e:
            logger.error(f"Failed to scrape {scraper.issuer_name}: {e}", exc_info=True)
    
    # Save to disk (save even if we didn't get all cards - partial data is better than no data)
    try:
        if all_cards or all_rules:
            data_manager.save_cards_and_rules(all_cards, all_rules)
            logger.info(f"✅ Successfully scraped and saved {len(all_cards)} cards and {len(all_rules)} rules")
            return True
        else:
            logger.warning("⚠️  No cards or rules scraped - nothing to save")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to save data: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = scrape_all_cards_and_rules()
    sys.exit(0 if success else 1)

