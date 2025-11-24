"""
FastAPI web application for credit card optimization service.

Provides REST API endpoints for querying credit card recommendations.
"""

import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import os

from .config import MAX_RECOMMENDATIONS, OFFLINE_MODE, USE_CACHE
from .data_manager import DataManager
from .engine import find_best_cards_for_query
from .models import CardProduct, EarningRule
from .scraper_job import scrape_all_cards_and_rules

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global cache for cards and rules (in-memory cache)
_cards_cache: Optional[List[CardProduct]] = None
_rules_cache: Optional[List[EarningRule]] = None
_data_manager = DataManager()


def load_all_cards_and_rules(force_refresh: bool = False) -> tuple[List[CardProduct], List[EarningRule]]:
    """
    Load cards and rules from persisted data (not scraping).
    
    This loads from disk (.data/cards.json and .data/rules.json) which
    should be populated by the scraper_job.py running periodically.
    
    Args:
        force_refresh: If True, reload from disk even if cached in memory
        
    Returns:
        Tuple of (all_cards, all_rules)
    """
    global _cards_cache, _rules_cache
    
    # Return in-memory cache if available and not forcing refresh
    if not force_refresh and _cards_cache is not None and _rules_cache is not None:
        return _cards_cache, _rules_cache
    
    # Load from disk
    try:
        cards, rules = _data_manager.load_cards_and_rules()
        
        # If no data exists, log warning but return empty lists
        if not cards and not rules:
            logger.warning(
                "No card data found. Run scraper_job.py first to populate data. "
                "API will work but return no recommendations."
            )
        
        _cards_cache = cards
        _rules_cache = rules
        
        return cards, rules
    except Exception as e:
        logger.error(f"Failed to load cards and rules: {e}", exc_info=True)
        return [], []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load cards and rules on startup."""
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files if they exist
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/", include_in_schema=False)
    async def serve_index():
        """Serve the frontend HTML page."""
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "API is running. Visit /docs for API documentation."}


# Pydantic models for API responses
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
    """Convert CardProduct to API response model."""
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
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Credit Card Optimizer API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health():
    """Detailed health check."""
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
    """
    Manually trigger a refresh of card data.
    
    This will scrape all issuers and update the persisted data.
    Use sparingly to avoid rate limiting.
    """
    try:
        logger.info("Manual refresh triggered via API")
        success = scrape_all_cards_and_rules()
        
        if success:
            # Reload from disk
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
    query: str = Query(..., description="Merchant name or category (e.g., 'Amazon', 'groceries')"),
    max_results: int = Query(MAX_RECOMMENDATIONS, ge=1, le=20, description="Maximum number of recommendations")
):
    """
    Get credit card recommendations for a merchant or category.
    
    Examples:
    - /api/recommend?query=Amazon
    - /api/recommend?query=groceries&max_results=3
    - /api/recommend?query=Macy's
    """
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
    """List all available credit cards."""
    try:
        all_cards, _ = load_all_cards_and_rules()
        return [card_to_response(card) for card in all_cards]
    except Exception as e:
        logger.error(f"Error listing cards: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing cards: {str(e)}")


@app.get("/api/stats", tags=["Stats"])
async def get_stats():
    """Get statistics about loaded cards and rules."""
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
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# For Render deployment - run as module
def create_app():
    """Factory function for Render deployment."""
    return app

