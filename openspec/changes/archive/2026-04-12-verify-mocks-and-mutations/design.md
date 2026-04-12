# Design

## Phase 1: Real API Comparison (DONE)
- Finding API: rate-limited (HTTP 500 errorId=10001) but error XML confirms same namespace. XML structure is a stable RESTful API — fixtures match the documented schema.
- Sold HTML: fetched real page (1.5MB). Discovered BREAKING CHANGE:
  - `li.s-item` → `li.s-card` (62 cards on real page)
  - `.s-item__title` → `.s-card__title`
  - `.s-item__price` → `.s-card__price`
  - `a.s-item__link` → `a.s-card__link`
  - `img.s-item__image-img` → `img.s-card__image`
  - `.s-item__ended-date` → `.s-card__caption` with `span.su-styled-text.positive` "Sold  DD Mon YYYY"
  - `.s-item__title--tagblock` → ghost item is still "Shop on eBay" but structure changed
  - `.s-item__purchase-options-with-icon` → `.s-card__attribute-row` with purchase type text
  - `a.pagination__next` → **still works**

## Phase 2: Production Scraper Fix
- Update `_parse_page()` in `sold_scraper.py` to use new `s-card` selectors
- Keep backward compatibility with `s-item` as fallback (eBay may serve different HTML to different User-Agents or regions)
- Update `_extract_next_page_url()` — pagination__next still works, no change needed

## Phase 3: Fixture Updates
- Update `sold_page.html` and `sold_page_with_next.html` to use new `s-card` HTML structure matching real eBay

## Phase 4: Test Updates
- Update test assertions in `test_sold_scraper_fetch.py` to expect correct parsing from new HTML

## Phase 5: Mutation Testing (Principle 8)
- 5 mutations per distinct behavior tested, per test file
- Categories: off-by-one, wrong type, flipped condition, completely wrong output, boundary break
