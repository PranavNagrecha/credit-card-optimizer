# Credit Card Optimizer - Expansion Plan

## Current State
- ✅ 10 issuers covered (Chase, Amex, Citi, Capital One, BoA, Discover, US Bank, Wells Fargo, Barclays, Co-branded)
- ✅ ~29 cards loaded
- ✅ Basic merchant mapping (~10 merchants)
- ✅ Basic category normalization

## Gaps Identified

### 1. Missing Credit Cards
- **Apple Card** (Goldman Sachs) - Popular cashback card
- **Airline Co-branded Cards**:
  - United Airlines (Chase)
  - Delta SkyMiles (Amex)
  - American Airlines (Citi)
  - Southwest Rapid Rewards (Chase)
  - JetBlue (Barclays)
- **Hotel Co-branded Cards**:
  - Marriott Bonvoy (Chase, Amex)
  - Hilton Honors (Amex)
  - Hyatt (Chase)
  - IHG (Chase)
- **More Premium Cards**:
  - Chase Ink Business cards
  - Amex Business cards
  - Citi Prestige
  - Capital One Venture X
- **Store Cards**:
  - Target RedCard
  - Amazon Prime Visa
  - Costco Anywhere Visa

### 2. Limited Merchant Mapping
Currently only ~10 merchants mapped. Need to add:
- **Grocery Chains**: Safeway, Albertsons, Publix, Wegmans, H-E-B, Stop & Shop, Giant, Food Lion, etc.
- **Retailers**: Best Buy, Home Depot, Lowe's, Macy's, Nordstrom, etc.
- **Restaurants**: McDonald's, Starbucks, Chipotle, Subway, etc.
- **Gas Stations**: Shell, Chevron, BP, Exxon, Mobil, etc.
- **Streaming**: Netflix, Spotify, Hulu, Disney+, etc.
- **Travel**: Uber, Lyft, Airbnb, Booking.com, etc.

### 3. Category Expansion
Need more granular categories:
- **Groceries**: Supermarkets, convenience stores, wholesale clubs
- **Dining**: Fast food, casual dining, fine dining, cafes
- **Travel**: Airlines, hotels, car rentals, cruises, trains
- **Entertainment**: Movies, concerts, sports, streaming
- **Shopping**: Online, department stores, specialty retail
- **Gas**: Gas stations, EV charging
- **Utilities**: Phone, internet, cable, electricity
- **Healthcare**: Pharmacies, medical services
- **Education**: Schools, universities, online courses

### 4. Better Merchant Resolution
- Fuzzy matching for merchant names
- Handle common misspellings
- Support partial matches
- Chain store recognition (e.g., "Walmart Supercenter" = "Walmart")

## Implementation Priority

### Phase 1: Merchant Mapping Expansion (High Priority)
1. Add 100+ common merchants to `normalization.py`
2. Expand MCC mappings
3. Test with real queries

### Phase 2: Missing Cards (Medium Priority)
1. Add Apple Card scraper
2. Add airline co-branded cards
3. Add hotel co-branded cards

### Phase 3: Category Enhancement (Medium Priority)
1. Expand category synonyms
2. Add subcategories
3. Improve category matching logic

### Phase 4: Advanced Features (Low Priority)
1. Fuzzy merchant matching
2. Machine learning for category detection
3. User feedback loop for improvements

