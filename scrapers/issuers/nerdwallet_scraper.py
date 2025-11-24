"""
NerdWallet credit card scraper - Primary data source.

Scrapes comprehensive credit card data from NerdWallet, which aggregates
and normalizes data from all major issuers. This is more reliable than
scraping individual issuer sites.
"""

import json
import logging
import re
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Handle both package and flat structure imports
try:
    from ...models import (
        CardIssuer,
        CardNetwork,
        CardProduct,
        Cap,
        EarningRule,
        RewardProgram,
        RewardType,
    )
except ImportError:
    # Fallback for flat structure (Render): add parent directories to path
    current_file = Path(__file__).resolve()
    # Go up 3 levels: scrapers/issuers/ -> root
    root_dir = current_file.parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    from models import (
        CardIssuer,
        CardNetwork,
        CardProduct,
        Cap,
        EarningRule,
        RewardProgram,
        RewardType,
    )

from ..base import BaseScraper

logger = logging.getLogger(__name__)


class NerdWalletScraper(BaseScraper):
    """Comprehensive scraper for NerdWallet credit card listings."""
    
    BASE_URL = "https://www.nerdwallet.com"
    CARDS_LIST_URL = "https://www.nerdwallet.com/credit-cards"
    
    # Network mapping
    NETWORK_MAP = {
        "visa": CardNetwork.VISA,
        "mastercard": CardNetwork.MASTERCARD,
        "amex": CardNetwork.AMEX,
        "american express": CardNetwork.AMEX,
        "discover": CardNetwork.DISCOVER,
    }
    
    # Reward type mapping
    REWARD_TYPE_MAP = {
        "cash back": RewardType.CASHBACK_PERCENT,
        "cashback": RewardType.CASHBACK_PERCENT,
        "points": RewardType.POINTS_PER_DOLLAR,
        "miles": RewardType.MILES_PER_DOLLAR,
        "rewards": RewardType.POINTS_PER_DOLLAR,
    }
    
    # Issuer name mapping - ordered by specificity (longer/more specific first)
    ISSUER_MAP = {
        # Full names first (most specific)
        "american express": "American Express",
        "bank of america": "Bank of America",
        "capital one": "Capital One",
        "goldman sachs": "Goldman Sachs",
        "wells fargo": "Wells Fargo",
        "us bank": "U.S. Bank",
        # Abbreviations and variations
        "amex": "American Express",
        "boa": "Bank of America",
        "citibank": "Citi",
        "barclays": "Barclays",
        "barclay": "Barclays",  # Common misspelling
        # Single word issuers
        "chase": "Chase",
        "citi": "Citi",
        "discover": "Discover",
        "apple": "Goldman Sachs",  # Apple Card is issued by Goldman Sachs
        # Co-branded card issuers (for URL detection)
        "united": "Chase",  # United cards are issued by Chase
        "delta": "American Express",  # Delta cards are issued by Amex
        "southwest": "Chase",  # Southwest cards are issued by Chase
        "marriott": "Chase",  # Marriott cards are issued by Chase
        "hilton": "American Express",  # Hilton cards are issued by Amex
        "hyatt": "Chase",  # Hyatt cards are issued by Chase
        "ihg": "Chase",  # IHG cards are issued by Chase
        "jetblue": "Barclays",  # JetBlue cards are issued by Barclays
        "alaska": "Bank of America",  # Alaska Airlines cards are issued by BoA
        "american airlines": "Citi",  # AA cards are issued by Citi
        "aadvantage": "Citi",  # AA cards are issued by Citi
    }
    
    # Issuer website URLs
    ISSUER_URLS = {
        "Chase": "https://www.chase.com",
        "American Express": "https://www.americanexpress.com",
        "Citi": "https://www.citi.com",
        "Capital One": "https://www.capitalone.com",
        "Bank of America": "https://www.bankofamerica.com",
        "Discover": "https://www.discover.com",
        "U.S. Bank": "https://www.usbank.com",
        "Wells Fargo": "https://www.wellsfargo.com",
        "Barclays": "https://www.barclaysus.com",
        "Goldman Sachs": "https://www.goldmansachs.com",
    }
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False, use_selenium: bool = True):
        # Use Selenium by default for NerdWallet since pages are JS-rendered
        super().__init__("NerdWallet", use_cache=use_cache, offline_mode=offline_mode, use_selenium=use_selenium)
        self.issuer = CardIssuer(
            name="Various",
            website_url=self.BASE_URL,
            support_contact=""
        )
        self._visited_urls: Set[str] = set()
        self._card_urls: List[str] = []
    
    def _parse_annual_fee(self, text: str) -> float:
        """Parse annual fee from text."""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Check for "no annual fee" first
        if re.search(r'\bno\s+annual\s+fee\b', text_lower):
            return 0.0
        
        # Look for dollar amounts - prioritize patterns that explicitly mention "annual fee"
        # This helps avoid picking up other dollar amounts
        patterns = [
            r'annual\s+fee[:\s]+\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # "Annual Fee: $95"
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s+annual\s+fee',  # "$95 annual fee"
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:annual|yearly|per\s+year|fee)',  # "$95 annual"
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:annual|yearly)\s+fee',  # "95 annual fee"
        ]
        
        # Try patterns in order
        for pattern in patterns:
            matches = list(re.finditer(pattern, text_lower))
            if matches:
                # Take the first match that's near "annual fee" context
                for match in matches:
                    try:
                        fee_str = match.group(1).replace(',', '')
                        fee = float(fee_str)
                        # Validate reasonable range (0-1000)
                        if 0 <= fee <= 1000:
                            return fee
                    except (IndexError, ValueError):
                        continue
        
        return 0.0  # Default to $0 if not found
    
    def _parse_multiplier(self, text: str, reward_type: Optional[RewardType] = None) -> float:
        """Parse reward multiplier from text.
        
        For cashback cards: "6%" or "6x" means 6% cashback
        For points cards: "3x" means 3 points per dollar
        """
        if not text:
            return 1.0
        
        # Look for patterns like "3x", "5%", "2 points per dollar"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*%',  # 5%, 1.5% - always percentage
            r'(\d+(?:\.\d+)?)\s*x\b',  # 3x, 2.5x - depends on reward type
            r'(\d+(?:\.\d+)?)\s*(?:points?|miles?|percent)\s*(?:per|for|on)',
            r'earn\s+(\d+(?:\.\d+)?)\s*(?:points?|miles?|%|percent)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    value = float(match.group(1))
                    
                    # For cashback cards, "x" means percentage (6x = 6%)
                    # For points/miles cards, "x" means multiplier (3x = 3 points per dollar)
                    if '%' in match.group(0) or (reward_type == RewardType.CASHBACK_PERCENT and 'x' in match.group(0)):
                        # This is a percentage - validate range
                        # Real cashback cards: max 6% (except special 5% rotating categories)
                        # Anything over 10% is definitely wrong (likely from comparison tables)
                        if 0 <= value <= 6:  # Max 6% cashback is realistic
                            return value
                        elif 6 < value <= 10:
                            # Between 6-10%: might be legitimate (e.g., special promotions)
                            # But log it for review
                            logger.debug(f"Found high cashback rate {value}% - may need validation")
                            return value
                        else:
                            # Over 10%: definitely wrong, skip it
                            logger.warning(f"Skipping impossible cashback rate {value}%")
                            return 1.0  # Return default instead
                    else:
                        # This is a multiplier for points/miles - validate range
                        if 0 <= value <= 15:  # Max 15x points is reasonable
                            return value
                except (IndexError, ValueError):
                    continue
        
        return 1.0
    
    def _extract_categories(self, text: str) -> List[str]:
        """Extract normalized categories from reward description."""
        if not text:
            return []
        
        category_keywords = {
            "groceries": ["grocery", "supermarket", "grocery store", "grocery stores", "food store"],
            "restaurants": ["restaurant", "dining", "dine", "food", "fast food", "cafe", "café"],
            "travel": ["travel", "trip", "airline", "hotel", "flight", "airport", "lodging"],
            "gas": ["gas", "gasoline", "fuel", "gas station", "gas stations"],
            "streaming": ["streaming", "netflix", "spotify", "hulu", "disney", "entertainment"],
            "utilities": ["utility", "phone", "internet", "cable", "electric", "water"],
            "pharmacy": ["pharmacy", "drugstore", "cvs", "walgreens", "rite aid"],
            "entertainment": ["entertainment", "movie", "theater", "cinema", "concert"],
            "online_shopping": ["online", "internet", "e-commerce", "internet purchase"],
            "department_store": ["department store", "retail"],
            "wholesale": ["wholesale", "warehouse", "costco", "sam's club"],
            "transit": ["transit", "uber", "lyft", "taxi", "public transportation"],
        }
        
        text_lower = text.lower()
        categories = []
        
        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)
        
        return categories
    
    def _parse_cap(self, text: str) -> Optional[Cap]:
        """Parse spending cap from text."""
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Look for patterns like "up to $1,500 per quarter", "$25,000 per year"
        patterns = [
            r'(?:up\s+to|max|maximum)\s+\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per|/)\s*(quarter|year|month|qtr)',
            r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per|/)\s*(quarter|year|month|qtr)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:in|per)\s*(quarter|year|month|qtr)',
        ]
        
        period_map = {
            "quarter": "quarter",
            "qtr": "quarter",
            "year": "year",
            "month": "month",
        }
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    period = match.group(2).lower()
                    period_normalized = period_map.get(period, "year")
                    return Cap(amount_dollars=amount, period=period_normalized)
                except (IndexError, ValueError):
                    continue
        
        return None
    
    def _extract_issuer_from_text(self, text: str) -> Optional[str]:
        """Extract issuer name from text.
        
        Uses word boundary matching to avoid false positives.
        For example, "chase" in "chase sapphire" should match, but not "chase" in "purchase".
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Sort by length (longest first) to match most specific first
        sorted_issuers = sorted(self.ISSUER_MAP.items(), key=lambda x: len(x[0]), reverse=True)
        
        for key, issuer in sorted_issuers:
            # Use word boundary matching for single-word issuers
            if len(key.split()) == 1:
                # Single word: use word boundaries to avoid false matches
                pattern = r'\b' + re.escape(key) + r'\b'
                if re.search(pattern, text_lower):
                    return issuer
            else:
                # Multi-word: simple substring match (already specific enough)
                if key in text_lower:
                    return issuer
        
        return None
    
    def _extract_issuer_from_url(self, url: str) -> Optional[str]:
        """Extract issuer name from NerdWallet URL slug.
        
        NerdWallet URLs are like: /reviews/credit-cards/chase-sapphire-preferred
        The issuer is usually the first part(s) of the slug.
        """
        if not url:
            return None
        
        # Extract slug from URL
        match = re.search(r'/reviews/credit-cards/([^/?#]+)', url)
        if not match:
            return None
        
        slug = match.group(1).lower()
        
        # Split slug into parts
        parts = slug.split('-')
        if not parts:
            return None
        
        # Check if first part(s) match an issuer (try longest combinations first)
        # Try 2-word combinations first (e.g., "american-express", "capital-one")
        for i in range(min(3, len(parts)), 0, -1):  # Try 3-word, 2-word, then 1-word
            potential_issuer = '-'.join(parts[:i])
            if potential_issuer in self.ISSUER_MAP:
                return self.ISSUER_MAP[potential_issuer]
        
        # Also check individual words in the slug (for single-word issuers)
        for part in parts[:3]:  # Check first 3 parts
            if part in self.ISSUER_MAP:
                return self.ISSUER_MAP[part]
        
        return None
    
    def _extract_network_from_text(self, text: str) -> Optional[CardNetwork]:
        """Extract card network from text."""
        if not text:
            return None
        
        text_lower = text.lower()
        for key, network in self.NETWORK_MAP.items():
            if key in text_lower:
                return network
        return None
    
    def _extract_reward_type_from_text(self, text: str) -> Optional[RewardType]:
        """Extract reward type from text."""
        if not text:
            return None
        
        text_lower = text.lower()
        for key, reward_type in self.REWARD_TYPE_MAP.items():
            if key in text_lower:
                return reward_type
        return None
    
    def _discover_card_urls(self) -> List[str]:
        """Discover all credit card review URLs from NerdWallet."""
        logger.info("Discovering card URLs from NerdWallet...")
        
        card_urls = []
        
        # Method 1: Try sitemap (most comprehensive)
        try:
            sitemap_urls = [
                'https://www.nerdwallet.com/sitemap.xml',
                'https://www.nerdwallet.com/sitemap_index.xml',
            ]
            
            for sitemap_url in sitemap_urls:
                try:
                    html = self.fetch_url(sitemap_url)
                    if html:
                        # Parse XML sitemap
                        import xml.etree.ElementTree as ET
                        try:
                            root = ET.fromstring(html)
                            # Find all URLs containing /reviews/credit-cards/
                            for url_elem in root.iter():
                                if url_elem.tag.endswith('loc'):
                                    url_text = url_elem.text
                                    if url_text and '/reviews/credit-cards/' in url_text:
                                        # Skip non-card pages
                                        if not any(skip in url_text for skip in ['/compare', '/best', '/top', '/category', '/type']):
                                            if url_text not in card_urls:
                                                card_urls.append(url_text)
                            if card_urls:
                                logger.info(f"Found {len(card_urls)} card URLs from sitemap")
                                break
                        except ET.ParseError:
                            # Not XML, try HTML parsing
                            soup = BeautifulSoup(html, 'html.parser')
                            links = soup.find_all('a', href=re.compile(r'/reviews/credit-cards/'))
                            for link in links:
                                href = link.get('href', '')
                                if href and '/reviews/credit-cards/' in href:
                                    full_url = urljoin(self.BASE_URL, href)
                                    if full_url not in card_urls and not any(skip in full_url for skip in ['/compare', '/best', '/top']):
                                        card_urls.append(full_url)
                            if card_urls:
                                logger.info(f"Found {len(card_urls)} card URLs from sitemap HTML")
                                break
                except Exception as e:
                    logger.debug(f"Error fetching sitemap {sitemap_url}: {e}")
                    continue
        except Exception as e:
            logger.debug(f"Error with sitemap discovery: {e}")
        
            # Method 2: Use Selenium to scrape JS-rendered pages
            if len(card_urls) < 50:  # If we didn't get many from sitemap
                if self.use_selenium:
                    try:
                        logger.info("Using Selenium to discover cards from JS-rendered pages...")
                        driver = self._get_selenium_driver()
                        if driver:
                            # Visit main credit cards page
                            driver.get(self.CARDS_LIST_URL)
                            time.sleep(3)  # Wait for JS to render
                            
                            # Scroll to load more content (lazy loading)
                            last_height = driver.execute_script("return document.body.scrollHeight")
                            scroll_attempts = 0
                            while scroll_attempts < 5:  # Scroll 5 times to load more
                                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                time.sleep(2)
                                new_height = driver.execute_script("return document.body.scrollHeight")
                                if new_height == last_height:
                                    break
                                last_height = new_height
                                scroll_attempts += 1
                            
                            # Get page source after JS rendering
                            html = driver.page_source
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Find all links
                            card_links = soup.find_all('a', href=re.compile(r'/reviews/credit-cards/'))
                            
                            for link in card_links:
                                href = link.get('href', '')
                                if href and '/reviews/credit-cards/' in href:
                                    # Skip comparison pages and other non-card pages
                                    if any(skip in href for skip in ['/compare', '/best', '/top', '/category', '/type', '/guide']):
                                        continue
                                    # Skip if it's not a card review
                                    parts = href.split('/reviews/credit-cards/')
                                    if len(parts) < 2 or not parts[1] or parts[1].strip() == '':
                                        continue
                                    
                                    full_url = urljoin(self.BASE_URL, href)
                                    if full_url not in card_urls:
                                        card_urls.append(full_url)
                            
                            logger.info(f"Found {len(card_links)} potential card links via Selenium")
                        else:
                            logger.warning("Selenium not available, falling back to HTML parsing")
                    except Exception as e:
                        logger.warning(f"Error using Selenium for discovery: {e}")
                
                # Fallback: Try HTML parsing of multiple listing pages
                if len(card_urls) < 50:
                    listing_urls = [
                        self.CARDS_LIST_URL,
                    ]
                    
                    for listing_url in listing_urls:
                        try:
                            html = self.fetch_url(listing_url)
                            if not html:
                                continue
                            
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Find all links to card review pages
                            card_links = soup.find_all('a', href=re.compile(r'/reviews/credit-cards/'))
                            
                            for link in card_links:
                                href = link.get('href', '')
                                if href and '/reviews/credit-cards/' in href:
                                    # Skip comparison pages and other non-card pages
                                    if any(skip in href for skip in ['/compare', '/best', '/top', '/category', '/type', '/guide']):
                                        continue
                                    # Skip if it's not a card review
                                    parts = href.split('/reviews/credit-cards/')
                                    if len(parts) < 2 or not parts[1] or parts[1].strip() == '':
                                        continue
                                    
                                    full_url = urljoin(self.BASE_URL, href)
                                    if full_url not in card_urls:
                                        card_urls.append(full_url)
                            
                            # Small delay between pages
                            time.sleep(0.5)
                            
                        except Exception as e:
                            logger.warning(f"Error fetching {listing_url}: {e}")
                            continue
        
        # Comprehensive list of known cards on NerdWallet (100+ cards)
        # This list is built from known card reviews on NerdWallet
        known_card_slugs = [
            # Chase (verified cards that exist on NerdWallet)
            "chase-sapphire-preferred", "chase-sapphire-reserve", "chase-freedom-flex",
            "chase-freedom-unlimited", "chase-freedom-rise", "chase-slate", 
            "chase-ink-business-unlimited",
            
            # American Express (verified cards)
            "american-express-blue-cash-preferred", "american-express-blue-cash-everyday",
            "american-express-business-platinum", "american-express-business-gold",
            "american-express-cash-magnet",
            
            # Citi (verified cards)
            "citi-double-cash", "citi-custom-cash", "citi-rewards-plus",
            "citi-diamond-preferred", "citi-aadvantage-executive",
            "citi-aadvantage-mileup", "citi-costco-anywhere", "citi-simplicity",
            "citi-secured",
            
            # Capital One (verified cards)
            "capital-one-venture-x", "capital-one-venture", "capital-one-quicksilver",
            "capital-one-spark-miles", "capital-one-ventureone",
            "capital-one-platinum", "capital-one-platinum-secured",
            "capital-one-walmart-rewards", "capital-one-savor",
            
            # Bank of America (verified cards)
            "bank-of-america-premium-rewards", "bank-of-america-travel-rewards",
            
            # Discover (verified cards)
            "discover-it-cash-back", "discover-it-miles", "discover-it-chrome",
            "discover-it-secured",
            
            # U.S. Bank (verified cards)
            "us-bank-altitude-go", "us-bank-cash-plus",
            "us-bank-altitude-connect",
            
            # Wells Fargo (verified cards)
            "wells-fargo-active-cash", "wells-fargo-autograph", "wells-fargo-platinum",
            "wells-fargo-cash-wise", "wells-fargo-propel",
            
            # Other issuers (verified cards)
            "apple-card", "barclays-arrival-plus", "alliant-cashback",
            "fidelity-rewards", "paypal-cashback", "amazon-prime-rewards", "target-redcard",
            "costco-anywhere-visa", "td-double-up",
        ]
        
        # Generate URLs from known slugs
        fallback_urls = [f"{self.BASE_URL}/reviews/credit-cards/{slug}" for slug in known_card_slugs]
        
        try:
            # Try multiple listing pages
            listing_urls = [
                self.CARDS_LIST_URL,
                "https://www.nerdwallet.com/best/credit-cards",
            ]
            
            for listing_url in listing_urls:
                try:
                    html = self.fetch_url(listing_url)
                    if not html:
                        continue
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find all links to card review pages
                    card_links = soup.find_all('a', href=re.compile(r'/reviews/credit-cards/'))
                    
                    for link in card_links:
                        href = link.get('href', '')
                        if href and '/reviews/credit-cards/' in href:
                            # Skip comparison pages and other non-card pages
                            if any(skip in href for skip in ['/compare', '/best', '/top', '/category', '/type']):
                                continue
                            # Skip if it's not a card review (should have card name after /reviews/credit-cards/)
                            parts = href.split('/reviews/credit-cards/')
                            if len(parts) < 2 or not parts[1] or parts[1].strip() == '':
                                continue
                            
                            full_url = urljoin(self.BASE_URL, href)
                            if full_url not in self._visited_urls and full_url not in card_urls:
                                card_urls.append(full_url)
                                self._visited_urls.add(full_url)
                    
                    # Small delay between pages
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"Error fetching {listing_url}: {e}")
                    continue
            
            # Remove duplicates and sort
            card_urls = sorted(list(set(card_urls)))
            
            # If we didn't find many URLs, use fallback list
            if len(card_urls) < 20:
                logger.info(f"Only found {len(card_urls)} URLs, using comprehensive fallback list")
                # Add fallback URLs that aren't already in card_urls
                for url in fallback_urls:
                    if url not in card_urls:
                        card_urls.append(url)
            
            logger.info(f"Discovered {len(card_urls)} unique card URLs")
            return card_urls
            
        except Exception as e:
            logger.error(f"Error discovering card URLs: {e}, using fallback list", exc_info=True)
            return fallback_urls
    
    def _parse_card_page(self, url: str) -> Optional[CardProduct]:
        """Parse a single NerdWallet card review page."""
        try:
            html = self.fetch_url(url)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try to extract structured data from JSON-LD first
            json_ld_data = None
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and ('@type' in data or 'name' in data):
                        json_ld_data = data
                        break
                except:
                    continue
            
            # Extract card name
            card_name = None
            
            # Try h1 first (most reliable)
            h1 = soup.find('h1')
            if h1:
                card_name = h1.get_text().strip()
                # Clean up common suffixes
                card_name = re.sub(r'\s*(?:Review|Credit Card|Card|:).*$', '', card_name, flags=re.I).strip()
            
            # Try title tag
            if not card_name:
                title_tag = soup.find('title')
                if title_tag:
                    title_text = title_tag.get_text()
                    # Extract card name from title (usually "Card Name Review - NerdWallet")
                    match = re.search(r'^([^-]+?)\s*(?:Review|Card|Credit Card)', title_text)
                    if match:
                        card_name = match.group(1).strip()
            
            # Try JSON-LD
            if not card_name and json_ld_data:
                card_name = json_ld_data.get('name') or json_ld_data.get('headline')
                if card_name:
                    card_name = re.sub(r'\s*(?:Review|Credit Card|Card).*$', '', card_name, flags=re.I).strip()
            
            # Try meta tags
            if not card_name:
                meta_title = soup.find('meta', property='og:title')
                if meta_title:
                    card_name = meta_title.get('content', '').strip()
                    card_name = re.sub(r'\s*(?:Review|Credit Card|Card).*$', '', card_name, flags=re.I).strip()
            
            # Try extracting from URL as last resort
            if not card_name:
                url_match = re.search(r'/reviews/credit-cards/([^/?#]+)', url)
                if url_match:
                    slug = url_match.group(1)
                    # Convert slug to readable name, but remove issuer prefix if present
                    parts = slug.split('-')
                    # Remove common issuer prefixes (check for multi-word first)
                    issuer_prefixes = [
                        'american-express', 'capital-one', 'bank-of-america', 'wells-fargo', 'us-bank',
                        'chase', 'amex', 'citi', 'discover', 'barclays', 'apple', 'goldman-sachs'
                    ]
                    # Check for 2-word prefix first
                    if len(parts) >= 2:
                        two_word_prefix = '-'.join(parts[:2])
                        if two_word_prefix in issuer_prefixes:
                            parts = parts[2:]  # Remove 2-word issuer prefix
                    # Check for 1-word prefix
                    elif len(parts) >= 1 and parts[0] in issuer_prefixes:
                        parts = parts[1:]  # Remove issuer prefix
                    
                    if parts:
                        card_name = ' '.join(parts).title()
                        logger.debug(f"Extracted card name from URL slug: {card_name}")
                    else:
                        # If all parts were issuer, use slug as-is
                        card_name = slug.replace('-', ' ').title()
                        logger.debug(f"Using full slug as card name: {card_name}")
            
            if not card_name:
                logger.warning(f"Could not extract card name from {url}, trying fallback methods...")
                # Try harder: extract from URL slug
                url_match = re.search(r'/reviews/credit-cards/([^/?#]+)', url)
                if url_match:
                    slug = url_match.group(1)
                    # Convert slug to readable name
                    card_name = slug.replace('-', ' ').title()
                    logger.info(f"Extracted card name from URL slug: {card_name}")
                else:
                    logger.warning(f"Could not extract card name from {url} - skipping")
                    return None
            
            # Extract annual fee
            annual_fee = 0.0
            page_text = soup.get_text()
            
            # Look for annual fee in various sections - prioritize sections with "Annual Fee" label
            # Look for patterns like "Annual Fee$95" or "Annual Fee: $95"
            fee_pattern = re.compile(r'annual\s+fee\s*[:\$]?\s*\$?(\d+)', re.I)
            fee_matches = list(fee_pattern.finditer(page_text))
            
            if fee_matches:
                # Take matches and validate - prefer common annual fee amounts
                common_fees = [0, 95, 99, 150, 195, 250, 295, 300, 395, 450, 550, 695]
                best_match = None
                best_score = 0
                
                for match in fee_matches:
                    try:
                        fee_str = match.group(1)
                        fee = float(fee_str)
                        # Validate reasonable range
                        if 0 <= fee <= 1000:
                            # Score: prefer common fees, prefer earlier matches
                            score = 100 if fee in common_fees else 50
                            score += (len(fee_matches) - fee_matches.index(match)) * 10  # Earlier = better
                            if score > best_score:
                                best_score = score
                                best_match = fee
                    except (ValueError, IndexError):
                        continue
                
                if best_match is not None:
                    annual_fee = best_match
                    logger.debug(f"Found annual fee ${annual_fee} from direct pattern")
                else:
                    annual_fee = 0.0
            
            # Fallback: look in sections
            if annual_fee == 0.0:
                fee_sections = soup.find_all(['div', 'section', 'p', 'span', 'td'], 
                                            string=re.compile(r'annual\s+fee', re.I))
                for section in fee_sections:
                    # Get parent context
                    parent = section.parent if hasattr(section, 'parent') else section
                    fee_text = parent.get_text()
                    # Look for pattern right after "annual fee"
                    match = re.search(r'annual\s+fee\s*[:\$]?\s*\$?(\d+)', fee_text, re.I)
                    if match:
                        try:
                            fee_str = match.group(1)
                            fee = float(fee_str)
                            if 0 <= fee <= 1000:
                                annual_fee = fee
                                break
                        except (ValueError, IndexError):
                            continue
                
                # Last resort: parse from text
                if annual_fee == 0.0:
                    annual_fee = self._parse_annual_fee(page_text)
            
            # Extract issuer - prioritize URL slug (most reliable), then card name, then page content
            issuer_name = "Unknown"
            issuer_url = ""
            
            # Strategy 1: Extract from URL slug (most reliable for NerdWallet)
            issuer = self._extract_issuer_from_url(url)
            if issuer:
                issuer_name = issuer
                issuer_url = self.ISSUER_URLS.get(issuer, "")
                logger.debug(f"Extracted issuer '{issuer_name}' from URL slug")
            
            # Strategy 2: Extract from card name (if URL didn't work)
            if issuer_name == "Unknown":
                issuer = self._extract_issuer_from_text(card_name)
                if issuer:
                    issuer_name = issuer
                    issuer_url = self.ISSUER_URLS.get(issuer, "")
                    logger.debug(f"Extracted issuer '{issuer_name}' from card name")
            
            # Strategy 3: Look for explicit issuer mentions in page content (least reliable)
            if issuer_name == "Unknown":
                issuer_sections = soup.find_all(string=re.compile(r'issued\s+by|from\s+\w+|by\s+\w+', re.I))
                for section in issuer_sections:
                    issuer = self._extract_issuer_from_text(section)
                    if issuer:
                        issuer_name = issuer
                        issuer_url = self.ISSUER_URLS.get(issuer, "")
                        logger.debug(f"Extracted issuer '{issuer_name}' from page content")
                        break
            
            # Extract network
            # Default based on issuer (Chase/Citi/Capital One = Visa, Amex = Amex, etc.)
            network = CardNetwork.VISA  # Default
            issuer_lower = issuer_name.lower()
            if "amex" in issuer_lower or "american express" in issuer_lower:
                network = CardNetwork.AMEX
            elif "discover" in issuer_lower:
                network = CardNetwork.DISCOVER
            elif "chase" in issuer_lower or "citi" in issuer_lower or "capital one" in issuer_lower:
                network = CardNetwork.VISA  # Most Chase/Citi/Capital One cards are Visa
            
            # Try to extract from page content (but trust issuer-based default more)
            network_text = soup.get_text()
            extracted_network = self._extract_network_from_text(network_text)
            # Only use extracted if it makes sense (don't override issuer-based logic)
            if extracted_network and (
                (network == CardNetwork.VISA and extracted_network == CardNetwork.VISA) or
                (network == CardNetwork.AMEX and extracted_network == CardNetwork.AMEX) or
                (network == CardNetwork.DISCOVER and extracted_network == CardNetwork.DISCOVER)
            ):
                network = extracted_network
            
            # Extract reward type
            # Default based on card name and issuer
            reward_type = RewardType.POINTS_PER_DOLLAR  # Default
            card_name_lower = card_name.lower()
            reward_text = soup.get_text().lower()
            
            # Check card name for clues (most reliable) - prioritize these
            if "sapphire" in card_name_lower:
                reward_type = RewardType.POINTS_PER_DOLLAR  # Sapphire cards always use points
            elif "cash" in card_name_lower or "cashback" in card_name_lower or "double cash" in card_name_lower:
                reward_type = RewardType.CASHBACK_PERCENT
            elif "miles" in card_name_lower or "mileage" in card_name_lower or "skymiles" in card_name_lower:
                reward_type = RewardType.MILES_PER_DOLLAR
            elif "premier" in card_name_lower or "venture" in card_name_lower:
                reward_type = RewardType.POINTS_PER_DOLLAR
            elif "freedom" in card_name_lower:
                reward_type = RewardType.POINTS_PER_DOLLAR  # Chase Freedom cards use points
            
            # Check page content for reward type mentions (override if card name didn't set it)
            # For Sapphire cards, always use points regardless of page content
            if "sapphire" in card_name_lower:
                reward_type = RewardType.POINTS_PER_DOLLAR
            # Check for reward programs that indicate points (highest priority after card name)
            elif "ultimate rewards" in reward_text or "membership rewards" in reward_text or "thankyou points" in reward_text:
                reward_type = RewardType.POINTS_PER_DOLLAR
            # If card name suggests points and page mentions points, use points
            elif ("premier" in card_name_lower or "venture" in card_name_lower or "freedom" in card_name_lower) and "points" in reward_text:
                reward_type = RewardType.POINTS_PER_DOLLAR
            # Check issuer - Chase/Citi/Amex premium cards usually use points
            elif issuer_name in ["Chase", "Citi", "American Express"] and ("premier" in card_name_lower or "reserve" in card_name_lower or "platinum" in card_name_lower or "gold" in card_name_lower):
                reward_type = RewardType.POINTS_PER_DOLLAR
            elif ("points" in reward_text or "point" in reward_text) and (
                "premier" in card_name_lower or 
                "venture" in card_name_lower or
                "freedom" in card_name_lower
            ):
                reward_type = RewardType.POINTS_PER_DOLLAR
            elif "cash back" in reward_text and "points" not in reward_text and "ultimate rewards" not in reward_text:
                reward_type = RewardType.CASHBACK_PERCENT
            elif "miles" in reward_text and "points" not in reward_text and "ultimate rewards" not in reward_text:
                reward_type = RewardType.MILES_PER_DOLLAR
            
            # Try to extract from page content (as final check)
            # BUT: Don't override if we already determined it from card name or reward programs
            if reward_type == RewardType.CASHBACK_PERCENT:  # Only override if still default or cashback
                extracted_reward_type = self._extract_reward_type_from_text(reward_text)
                if extracted_reward_type:
                    reward_type = extracted_reward_type
            
            # Determine reward program
            reward_program = None
            if reward_type == RewardType.POINTS_PER_DOLLAR:
                if "chase" in issuer_name.lower():
                    reward_program = RewardProgram(
                        id="CHASE_UR",
                        name="Chase Ultimate Rewards",
                        base_point_value_cents=0.017,
                        notes="Transferable to travel partners"
                    )
                elif "amex" in issuer_name.lower() or "american express" in issuer_name.lower():
                    reward_program = RewardProgram(
                        id="AMEX_MR",
                        name="American Express Membership Rewards",
                        base_point_value_cents=0.017,
                        notes="Transferable to travel partners"
                    )
                elif "citi" in issuer_name.lower():
                    reward_program = RewardProgram(
                        id="CITI_TY",
                        name="Citi ThankYou Points",
                        base_point_value_cents=0.015,
                        notes="Transferable to travel partners"
                    )
            
            # Foreign transaction fee (default to 3% for most cards)
            foreign_transaction_fee = 0.03
            if "sapphire" in card_name.lower() or "reserve" in card_name.lower():
                foreign_transaction_fee = 0.0
            
            # Generate card ID
            card_id = re.sub(r'[^a-z0-9]+', '_', card_name.lower()).strip('_')
            
            issuer_obj = CardIssuer(
                name=issuer_name,
                website_url=issuer_url,
                support_contact=""
            )
            
            card = CardProduct(
                id=card_id,
                issuer=issuer_obj,
                name=card_name,
                network=network,
                type=reward_type,
                annual_fee=annual_fee,
                foreign_transaction_fee=foreign_transaction_fee,
                reward_program=reward_program,
                official_url=url,
                metadata={"source": "nerdwallet", "scraped_at": time.time()}
            )
            
            logger.info(f"Parsed card: {card_name} (fee: ${annual_fee}, issuer: {issuer_name})")
            return card
            
        except Exception as e:
            logger.error(f"Error parsing card page {url}: {e}", exc_info=True)
            return None
    
    def _parse_earning_rules(self, url: str, card: CardProduct) -> List[EarningRule]:
        """Parse earning rules from a NerdWallet card page using rule-based parser."""
        try:
            html = self.fetch_url(url)
            if not html:
                return []
            
            # Try structured rule parser first (more accurate)
            try:
                from scrapers.issuers.nerdwallet_rule_parser import NerdWalletRuleParser
                parser = NerdWalletRuleParser(card.type)
                structured_rules = parser.parse_from_html(html, card.id)
                
                if structured_rules:
                    logger.info(f"Parsed {len(structured_rules)} structured rules for {card.name}")
                    return structured_rules
            except ImportError:
                logger.warning("Structured rule parser not available, using fallback")
            except Exception as e:
                logger.warning(f"Structured parser failed: {e}, using fallback")
            
            # Fallback to original parsing method
            soup = BeautifulSoup(html, 'html.parser')
            rules = []
            
            # Look for reward/earning sections
            # NerdWallet typically has sections with reward information
            reward_sections = soup.find_all(['section', 'div', 'article'],
                                          class_=lambda x: x and (
                                              'reward' in str(x).lower() or
                                              'earning' in str(x).lower() or
                                              'benefit' in str(x).lower() or
                                              'category' in str(x).lower()
                                          ))
            
            # Also look for lists with reward information
            reward_lists = soup.find_all(['ul', 'ol'], 
                                       class_=lambda x: x and (
                                           'reward' in str(x).lower() or
                                           'earning' in str(x).lower() or
                                           'benefit' in str(x).lower()
                                       ))
            
            all_sections = reward_sections + reward_lists
            
            for section in all_sections:
                text = section.get_text()
                
                # Skip marketing/comparison sections
                text_lower = text.lower()
                skip_phrases = [
                    'compare', 'comparison', 'vs', 'versus', 'better than', 'best for',
                    'prominent brands', 'heard of', 'advertisement', 'ad', 'sponsored',
                    'sign up bonus', 'welcome bonus', 'introductory offer', 'new cardmember'
                ]
                if any(phrase in text_lower for phrase in skip_phrases):
                    continue  # Skip marketing/comparison text
                
                # Look for multiplier patterns (pass reward type for correct interpretation)
                multiplier = self._parse_multiplier(text, card.type)
                if multiplier <= 1.0:
                    continue  # Skip if no meaningful multiplier
                
                # Additional validation: filter out obviously wrong values
                if card.type == RewardType.CASHBACK_PERCENT and multiplier > 10:
                    logger.warning(f"Skipping suspicious cashback rate {multiplier}% for {card.name} (text: {text[:100]})")
                    continue
                
                # For cashback cards, validate against known maximums
                # Real cashback cards rarely exceed 6% (except special promotions)
                if card.type == RewardType.CASHBACK_PERCENT and multiplier > 6:
                    # Only allow if it's a well-known high cashback card (like 5% rotating)
                    # But 20% is definitely wrong - skip it
                    if multiplier >= 15:
                        logger.warning(f"Skipping impossible cashback rate {multiplier}% for {card.name}")
                        continue
                
                # Extract categories
                categories = self._extract_categories(text)
                
                # Extract cap
                cap = self._parse_cap(text)
                caps = [cap] if cap else []
                
                # Check for rotating categories - be more thorough
                rotating_keywords = [
                    'rotating', 'quarterly', 'changes', 'each quarter', 'per quarter',
                    'activate', 'enrollment required', 'select categories', 'bonus categories',
                    'different places', 'different categories', 'changes quarterly'
                ]
                is_rotating = any(keyword in text.lower() for keyword in rotating_keywords)
                
                # Create earning rule
                rule = EarningRule(
                    card_id=card.id,
                    description=text[:300].strip(),  # Truncate for description
                    merchant_categories=categories,
                    multiplier=multiplier,
                    caps=caps,
                    is_rotating=is_rotating,
                    reward_type=card.type,
                )
                rules.append(rule)
            
            # If no structured sections found, try to parse from general text
            if not rules:
                page_text = soup.get_text()
                
                # Look for reward patterns in the page
                reward_patterns = [
                    r'(\d+(?:\.\d+)?)\s*x\s+(?:points?|miles?|%|percent)\s+(?:on|for|at)\s+([^\.]+)',
                    r'earn\s+(\d+(?:\.\d+)?)\s*(?:x|points?|miles?|%)\s+(?:on|for|at)\s+([^\.]+)',
                    r'(\d+(?:\.\d+)?)%\s+(?:cash\s+back|back)\s+(?:on|for|at)\s+([^\.]+)',
                ]
                
                for pattern in reward_patterns:
                    matches = re.finditer(pattern, page_text, re.IGNORECASE)
                    for match in matches:
                        raw_multiplier = float(match.group(1))
                        category_text = match.group(2)
                        
                        # For cashback cards, "x" in pattern means percentage
                        # For points cards, "x" means multiplier
                        if card.type == RewardType.CASHBACK_PERCENT and 'x' in match.group(0):
                            multiplier = raw_multiplier  # 6x = 6% for cashback
                        else:
                            multiplier = raw_multiplier  # 3x = 3 points for points cards
                        
                        # Skip marketing/comparison text
                        if any(phrase in category_text.lower() for phrase in ['prominent brands', 'heard of', 'compare', 'vs']):
                            continue
                        
                        # Validate multiplier
                        if card.type == RewardType.CASHBACK_PERCENT and multiplier > 10:
                            logger.warning(f"Skipping suspicious cashback rate {multiplier}% for {card.name}")
                            continue
                        # For cashback, anything over 6% is suspicious (except known 5% rotating cards)
                        if card.type == RewardType.CASHBACK_PERCENT and multiplier >= 15:
                            logger.warning(f"Skipping impossible cashback rate {multiplier}% for {card.name}")
                            continue
                        if multiplier <= 1.0:
                            continue  # Skip low multipliers
                        
                        categories = self._extract_categories(category_text)
                        cap = self._parse_cap(category_text)
                        caps = [cap] if cap else []
                        
                        # Check for rotating categories in the category text
                        rotating_keywords = [
                            'rotating', 'quarterly', 'changes', 'each quarter', 'per quarter',
                            'activate', 'enrollment', 'select categories', 'bonus categories',
                            'different places', 'different categories'
                        ]
                        is_rotating = any(keyword in category_text.lower() for keyword in rotating_keywords)
                        
                        rule = EarningRule(
                            card_id=card.id,
                            description=f"{multiplier}{'%' if card.type == RewardType.CASHBACK_PERCENT else 'x'} on {category_text.strip()}",
                            merchant_categories=categories,
                            multiplier=multiplier,
                            caps=caps,
                            reward_type=card.type,
                            is_rotating=is_rotating,
                        )
                        rules.append(rule)
            
            # Deduplicate rules
            seen = set()
            unique_rules = []
            for rule in rules:
                rule_key = (rule.multiplier, tuple(sorted(rule.merchant_categories)))
                if rule_key not in seen:
                    seen.add(rule_key)
                    unique_rules.append(rule)
            
            logger.info(f"Parsed {len(unique_rules)} earning rules for {card.name}")
            return unique_rules
            
        except Exception as e:
            logger.error(f"Error parsing earning rules from {url}: {e}", exc_info=True)
            return []
    
    def scrape_cards(self) -> List[CardProduct]:
        """Scrape all credit cards from NerdWallet."""
        logger.info("Starting NerdWallet card scraping...")
        
        # Discover card URLs
        card_urls = self._discover_card_urls()
        
        # _discover_card_urls() now always returns a list (either discovered or fallback)
        # So we don't need this check anymore, but keep it as safety
        if not card_urls:
            logger.warning("No card URLs available - this should not happen")
            return []
        
        logger.info(f"Found {len(card_urls)} card URLs to scrape")
        cards = []
        failed_urls = []
        
        for i, url in enumerate(card_urls):
            try:
                logger.info(f"Scraping card {i+1}/{len(card_urls)}: {url}")
                card = self._parse_card_page(url)
                if card:
                    cards.append(card)
                    logger.debug(f"  ✅ Successfully parsed: {card.name}")
                else:
                    failed_urls.append(url)
                    logger.warning(f"  ❌ Failed to parse card from {url}")
                
                # Rate limiting (use config value or default)
                try:
                    from config import RATE_LIMIT_DELAY
                    time.sleep(RATE_LIMIT_DELAY)
                except ImportError:
                    time.sleep(1.0)  # Default 1 second delay
                
            except Exception as e:
                failed_urls.append(url)
                logger.error(f"  ❌ Error scraping {url}: {e}", exc_info=True)
                continue
        
        logger.info(f"✅ Successfully scraped {len(cards)} cards from NerdWallet (out of {len(card_urls)} attempted)")
        if len(cards) < len(card_urls):
            logger.warning(f"⚠️  Only scraped {len(cards)}/{len(card_urls)} cards ({len(failed_urls)} failed)")
            if len(failed_urls) <= 10:
                logger.warning(f"Failed URLs: {failed_urls}")
            else:
                logger.warning(f"First 10 failed URLs: {failed_urls[:10]}")
        return cards
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """Scrape earning rules for a card from NerdWallet."""
        if not card.official_url:
            return []
        
        return self._parse_earning_rules(card.official_url, card)
