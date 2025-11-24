"""
Structured rule parser for NerdWallet pages.

This parser uses a rule-based approach to extract reward rules
from NerdWallet's structured format, avoiding comparison tables
and marketing text.
"""

import re
import logging
from typing import List, Optional
from bs4 import BeautifulSoup

from models import EarningRule, RewardType, Cap
from rule_engine import RuleParser, ParsedRewardRule

logger = logging.getLogger(__name__)


class NerdWalletRuleParser:
    """Parses structured reward rules from NerdWallet pages."""
    
    def __init__(self, reward_type: RewardType):
        self.reward_type = reward_type
    
    def parse_from_html(self, html: str, card_id: str) -> List[EarningRule]:
        """
        Parse earning rules from NerdWallet HTML.
        
        Looks for structured reward sections like:
        "Rewards:
         6% cash back at U.S. supermarkets, on up to $6,000 in spending per year.
         6% cash back on select U.S. streaming subscriptions.
         3% cash back at U.S. gas stations.
         3% cash back on transit.
         1% cash back on other purchases."
        """
        soup = BeautifulSoup(html, 'html.parser')
        rules = []
        
        # Strategy 1: Look for structured "Rewards:" sections
        # NerdWallet often has a section with "Rewards:" header followed by a list
        rewards_section = self._find_rewards_section(soup)
        if rewards_section:
            parsed_rules = RuleParser.parse_reward_text(rewards_section, self.reward_type)
            for parsed in parsed_rules:
                rule = self._convert_to_earning_rule(parsed, card_id)
                if rule:
                    rules.append(rule)
        
        # Strategy 2: Look for bulleted lists with reward information
        if not rules:
            reward_lists = self._find_reward_lists(soup)
            for list_text in reward_lists:
                parsed_rules = RuleParser.parse_reward_text(list_text, self.reward_type)
                for parsed in parsed_rules:
                    rule = self._convert_to_earning_rule(parsed, card_id)
                    if rule:
                        rules.append(rule)
        
        # Strategy 3: Look for definition lists (dl/dt/dd) with rewards
        if not rules:
            dl_rules = self._parse_definition_list(soup)
            for parsed in dl_rules:
                rule = self._convert_to_earning_rule(parsed, card_id)
                if rule:
                    rules.append(rule)
        
        # Deduplicate rules
        rules = self._deduplicate_rules(rules)
        
        logger.info(f"Parsed {len(rules)} structured reward rules")
        return rules
    
    def _find_rewards_section(self, soup: BeautifulSoup) -> Optional[str]:
        """Find the main rewards section text."""
        # Look for "Rewards:" heading
        headings = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b'], 
                                string=re.compile(r'^Rewards?:?\s*$', re.I))
        
        for heading in headings:
            # Get the next sibling or parent's text
            parent = heading.parent
            if parent:
                # Get text from parent, but only after the heading
                text = parent.get_text(separator='\n')
                # Extract text after "Rewards:"
                match = re.search(r'Rewards?:?\s*\n(.+)', text, re.DOTALL | re.I)
                if match:
                    return match.group(1).strip()
        
        return None
    
    def _find_reward_lists(self, soup: BeautifulSoup) -> List[str]:
        """Find lists that contain reward information."""
        reward_lists = []
        
        # Look for ul/ol elements near "Rewards" or "Earning" text
        all_lists = soup.find_all(['ul', 'ol'])
        
        for list_elem in all_lists:
            # Check if this list is near reward-related text
            parent_text = list_elem.parent.get_text() if list_elem.parent else ''
            list_text = list_elem.get_text(separator='\n')
            
            # Check if it contains reward patterns
            if re.search(r'\d+%\s*cash\s*back|\d+x\s*points?', list_text, re.I):
                # Check if parent mentions rewards
                if re.search(r'reward|earning', parent_text, re.I):
                    reward_lists.append(list_text)
        
        return reward_lists
    
    def _parse_definition_list(self, soup: BeautifulSoup) -> List[ParsedRewardRule]:
        """Parse definition lists (dl/dt/dd) for reward information."""
        rules = []
        
        dls = soup.find_all('dl')
        for dl in dls:
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            
            for dt, dd in zip(dts, dds):
                term = dt.get_text().strip()
                definition = dd.get_text().strip()
                
                # Check if this looks like a reward rule
                if re.search(r'\d+%\s*cash\s*back|\d+x\s*points?', definition, re.I):
                    parsed = RuleParser.parse_reward_text(definition, self.reward_type)
                    rules.extend(parsed)
        
        return rules
    
    def _convert_to_earning_rule(self, parsed: ParsedRewardRule, card_id: str) -> Optional[EarningRule]:
        """Convert ParsedRewardRule to EarningRule."""
        # Validate multiplier
        if self.reward_type == RewardType.CASHBACK_PERCENT:
            if parsed.multiplier > 10:
                logger.warning(f"Skipping invalid cashback rate {parsed.multiplier}%")
                return None
            if parsed.multiplier >= 15:
                logger.warning(f"Skipping impossible cashback rate {parsed.multiplier}%")
                return None
        
        # Build caps
        caps = []
        if parsed.cap_amount:
            caps.append(Cap(
                amount_dollars=parsed.cap_amount,
                period=parsed.cap_period or 'year'
            ))
        
        return EarningRule(
            card_id=card_id,
            description=parsed.description,
            merchant_categories=parsed.category_keywords,
            multiplier=parsed.multiplier,
            reward_type=self.reward_type,
            caps=caps,
            is_rotating=parsed.is_rotating
        )
    
    def _deduplicate_rules(self, rules: List[EarningRule]) -> List[EarningRule]:
        """Remove duplicate rules."""
        seen = set()
        unique = []
        
        for rule in rules:
            # Create a key from multiplier, categories, and caps
            key = (
                rule.multiplier,
                tuple(sorted(rule.merchant_categories)),
                tuple(sorted([(c.amount_dollars, c.period) for c in rule.caps]))
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(rule)
        
        return unique

