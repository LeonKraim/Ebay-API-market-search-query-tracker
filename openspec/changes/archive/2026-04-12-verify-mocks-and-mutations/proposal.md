# Proposal: Verify Mock Fixtures Against Real eBay API + Mutation Tests

## What
1. Call the real eBay Finding API and scrape a real sold-listings page to compare the XML/HTML structure against our test fixtures
2. Fix any structural gaps discovered
3. Run the full Principle 8 mutation testing protocol (5 mutations per behavior) on all 3 new test files

## Why
Mock tests only have value if the mock data matches real API responses. Structural drift (missing elements, wrong namespaces, renamed CSS classes) would make tests pass while production code breaks. Mutation testing confirms the tests actually detect failures.

## What Changes
- **CRITICAL**: Real eBay HTML has changed from `s-item__*` to `s-card__*` selectors — production scraper returns 0 items
- `sold_scraper.py` updated to use new eBay `s-card` CSS selectors
- HTML fixture files updated to match new eBay HTML structure
- Test assertions updated for new selector patterns
- Finding API XML fixtures confirmed correct (namespace and element structure unchanged)
- Mutation testing on all 3 test files
