# Tasks: eBay Market Intelligence Platform

## Phase 1 — Backend Scaffold

- [ ] T01: Create directory structure: `backend/app/`, `backend/tests/`, `backend/migrations/`, `logs/`
- [ ] T02: Create `backend/config.toml` with all non-secret settings
- [ ] T03: Create `backend/pyproject.toml` with all dependencies + pytest config
- [ ] T04: Create `.env.example` with all required secret keys documented
- [ ] T05: Create `backend/app/config.py` — Pydantic-Settings loading config.toml + .env
- [ ] T06: Create `backend/app/logging_setup.py` — Loguru dual sink (stdout colour + logs/app.log rotation)
- [ ] T07: Create `backend/app/database.py` — async engine + AsyncSession factory

## Phase 2 — Database Models + Migrations

- [ ] T08: Create `backend/app/models/query.py` — SearchQuery ORM model
- [ ] T09: Create `backend/app/models/snapshot.py` — Snapshot ORM model
- [ ] T10: Create `backend/app/models/listing.py` — ListingRecord ORM model
- [ ] T11: Create `backend/app/models/sold.py` — SoldRecord ORM model
- [ ] T12: Create `backend/migrations/env.py` and `alembic.ini`
- [ ] T13: Create `backend/migrations/versions/0001_initial_schema.py` — all 4 tables

## Phase 3 — Pydantic Schemas

- [ ] T14: Create `backend/app/schemas/query.py` — QueryCreate, QueryRead, QueryUpdate, QueryList
- [ ] T15: Create `backend/app/schemas/listing.py` — ListingRead, ListingFilter, ListingHistoryRead
- [ ] T16: Create `backend/app/schemas/sold.py` — SoldRead, SoldFilter
- [ ] T17: Create `backend/app/schemas/stats.py` — PriceTrendPoint, SoldTrendPoint, VelocityPoint, QuerySummary, ItemsEvaluated

## Phase 4 — Services

- [ ] T18: Create `backend/app/services/ebay_finding.py` — async httpx client for eBay Finding API XML, pagination, retry logic
- [ ] T19: Create `backend/app/services/ebay_browse.py` — async httpx client for eBay Browse API JSON, retry logic
- [ ] T20: Create `backend/app/services/sold_scraper.py` — async BS4 scraper for eBay completed/sold listings, retry + delay
- [ ] T21: Create `backend/app/services/dedup.py` — classify raw items as new/updated/unchanged against existing item IDs
- [ ] T22: Create `backend/app/services/poll_runner.py` — full poll orchestration: snapshot lifecycle, fan-out to clients, dedup, DB writes, logging

## Phase 5 — Auth

- [ ] T23: Create `backend/app/routers/auth.py` — `verify_token` dependency using `secrets.compare_digest`

## Phase 6 — FastAPI Routers

- [ ] T24: Create `backend/app/routers/queries.py` — CRUD + run-now endpoint
- [ ] T25: Create `backend/app/routers/snapshots.py` — list + detail + listings-in-snapshot
- [ ] T26: Create `backend/app/routers/listings.py` — paginated, filtered, sorted; item history endpoint
- [ ] T27: Create `backend/app/routers/sold.py` — paginated, filtered, sorted
- [ ] T28: Create `backend/app/routers/stats.py` — price-trend, sold-trend, velocity, summary, items-evaluated
- [ ] T29: Create `backend/app/routers/scheduler.py` — status, pause, resume, run-all
- [ ] T30: Create `backend/app/routers/config_router.py` — GET /config (non-secret values only)
- [ ] T31: Create `backend/app/routers/logs_router.py` — GET /logs/download (stream app.log)

## Phase 7 — Scheduler

- [ ] T32: Create `backend/app/scheduler.py` — APScheduler 4 AsyncScheduler, per-query interval jobs, overlap prevention, jitter

## Phase 8 — App Entry Point

- [ ] T33: Create `backend/app/main.py` — FastAPI app factory, lifespan (scheduler start/stop, DB init), register all routers, CORS, auth dependency conditional

## Phase 9 — Backend Tests

