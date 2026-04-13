# Design: Hybrid Sold Tracking

## 1. Disappearance Tracking (poll_runner.py)

After fetching listings from the Browse API, compare current snapshot's item_ids against the previous snapshot's item_ids for the same query. Items present in the previous snapshot but absent from the current one are "disappeared" — likely sold or ended.

### Logic:
1. Before inserting new listings, query `listing_records` for the most recent previous snapshot of this query.
2. Get the set of item_ids from that previous snapshot.
3. Compute `disappeared_ids = previous_ids - current_ids`.
4. For each disappeared item, insert a `sold_records` row using the listing's last known metadata (price, title, image, etc.) with `source='disappeared'` and `sold_date=now()`.
5. Use `ON CONFLICT DO NOTHING` on `(item_id, sold_date)` to avoid duplicates.

### Constraints:
- Only runs when there is a previous snapshot (skip on first poll).
- Uses the listing's `current_price` as the `sold_price` (best available approximation).
- `sold_date` is set to the current timestamp (we know it disappeared between this poll and the last).

## 2. SoldRecord Model Change

Add a `source` column:
- `VARCHAR(20)`, default `'scraped'`, NOT NULL
- Values: `'scraped'` (from HTML scraper), `'disappeared'` (from snapshot comparison)

## 3. Scraper Hardening (sold_scraper.py)

### CAPTCHA Detection:
After receiving a 200 OK response, check the HTML body for CAPTCHA indicators before parsing:
- Presence of strings: `captcha`, `robot`, `Please verify`, `Are you a human`
- If detected: log a WARNING, skip page, return what was collected so far.

### Rotating User-Agents:
Replace the static `scraper_user_agent` with a pool of 6-8 realistic browser UAs. Randomly select one per request.

### Random Jitter:
Replace fixed `scraper_delay_between_pages_seconds` with a randomized delay: `base_delay + random(0, base_delay)` to make request patterns less predictable.

## 4. Migration

New Alembic migration `0004_add_sold_source_column.py`:
- `ALTER TABLE sold_records ADD COLUMN source VARCHAR(20) NOT NULL DEFAULT 'scraped'`
