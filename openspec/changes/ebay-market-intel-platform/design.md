# Design: eBay Market Intelligence Platform

## Architecture Overview

The system consists of three main components:

### Backend (FastAPI + Python 3.12)
- Async SQLAlchemy 2 ORM with PostgreSQL
- APScheduler 4 for scheduled eBay API polling
- eBay Finding API and Browse API clients (httpx)
- Completed listings scraper (BeautifulSoup4)
- Loguru for structured logging
- Full REST API with OpenAPI documentation

### Frontend (React 18 + Vite)
- Single-page application (SPA)
- TanStack Query v5 for server state management
- TanStack Router v1 for routing
- shadcn/ui component library
- Tailwind CSS 3 for styling
- NProgress for top loading bar
- Recharts for price trend visualization

### Database (PostgreSQL 16)
- Time-series schema for listings and sold items
- Snapshot-based polling records
- Search query configuration
- Alembic migrations for schema versioning

## Data Flow

```
APScheduler tick
  → poll_runner.run(query_id)
    → ebay_finding.fetch_all_pages(keyword, category, site)
    → [if include_sold] sold_scraper.scrape(keyword, site)
    → dedup.classify(raw_items, existing_item_ids)
    → DB insert/update listings and sold_records
    → Update snapshot status
```

## Database Schema

### search_queries
- id, name, keyword, category_id, site_id, interval_minutes, enabled, include_sold, created_at, last_polled_at, total_snapshots

### snapshots
- id, query_id, started_at, finished_at, items_found, items_new, items_updated, status, error_message

### listing_records
- id, snapshot_id, query_id, item_id, title, description, image_url, current_price, currency, buy_it_now, listing_type, watch_count, bid_count, selling_state, country, postal_code, end_time, item_url, first_seen_at, last_seen_at
- UNIQUE(item_id, snapshot_id)

### sold_records
- id, query_id, item_id, title, sold_price, currency, sold_date, listing_type, image_url, item_url, scraped_at
- UNIQUE(item_id, sold_date)

## API Endpoints

### /api/v1/queries
GET, POST /queries - list and create queries
GET, PATCH, DELETE /queries/{id} - single query operations
POST /queries/{id}/run - trigger immediate poll

### /api/v1/listings
GET /listings - paginated listings with filters (price, date, search, sort)
GET /listings/{id} - single listing
GET /listings/item/{item_id} - price history for item

### /api/v1/sold
GET /sold - paginated sold records with filters
GET /sold/{id} - single sold record

### /api/v1/snapshots
GET /snapshots - snapshot list
GET /snapshots/{id} - snapshot detail with item counts
GET /snapshots/{id}/listings - listings in snapshot

### /api/v1/stats
GET /stats/price-trend - avg/min/max prices over time
GET /stats/sold-trend - sold items trend
GET /stats/velocity - listing disappearance rate
GET /stats/summary - overall statistics
GET /stats/items-evaluated - total unique items count

### /api/v1/scheduler
GET /scheduler/status - scheduler state and next runs
POST /scheduler/pause - pause all jobs
POST /scheduler/resume - resume all jobs
POST /scheduler/run-all - trigger all queries immediately

### /api/v1/config
GET /config - non-secret configuration values

### /api/v1/logs
GET /logs/download - stream application log file

## Configuration

### config.toml (committed)
```
[app]
title = "eBay Market Intelligence"
debug = false
log_level = "INFO"
log_file = "logs/app.log"

[api]
host = "0.0.0.0"
port = 8000
cors_origins = ["http://localhost:5173"]

[auth]
enabled = false

[database]
host = "localhost"
port = 5432
name = "ebay_market_intel"

[ebay]
site_id = "EBAY-GB"
max_pages = 10
results_per_page = 100
retry_attempts = 3

[scraper]
enabled = true
completed_days = 90
delay_between_pages_seconds = 1.5

[scheduler]
default_interval_minutes = 60
max_concurrent_polls = 3
jitter_seconds = 30
```

### .env (secrets, never committed)
```
EBAY_APP_ID=<provided>
EBAY_CERT_ID=<provided>
DATABASE_USER=ebay
DATABASE_PASSWORD=<secure>
API_TOKEN=<if auth enabled>
```

## Logging

All logs go to `logs/app.log` (50MB rotation, 30-day retention) and console simultaneously.

Format: `timestamp | level | module:function:line | message`

Example:
```
2026-04-12 14:23:01.452 | INFO     | poll_runner:run:87  | [POLL] Starting snapshot #142 for query 'raspberry pi 4'
2026-04-12 14:23:02.101 | INFO     | ebay_finding:fetch:34 | [FINDING] Page 1/8 — 100 items fetched (200 OK, 312ms)
```

## Frontend UX

### Top Loading Bar
NProgress bar appears on route changes and API calls, completes on success/error.

### Items Evaluated Badge
Fixed bottom-right corner widget showing total unique items ever archived. Polls `/stats/items-evaluated` every 5 seconds. Shows animated spinner while scheduler is running.

### Pages
- Dashboard: summary stats and recent snapshot timeline
- Queries: search query management (CRUD)
- Listings: global live listing browser with filters
- Sold: global sold listing browser with filters
- Stats: price trends, velocity, top keywords
- Scheduler: job status and control buttons
- Settings: configuration display and system info
