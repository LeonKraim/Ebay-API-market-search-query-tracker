# Design: eBay Market Intelligence Platform

## Repository Layout

```
ebay-market-intel/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app factory, lifespan
│   │   ├── config.py                # Pydantic-Settings loader (config.toml + .env)
│   │   ├── logging_setup.py         # Loguru dual sink (stdout + logs/app.log)
│   │   ├── database.py              # Async engine, AsyncSession factory
│   │   ├── scheduler.py             # APScheduler 4 AsyncScheduler
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── query.py             # SearchQuery ORM model
│   │   │   ├── snapshot.py          # Snapshot ORM model
│   │   │   ├── listing.py           # ListingRecord ORM model
│   │   │   └── sold.py              # SoldRecord ORM model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── query.py             # QueryCreate, QueryRead, QueryUpdate
│   │   │   ├── listing.py           # ListingRead, ListingFilter
│   │   │   ├── sold.py              # SoldRead, SoldFilter
│   │   │   └── stats.py             # PriceTrend, SoldTrend, Summary, Velocity
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── queries.py
│   │   │   ├── snapshots.py
│   │   │   ├── listings.py
│   │   │   ├── sold.py
│   │   │   ├── stats.py
│   │   │   ├── scheduler.py
│   │   │   ├── config_router.py     # GET /config (non-secret values)
│   │   │   ├── logs_router.py       # GET /logs/download
│   │   │   └── auth.py              # verify_token dependency
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── ebay_finding.py      # Finding API client (httpx async)
│   │       ├── ebay_browse.py       # Browse API client (httpx async)
│   │       ├── sold_scraper.py      # Completed-listings scraper (BS4)
│   │       ├── poll_runner.py       # Full poll cycle orchestrator
│   │       └── dedup.py             # Item deduplication
│   ├── migrations/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   ├── tests/
│   │   ├── conftest.py              # async engine, test DB, fixtures
│   │   ├── fixtures/
│   │   │   ├── ebay_finding_page1.xml
│   │   │   ├── ebay_finding_empty.xml
│   │   │   ├── ebay_sold_page1.html
│   │   │   └── ebay_sold_zero.html
│   │   ├── unit/
│   │   │   ├── test_ebay_finding.py
│   │   │   ├── test_ebay_browse.py
│   │   │   ├── test_sold_scraper.py
│   │   │   ├── test_dedup.py
│   │   │   ├── test_poll_runner.py
│   │   │   ├── test_config.py
│   │   │   └── test_logging.py
│   │   ├── integration/
│   │   │   ├── test_queries_router.py
│   │   │   ├── test_listings_router.py
│   │   │   ├── test_sold_router.py
│   │   │   ├── test_stats_router.py
│   │   │   ├── test_auth.py
│   │   │   └── test_scheduler_router.py
│   │   └── edge_cases/
│   │       ├── test_ebay_api_errors.py
│   │       ├── test_db_constraint_errors.py
│   │       ├── test_scraper_html_variants.py
│   │       └── test_scheduler_overlap.py
│   ├── config.toml
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.tsx                 # React root, NProgress global init
│   │   ├── App.tsx
│   │   ├── router.tsx               # TanStack Router definition
│   │   ├── api/
│   │   │   ├── client.ts            # fetch wrapper, token injection, NProgress hooks
│   │   │   ├── queryKeys.ts         # TanStack Query key factories
│   │   │   └── hooks/
│   │   │       ├── useSearchQueries.ts
│   │   │       ├── useListings.ts
│   │   │       ├── useSold.ts
│   │   │       ├── useStats.ts
│   │   │       └── useScheduler.ts
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── TopLoadingBar.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── AppShell.tsx
│   │   │   ├── ui/                  # shadcn/ui component re-exports
│   │   │   ├── ItemsEvaluatedBadge.tsx
│   │   │   ├── QueryCard.tsx
│   │   │   ├── ListingTable.tsx
│   │   │   ├── SoldTable.tsx
│   │   │   ├── PriceTrendChart.tsx
│   │   │   ├── SnapshotTimeline.tsx
│   │   │   └── StatusBadge.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Queries/
│   │   │   │   ├── index.tsx
│   │   │   │   ├── New.tsx
│   │   │   │   └── Detail.tsx
│   │   │   ├── Listings.tsx
│   │   │   ├── Sold.tsx
│   │   │   ├── Stats.tsx
│   │   │   ├── Scheduler.tsx
│   │   │   └── Settings.tsx
│   │   └── lib/
│   │       ├── logger.ts
│   │       └── format.ts
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── components/
│   │   │   └── lib/
│   │   └── e2e/
│   ├── index.html
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   └── playwright.config.ts
├── docker-compose.yml
├── .env.example
└── README.md
```

