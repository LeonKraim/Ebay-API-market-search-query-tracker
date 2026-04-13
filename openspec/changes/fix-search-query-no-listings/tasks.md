# Tasks: Fix Search Query Not Returning Listings

- [x] Task 1: Chunk new_rows INSERT into batches of 3,000 in poll_runner.py
- [x] Task 1b: Correct batch size — asyncpg limit is 32,767 (signed int16), not 65,535; reduce to 1,500 rows (28,500 params)
- [ ] Task 2: Trigger a poll and verify total_snapshots > 0 and listings appear in UI
