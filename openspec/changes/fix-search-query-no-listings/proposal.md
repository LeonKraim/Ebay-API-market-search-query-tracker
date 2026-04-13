# Proposal: Fix Search Query Not Returning Listings

## What
Batch INSERT operations in `poll_runner.py` exceed PostgreSQL's hard limit of 65,535 bind parameters when a query returns more than ~3,449 listings. This causes the entire DB write transaction to be rolled back silently, resulting in 0 listings stored.

## Why
User's query "nintendo switch" on EBAY-DE with price range 0–200 EUR returns ~6,000+ listings. Each listing row has 19 columns, so 6,000 × 19 = 114,000 bind parameters — well above the 65,535 PostgreSQL limit. The error causes the session to rollback everything, leaving `total_snapshots = 0` and no listings visible.

## Root Cause
`psycopg2` / PostgreSQL error: too many bind parameters in a single prepared statement. SQLAlchemy raises this as error code `rvf5` which causes the poll's DB session to rollback.

## Fix
Chunk the `new_rows` list into batches of ≤ 3,000 rows before inserting. 3,000 × 19 = 57,000 parameters, safely under 65,535.

## Acceptance Criteria
1. Triggering "Run now" on a query results in listings being stored in the DB (total > 0)
2. `GET /queries/{id}` returns `total_snapshots >= 1` and `last_polled_at` is non-null
3. The Listings page in the UI shows results
4. No SQLAlchemy `rvf5` error in the logs after a poll completes
