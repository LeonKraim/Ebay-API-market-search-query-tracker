# Proposal: Fix listing count growth and add price range filter

## What Changes

### 1. Reduce `max_pages` default from 10 → 3
The eBay Browse API fetch currently pulls 10 pages × 100 items = 1,000 items per scheduler run.
Change `max_pages` in `config.toml` from `10` to `3` (300 items per run).

### 2. Add `min_price` / `max_price` per-query filter
Add optional minimum and maximum price fields to `SearchQuery`. When set, the Browse API
`filter` parameter is appended with `price:[MIN..MAX],priceCurrency:CURRENCY` so eBay only
returns listings within the price range. This narrows the search space and reduces result
rotation between runs.

## Why

### Root cause of rapid count growth (from log/DB analysis)
Snapshot data from the live database:
```
id | items_found | items_new
 4 |        1000 |      1000   ← first successful run (DB empty)
 5 |        1000 |      1000   ← 1 hour later – all new again (DB was cleared between 4 and 5)
 6 |        1000 |       119   ← 6 min after run 5, most overlap
 7 |        1000 |       794   ← 36 min after run 6, 79% churn
```

With `max_pages=10` the fetch samples 1,000 items from eBay's "nintendo switch" search.
eBay sorts by `newlyListed` and the result set is highly volatile — auctions end, new listings
appear, bid counts change. Between runs mere minutes apart, ~80% of the 1,000 sampled items are
different item IDs. The deduplication logic is correct; the problem is the fetch scope is too
broad for useful per-run tracking.

Reducing to 3 pages (300 items) captures the most-relevant top results and dramatically reduces
result churn, since the top 300 "best match" results are far more stable than items on pages 4-10.

### Price filter rationale
A buyer searching "nintendo switch" only wants consoles in a certain price band (e.g. €150–€250).
Allowing min/max price per query narrows the eBay search to that band, which:
- Produces a smaller, more stable result set
- Makes deduplication more effective (items stay in range longer)
- Enables meaningful market price-band analysis

## Acceptance Criteria
1. After the fix, a manual scheduler run on "nintendo switch" finds significantly fewer new items
   than the previous run (not 700-1000 new items).
2. A query with `min_price=100` and `max_price=300` passes a `price:[100..300]` filter to the
   eBay Browse API request, visible in backend logs.
3. The query create/edit form has optional Min Price and Max Price number inputs.
4. Existing queries without price range continue to function unchanged.
5. Alembic migration `0002` runs cleanly against the live Postgres DB without data loss.
