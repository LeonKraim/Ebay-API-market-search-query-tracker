# Config Env Override Spec

## ADDED Requirements

### Requirement: Database env var override
The `get_settings()` function MUST apply environment variable overrides for `DATABASE_HOST`, `DATABASE_PORT`, and `DATABASE_NAME` after loading config.toml, so that Docker runtime env vars take precedence.

#### Scenario: Docker environment provides DATABASE_HOST
Given the environment variable `DATABASE_HOST` is set to `postgres`
When `get_settings()` is called
Then `settings.db_host` MUST equal `postgres`

#### Scenario: No DATABASE_HOST in environment
Given the environment variable `DATABASE_HOST` is not set
When `get_settings()` is called
Then `settings.db_host` MUST equal the value from config.toml (default `localhost`)

#### Scenario: Docker environment provides DATABASE_NAME
Given the environment variable `DATABASE_NAME` is set to `ebay_market_intel`
When `get_settings()` is called
Then `settings.db_name` MUST equal `ebay_market_intel`
