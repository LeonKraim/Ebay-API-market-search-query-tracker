# Implementation Tasks: eBay Market Intelligence Platform

## Phase 1: Backend Configuration & Setup

- [ ] Task 1.1: Create `backend/pyproject.toml` with all dependencies (FastAPI, SQLAlchemy, asyncpg, APScheduler, httpx, BeautifulSoup4, Loguru, Pydantic-Settings, Alembic, pytest, pytest-asyncio)
- [ ] Task 1.2: Initialize Alembic migration environment
- [ ] Task 1.3: Create `backend/config.toml` with all configuration sections (app, api, auth, database, ebay, scraper, scheduler)
- [ ] Task 1.4: Create `.env.example` and `.env` (with provided eBay API credentials)
- [ ] Task 1.5: Implement `backend/app/logging_setup.py` using Loguru (dual sink: console + logs/app.log, 50MB rotation, 30-day retention)
- [ ] Task 1.6: Implement `backend/app/config.py` using Pydantic-Settings (load config.toml + .env, validate all fields)

## Phase 2: Database & ORM

- [ ] Task 2.1: Implement `backend/app/models/__init__.py` and all model files (query.py, snapshot.py, listing.py, sold.py) using SQLAlchemy 2 ORM
- [ ] Task 2.2: Implement `backend/app/database.py` (AsyncEngine, SessionLocal factory, get_db dependency)
- [ ] Task 2.3: Create initial Alembic migration with all tables (search_queries, snapshots, listing_records, sold_records)
- [ ] Task 2.4: Implement `backend/app/schemas/` with all Pydantic schemas (QueryCreate, QueryRead, ListingRead, SoldRead, etc.)

## Phase 3: eBay API Clients & Scraper

- [ ] Task 3.1: Implement `backend/app/services/ebay_finding.py` (Finding API client using httpx, parse XML response, handle pagination, retry logic)
- [ ] Task 3.2: Implement `backend/app/services/ebay_browse.py` (Browse API client using httpx)
- [ ] Task 3.3: Implement `backend/app/services/sold_scraper.py` (BeautifulSoup4 scraper for completed listings, parse HTML, extract prices, dates, item URLs)
- [ ] Task 3.4: Implement `backend/app/services/dedup.py` (classify items as new/updated/unchanged)
- [ ] Task 3.5: Write unit tests for all three (ebay_finding, sold_scraper) in `backend/tests/unit/`

## Phase 4: Poll Orchestration & Scheduler

- [ ] Task 4.1: Implement `backend/app/services/poll_runner.py` (orchestrate full poll cycle: Finding API → scraper → dedup → DB write)
- [ ] Task 4.2: Implement `backend/app/scheduler.py` (APScheduler 4 AsyncScheduler, add job, pause, resume, concurrent lock)
- [ ] Task 4.3: Write unit + integration tests for poll_runner and scheduler
- [ ] Task 4.4: Implement `backend/app/main.py` (FastAPI app factory, lifespan events, middleware, CORS, routers)

## Phase 5: API Routers

- [ ] Task 5.1: Implement `backend/app/routers/auth.py` (Bearer token verify_token dependency)
- [ ] Task 5.2: Implement `backend/app/routers/queries.py` (GET all, POST create, GET single, PATCH update, DELETE, POST run-now)
- [ ] Task 5.3: Implement `backend/app/routers/listings.py` (GET with filters, pagination, sorting, price range)
- [ ] Task 5.4: Implement `backend/app/routers/sold.py` (same shape as listings)
- [ ] Task 5.5: Implement `backend/app/routers/snapshots.py` (GET all, GET single, GET listings in snapshot)
- [ ] Task 5.6: Implement `backend/app/routers/stats.py` (price-trend, sold-trend, velocity, summary, items-evaluated)
- [ ] Task 5.7: Implement `backend/app/routers/scheduler.py` (GET status, POST pause, resume, run-all)
- [ ] Task 5.8: Implement `backend/app/routers/config_router.py` (GET /config returns non-secret values)
- [ ] Task 5.9: Implement `backend/app/routers/logs_router.py` (GET /logs/download streams app.log)
- [ ] Task 5.10: Write integration tests for all routers in `backend/tests/integration/`

## Phase 6: Backend Test Suite

- [ ] Task 6.1: Implement conftest.py with async fixtures (test DB, async client, mocked eBay responses)
- [ ] Task 6.2: Write edge case tests: eBay API errors (429, 503, malformed JSON), DB constraint errors, scraper HTML variants, scheduler overlap
- [ ] Task 6.3: Run full backend test suite, ensure 100% pass rate
- [ ] Task 6.4: Run mutation tests per Principle 8 (inject defects, verify tests fail, restore)

## Phase 7: Frontend Scaffold

