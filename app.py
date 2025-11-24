"""
Standalone app.py file for Render deployment.
This file imports everything directly without package structure issues.
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add parent directory to path for package imports
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import directly (we're in the credit_card_optimizer directory)
# This avoids package import issues
import config
import data_manager
import engine
import models

# Import what we need
from config import MAX_RECOMMENDATIONS, OFFLINE_MODE, USE_CACHE
from data_manager import DataManager
from engine import find_best_cards_for_query
from models import CardProduct, EarningRule

# For scraper_job, we implement it directly using direct imports
def scrape_all_cards_and_rules():
    """Scrape all cards and rules from all issuers and save to disk."""
    # Add scrapers directory to path
    scrapers_dir = os.path.join(current_dir, "scrapers")
    if scrapers_dir not in sys.path:
        sys.path.insert(0, scrapers_dir)
    
    try:
        # Import scrapers using direct imports
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
        
        logger.info("Starting card and rule scraping job...")
        
        all_cards = []
        all_rules = []
        
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
        
        # Save to disk
        try:
            _data_manager.save_cards_and_rules(all_cards, all_rules)
            logger.info(f"✅ Successfully scraped and saved {len(all_cards)} cards and {len(all_rules)} rules")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save data: {e}", exc_info=True)
            return False
    except Exception as e:
        logger.error(f"Failed to import scrapers: {e}", exc_info=True)
        return False

# Now import api components
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global cache
_cards_cache: Optional[List[CardProduct]] = None
_rules_cache: Optional[List[EarningRule]] = None
_data_manager = DataManager()

def load_all_cards_and_rules(force_refresh: bool = False) -> tuple[List[CardProduct], List[EarningRule]]:
    global _cards_cache, _rules_cache
    
    if not force_refresh and _cards_cache is not None and _rules_cache is not None:
        return _cards_cache, _rules_cache
    
    try:
        cards, rules = _data_manager.load_cards_and_rules()
        if not cards and not rules:
            logger.warning("No card data found. Run scraper_job.py first.")
        _cards_cache = cards
        _rules_cache = rules
        return cards, rules
    except Exception as e:
        logger.error(f"Failed to load cards and rules: {e}", exc_info=True)
        return [], []

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading cards and rules...")
    load_all_cards_and_rules()
    logger.info("Cards and rules loaded successfully")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="Credit Card Optimizer API",
    description="API for finding the best credit card for purchases based on rewards",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
static_dir = os.path.join(current_dir, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "API is running. Visit /docs for API documentation."}

# Response models
class CardIssuerResponse(BaseModel):
    name: str
    website_url: str
    support_contact: Optional[str] = None

class RewardProgramResponse(BaseModel):
    id: str
    name: str
    base_point_value_cents: float
    notes: Optional[str] = None

class CardResponse(BaseModel):
    id: str
    issuer: CardIssuerResponse
    name: str
    network: str
    type: str
    annual_fee: float
    foreign_transaction_fee: float
    reward_program: Optional[RewardProgramResponse] = None
    official_url: Optional[str] = None

class CardScoreResponse(BaseModel):
    card: CardResponse
    effective_rate_cents_per_dollar: float
    explanation: str
    notes: List[str] = Field(default_factory=list)

class RecommendationResponse(BaseModel):
    merchant_query: str
    resolved_categories: List[str]
    candidate_cards: List[CardScoreResponse]
    explanation: str

def card_to_response(card: CardProduct) -> CardResponse:
    return CardResponse(
        id=card.id,
        issuer=CardIssuerResponse(
            name=card.issuer.name,
            website_url=card.issuer.website_url,
            support_contact=card.issuer.support_contact
        ),
        name=card.name,
        network=card.network.value,
        type=card.type.value,
        annual_fee=card.annual_fee,
        foreign_transaction_fee=card.foreign_transaction_fee,
        reward_program=RewardProgramResponse(
            id=card.reward_program.id,
            name=card.reward_program.name,
            base_point_value_cents=card.reward_program.base_point_value_cents,
            notes=card.reward_program.notes
        ) if card.reward_program else None,
        official_url=card.official_url
    )

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "service": "Credit Card Optimizer API",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health():
    cards, rules = load_all_cards_and_rules()
    last_updated = _data_manager.get_last_updated()
    cache_expired = _data_manager.is_cache_expired()
    
    return {
        "status": "healthy",
        "cards_loaded": len(cards),
        "rules_loaded": len(rules),
        "last_updated": last_updated.isoformat() if last_updated else None,
        "cache_expired": cache_expired,
        "cache_enabled": USE_CACHE,
        "offline_mode": OFFLINE_MODE
    }

@app.post("/api/refresh", tags=["Admin"])
async def refresh_data():
    try:
        logger.info("Manual refresh triggered via API")
        success = scrape_all_cards_and_rules()
        
        if success:
            load_all_cards_and_rules(force_refresh=True)
            return {
                "status": "success",
                "message": "Card data refreshed successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to refresh card data. Check logs for details."
            )
    except Exception as e:
        logger.error(f"Error refreshing data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error refreshing data: {str(e)}"
        )

@app.get("/api/recommend", response_model=RecommendationResponse, tags=["Recommendations"])
async def get_recommendation(
    query: str = Query(..., description="Merchant name or category"),
    max_results: int = Query(MAX_RECOMMENDATIONS, ge=1, le=20, description="Maximum number of recommendations")
):
    try:
        all_cards, all_rules = load_all_cards_and_rules()
        
        recommendation = find_best_cards_for_query(
            query=query,
            all_cards=all_cards,
            all_rules=all_rules,
            max_results=max_results
        )
        
        return RecommendationResponse(
            merchant_query=recommendation.merchant_query,
            resolved_categories=recommendation.resolved_categories,
            candidate_cards=[
                CardScoreResponse(
                    card=card_to_response(card_score.card),
                    effective_rate_cents_per_dollar=card_score.effective_rate_cents_per_dollar,
                    explanation=card_score.explanation,
                    notes=card_score.notes or []
                )
                for card_score in recommendation.candidate_cards
            ],
            explanation=recommendation.explanation
        )
    except Exception as e:
        logger.error(f"Error processing recommendation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing recommendation: {str(e)}")

@app.get("/api/cards", response_model=List[CardResponse], tags=["Cards"])
async def list_cards():
    try:
        all_cards, _ = load_all_cards_and_rules()
        return [card_to_response(card) for card in all_cards]
    except Exception as e:
        logger.error(f"Error listing cards: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing cards: {str(e)}")

@app.get("/api/stats", tags=["Stats"])
async def get_stats():
    try:
        all_cards, all_rules = load_all_cards_and_rules()
        
        issuers = {}
        networks = {}
        reward_types = {}
        
        for card in all_cards:
            issuer_name = card.issuer.name
            issuers[issuer_name] = issuers.get(issuer_name, 0) + 1
            
            network = card.network.value
            networks[network] = networks.get(network, 0) + 1
            
            reward_type = card.type.value
            reward_types[reward_type] = reward_types.get(reward_type, 0) + 1
        
        return {
            "total_cards": len(all_cards),
            "total_rules": len(all_rules),
            "issuers": issuers,
            "networks": networks,
            "reward_types": reward_types
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

