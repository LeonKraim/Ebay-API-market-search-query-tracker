# Design: Mock Data Tests for eBay API Logic

## Approach
Use `unittest.mock.patch` / `AsyncMock` to replace `httpx.AsyncClient.get` with canned responses. Realistic XML (Finding API) and HTML (sold scraper) fixtures are stored in `tests/fixtures/`.

## Test Files

### 1. `tests/unit/test_ebay_finding_fetch.py`
Tests `fetch_all_listings()` and `_fetch_page()`:
- Single-page successful fetch (1 page, 3 items)
- Multi-page pagination (2 pages)
- Retry on HTTP 429 (rate limit)
- Retry on HTTP 500 (server error)
- Non-retryable HTTP 4xx raises immediately
- Timeout → retry → success
- All retries exhausted → raises
- Non-success ack returns empty
- Empty search results

### 2. `tests/unit/test_sold_scraper_fetch.py`
Tests `scrape_sold_listings()` and `_parse_page()`:
- Parse realistic sold items HTML (multiple items)
- Multi-page pagination (next page link present)
- Scraper disabled → returns empty
- Different site IDs → correct base URL
- HTTP error → retry → success
- Ghost "Shop on eBay" placeholder filtered

### 3. `tests/unit/test_poll_runner.py`
Tests `run_poll()`:
- Happy path: fetch listings + sold items, writes to DB
- Concurrent job guard (already running → skip)
- Query not found → abort
- Query disabled → skip
- eBay fetch error → snapshot status=error
- No sold items when include_sold=False

## Fixture Files
- `tests/fixtures/finding_single_page.xml` — 3 items, 1 page  
- `tests/fixtures/finding_page1.xml` — 3 items, page 1 of 2
- `tests/fixtures/finding_page2.xml` — 2 items, page 2 of 2
- `tests/fixtures/finding_empty.xml` — 0 items
- `tests/fixtures/finding_failure_ack.xml` — ack=Failure
- `tests/fixtures/sold_page.html` — realistic eBay sold listings HTML (3 items)
- `tests/fixtures/sold_page_with_next.html` — sold HTML with pagination next link

## Dependencies
No new dependencies — uses `pytest-mock` and `unittest.mock.AsyncMock` already available.
