## Why

The eBay Finding API (`svcs.ebay.com/services/search/FindingService/v1`) is permanently rate-limited for our App ID (`LeonJami-llmsearc-PRD-9bf497123-acd64d2f`) — every request returns HTTP 500 with `errorId=10001` (SecurityRateLimiter) across all eBay marketplaces. The eBay Browse API (`api.ebay.com/buy/browse/v1/item_summary/search`) works correctly with the same credentials (verified 200 OK via eBay API Explorer). Switching unblocks all query execution functionality.

## What Changes

- **BREAKING**: Replace the Finding API XML client (`ebay_finding.py`) with the Browse API JSON client
  - New endpoint: `GET https://api.ebay.com/buy/browse/v1/item_summary/search`
  - Auth: `Authorization: Bearer <token>` header (instead of `SECURITY-APPNAME` query param)
  - Marketplace: `X-EBAY-C-MARKETPLACE-ID: EBAY_US` header with underscore format (instead of `GLOBAL-ID` query param with hyphen format)
  - Response format: JSON (instead of XML)
  - Pagination: offset-based (`offset` + `limit`, max 200/page, max 10,000 total) instead of page-based
- Keep `RawListing` dataclass interface identical — no downstream changes needed
- Keep `fetch_all_listings()` function signature identical — `poll_runner.py`, `dedup.py`, etc. remain unchanged
- Replace XML test fixtures with JSON equivalents
- Rewrite parser and fetch unit tests for JSON responses

**Sources:**
- [eBay Browse API search docs](https://developer.ebay.com/api-docs/buy/browse/resources/item_summary/methods/search)
- User-verified: Browse API returns 200 OK with same App ID via eBay API Explorer

## Capabilities

### New Capabilities
- `browse-api-client`: eBay Browse API JSON client replacing the Finding API XML client

### Modified Capabilities
(none — the `RawListing` dataclass and `fetch_all_listings()` public API remain identical)

## Impact

- **Code**: `backend/app/services/ebay_finding.py` — full rewrite (internal implementation only)
- **Tests**: `test_ebay_finding_parser.py`, `test_ebay_finding_fetch.py` — rewrite for JSON
- **Fixtures**: Replace 5 XML fixture files with 4 JSON fixture files
- **Dependencies**: No new dependencies (httpx already supports JSON)
- **Config**: `ebay_auth_token` (already in `.env`) used as Bearer token; `ebay_results_per_page` capped at 200 (Browse API max)
- **No downstream changes**: `poll_runner.py`, `dedup.py`, `__init__.py`, all other tests — unchanged
