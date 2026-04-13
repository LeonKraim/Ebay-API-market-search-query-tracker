# Ebay-API-market-search-query-tracker

A self-hosted market intelligence tool that periodically snapshots eBay listings for tracked search queries and archives the results in PostgreSQL. Built for tracking marketplace trends, competitor pricing, and demand signals.

## What This Project Does

This is a DIY replacement for eBay's Market Insights API. The core idea is simple: run saved search queries on a schedule, snapshot every result, and build up your own time-series database of the market.

Over days and weeks you start to see what is actually selling, how prices move, which listings linger and which get snapped up fast.

Concretely, the project aims to:

- Track any eBay search query over time by configuring keywords and categories once
- Archive rich listing data: title, description, images, current price, buy-it-now availability, listing type, watcher count, country, and end time
- Track sold and completed listings by scraping eBay's completed-items pages
- Build a personal market database in PostgreSQL
- Support trend analysis with data accumulating over time in a structured schema

## Key Features

### Query Management

- Create queries with keyword, eBay site, category, and min/max price filters
- Enable or disable queries without stopping active polls
- Configurable poll intervals
- Include or exclude sold listings
- Inline controls on each query card to run, stop, edit, or delete

### Real-Time Polling

- Automatic background scheduler runs enabled queries on their configured intervals
- Cooperative cancellation to stop an active poll without waiting for completion
- Cancellation stops between eBay API page requests, not after the entire fetch
- Optimistic UI so stop button feedback is instant with no delay

### Snapshots and Deduplication

- Each poll creates a snapshot record capturing number of listings found
- Tracks number of new vs updated vs previous listings
- Captures poll start and finish times along with status
- Intelligent deduplication groups listings by ID across multiple polls and queries
- Tracks item price changes, condition updates, and time-to-sell

### Scraping

- eBay Browse API integration for live listings
- Optional sold-listing scraper extracts metadata from completed eBay listings

### Dashboard and Analytics

- Dashboard page shows total unique items evaluated and scheduler running status
- Stats page displays marketplace trends and item metrics
- Listings page shows all captured listings with detailed filtration
- Sold page displays scraped sold listing data
- Logs page with real-time refresh showing all API and scheduler activity

### Scheduler Controls

- Pause or resume all enabled scheduled queries
- View which queries are actively polling
- Stop a specific running query without pausing others
- Graceful shutdown on app termination

## Tech Stack

### Backend

FastAPI 0.115.12, Uvicorn 0.34.0, SQLAlchemy 2.0.40, Alembic 1.15.2, APScheduler 4.0.0a5, Pydantic 2.11.3, httpx 0.28.1, BeautifulSoup4 4.13.3, Loguru 0.7.3

### Database

PostgreSQL 16 with async driver asyncpg, Alembic migrations for schema management, cascade delete support

### Frontend

React 18.3.1, TypeScript 5.5.3, Vite 5.3.4, TanStack Query 5.51.1, TanStack Router 1.48.0, Tailwind CSS 3.4.6, Recharts 2.12.7, Lucide React 0.418.0

### Deployment

Docker and Docker Compose for containerization, Nginx reverse proxy in frontend container

## Architecture

