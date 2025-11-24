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
from models import CardProduct, EarningRule, RewardType

# For scraper_job, we run it directly with proper PYTHONPATH setup
def scrape_all_cards_and_rules():
    """Scrape all cards and rules from all issuers and save to disk."""
    import subprocess
    
    scraper_script = os.path.join(current_dir, "scraper_job.py")
    
    if not os.path.exists(scraper_script):
        logger.error(f"scraper_job.py not found at {scraper_script}")
        return False
    
    try:
        logger.info("Running scraper_job.py...")
        
        # On Render: files are in /opt/render/project/src/ directly
        # For relative imports (from ...models) to work, we need:
        # 1. parent_dir in PYTHONPATH (so src/ can be treated as package root)
        # 2. current_dir in PYTHONPATH (for direct imports)
        # This makes scrapers/scrapers/issuers/chase_manual.py able to do "from ...models"
        # because Python will resolve "..." relative to the package root
        
        env = os.environ.copy()
        pythonpath_parts = []
        
        # Add parent_dir first - this is critical for relative imports
        # When scrapers do "from ...models", Python needs to know where the package root is
        if parent_dir:
            pythonpath_parts.append(parent_dir)
        
        # Add current_dir for direct imports
        if current_dir:
            pythonpath_parts.append(current_dir)
        
        # Preserve existing PYTHONPATH
        existing_pythonpath = env.get('PYTHONPATH', '')
        if existing_pythonpath:
            pythonpath_parts.append(existing_pythonpath)
        
        env['PYTHONPATH'] = os.pathsep.join(pythonpath_parts)
        
        logger.info(f"PYTHONPATH: {env['PYTHONPATH']}")
        logger.info(f"Running from: {current_dir}")
        logger.info(f"Script: {scraper_script}")
        
        # On Render: files are in /opt/render/project/src/ directly
        # To make relative imports work, we need to make src/ importable as credit_card_optimizer
        # Solution: Create a temporary package structure by modifying PYTHONPATH
        # and running Python with -m flag from parent directory
        
        # Create credit_card_optimizer symlink/copy in parent (if possible)
        # OR: Run Python with modified import path
        
        # Best solution: Run as module from parent with proper setup
        # We'll create a small wrapper that sets up the environment
        
        # For now, run directly with comprehensive PYTHONPATH
        # The key is ensuring parent_dir is in PYTHONPATH so relative imports resolve
        result = subprocess.run(
            [sys.executable, scraper_script],
            cwd=current_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes - scraping 97 cards takes time
        )
        
        if result.returncode == 0:
            logger.info("✅ Scraper job completed successfully")
            if result.stdout:
                logger.info(f"Scraper output: {result.stdout[-500:]}")  # Last 500 chars
            return True
        else:
            logger.error(f"❌ Scraper job failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"Error: {result.stderr[-500:]}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Scraper job timed out after 10 minutes")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to run scraper job: {e}", exc_info=True)
        return False

# Now import api components
import logging
import threading
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime, time

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
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

# Background scheduler for daily refresh
_scheduler = None

def run_daily_refresh():
    """Background job that runs daily at midnight to refresh card data."""
    logger.info("🔄 Daily refresh job started (runs at midnight)")
    try:
        success = scrape_all_cards_and_rules()
        if success:
            # Reload cache with fresh data
            load_all_cards_and_rules(force_refresh=True)
            logger.info("✅ Daily refresh completed successfully")
        else:
            logger.error("❌ Daily refresh failed - using cached data")
    except Exception as e:
        logger.error(f"❌ Error in daily refresh job: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler
    
    logger.info("Loading cards and rules...")
    cards, rules = load_all_cards_and_rules()
    
    # If no data exists, run scraper once on startup
    if not cards and not rules:
        logger.warning("⚠️  No card data found. Running initial scrape...")
        logger.info("This will take 2-5 minutes. Please wait...")
        try:
            success = scrape_all_cards_and_rules()
            if success:
                cards, rules = load_all_cards_and_rules(force_refresh=True)
                logger.info(f"✅ Initial scrape completed! Loaded {len(cards)} cards and {len(rules)} rules")
            else:
                logger.error("❌ Initial scrape failed. API will work once data is available.")
        except Exception as e:
            logger.error(f"❌ Error during initial scrape: {e}", exc_info=True)
    else:
        logger.info(f"✅ Cards and rules loaded successfully ({len(cards)} cards, {len(rules)} rules)")
    
    # Set up daily scheduler (runs at midnight UTC)
    logger.info("Setting up daily refresh scheduler (runs at midnight UTC)...")
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        run_daily_refresh,
        trigger=CronTrigger(hour=0, minute=0),  # Midnight UTC
        id='daily_refresh',
        name='Daily card data refresh',
        replace_existing=True
    )
    _scheduler.start()
    logger.info("✅ Daily refresh scheduler started (will run at 00:00 UTC daily)")
    
    yield
    
    # Shutdown scheduler
    if _scheduler:
        _scheduler.shutdown()
        logger.info("Scheduler shut down")
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
    """
    Manually trigger data refresh (admin only).
    
    Note: Data also refreshes automatically daily at midnight UTC.
    This endpoint is for emergency manual refreshes only.
    """
    logger.info("Manual refresh triggered via API")
    try:
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
    max_results: int = Query(MAX_RECOMMENDATIONS, ge=1, le=50, description="Maximum number of recommendations"),
    issuer: Optional[str] = Query(None, description="Filter by issuer name (e.g., 'Chase', 'American Express')"),
    reward_type: Optional[str] = Query(None, description="Filter by reward type: 'cashback', 'points', 'miles'"),
    network: Optional[str] = Query(None, description="Filter by network: 'VISA', 'MASTERCARD', 'AMEX', 'DISCOVER'"),
    include_business: bool = Query(False, description="Include business cards (default: False, only personal cards)")
):
    try:
        all_cards, all_rules = load_all_cards_and_rules()
        
        recommendation = find_best_cards_for_query(
            query=query,
            all_cards=all_cards,
            all_rules=all_rules,
            max_results=max_results * 2  # Get more results, then filter
        )
        
        # Apply filters
        filtered_cards = recommendation.candidate_cards
        
        # Filter by business/personal (default: personal only)
        if not include_business:
            filtered_cards = [cs for cs in filtered_cards if not cs.card.is_business_card]
        
        if issuer:
            filtered_cards = [cs for cs in filtered_cards if issuer.lower() in cs.card.issuer.name.lower()]
        if reward_type:
            reward_type_map = {
                'cashback': RewardType.CASHBACK_PERCENT,
                'points': RewardType.POINTS_PER_DOLLAR,
                'miles': RewardType.MILES_PER_DOLLAR
            }
            target_type = reward_type_map.get(reward_type.lower())
            if target_type:
                filtered_cards = [cs for cs in filtered_cards if cs.card.type == target_type]
        if network:
            from models import CardNetwork
            network_map = {
                'visa': CardNetwork.VISA,
                'mastercard': CardNetwork.MASTERCARD,
                'amex': CardNetwork.AMEX,
                'american express': CardNetwork.AMEX,
                'discover': CardNetwork.DISCOVER
            }
            target_network = network_map.get(network.lower())
            if target_network:
                filtered_cards = [cs for cs in filtered_cards if cs.card.network == target_network]
        
        # Limit to max_results after filtering
        filtered_cards = filtered_cards[:max_results]
        
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
                for card_score in filtered_cards
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

