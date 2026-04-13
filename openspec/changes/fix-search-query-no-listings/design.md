# Design: Fix PostgreSQL Parameter Limit in Batch INSERT

## Technical Details

### Constraint
PostgreSQL (and psycopg2) limit bind parameters to 65,535 per statement.

### Columns per listing row
19 columns: snapshot_id, query_id, item_id, title, gallery_url, image_url, current_price, currency, buy_it_now, listing_type, watch_count, bid_count, selling_state, country, postal_code, end_time, item_url, first_seen_at, last_seen_at

### Safe batch size
asyncpg uses **signed int16** for the parameter count field in the PostgreSQL extended query Bind message, giving a **hard limit of 32,767 parameters per statement** (not 65,535). Confirmed by observing `rvf5` errors with 3,000 rows × 19 cols = 57,000 params.

`floor(32767 / 19) = 1,724` → use `BATCH_SIZE = 1_500` for a comfortable safety margin (1,500 × 19 = 28,500 params).

## Change
**File:** `backend/app/services/poll_runner.py`

Replace the single `pg_insert(ListingRecord).values(new_rows)` call with a loop that chunks `new_rows` into batches of 3,000 rows each.

## No schema changes required
