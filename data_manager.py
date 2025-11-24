"""
Data persistence layer for cards and rules.

Saves scraped data to JSON files so the API doesn't need to scrape on every startup.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

from models import CardProduct, EarningRule

logger = logging.getLogger(__name__)

DATA_DIR = Path(".data")
CARDS_FILE = DATA_DIR / "cards.json"
RULES_FILE = DATA_DIR / "rules.json"
METADATA_FILE = DATA_DIR / "metadata.json"

# Cache expiration: refresh data if older than 24 hours
CACHE_EXPIRATION_HOURS = 24


class DataManager:
    """Manages persistence of card and rule data."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize data manager.
        
        Args:
            data_dir: Directory for data files (default: .data)
        """
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cards_file = self.data_dir / "cards.json"
        self.rules_file = self.data_dir / "rules.json"
        self.metadata_file = self.data_dir / "metadata.json"
    
    def save_cards_and_rules(
        self, 
        cards: List[CardProduct], 
        rules: List[EarningRule]
    ) -> None:
        """
        Save cards and rules to JSON files.
        
        Args:
            cards: List of CardProduct objects
            rules: List of EarningRule objects
        """
        try:
            # Convert to dict format for JSON serialization
            cards_data = [self._card_to_dict(card) for card in cards]
            rules_data = [self._rule_to_dict(rule) for rule in rules]
            
            # Save cards
            with open(self.cards_file, "w", encoding="utf-8") as f:
                json.dump(cards_data, f, indent=2, default=str)
            
            # Save rules
            with open(self.rules_file, "w", encoding="utf-8") as f:
                json.dump(rules_data, f, indent=2, default=str)
            
            # Save metadata
            metadata = {
                "last_updated": datetime.now().isoformat(),
                "cards_count": len(cards),
                "rules_count": len(rules),
                "cache_expires_at": (datetime.now() + timedelta(hours=CACHE_EXPIRATION_HOURS)).isoformat()
            }
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Saved {len(cards)} cards and {len(rules)} rules to {self.data_dir}")
        except Exception as e:
            logger.error(f"Failed to save cards and rules: {e}", exc_info=True)
            raise
    
    def load_cards_and_rules(self) -> Tuple[List[CardProduct], List[EarningRule]]:
        """
        Load cards and rules from JSON files.
        
        Returns:
            Tuple of (cards, rules)
        """
        cards: List[CardProduct] = []
        rules: List[EarningRule] = []
        
        try:
            # Load cards
            if self.cards_file.exists():
                with open(self.cards_file, "r", encoding="utf-8") as f:
                    cards_data = json.load(f)
                    cards = [self._dict_to_card(card_dict) for card_dict in cards_data]
            
            # Load rules
            if self.rules_file.exists():
                with open(self.rules_file, "r", encoding="utf-8") as f:
                    rules_data = json.load(f)
                    rules = [self._dict_to_rule(rule_dict) for rule_dict in rules_data]
            
            logger.info(f"Loaded {len(cards)} cards and {len(rules)} rules from {self.data_dir}")
        except Exception as e:
            logger.error(f"Failed to load cards and rules: {e}", exc_info=True)
        
        return cards, rules
    
    def is_cache_expired(self) -> bool:
        """
        Check if cached data has expired.
        
        Returns:
            True if cache is expired or doesn't exist
        """
        if not self.metadata_file.exists():
            return True
        
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            expires_at_str = metadata.get("cache_expires_at")
            if not expires_at_str:
                return True
            
            expires_at = datetime.fromisoformat(expires_at_str)
            return datetime.now() >= expires_at
        except Exception as e:
            logger.warning(f"Failed to check cache expiration: {e}")
            return True
    
    def get_last_updated(self) -> Optional[datetime]:
        """Get timestamp of last update."""
        if not self.metadata_file.exists():
            return None
        
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            last_updated_str = metadata.get("last_updated")
            if last_updated_str:
                return datetime.fromisoformat(last_updated_str)
        except Exception as e:
            logger.warning(f"Failed to get last updated time: {e}")
        
        return None
    
    def _card_to_dict(self, card: CardProduct) -> dict:
        """Convert CardProduct to dictionary."""
        return {
            "id": card.id,
            "issuer": {
                "name": card.issuer.name,
                "website_url": card.issuer.website_url,
                "support_contact": card.issuer.support_contact,
            },
            "name": card.name,
            "network": card.network.value,
            "type": card.type.value,
            "annual_fee": card.annual_fee,
            "foreign_transaction_fee": card.foreign_transaction_fee,
            "reward_program": {
                "id": card.reward_program.id,
                "name": card.reward_program.name,
                "base_point_value_cents": card.reward_program.base_point_value_cents,
                "notes": card.reward_program.notes,
            } if card.reward_program else None,
            "official_url": card.official_url,
            "is_business_card": card.is_business_card,
            "metadata": card.metadata,
        }
    
    def _dict_to_card(self, card_dict: dict) -> CardProduct:
        """Convert dictionary to CardProduct."""
        from models import CardIssuer, RewardProgram, CardNetwork, RewardType
        
        issuer_data = card_dict["issuer"]
        issuer = CardIssuer(
            name=issuer_data["name"],
            website_url=issuer_data["website_url"],
            support_contact=issuer_data.get("support_contact"),
        )
        
        reward_program = None
        if card_dict.get("reward_program"):
            rp_data = card_dict["reward_program"]
            reward_program = RewardProgram(
                id=rp_data["id"],
                name=rp_data["name"],
                base_point_value_cents=rp_data["base_point_value_cents"],
                notes=rp_data.get("notes"),
            )
        
        return CardProduct(
            id=card_dict["id"],
            issuer=issuer,
            name=card_dict["name"],
            network=CardNetwork(card_dict["network"]),
            type=RewardType(card_dict["type"]),
            annual_fee=card_dict["annual_fee"],
            foreign_transaction_fee=card_dict["foreign_transaction_fee"],
            reward_program=reward_program,
            official_url=card_dict.get("official_url"),
            is_business_card=card_dict.get("is_business_card", False),
            metadata=card_dict.get("metadata", {}),
        )
    
    def _rule_to_dict(self, rule: EarningRule) -> dict:
        """Convert EarningRule to dictionary."""
        return {
            "card_id": rule.card_id,
            "description": rule.description,
            "merchant_categories": rule.merchant_categories,
            "merchant_names": rule.merchant_names,
            "mcc_list": rule.mcc_list,
            "multiplier": rule.multiplier,
            "reward_type": rule.reward_type.value,
            "caps": [
                {
                    "amount_dollars": cap.amount_dollars,
                    "period": cap.period,
                }
                for cap in rule.caps
            ],
            "is_rotating": rule.is_rotating,
            "is_intro_offer_only": rule.is_intro_offer_only,
            "stacking_rules": rule.stacking_rules,
        }
    
    def _dict_to_rule(self, rule_dict: dict) -> EarningRule:
        """Convert dictionary to EarningRule."""
        from models import Cap, RewardType
        
        caps = [
            Cap(
                amount_dollars=cap_dict["amount_dollars"],
                period=cap_dict["period"],
            )
            for cap_dict in rule_dict.get("caps", [])
        ]
        
        return EarningRule(
            card_id=rule_dict["card_id"],
            description=rule_dict["description"],
            merchant_categories=rule_dict.get("merchant_categories", []),
            merchant_names=rule_dict.get("merchant_names", []),
            mcc_list=rule_dict.get("mcc_list", []),
            multiplier=rule_dict["multiplier"],
            reward_type=RewardType(rule_dict["reward_type"]),
            caps=caps,
            is_rotating=rule_dict.get("is_rotating", False),
            is_intro_offer_only=rule_dict.get("is_intro_offer_only", False),
            stacking_rules=rule_dict.get("stacking_rules"),
        )

