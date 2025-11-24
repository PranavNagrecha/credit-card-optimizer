"""
Chase credit card scraper.

Production implementation using structured DOM selectors and schema.org data.
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


class ChaseScraper(BaseScraper):
    """Scraper for Chase credit cards."""
    
    # Known Chase card URLs - these are the main consumer cards
    CARD_URLS = [
        "https://www.chase.com/personal/credit-cards/sapphire/sapphire-preferred",
        "https://www.chase.com/personal/credit-cards/sapphire/sapphire-reserve",
        "https://www.chase.com/personal/credit-cards/freedom/freedom-flex",
        "https://www.chase.com/personal/credit-cards/freedom/freedom-unlimited",
        "https://www.chase.com/personal/credit-cards/slate-edge",
        "https://www.chase.com/personal/credit-cards/freedom/freedom-rise",
    ]
    
    def __init__(self, use_cache: bool = True, offline_mode: bool = False):
        super().__init__("Chase", use_cache=use_cache, offline_mode=offline_mode)
        self.issuer = CardIssuer(
            name="Chase",
            website_url="https://www.chase.com",
            support_contact="1-800-935-9935"
        )
        self.reward_program = RewardProgram(
            id="CHASE_UR",
            name="Chase Ultimate Rewards",
            base_point_value_cents=0.017,
            notes="Transferable to travel partners"
        )
    
    def _extract_schema_org_data(self, soup) -> Optional[dict]:
        """Extract structured data from schema.org JSON-LD."""
        schema_data = None
        
        # Look for JSON-LD script tags with schema.org data
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get("@type") in ["Product", "FinancialProduct", "CreditCard"]:
                        schema_data = data
                        break
                    elif "@graph" in data:
                        # Some sites use @graph
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
            "h1",
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                name = element.get_text().strip()
                if name and len(name) < 100:
                    return name
        
        # Fallback: extract from URL
        url_parts = card_url.rstrip("/").split("/")
        if url_parts:
            last_part = url_parts[-1].replace("-", " ").title()
            return f"Chase {last_part}"
        
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
                    # Extract numeric value
                    match = re.search(r'(\d+(?:\.\d+)?)', str(price))
                    if match:
                        return float(match.group(1))
        
        # Try specific fee selectors
        fee_selectors = [
            "[data-testid='annual-fee']",
            ".annual-fee",
            ".fee-amount",
            "[data-annual-fee]",
        ]
        
        for selector in fee_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text()
                match = re.search(r'\$(\d+(?:\.\d+)?)', text)
                if match:
                    return float(match.group(1))
        
        # Look in structured fee tables
        fee_tables = soup.find_all("table", class_=re.compile(r'fee|pricing', re.I))
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
        
        # Check for "$0 annual fee" or "no annual fee" in page
        page_text = soup.get_text().lower()
        if re.search(r'(no annual fee|zero annual fee|\$0\s*annual)', page_text):
            return 0.0
        
        raise ValueError(f"Could not extract annual fee from {card_url}")
    
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
            elif "amex" in alt_text or "american express" in alt_text:
                return CardNetwork.AMEX
            elif "discover" in alt_text:
                return CardNetwork.DISCOVER
        
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
        
        # Default based on card type
        card_lower = card_name.lower()
        if "freedom flex" in card_lower:
            return CardNetwork.MASTERCARD
        elif "sapphire" in card_lower or "freedom unlimited" in card_lower:
            return CardNetwork.VISA
        
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
        
        # Check page content
        page_text = soup.get_text().lower()
        if "cash back" in page_text or "cashback" in page_text:
            return RewardType.CASHBACK_PERCENT
        elif "points" in page_text or "ultimate rewards" in page_text:
            return RewardType.POINTS_PER_DOLLAR
        elif "miles" in page_text:
            return RewardType.MILES_PER_DOLLAR
        
        # Default based on card
        card_lower = card_name.lower()
        if "sapphire" in card_lower or "freedom" in card_lower:
            return RewardType.POINTS_PER_DOLLAR
        
        return RewardType.CASHBACK_PERCENT
    
    def scrape_cards(self) -> List[CardProduct]:
        """
        Scrape Chase cards from their website using structured selectors.
        
        Returns:
            List of CardProduct objects
            
        Raises:
            ValueError: If scraping fails completely
        """
        cards = []
        
        for card_url in self.CARD_URLS:
            try:
                html = self.fetch_url(card_url)
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
                card_id = f"chase_{card_id}"
                
                # Determine reward program
                reward_program = None
                if reward_type == RewardType.POINTS_PER_DOLLAR:
                    reward_program = self.reward_program
                
                # Foreign transaction fee
                foreign_transaction_fee = 0.03
                if "sapphire" in card_name.lower():
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
            raise ValueError("Chase scraper failed: Unable to fetch any card data. Check network connection and Chase website availability.")
        
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
        }
        
        # Look for structured rewards sections
        reward_sections = soup.find_all(["section", "div"], 
                                       class_=re.compile(r'reward|earning|benefit', re.I),
                                       id=re.compile(r'reward|earning|benefit', re.I))
        
        # Also check for lists with reward data
        reward_lists = soup.find_all(["ul", "ol"], class_=re.compile(r'reward|earning|benefit', re.I))
        
        all_sections = reward_sections + reward_lists
        
        for section in all_sections:
            section_text = section.get_text()
            section_lower = section_text.lower()
            
            # Skip if this looks like signup bonus or marketing fluff
            if any(phrase in section_lower for phrase in ["sign up", "welcome bonus", "introductory", "new cardmember"]):
                continue
            
            # Extract multiplier
            multiplier = None
            multiplier_patterns = [
                r'(\d+(?:\.\d+)?)\s*x\s*points?\s*(?:per dollar|on)',
                r'(\d+(?:\.\d+)?)\s*points?\s*per dollar',
                r'(\d+(?:\.\d+)?)\s*%\s*cash\s*back',
                r'earn\s*(\d+(?:\.\d+)?)\s*x',
                r'(\d+(?:\.\d+)?)\s*points?\s*per\s*\$1',
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
            activation_required = "activate" in section_lower or "enrollment" in section_lower
            
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
                stacking_rules="Activation required" if activation_required else None,
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
        Scrape earning rules for a Chase card from its detail page.
        
        Args:
            card: CardProduct to get rules for
            
        Returns:
            List of EarningRule objects
            
        Raises:
            ValueError: If scraping or parsing fails
        """
        if not card.official_url:
            raise ValueError(f"No URL available for {card.name}")
        
        html = self.fetch_url(card.official_url)
        if not html:
            raise ValueError(f"Unable to fetch earning rules for {card.name} from {card.official_url}")
        
        soup = self.parse_html(html)
        rules = self._parse_earning_rules_from_html(soup, card)
        
        if not rules:
            raise ValueError(f"Unable to parse earning rules for {card.name}. Page structure may have changed.")
        
        logger.info(f"Parsed {len(rules)} earning rules for {card.name}")
        return rules