## Data Flow

```
APScheduler tick
  → poll_runner.run(query_id)
    → ebay_finding.fetch_all_pages(keyword, category, site)
       returns List[RawItem]
    → [if include_sold] sold_scraper.scrape(keyword, site)
       returns List[RawSoldItem]
    → dedup.classify(raw_items, existing_item_ids)
       returns {new: [...], updated: [...], unchanged: [...]}
    → DB: INSERT listing_records (new), UPDATE last_seen_at+price (updated)
    → DB: INSERT sold_records ON CONFLICT DO NOTHING
    → DB: UPDATE snapshot (status=complete, counts)
    → DB: UPDATE search_queries (last_polled_at, total_snapshots++)
```

## Authentication Model

Bearer token from `.env`. Single token, verified in `auth.py` as a FastAPI
`Depends()` dependency. Applied to the router with `dependencies=[Depends(verify_token)]`
when `config.auth.enabled = True`. Token is compared using `secrets.compare_digest`
to prevent timing attacks.

## Configuration Model

### config.toml (committed, all non-secret values)
```toml
[app]
title        = "eBay Market Intelligence"
debug        = false
log_level    = "INFO"
log_file     = "logs/app.log"
log_rotation = "50 MB"
log_retention = "30 days"

[api]
host         = "0.0.0.0"
port         = 8000
cors_origins = ["http://localhost:5173"]

[auth]
enabled      = false

[database]
host         = "localhost"
port         = 5432
name         = "ebay_intel"
pool_size    = 10
pool_max_overflow = 5

[ebay]
site_id      = "EBAY-GB"
max_pages    = 10
results_per_page = 100
request_timeout_seconds = 15
retry_attempts = 3
retry_backoff_seconds  = 2.0

[scraper]
enabled        = true
completed_days = 90
user_agent     = "Mozilla/5.0 (compatible; EbayIntelBot/1.0)"
delay_between_pages_seconds = 1.5

[scheduler]
default_interval_minutes = 60
max_concurrent_polls     = 3
jitter_seconds           = 30
```

### .env (never committed, secrets only)
```
EBAY_APP_ID=
EBAY_CERT_ID=
DATABASE_USER=
DATABASE_PASSWORD=
API_TOKEN=
```

## Database Schema

### search_queries
- id SERIAL PK
- name VARCHAR(200) NOT NULL
- keyword VARCHAR(500) NOT NULL
- category_id VARCHAR(20)
- site_id VARCHAR(20) DEFAULT 'EBAY-GB'
- interval_minutes INT DEFAULT 60
- enabled BOOLEAN DEFAULT TRUE
- include_sold BOOLEAN DEFAULT TRUE
- created_at TIMESTAMPTZ DEFAULT NOW()
- last_polled_at TIMESTAMPTZ
- total_snapshots INT DEFAULT 0

### snapshots
- id SERIAL PK
- query_id INT FK → search_queries(id) ON DELETE CASCADE
- started_at TIMESTAMPTZ NOT NULL
- finished_at TIMESTAMPTZ
- items_found INT DEFAULT 0
- items_new INT DEFAULT 0
- items_updated INT DEFAULT 0
- status VARCHAR(20) DEFAULT 'running'
- error_message TEXT

