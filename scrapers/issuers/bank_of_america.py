"""
Bank of America credit card scraper.

Uses manually curated data since pages are JavaScript-rendered.
For production scraping with Selenium, see bank_of_america_manual.py pattern.
"""

import json
import logging
import re
from typing import List, Optional

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

logger = logging.getLogger(__name__)


class BankOfAmericaScraper(BaseScraper):
    """Scraper for Bank of America credit cards."""
    
    # Known Bank of America card URLs
    CARD_URLS = [
        "https://www.bankofamerica.com/credit-cards/products/premium-rewards-credit-card",
        "https://www.bankofamerica.com/credit-cards/products/cash-back-credit-card",
        "https://www.bankofamerica.com/credit-cards/products/travel-rewards-credit-card",
        "https://www.bankofamerica.com/credit-cards/products/accelerated-rewards-credit-card",
    ]
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False, use_selenium: bool = True):
        super().__init__("Bank of America", use_cache=use_cache, offline_mode=offline_mode, use_selenium=use_selenium)
        self.issuer = CardIssuer(
            name="Bank of America",
            website_url="https://www.bankofamerica.com",
            support_contact="1-800-732-9194"
        )
        self.reward_program = RewardProgram(
            id="BOA_POINTS",
            name="Bank of America Rewards",
            base_point_value_cents=0.01,
            notes="Points redeemable for cash, travel, or gift cards"
        )
    
    def _extract_schema_org_data(self, soup) -> Optional[dict]:
        """Extract structured data from schema.org JSON-LD."""
        schema_data = None
        
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get("@type") in ["Product", "FinancialProduct", "CreditCard"]:
                        schema_data = data
                        break
                    elif "@graph" in data:
                        for item in data.get("@graph", []):
                            if item.get("@type") in ["Product", "FinancialProduct", "CreditCard"]:
                                schema_data = item
                                break
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return schema_data
    
    def _extract_card_name(self, soup, schema_data: Optional[dict], card_url: str) -> str:
        """Extract card name using structured selectors."""
        # Try schema.org first
        if schema_data:
            name = schema_data.get("name") or schema_data.get("title")
            if name:
                return name.strip()
        
        # Try specific DOM selectors
        selectors = [
            "h1.card-title",
            "h1.product-title",
            "h1[data-testid='card-title']",
            ".card-name",
            ".product-name",
            "h1",
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                name = element.get_text().strip()
                if name and len(name) < 100 and "Bank of America" not in name:
                    return name
        
        # Fallback: extract from URL
        url_parts = card_url.rstrip("/").split("/")
        if url_parts:
            last_part = url_parts[-1].replace("-", " ").title()
            return f"Bank of America {last_part}"
        
        raise ValueError(f"Could not extract card name from {card_url}")
    
    def _extract_annual_fee(self, soup, schema_data: Optional[dict], card_url: str) -> float:
        """Extract annual fee using structured selectors."""
        # Try schema.org
        if schema_data:
            offers = schema_data.get("offers", [])
            if isinstance(offers, dict):
                offers = [offers]
            for offer in offers:
                price = offer.get("price")
                if price:
                    match = re.search(r'(\d+(?:\.\d+)?)', str(price))
                    if match:
                        return float(match.group(1))
        
        # Try specific fee selectors
        fee_selectors = [
            "[data-testid='annual-fee']",
            "[data-annual-fee]",
            ".annual-fee",
            ".fee-amount",
            "[aria-label*='annual fee']",
        ]
        
        for selector in fee_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text()
                match = re.search(r'\$(\d+(?:\.\d+)?)', text)
                if match:
                    return float(match.group(1))
        
        # Look in structured fee tables
        fee_tables = soup.find_all("table", class_=re.compile(r'fee|pricing|cost', re.I))
        for table in fee_tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    label = cells[0].get_text().lower()
                    if "annual fee" in label:
                        value_text = cells[1].get_text()
                        match = re.search(r'\$(\d+(?:\.\d+)?)', value_text)
                        if match:
                            return float(match.group(1))
                        elif "0" in value_text or "no" in value_text.lower():
                            return 0.0
        
        # Check page text for annual fee mentions
        page_text = soup.get_text()
        page_text_lower = page_text.lower()
        
        # More aggressive search - look for fee in various formats
        if re.search(r'(no annual fee|zero annual fee|\$0\s*annual|free)', page_text_lower):
            return 0.0
        
        # Look for fee in common patterns (case-insensitive search in original text)
        fee_patterns = [
            r'\$(\d+)\s*(?:per year|annually|annual fee)',
            r'annual fee[:\s]+\$(\d+)',
            r'\$(\d+)\s*annual',
            r'(\d+)\s*(?:per year|annually).*annual fee',  # "95 per year annual fee"
            r'annual fee.*\$(\d+)',  # "annual fee $95"
            r'(\d+)\s*annual fee',  # "95 annual fee"
        ]
        
        for pattern in fee_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                fee = float(match.group(1))
                # Sanity check: annual fees are typically 0, 95, 250, 395, 550, etc.
                if 0 <= fee <= 1000:
                    logger.debug(f"Found annual fee ${fee} using pattern: {pattern}")
                    return fee
        
        # Look for common fee amounts in context (wider search)
        common_fees = [550, 395, 250, 95, 0]
        for fee in common_fees:
            # Look for fee amount near "annual" keyword (within 50 chars)
            pattern = rf'.{{0,50}}{fee}.{{0,50}}annual|.{{0,50}}annual.{{0,50}}{fee}'
            if re.search(pattern, page_text, re.IGNORECASE):
                logger.debug(f"Found annual fee ${fee} using context search")
                return float(fee)
        
        # If we can't find it, check card name/URL for hints
        if "premium" in card_url.lower() and "rewards" in card_url.lower():
            logger.warning(f"Could not extract annual fee from {card_url}, using default $95 for Premium Rewards")
            return 95.0  # Premium Rewards typically has $95 fee
        elif "cash" in card_url.lower() or "customized" in card_url.lower():
            return 0.0  # Cash back cards typically have no fee
        
        # Last resort: return 0 and log warning
        logger.warning(f"Could not extract annual fee from {card_url}, defaulting to $0")
        return 0.0
    
    def _extract_network(self, soup, schema_data: Optional[dict], card_name: str) -> CardNetwork:
        """Extract card network using structured selectors."""
        # Check for network logos/images
        network_img = soup.find("img", alt=re.compile(r'visa|mastercard|amex|discover', re.I))
        if network_img:
            alt_text = network_img.get("alt", "").lower()
            if "visa" in alt_text:
                return CardNetwork.VISA
            elif "mastercard" in alt_text:
                return CardNetwork.MASTERCARD
        
        # Check schema.org
        if schema_data:
            brand = schema_data.get("brand", {})
            if isinstance(brand, dict):
                brand_name = brand.get("name", "").lower()
            else:
                brand_name = str(brand).lower()
            
            if "visa" in brand_name:
                return CardNetwork.VISA
            elif "mastercard" in brand_name:
                return CardNetwork.MASTERCARD
        
        # Check page text
        page_text = soup.get_text().lower()
        if "visa" in page_text:
            return CardNetwork.VISA
        elif "mastercard" in page_text:
            return CardNetwork.MASTERCARD
        
        # Bank of America cards are typically Visa
        return CardNetwork.VISA
    
    def _extract_reward_type(self, soup, schema_data: Optional[dict], card_name: str) -> RewardType:
        """Extract reward type using structured selectors."""
        # Check for reward type indicators
        reward_selectors = [
            "[data-reward-type]",
            ".reward-type",
            "[data-testid='reward-type']",
        ]
        
        for selector in reward_selectors:
            element = soup.select_one(selector)
            if element:
                reward_type = element.get_text().lower() or element.get("data-reward-type", "").lower()
                if "cash" in reward_type:
                    return RewardType.CASHBACK_PERCENT
                elif "point" in reward_type:
                    return RewardType.POINTS_PER_DOLLAR
                elif "mile" in reward_type:
                    return RewardType.MILES_PER_DOLLAR
        
        # Check page content (more thorough)
        page_text = soup.get_text()
        page_text_lower = page_text.lower()
        
        # Check for explicit mentions
        if "cash back" in page_text_lower or "cashback" in page_text_lower:
            # But check if it's points that can be redeemed as cash
            if "points" in page_text_lower and "redeem" in page_text_lower:
                return RewardType.POINTS_PER_DOLLAR
            return RewardType.CASHBACK_PERCENT
        elif "points" in page_text_lower:
            # Check if it's actually points (not just "points" in marketing)
            if any(phrase in page_text_lower for phrase in ["earn points", "points per", "points for", "points on"]):
                return RewardType.POINTS_PER_DOLLAR
        elif "miles" in page_text_lower:
            return RewardType.MILES_PER_DOLLAR
        
        # Default based on card name (more reliable)
        card_lower = card_name.lower()
        if "cash" in card_lower and "rewards" not in card_lower:
            return RewardType.CASHBACK_PERCENT
        elif "premium rewards" in card_lower:
            return RewardType.POINTS_PER_DOLLAR  # Premium Rewards uses points
        elif "travel rewards" in card_lower:
            return RewardType.POINTS_PER_DOLLAR
        elif "rewards" in card_lower and "cash" not in card_lower:
            return RewardType.POINTS_PER_DOLLAR
        
        return RewardType.CASHBACK_PERCENT
    
    def scrape_cards(self) -> List[CardProduct]:
        """
        Scrape Bank of America cards from their website.
        
        Returns:
            List of CardProduct objects
            
        Raises:
            ValueError: If scraping fails completely
        """
        cards = []
        
        for card_url in self.CARD_URLS:
            try:
                # Use Selenium for JS-rendered pages, wait for main content
                html = self.fetch_url(card_url, wait_for_element="main, article, [role='main']")
                if not html:
                    logger.error(f"Failed to fetch {card_url}")
                    continue
                
                soup = self.parse_html(html)
                schema_data = self._extract_schema_org_data(soup)
                
                card_name = self._extract_card_name(soup, schema_data, card_url)
                annual_fee = self._extract_annual_fee(soup, schema_data, card_url)
                network = self._extract_network(soup, schema_data, card_name)
                reward_type = self._extract_reward_type(soup, schema_data, card_name)
                
                # Generate card ID from name
                card_id = re.sub(r'[^a-z0-9]+', '_', card_name.lower()).strip('_')
                card_id = f"boa_{card_id}"
                
                # Determine reward program
                reward_program = None
                if reward_type == RewardType.POINTS_PER_DOLLAR:
                    reward_program = self.reward_program
                
                # Foreign transaction fee (most BoA cards have 3% except premium)
                foreign_transaction_fee = 0.03
                if "premium" in card_name.lower() or "travel" in card_name.lower():
                    foreign_transaction_fee = 0.0
                
                card = CardProduct(
                    id=card_id,
                    issuer=self.issuer,
                    name=card_name,
                    network=network,
                    type=reward_type,
                    annual_fee=annual_fee,
                    foreign_transaction_fee=foreign_transaction_fee,
                    reward_program=reward_program,
                    official_url=card_url,
                    metadata={"schema_data": schema_data is not None}
                )
                
                cards.append(card)
                logger.info(f"Scraped card: {card_name} (fee: ${annual_fee}, network: {network.value})")
                
            except Exception as e:
                logger.error(f"Error scraping card from {card_url}: {e}")
                continue
        
        # Fail if no cards scraped
        if not cards:
            raise ValueError("Bank of America scraper failed: Unable to fetch any card data. Check network connection and website availability.")
        
        return cards
    
    def _parse_earning_rules_from_html(self, soup, card: CardProduct) -> List[EarningRule]:
        """
        Parse earning rules using structured selectors.
        
        Looks for:
        - Dedicated rewards sections
        - Structured lists of earning categories
        - Schema.org offer data
        """
        rules = []
        page_text = soup.get_text()
        page_text_lower = page_text.lower()
        
        # Category mapping for normalization
        category_map = {
            "dining": "restaurants",
            "restaurants": "restaurants",
            "restaurant": "restaurants",
            "grocery": "groceries",
            "groceries": "groceries",
            "supermarket": "groceries",
            "supermarkets": "groceries",
            "gas": "gas",
            "gas station": "gas",
            "gas stations": "gas",
            "fuel": "gas",
            "travel": "travel",
            "hotel": "travel",
            "airline": "travel",
            "airlines": "travel",
            "drugstore": "pharmacy",
            "drug stores": "pharmacy",
            "pharmacy": "pharmacy",
            "wholesale": "wholesale",
            "warehouse": "wholesale",
            "warehouse club": "wholesale",
            "online": "online_shopping",
            "internet": "online_shopping",
            "online shopping": "online_shopping",
            "home improvement": "home_improvement",
        }
        
        # Look for structured rewards sections
        reward_sections = soup.find_all(["section", "div"], 
                                       class_=re.compile(r'reward|earning|benefit|cashback|points|rate', re.I),
                                       id=re.compile(r'reward|earning|benefit|rate', re.I))
        
        # Also check for lists with reward data
        reward_lists = soup.find_all(["ul", "ol"], class_=re.compile(r'reward|earning|benefit|rate', re.I))
        
        # Also check main content areas and card details
        main_content = soup.find_all(["main", "article", "div"], 
                                    class_=re.compile(r'content|main|product|card-detail|feature', re.I))
        
        # Look for tables with reward info
        reward_tables = soup.find_all("table", class_=re.compile(r'reward|earning|rate|benefit', re.I))
        
        all_sections = reward_sections + reward_lists + main_content[:5] + reward_tables
        
        for section in all_sections:
            section_text = section.get_text()
            section_lower = section_text.lower()
            
            # Skip if this looks like signup bonus or marketing fluff
            if any(phrase in section_lower for phrase in ["sign up", "welcome bonus", "introductory", "new cardmember", "apply now"]):
                continue
            
            # Extract multiplier
            multiplier = None
            multiplier_patterns = [
                r'(\d+(?:\.\d+)?)\s*x\s*points?\s*(?:per dollar|on)',
                r'(\d+(?:\.\d+)?)\s*points?\s*per dollar',
                r'(\d+(?:\.\d+)?)\s*%\s*cash\s*back',
                r'earn\s*(\d+(?:\.\d+)?)\s*x',
                r'(\d+(?:\.\d+)?)\s*points?\s*per\s*\$1',
                r'(\d+(?:\.\d+)?)\s*%',
            ]
            
            for pattern in multiplier_patterns:
                match = re.search(pattern, section_lower)
                if match:
                    multiplier = float(match.group(1))
                    break
            
            if not multiplier:
                continue
            
            # Extract categories
            categories = []
            for keyword, normalized in category_map.items():
                if keyword in section_lower:
                    if normalized not in categories:
                        categories.append(normalized)
            
            # Extract caps
            caps = []
            cap_patterns = [
                r'(?:up to|on up to|first)\s*\$(\d+(?:,\d+)?)\s*(?:per|/)\s*(quarter|month|year|billing cycle)',
                r'\$(\d+(?:,\d+)?)\s*(?:per|/)\s*(quarter|month|year)',
                r'(\d+(?:,\d+)?)\s*(?:per|/)\s*(quarter|month|year)',
            ]
            
            for pattern in cap_patterns:
                matches = re.finditer(pattern, section_lower)
                for match in matches:
                    amount = float(match.group(1).replace(",", ""))
                    period = match.group(2)
                    caps.append(Cap(amount_dollars=amount, period=period))
            
            # Check for rotating categories
            is_rotating = any(phrase in section_lower for phrase in ["rotating", "quarterly categories", "activate"])
            
            # Check for activation required
            activation_required = "activate" in section_lower or "enrollment" in section_lower or "choose" in section_lower
            
            # Create rule
            description = section_text.strip()[:200] if len(section_text) > 200 else section_text.strip()
            
            rule = EarningRule(
                card_id=card.id,
                description=description,
                merchant_categories=categories,
                multiplier=multiplier,
                reward_type=card.type,
                caps=caps,
                is_rotating=is_rotating,
                stacking_rules="Activation/selection required" if activation_required else None,
            )
            
            rules.append(rule)
        
        # Deduplicate rules (same multiplier + categories)
        seen = set()
        unique_rules = []
        for rule in rules:
            key = (rule.multiplier, tuple(sorted(rule.merchant_categories)))
            if key not in seen:
                seen.add(key)
                unique_rules.append(rule)
        
        return unique_rules
    
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """
        Scrape earning rules for a Bank of America card from its detail page.
        
        Args:
            card: CardProduct to get rules for
            
        Returns:
            List of EarningRule objects
            
        Raises:
            ValueError: If scraping or parsing fails
        """
        if not card.official_url:
            raise ValueError(f"No URL available for {card.name}")
        
        # Use Selenium to get fully rendered page
        html = self.fetch_url(card.official_url, wait_for_element="main, article, [role='main']")
        if not html:
            raise ValueError(f"Unable to fetch earning rules for {card.name} from {card.official_url}")
        
        soup = self.parse_html(html)
        rules = self._parse_earning_rules_from_html(soup, card)
        
        # If no rules found, create a default rule based on card type
        if not rules:
            logger.warning(f"Could not parse earning rules for {card.name}, creating default rule")
            # Create a default flat-rate rule
            default_multiplier = 1.5 if card.type == RewardType.POINTS_PER_DOLLAR else 1.0
            rules = [
                EarningRule(
                    card_id=card.id,
                    description="All purchases (default - specific rules could not be parsed)",
                    merchant_categories=[],
                    multiplier=default_multiplier,
                    reward_type=card.type,
                )
            ]
        
        logger.info(f"Parsed {len(rules)} earning rules for {card.name}")
        return rules
