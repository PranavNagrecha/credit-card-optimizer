#!/usr/bin/env python3
"""
Script to verify and find correct URLs for credit card pages.
"""

import requests
from bs4 import BeautifulSoup
import time

def test_url(url, expected_keywords=None):
    """Test if a URL is valid and contains expected content."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        r = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('title')
            title_text = title.text if title else "No title"
            
            # Check if it's a valid card page (not a 404 or error page)
            is_valid = True
            error_indicators = ['page not found', '404', 'error', 'not available']
            if any(indicator in title_text.lower() for indicator in error_indicators):
                is_valid = False
            
            # Check for expected keywords if provided
            if expected_keywords:
                page_text = r.text.lower()
                if not any(keyword.lower() in page_text for keyword in expected_keywords):
                    is_valid = False
            
            return {
                'status': r.status_code,
                'valid': is_valid,
                'title': title_text[:80],
                'final_url': r.url
            }
        else:
            return {
                'status': r.status_code,
                'valid': False,
                'title': f'HTTP {r.status_code}',
                'final_url': r.url
            }
    except Exception as e:
        return {
            'status': 'ERROR',
            'valid': False,
            'title': str(e)[:80],
            'final_url': url
        }

# Test URLs from all issuers
test_cases = {
    'Chase': [
        ('https://www.chase.com/personal/credit-cards/sapphire/sapphire-preferred', ['sapphire', 'preferred']),
        ('https://www.chase.com/credit-cards/sapphire-preferred', ['sapphire', 'preferred']),
        ('https://www.chase.com/personal/credit-cards/sapphire/sapphire-reserve', ['sapphire', 'reserve']),
        ('https://www.chase.com/credit-cards/sapphire-reserve', ['sapphire', 'reserve']),
        ('https://www.chase.com/personal/credit-cards/freedom/freedom-flex', ['freedom', 'flex']),
        ('https://www.chase.com/credit-cards/freedom/flex', ['freedom', 'flex']),
        ('https://www.chase.com/personal/credit-cards/freedom/freedom-unlimited', ['freedom', 'unlimited']),
        ('https://www.chase.com/credit-cards/freedom/unlimited', ['freedom', 'unlimited']),
    ],
    'Amex': [
        ('https://www.americanexpress.com/us/credit-cards/card/gold-card', ['gold']),
        ('https://www.americanexpress.com/us/credit-cards/gold-card/', ['gold']),
        ('https://www.americanexpress.com/us/credit-cards/card/platinum-card', ['platinum']),
        ('https://www.americanexpress.com/us/credit-cards/platinum-card/', ['platinum']),
    ],
    'Citi': [
        ('https://www.citi.com/credit-cards/citi-premier-card', ['premier']),
        ('https://www.citi.com/credit-cards/premier', ['premier']),
        ('https://www.citi.com/credit-cards/citi-double-cash-card', ['double', 'cash']),
        ('https://www.citi.com/credit-cards/double-cash', ['double', 'cash']),
    ],
    'Capital One': [
        ('https://www.capitalone.com/credit-cards/venture-x', ['venture', 'x']),
        ('https://www.capitalone.com/credit-cards/venture-x/', ['venture', 'x']),
        ('https://www.capitalone.com/credit-cards/venture', ['venture']),
    ],
}

print("Testing URLs to find correct ones...\n")

working_urls = {}
for issuer, urls in test_cases.items():
    print(f"\n{issuer}:")
    working_urls[issuer] = []
    for url, keywords in urls:
        result = test_url(url, keywords)
        status_icon = "✅" if result['valid'] else "❌"
        print(f"  {status_icon} {result['status']:3} {url}")
        print(f"      -> {result['title']}")
        if result['valid']:
            working_urls[issuer].append((url, result['final_url']))
        time.sleep(0.5)  # Rate limiting

print("\n\n✅ Working URLs:")
for issuer, urls in working_urls.items():
    if urls:
        print(f"\n{issuer}:")
        for original, final in urls:
            print(f"  {final}")