### Backend Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app factory and lifespan
│   ├── config.py                  # Configuration from config.toml and .env
│   ├── database.py                # SQLAlchemy session and engine
│   ├── logging_setup.py           # Loguru configuration
│   ├── scheduler.py               # APScheduler lifecycle and sync
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── query.py               # SearchQuery model
│   │   ├── snapshot.py            # Snapshot poll records
│   │   ├── listing.py             # Live listing records
│   │   ├── sold.py                # Sold listing records
│   ├── routers/                   # FastAPI route handlers
│   │   ├── queries.py             # Query CRUD and stop endpoint
│   │   ├── snapshots.py           # Snapshot queries
│   │   ├── listings.py            # Listing queries
│   │   ├── sold.py                # Sold records
│   │   ├── scheduler.py           # Scheduler status and control
│   │   ├── stats.py               # Analytics
│   │   ├── logs.py                # Log file retrieval
│   │   ├── auth.py                # Token verification
│   ├── services/                  # Business logic
│   │   ├── poll_runner.py         # Poll orchestration and cancellation
│   │   ├── ebay_finding.py        # eBay Browse API integration
│   │   ├── sold_scraper.py        # HTML scraping
│   │   ├── dedup.py               # Deduplication logic
│   ├── schemas/                   # Pydantic request and response schemas
├── tests/
│   ├── unit/                      # Unit tests with mocked DB and API calls
│   ├── integration/               # Integration tests with real DB
│   ├── edge_cases/                # Edge case tests
├── migrations/                    # Alembic SQL migrations
├── pyproject.toml                 # Dependencies and pytest config
├── config.toml                    # Non-secret settings
├── Dockerfile                     # Backend container
```

### Frontend Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx          # Main dashboard
│   │   ├── Queries.tsx            # Query CRUD and polling controls
│   │   ├── Listings.tsx           # Browse all listings
│   │   ├── Sold.tsx               # Browse sold records
│   │   ├── Stats.tsx              # Analytics charts
│   │   ├── Scheduler.tsx          # Scheduler pause and resume
│   │   ├── Logs.tsx               # Real-time logs viewer
│   │   ├── Settings.tsx           # App configuration
│   ├── components/
│   │   ├── ui/                    # Reusable UI components
│   ├── api/
│   │   ├── client.ts              # Typed API client
│   │   ├── hooks.ts               # TanStack Query hooks
│   ├── lib/
│   │   ├── format.ts              # Date and number formatting
│   ├── App.tsx                    # Router setup
│   ├── main.tsx                   # React entry point
├── tests/                         # Vitest and Playwright tests
├── package.json
├── tsconfig.json
├── vite.config.ts                 # Vite build config
├── tailwind.config.js
├── Dockerfile                     # Frontend container with Nginx
```

### Database Schema

SearchQuery stores user-defined search configurations with id, keyword, category_id, site_id, min_price, max_price, interval_minutes, enabled, include_sold, created_at, last_polled_at, and total_snapshots.

Snapshot captures one record per poll attempt with id, query_id, started_at, finished_at, status, items_found, items_new, items_updated, and error_message.

ListingRecord stores individual eBay listings captured during polls with id, query_id, snapshot_id, item_id, title, price, condition, category, seller, url, created_at, and updated_at.

SoldRecord contains scraped metadata from completed listings with id, query_id, item_id, final_price, condition, and sold_date.

## Requirements

Python 3.12 or later, Node.js 18 or later for frontend build, Docker and Docker Compose for deployment, eBay Developer Account with API credentials, PostgreSQL 14 or later

## Setup and Installation

### Clone the Repository

```bash
git clone https://github.com/LeonKraim/Ebay-API-market-search-query-tracker.git
cd Ebay-API-market-search-query-tracker
```

### Environment Configuration

Copy the example environment file and fill in your eBay credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
EBAY_APP_ID=your_ebay_app_id_here
EBAY_CERT_ID=your_ebay_cert_id_here
DATABASE_USER=ebay
DATABASE_PASSWORD=your_secure_database_password
API_TOKEN=your_bearer_token_for_api_auth
```

### Register with eBay Developer Program

1. Go to https://developer.ebay.com/
2. Register for a developer account
3. Create a new application in the Developer Portal
4. Under Keys and Auth section, retrieve your App ID and Cert ID
5. Paste these into `.env`

### Backend Setup for Local Development

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
# On macOS and Linux:
source .venv/bin/activate
# On Windows:
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -e ".[test]"
```

### Frontend Setup for Local Development

```bash
cd frontend
npm install
```

### Run with Docker

From project root:

```bash
docker compose up --build -d
```

This starts PostgreSQL on localhost:5432, Backend API on localhost:8000, and Frontend on localhost:3000. Wait about 10 seconds for containers to initialize.

### Run Locally Without Docker

Start PostgreSQL:

```bash
# If installed locally
postgres -D /usr/local/var/postgres

# Or use Docker for just postgres:
docker run -d \
  -e POSTGRES_DB=ebay_market_intel \
  -e POSTGRES_USER=ebay \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:16-alpine
```

Start Backend:

