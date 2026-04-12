# Tasks: Fix listing count growth and add price range filter

- [ ] T01: Change `max_pages` from 10 to 3 in `backend/config.toml`
- [ ] T02: Add `min_price` / `max_price` columns to `SearchQuery` model (`backend/app/models/query.py`)
- [ ] T03: Add Alembic migration `0002` for the new columns
- [ ] T04: Update Pydantic schemas in `backend/app/schemas/query.py`
- [ ] T05: Update `_fetch_page` and `fetch_all_listings` in `backend/app/services/ebay_finding.py` to accept and apply price filter
- [ ] T06: Update `poll_runner.py` to pass `query.min_price` / `query.max_price` to `fetch_all_listings`
- [ ] T07: Update frontend types (`frontend/src/api/client.ts`) and query form (`frontend/src/pages/Queries.tsx`)
- [ ] T08: Run migration, rebuild containers, run tests, verify in browser
