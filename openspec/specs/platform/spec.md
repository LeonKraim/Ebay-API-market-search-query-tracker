# platform Specification

## Purpose
TBD - created by archiving change ebay-market-intel-platform. Update Purpose after archive.
## Requirements
### Requirement: Full-stack eBay market intelligence system
The system MUST provide a complete eBay market intelligence platform with FastAPI backend, React frontend, and PostgreSQL storage.

#### Scenario: Backend API is accessible
Given the Docker Compose stack is running
When a GET request is made to http://localhost:8000/api/v1/queries
Then the response MUST return HTTP 200 with a JSON array

#### Scenario: Frontend dashboard is accessible
Given the Docker Compose stack is running
When a browser navigates to http://localhost:3000
Then the eBay Market Intel dashboard MUST render with navigation sidebar and main content

#### Scenario: Search query can be created
Given the API is running with a connected database
When a POST request is made to /api/v1/queries with name, keyword, and site_id
Then the query MUST be persisted and returned in subsequent GET /api/v1/queries

#### Scenario: Scheduled poll runs and stores results
Given a search query exists and the scheduler is running
When the query's interval_minutes elapses
Then a snapshot MUST be created, eBay Finding API MUST be called, and listing_records MUST be inserted

### Requirement: eBay Finding API integration
The backend MUST poll eBay's Finding API to retrieve live listings based on configured search queries.

#### Scenario: Finding API fetches all pages up to max_pages
Given a keyword that has more than one page of results
When poll_runner executes for that query
Then pages MUST be fetched sequentially up to config.ebay.max_pages

#### Scenario: Finding API handles 429 rate limit with retry
Given the eBay API returns HTTP 429
When the client receives this response
Then it MUST retry with exponential backoff up to config.ebay.retry_attempts times

#### Scenario: Finding API handles malformed response
Given the eBay API returns unparseable XML
When the parser encounters the response
Then the snapshot MUST be marked as status=error and the error MUST be logged

### Requirement: Sold listings scraper
The backend MUST scrape completed/sold listings from eBay search results pages.

#### Scenario: Scraper extracts sold price and date
Given a keyword and a valid eBay completed listings HTML page
When the scraper runs
Then sold_price, sold_date, title, item_url MUST all be extracted for each listing

#### Scenario: Scraper detects HTML structure change
Given the eBay HTML page returns zero parsed items despite visible listings
When the scraper encounters this condition
Then a WARNING MUST be logged indicating potential HTML structure change

### Requirement: Price trend statistics
The stats API MUST provide aggregated price trends over time for configured queries.

#### Scenario: Price trend returns daily aggregates
Given a query with listing_records spanning multiple days
When GET /api/v1/stats/price-trend?query_id=X&interval=day is called
Then the response MUST include avg_price, min_price, max_price, count per day

#### Scenario: Items evaluated counter returns total
Given listing_records and sold_records exist in the database
When GET /api/v1/stats/items-evaluated is called
Then the response MUST return the total count of all unique items ever recorded

### Requirement: Optional Bearer token authentication
When auth is enabled, all API endpoints MUST require a valid Bearer token.

#### Scenario: Request without token returns 401 when auth enabled
Given config.auth.enabled is true
When an API request is made without an Authorization header
Then the response MUST be HTTP 401 Unauthorized

#### Scenario: Request with valid token succeeds
Given config.auth.enabled is true and a valid API_TOKEN is configured
When an API request includes Authorization: Bearer <token>
Then the request MUST be processed normally

#### Scenario: Token comparison uses timing-safe comparison
Given any token validation check
When the comparison is performed
Then secrets.compare_digest() MUST be used (not == operator) to prevent timing attacks

### Requirement: Structured logging with dual sink
The backend MUST log to both console and file simultaneously using Loguru.

#### Scenario: Logs written to both console and file
Given the application is running
When any log event occurs
Then it MUST appear in both stdout and logs/app.log

#### Scenario: Log file rotates at 50MB
Given logs/app.log reaches 50MB
When the next log entry is written
Then Loguru MUST rotate the log file and start a new one

#### Scenario: Sensitive values never logged
Given any logging operation
When the log message is written
Then API keys, tokens, passwords MUST NOT appear in any log output

### Requirement: Docker Compose multi-container deployment
The entire stack MUST be launchable via docker compose up with no additional setup.

#### Scenario: All three services start successfully
Given a valid .env file and docker compose up is run
When all containers start
Then postgres, backend, and frontend containers MUST all reach healthy/running state

#### Scenario: Backend waits for database health check
Given the postgres container is starting
When the backend container starts
Then it MUST wait for postgres to pass its health check before starting Alembic migrations