- [ ] T34: Create `backend/tests/conftest.py` — async test DB, session fixture, test client fixture, auth fixtures
- [ ] T35: Create test HTML/XML fixtures in `backend/tests/fixtures/`
- [ ] T36: Create `backend/tests/unit/test_config.py`
- [ ] T37: Create `backend/tests/unit/test_logging.py`
- [ ] T38: Create `backend/tests/unit/test_ebay_finding.py`
- [ ] T39: Create `backend/tests/unit/test_ebay_browse.py`
- [ ] T40: Create `backend/tests/unit/test_sold_scraper.py`
- [ ] T41: Create `backend/tests/unit/test_dedup.py`
- [ ] T42: Create `backend/tests/unit/test_poll_runner.py`
- [ ] T43: Create `backend/tests/integration/test_queries_router.py`
- [ ] T44: Create `backend/tests/integration/test_listings_router.py`
- [ ] T45: Create `backend/tests/integration/test_sold_router.py`
- [ ] T46: Create `backend/tests/integration/test_stats_router.py`
- [ ] T47: Create `backend/tests/integration/test_auth.py`
- [ ] T48: Create `backend/tests/integration/test_scheduler_router.py`
- [ ] T49: Create `backend/tests/edge_cases/test_ebay_api_errors.py`
- [ ] T50: Create `backend/tests/edge_cases/test_db_constraint_errors.py`
- [ ] T51: Create `backend/tests/edge_cases/test_scraper_html_variants.py`
- [ ] T52: Create `backend/tests/edge_cases/test_scheduler_overlap.py`

## Phase 10 — Frontend Scaffold

- [ ] T53: Scaffold Vite + React 18 + TypeScript project in `frontend/`
- [ ] T54: Install and configure Tailwind CSS 3 + shadcn/ui
- [ ] T55: Install TanStack Router v1, TanStack Query v5, Recharts, NProgress, lucide-react
- [ ] T56: Create `frontend/src/lib/logger.ts` — console wrapper with timestamp + component prefix
- [ ] T57: Create `frontend/src/lib/format.ts` — currency, date, duration, number formatters
- [ ] T58: Create `frontend/src/api/client.ts` — fetch wrapper injecting Bearer token + NProgress hooks
- [ ] T59: Create `frontend/src/api/queryKeys.ts` — TanStack Query key factories
- [ ] T60: Create all `frontend/src/api/hooks/` files — useSearchQueries, useListings, useSold, useStats, useScheduler

## Phase 11 — Frontend Components

- [ ] T61: Create `TopLoadingBar.tsx` — NProgress mount wrapper
- [ ] T62: Create `Sidebar.tsx` + `AppShell.tsx` layout components
- [ ] T63: Create `ItemsEvaluatedBadge.tsx` — live counter, spinner, 5s polling
- [ ] T64: Create `QueryCard.tsx` — name, keyword, badges, delete/edit/run buttons
- [ ] T65: Create `ListingTable.tsx` — virtualised/paginated table with filters + sort
- [ ] T66: Create `SoldTable.tsx`
- [ ] T67: Create `PriceTrendChart.tsx` — Recharts line chart, live vs sold overlay
- [ ] T68: Create `SnapshotTimeline.tsx`
- [ ] T69: Create `StatusBadge.tsx`

## Phase 12 — Frontend Pages

- [ ] T70: Create `Dashboard.tsx` — summary cards, sparkline, recent snapshots table, scheduler banner
- [ ] T71: Create `Queries/index.tsx` — query list with inline enable toggle
- [ ] T72: Create `Queries/New.tsx` — add query form with validation
- [ ] T73: Create `Queries/Detail.tsx` — tabbed: overview, live listings, sold, snapshots
- [ ] T74: Create `Listings.tsx` — global listing browser
- [ ] T75: Create `Sold.tsx` — global sold browser
- [ ] T76: Create `Stats.tsx` — multi-query price trend + sold vs listed gap
- [ ] T77: Create `Scheduler.tsx` — status + pause/resume/run-all + per-query next run
- [ ] T78: Create `Settings.tsx` — config display, auth status, log download

## Phase 13 — Frontend Tests

- [ ] T79: Create `vitest.config.ts` + `playwright.config.ts`
- [ ] T80: Create unit tests: TopLoadingBar, ItemsEvaluatedBadge, QueryCard, ListingTable, PriceTrendChart
- [ ] T81: Create unit tests: useSearchQueries, useStats hooks
- [ ] T82: Create unit tests: logger.ts, format.ts
- [ ] T83: Create E2E tests: dashboard, add-query, view-results, scheduler-controls, settings-token

## Phase 14 — Infrastructure

- [ ] T84: Create `backend/Dockerfile`
- [ ] T85: Create `frontend/Dockerfile` (Nginx)
- [ ] T86: Create `docker-compose.yml`
- [ ] T87: Create `.gitignore`
- [ ] T88: Create `README.md` with full setup + usage docs
