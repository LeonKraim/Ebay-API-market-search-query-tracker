# Proposal: Mock Data Tests for eBay API Logic

## What
Add comprehensive unit tests that exercise the eBay Finding API client (`fetch_all_listings`, `_fetch_page`), the sold listings scraper (`scrape_sold_listings`, `_parse_page`), and the poll runner orchestration (`run_poll`) — all using mock HTTP responses and mock DB sessions so no real eBay API calls or Postgres connections are needed.

## Why
The existing tests only cover XML/HTML *parsers* in isolation. The higher-level async functions (`fetch_all_listings`, `scrape_sold_listings`, `run_poll`) — which contain pagination loops, retry/backoff logic, error handling, and DB writes — have zero test coverage. These are the most bug-prone code paths and need mock-data tests.

## What Changes
- **New test files**: `test_ebay_finding_fetch.py`, `test_sold_scraper_fetch.py`, `test_poll_runner.py`
- **New fixtures**: `tests/fixtures/` gets realistic XML responses and HTML pages as static files
- **No production code changes** — tests only
- Uses `unittest.mock.AsyncMock` + `pytest-mock` (already in test deps) to mock `httpx.AsyncClient`