### listing_records
- id SERIAL PK
- snapshot_id INT FK → snapshots(id) ON DELETE CASCADE
- query_id INT FK → search_queries(id) ON DELETE CASCADE
- item_id VARCHAR(20) NOT NULL
- title VARCHAR(500)
- description TEXT
- image_url TEXT
- gallery_url TEXT
- current_price NUMERIC(12,2)
- currency VARCHAR(5) DEFAULT 'GBP'
- buy_it_now BOOLEAN
- listing_type VARCHAR(50)
- watch_count INT
- bid_count INT
- selling_state VARCHAR(50)
- country VARCHAR(10)
- postal_code VARCHAR(20)
- end_time TIMESTAMPTZ
- item_url TEXT
- first_seen_at TIMESTAMPTZ DEFAULT NOW()
- last_seen_at TIMESTAMPTZ DEFAULT NOW()
- UNIQUE(item_id, snapshot_id)

### sold_records
- id SERIAL PK
- query_id INT FK → search_queries(id) ON DELETE CASCADE
- item_id VARCHAR(20)
- title VARCHAR(500)
- sold_price NUMERIC(12,2)
- currency VARCHAR(5) DEFAULT 'GBP'
- sold_date TIMESTAMPTZ
- listing_type VARCHAR(50)
- image_url TEXT
- item_url TEXT
- scraped_at TIMESTAMPTZ DEFAULT NOW()
- UNIQUE(item_id, sold_date)

## API Surface

All routes prefixed `/api/v1/`. OpenAPI docs auto-generated at `/docs`.

### Queries: GET/POST /queries, GET/PATCH/DELETE /queries/{id}, POST /queries/{id}/run
### Listings: GET /listings, GET /listings/{id}, GET /listings/item/{item_id}
### Sold: GET /sold, GET /sold/{id}
### Snapshots: GET /snapshots, GET /snapshots/{id}, GET /snapshots/{id}/listings
### Stats: GET /stats/price-trend, /stats/sold-trend, /stats/velocity, /stats/summary, /stats/items-evaluated
### Scheduler: GET /scheduler/status, POST /scheduler/pause, /scheduler/resume, /scheduler/run-all
### Config: GET /config (non-secret config values only)
### Logs: GET /logs/download (streams app.log)

## Logging Format

```
2026-04-12 14:23:01.452 | INFO     | poll_runner:run:87      | [POLL]      Starting snapshot #142 for query 'raspberry pi 4'
2026-04-12 14:23:02.101 | INFO     | ebay_finding:fetch:34   | [FINDING]   Page 1/8 — 100 items fetched (200 OK, 312ms)
2026-04-12 14:23:14.889 | INFO     | poll_runner:run:121     | [POLL]      Snapshot #142 complete — 743 found, 12 new, 3 updated, 13.4s
2026-04-12 14:23:15.001 | WARNING  | sold_scraper:parse:67   | [SCRAPER]   Zero items parsed on page 2 — eBay HTML may have changed
2026-04-12 14:23:15.200 | INFO     | dedup:classify:45       | [DEDUP]     Batch 743: 12 new / 3 updated / 728 unchanged
2026-04-12 14:23:15.400 | INFO     | database:bulk_upsert:88 | [DB]        listing_records: 15 rows written (12 insert, 3 update)
```

## Frontend UX Detail

### Top Loading Bar
NProgress starts on: (a) any route transition, (b) any pending API call via the
TanStack Query global `onFetchStart`/`onFetchEnd` callbacks. Completes to 100% on
resolve or error. Configurable colour via Tailwind theme token.

### Items Evaluated Badge
Fixed bottom-right. Polls `GET /stats/items-evaluated` every 5 seconds.
Shows animated spinner icon while any snapshot has `status = 'running'`.
Displays comma-formatted total count of all listing_records + sold_records ever
recorded. Freezes spinner when scheduler is paused.

### Console Logging (frontend)
Every component logs to console:
- On mount: `[HH:MM:SS.mmm] [ComponentName] mounted`
- On significant state change: `[HH:MM:SS.mmm] [ComponentName] event description`
- On API call start: `[HH:MM:SS.mmm] [HookName] → GET /path`
- On API call success: `[HH:MM:SS.mmm] [HookName] ← 200 /path ({n} items, Xms)`
- On API call error: `[HH:MM:SS.mmm] [HookName] ✗ /path — {error message}`
