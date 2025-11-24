"""
Caching layer for scrapers to enable offline mode and reduce API calls.
"""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ScraperCache:
    """Simple file-based cache for scraper responses."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory for cache files (default: .cache/scrapers)
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path(".cache") / "scrapers"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL."""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_path(self, url: str) -> Path:
        """Get cache file path for URL."""
        key = self._get_cache_key(url)
        return self.cache_dir / f"{key}.html"
    
    def get(self, url: str) -> Optional[str]:
        """
        Get cached HTML for URL.
        
        Args:
            url: URL to look up
            
        Returns:
            Cached HTML or None if not found
        """
        cache_path = self._get_cache_path(url)
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed to read cache for {url}: {e}")
        return None
    
    def set(self, url: str, html: str) -> None:
        """
        Cache HTML for URL.
        
        Args:
            url: URL to cache
            html: HTML content to cache
        """
        cache_path = self._get_cache_path(url)
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            logger.warning(f"Failed to write cache for {url}: {e}")
    
    def clear(self) -> None:
        """Clear all cached files."""
        for cache_file in self.cache_dir.glob("*.html"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete cache file {cache_file}: {e}")
    
    def exists(self, url: str) -> bool:
        """Check if URL is cached."""
        return self._get_cache_path(url).exists()

