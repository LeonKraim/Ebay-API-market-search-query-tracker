# Proposal: eBay Market Intelligence Platform

## What

Build a complete, self-hosted eBay market intelligence system consisting of:

1. **Python/FastAPI backend** — polls eBay's Finding API and Browse API on a schedule, scrapes completed/sold listings, archives everything in PostgreSQL, and exposes a fully documented REST API.

2. **React/Vite frontend** — a single-page dashboard for configuring tracked search queries, browsing live and sold listing archives, viewing price trend charts, and controlling the scheduler. Extremely fast, with top loading bar (NProgress) and a live "items evaluated" counter.

3. **Comprehensive test suite** — pytest unit + integration tests for every backend service and router, Vitest unit tests for every frontend component and hook, Playwright E2E tests for every user workflow.

## Why

eBay shut down Market Insights API access for hobbyist/non-enterprise developers, removing the only programmatic route to historical sales trends, demand metrics, and competitor pricing. Terapeak (eBay's commercial successor) is paywalled. This project is a DIY replacement: run your own scheduled snapshots, accumulate time-series data in your own PostgreSQL instance, and query it freely.

## Referenced best-practice sources

- **FastAPI + async SQLAlchemy 2 pattern**: Official FastAPI docs (https://fastapi.tiangolo.com/tutorial/sql-databases/) and SQLAlchemy 2.0 async docs (https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) — the AsyncSession + async engine pattern is the standard for production FastAPI apps.

- **APScheduler 4 AsyncScheduler**: APScheduler 4.x docs (https://apscheduler.readthedocs.io/en/4.x/) — AsyncScheduler with AsyncIOScheduler backend is the correct modern pattern for in-process async scheduling in FastAPI.

- **React + Vite + shadcn/ui stack**: shadcn/ui official docs (https://ui.shadcn.com/docs), Vite official docs (https://vitejs.dev/guide/) — widely adopted in 2025-2026 React projects; TanStack Query v5 is the community standard for server state management.

- **NProgress top loading bar**: The nprogress library (https://ricostacruz.com/nprogress/) is the canonical solution for top-of-page loading indicators in SPAs.

- **Loguru for structured human-readable logging**: Loguru docs (https://loguru.readthedocs.io/en/stable/) — widely used in Python projects requiring human-readable structured logs with rotation and dual sink.

## Scope

- Backend: FastAPI 0.115, Python 3.12, SQLAlchemy 2 async, asyncpg, APScheduler 4, httpx, BeautifulSoup4, Loguru, Pydantic-Settings, Alembic
- Frontend: React 18, TypeScript, Vite 5, shadcn/ui, Tailwind CSS 3, TanStack Query v5, TanStack Router v1, Recharts, NProgress
- Testing: pytest + pytest-asyncio, Vitest + RTL, Playwright
- Infrastructure: Docker Compose, single config.toml, .env for secrets

## Out of scope (v1)

- Multi-user accounts
- Image blob archiving (URLs stored only)
- eBay OAuth / user-token scopes
- Price alerting / push notifications
- ML forecasting models
