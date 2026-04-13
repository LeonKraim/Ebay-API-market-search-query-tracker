# Design: Fix PostgreSQL Parameter Limit in Batch INSERT

## Technical Details

### Constraint
PostgreSQL (and psycopg2) limit bind parameters to 65,535 per statement.

### Columns per listing row
19 columns: snapshot_id, query_id, item_id, title, gallery_url, image_url, current_price, currency, buy_it_now, listing_type, watch_count, bid_count, selling_state, country, postal_code, end_time, item_url, first_seen_at, last_seen_at

### Safe batch size
`floor(65535 / 19) = 3,449` → use `BATCH_SIZE = 3_000` for safety margin

## Change
**File:** `backend/app/services/poll_runner.py`

Replace the single `pg_insert(ListingRecord).values(new_rows)` call with a loop that chunks `new_rows` into batches of 3,000 rows each.

## No schema changes required
