# Proposal: Fix Docker DB Config Override

## What
The backend cannot connect to Postgres when running inside Docker because `config.toml` hardcodes `db_host = "localhost"` and `db_name = "ebay_intel"`, and the docker-compose environment variables `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME` are never read by the Settings class.

## Why
`docker compose up` fails with `ConnectionRefusedError: [Errno 111] Connection refused` because the backend tries to connect to `localhost:5432/ebay_intel` instead of `postgres:5432/ebay_market_intel`.

## Root Cause
`get_settings()` calls `Settings()` (reads .env secrets), then `_apply_toml()` (reads config.toml). The docker-compose passes `DATABASE_HOST=postgres`, `DATABASE_PORT=5432`, `DATABASE_NAME=ebay_market_intel` as env vars, but `_apply_toml()` always overwrites `db_host`/`db_port`/`db_name` from config.toml — which has `localhost` and `ebay_intel`.

## Fix
After `_apply_toml()`, add an env-var override step that checks `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME` and applies them if present. This preserves the config.toml-first design while allowing Docker to override at runtime.
