## 1. Rewrite eBay API Client

- [ ] 1.1 Rewrite `backend/app/services/ebay_finding.py` — replace Finding API XML client with Browse API JSON client: new endpoint URL, Bearer auth header, `X-EBAY-C-MARKETPLACE-ID` header, offset-based pagination, JSON response parsing. Keep `RawListing` dataclass and `fetch_all_listings()` signature unchanged.

## 2. Create JSON Test Fixtures

- [ ] 2.1 Create `backend/tests/fixtures/browse_single_page.json` — 3 items, total=3 (mirrors finding_single_page.xml data)
- [ ] 2.2 Create `backend/tests/fixtures/browse_page1.json` — 3 items, total=5 (mirrors finding_page1.xml)
- [ ] 2.3 Create `backend/tests/fixtures/browse_page2.json` — 2 items, total=5 (mirrors finding_page2.xml)
- [ ] 2.4 Create `backend/tests/fixtures/browse_empty.json` — 0 items, total=0

## 3. Rewrite Tests

- [ ] 3.1 Rewrite `backend/tests/unit/test_ebay_finding_parser.py` — test `_parse_listing()` with JSON dicts instead of XML elements
- [ ] 3.2 Rewrite `backend/tests/unit/test_ebay_finding_fetch.py` — update mock responses to JSON, add `ebay_auth_token` to mock settings, update request URL assertions

## 4. Verify

- [ ] 4.1 Run full test suite (`pytest tests/ --tb=short`) — all tests must pass
- [ ] 4.2 Docker rebuild (`docker compose up --build -d`) and live test — create a query and run it, verify 200 OK and items returned from Browse API