```bash
cd backend
export DATABASE_HOST=localhost
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at http://localhost:8000. Swagger docs at http://localhost:8000/docs.

Start Frontend:

```bash
cd frontend
npm run dev
```

UI will be available at http://localhost:5173 or http://localhost:3000 depending on setup.

## Usage

### Create a Search Query

1. Go to Queries tab
2. Click New Query
3. Fill in the keyword which is required
4. Select eBay Site such as EBAY-GB, EBAY-DE, or EBAY-US
5. Enter Category details if needed
6. Set Min and Max Price for filtering
7. Choose Poll Interval, default is 60 minutes
8. Toggle Include Sold to include completed listings
9. Click Save

### Start Polling

Query is enabled by default so scheduler automatically starts polling on the configured interval. Click Run now to poll immediately. Click the enabled badge to toggle enable or disable on the fly. Click Stop while actively polling to stop on the fly with cancellation happening between API page requests.

### Monitor Activity

Dashboard shows scheduler status and recent activity. Scheduler tab shows pause and resume controls and running query count. Logs tab has real-time logs of all backend activity. Stats tab displays marketplace trends and item counts. Listings tab lets you browse all captured listings with filters.

## API Documentation

### Endpoints

All endpoints are prefixed with `/api/v1` and require `Authorization: Bearer <token>` if auth is enabled.

GET /queries lists all queries paginated.
GET /queries/{id} gets query details.
POST /queries creates a new query.
PATCH /queries/{id} updates query keyword, enabled, interval, and other fields.
DELETE /queries/{id} deletes query but fails if active poll is running.
POST /queries/{id}/run-now triggers immediate poll.
POST /queries/{id}/stop stops active poll and sends cancellation signal.

GET /snapshots lists all snapshots paginated.
GET /snapshots/{id} gets snapshot details.

GET /listings lists all captured listings paginated with filters.

GET /sold lists all scraped sold records.

GET /scheduler/status gets scheduler state with running, paused, active_schedules, running_jobs, and running_query_ids.
POST /scheduler/pause pauses all queries.
POST /scheduler/resume resumes all queries.

GET /stats/items-evaluated gets total unique items count.

GET /logs/app gets application log file content with optional tail parameter.

## Configuration

### Backend Settings

Edit backend/config.toml for app title and description, auth enabled flag, database pooling settings, and scheduler settings like jitter_seconds and max_concurrent_polls.

### Frontend Runtime Config

The frontend is configured via environment variables during Docker build with VITE_API_BASE_URL set to http://localhost:8000. To change API base URL, rebuild the frontend container or set the env var before npm run build.

## Database Migrations

Migrations are managed by Alembic. To create a new migration after changing models:

```bash
cd backend
alembic revision --autogenerate -m "Add new_column to SearchQuery"
alembic upgrade head
```

---

## Development

### Running Tests

Backend:

```bash
cd backend
pytest
pytest tests/unit/
pytest tests/integration/
pytest -v --tb=short
```

Frontend:

```bash
cd frontend
npm run test
npm run test:watch
npm run test:e2e
```

### Debugging

Backend logs:

```bash
# Docker
docker logs -f ebay-api-market-search-query-tracker-backend-1

# Local
tail -f ./logs/app.log
```

Frontend console:
Open browser DevTools with F12 and go to the Console tab.

## Performance Notes

### Query Optimization

Queries are indexed on keyword, site_id, enabled, and created_at for fast filtering. Snapshots are indexed on query_id and status for quick lookups. Listings use composite indexes on query_id and item_id for deduplication.

### Polling Concurrency

Default max concurrent polls is 3 and is configurable in config.toml. Semaphore-based rate limiting prevents overwhelming eBay API quota. Each poll can fetch up to about 1800 items per query limited by eBay pagination.

### Cancellation and Stop Behavior

Optimistic UI means stop button changes immediately without waiting for server confirmation. Server-side cancel event is set and next page request is skipped with current results discarded. Graceful handling means scheduler status clears running state and card swaps to Run now within next 5 second poll.

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs backend
docker compose logs frontend
docker compose logs postgres

# Restart
docker compose down
docker compose up --build -d
```

### Database Connection Failed

```bash
# Verify postgres is healthy
docker compose ps

# Check connectivity from backend container
docker exec ebay-api-market-search-query-tracker-backend-1 \
  psql -h postgres -U ebay -d ebay_market_intel -c "SELECT 1"
```

### eBay API 401 or 403 Errors

Verify EBAY_APP_ID and EBAY_CERT_ID in `.env` are correct. Ensure your eBay app has Browse API permissions enabled.

### Polls Not Running

1. Check Scheduler tab to see if it is running
2. Check Logs to look for scheduler startup and error messages
3. Verify query is enabled showing a green badge
4. Check interval_minutes is not set to 0

