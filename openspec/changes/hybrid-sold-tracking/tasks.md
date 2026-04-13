# Tasks: Hybrid Sold Tracking

- [x] Task 1: Create Alembic migration 0004 to add `source` column to `sold_records`
- [x] Task 2: Update `SoldRecord` model with `source` field (default='scraped')
- [x] Task 3: Add disappearance tracking logic to `poll_runner.py` — detect items that vanished between snapshots and insert them as `sold_records` with `source='disappeared'`
- [x] Task 4: Harden `sold_scraper.py` — CAPTCHA detection, rotating User-Agents, randomized delay jitter
- [x] Task 5: Update sold record insert in `poll_runner.py` to explicitly set `source='scraped'`
- [x] Task 6: Deploy, verify all acceptance criteria
