"""
Base scraper class with shared functionality.

Provides common methods for fetching, retrying, and parsing HTML.
"""

import logging
import os
import time
from abc import ABC, abstractmethod
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Handle imports for both package and flat structure
try:
    from ..config import (
        MAX_RETRIES,
        RATE_LIMIT_DELAY,
        REQUEST_TIMEOUT,
        RETRY_DELAY_SECONDS,
        USER_AGENT,
    )
    from ..models import CardProduct, EarningRule
except ImportError:
    # Fallback for flat structure (Render): add root to path
    import sys
    from pathlib import Path
    current_file = Path(__file__).resolve()
    # Go up 2 levels: scrapers/base.py -> root
    root_dir = current_file.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    from config import (
        MAX_RETRIES,
        RATE_LIMIT_DELAY,
        REQUEST_TIMEOUT,
        RETRY_DELAY_SECONDS,
        USER_AGENT,
    )
    from models import CardProduct, EarningRule

from .cache import ScraperCache

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for issuer-specific scrapers."""
    
    def __init__(self, issuer_name: str, use_cache: bool = True, offline_mode: bool = False, use_selenium: bool = False):
        """
        Initialize the scraper.
        
        Args:
            issuer_name: Name of the card issuer
            use_cache: Whether to use cache for responses
            offline_mode: If True, only use cache, don't make network requests
            use_selenium: If True, use Selenium for JavaScript-rendered pages
        """
        self.issuer_name = issuer_name
        self.use_cache = use_cache
        self.offline_mode = offline_mode
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.cache = ScraperCache() if use_cache else None
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.driver = None
    
    def _get_selenium_driver(self):
        """Get or create Selenium WebDriver."""
        if not self.use_selenium:
            return None
        
        if self.driver is None:
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={USER_AGENT}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.set_page_load_timeout(REQUEST_TIMEOUT)
            except Exception as e:
                logger.error(f"Failed to initialize Selenium: {e}")
                self.use_selenium = False
                return None
        
        return self.driver
    
    def fetch_url(self, url: str, retries: int = MAX_RETRIES, wait_for_element: Optional[str] = None) -> Optional[str]:
        """
        Fetch a URL with retry logic, rate limiting, and caching.
        Supports both regular HTTP and Selenium for JavaScript-rendered pages.
        
        Args:
            url: URL to fetch
            retries: Number of retry attempts
            wait_for_element: CSS selector to wait for (Selenium only)
            
        Returns:
            HTML content as string, or None if failed
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get(url)
            if cached:
                logger.debug(f"Cache hit for {url}")
                return cached
        
        # Offline mode: only use cache
        if self.offline_mode:
            logger.warning(f"Offline mode: No cache available for {url}")
            return None
        
        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)
        
        # Use Selenium for JavaScript-rendered pages
        if self.use_selenium:
            driver = self._get_selenium_driver()
            if driver:
                try:
                    driver.get(url)
                    
                    # Wait for specific element if provided
                    if wait_for_element:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
                        )
                    else:
                        # Default: wait a bit for JS to render
                        time.sleep(2)
                    
                    html = driver.page_source
                    
                    # Cache the response
                    if self.cache:
                        self.cache.set(url, html)
                    
                    return html
                except Exception as e:
                    logger.warning(f"Selenium fetch failed for {url}: {e}")
                    # Fall back to regular requests
                    self.use_selenium = False
        
        # Regular HTTP request
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                html = response.text
                
                # Cache the response
                if self.cache:
                    self.cache.set(url, html)
                
                return html
            except requests.RequestException as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{retries} failed for {url}: {e}"
                )
                if attempt < retries - 1:
                    time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
        return None
    
    def __del__(self):
        """Clean up Selenium driver."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML string into BeautifulSoup object.
        
        Args:
            html: HTML content
            
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, "html.parser")
    
    @abstractmethod
    def scrape_cards(self) -> List[CardProduct]:
        """
        Scrape all cards for this issuer.
        
        Returns:
            List of CardProduct objects
        """
        pass
    
    @abstractmethod
    def scrape_earning_rules(self, card: CardProduct) -> List[EarningRule]:
        """
        Scrape earning rules for a specific card.
        
        Args:
            card: CardProduct to get rules for
            
        Returns:
            List of EarningRule objects
        """
        pass