- [ ] Task 7.1: Initialize Vite + React + TypeScript project in `frontend/`
- [ ] Task 7.2: Set up Tailwind CSS + shadcn/ui component library
- [ ] Task 7.3: Create `frontend/src/api/client.ts` (fetch wrapper, Bearer token injection, error handling)
- [ ] Task 7.4: Create `frontend/src/api/queryKeys.ts` (TanStack Query key factories for all endpoints)
- [ ] Task 7.5: Create `frontend/src/api/hooks/` (useSearchQueries, useListings, useSold, useStats, useScheduler hooks)
- [ ] Task 7.6: Create `frontend/src/lib/logger.ts` (console logger with timestamp prefix, module name)
- [ ] Task 7.7: Create `frontend/src/lib/format.ts` (formatCurrency, formatDate, formatDuration, number comma formatting)
- [ ] Task 7.8: Set up TanStack Router v1 in `frontend/src/router.tsx`

## Phase 8: Frontend Components & Pages

- [ ] Task 8.1: Implement `frontend/src/components/layout/TopLoadingBar.tsx` (NProgress integration)
- [ ] Task 8.2: Implement `frontend/src/components/layout/Sidebar.tsx` and `AppShell.tsx`
- [ ] Task 8.3: Implement `frontend/src/components/ItemsEvaluatedBadge.tsx` (polls /stats/items-evaluated, shows spinner, formats count)
- [ ] Task 8.4: Implement all reusable components (QueryCard, ListingTable, SoldTable, PriceTrendChart, SnapshotTimeline, StatusBadge)
- [ ] Task 8.5: Implement `pages/Dashboard.tsx` (summary cards, sparkline, recent snapshots, scheduler status)
- [ ] Task 8.6: Implement `pages/Queries/index.tsx` (query list, add button, enable/disable toggle, delete)
- [ ] Task 8.7: Implement `pages/Queries/New.tsx` (create query form with validation)
- [ ] Task 8.8: Implement `pages/Queries/Detail.tsx` (tabs: overview, live, sold, snapshots)
- [ ] Task 8.9: Implement `pages/Listings.tsx` (global listing browser with filters)
- [ ] Task 8.10: Implement `pages/Sold.tsx` (global sold browser with filters)
- [ ] Task 8.11: Implement `pages/Stats.tsx` (price trends, velocity, top keywords)
- [ ] Task 8.12: Implement `pages/Scheduler.tsx` (status, pause/resume/run-all buttons, next job times)
- [ ] Task 8.13: Implement `pages/Settings.tsx` (display config values, auth status, log download, DB stats)

## Phase 9: Frontend Tests

- [ ] Task 9.1: Set up Vitest + React Testing Library + Playwright
- [ ] Task 9.2: Write unit tests for all components (TopLoadingBar, ItemsEvaluatedBadge, QueryCard, ListingTable, PriceTrendChart)
- [ ] Task 9.3: Write unit tests for all hooks (useSearchQueries, useStats, etc.)
- [ ] Task 9.4: Write unit tests for lib functions (logger, format)
- [ ] Task 9.5: Write E2E tests: dashboard loads, add query, view results, filter, sort, scheduler controls, settings
- [ ] Task 9.6: Run full frontend test suite, ensure 100% pass rate
- [ ] Task 9.7: Run mutation tests per Principle 8

## Phase 10: Docker & Deployment

- [ ] Task 10.1: Create `backend/Dockerfile` (Python 3.12 base, pip install, run Alembic migrate, gunicorn or uvicorn)
- [ ] Task 10.2: Create `frontend/Dockerfile` (Node 20 base, npm install, npm run build, serve with nginx)
- [ ] Task 10.3: Create `docker-compose.yml` (postgres, backend, frontend services with environment)
- [ ] Task 10.4: Test full stack with `docker compose up`, verify all services running
- [ ] Task 10.5: Create README.md with setup, usage, API docs link, troubleshooting

## Phase 11: Final Verification

- [ ] Task 11.1: Run all backend tests (unit + integration + edge cases)
- [ ] Task 11.2: Run all frontend tests (unit + E2E)
- [ ] Task 11.3: Run mutation tests for all test suites (Principle 8)
- [ ] Task 11.4: Full Docker Compose test: start all services, create query, trigger poll, view results in UI
- [ ] Task 11.5: Verify logging output (backend logs, frontend console logs)
- [ ] Task 11.6: Verify OpenSpec tasks all marked [x], run `openspec validate --strict`

## Phase 12: OpenSpec Finalization

- [ ] Task 12.1: Verify all OpenSpec artifacts (proposal.md, design.md, tasks.md) are complete and accurate
- [ ] Task 12.2: Run `openspec validate --strict --json`, fix any ERROR-level issues
- [ ] Task 12.3: Triage all WARNING-level issues for production impact, fix or accept
- [ ] Task 12.4: Run `openspec archive --yes` to finalize
- [ ] Task 12.5: Verify archive directory contains all specs and synced deltas

---

## Notes

- All credentials (EBAY_APP_ID, EBAY_CERT_ID, DATABASE_USER/PASSWORD, API_TOKEN) go in `.env` only, never committed
- Every function logs entry/exit using Loguru; every API call logs status + timing
- All tests must pass mutation checks (defects injected, verified to fail, then restored)
- Frontend uses TanStack Query v5 for stale-while-revalidate caching; NProgress for loading bar
- Docker Compose includes postgres service with volume persistence
