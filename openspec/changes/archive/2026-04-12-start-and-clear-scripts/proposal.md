# Proposal: Start and Clear Data Scripts

## Why

Developers need a single-command way to:
1. Start the entire stack (Postgres → backend → frontend) with build
2. Wipe all persisted data cleanly for a fresh start

Without these scripts, users must remember multiple Docker commands, set up `.env`, and wait
for health checks manually. A Windows-native `.bat` file is the right tool here because the
OS is Windows and the workspace already uses a Docker Compose stack.

## What Changes

- **`start.bat`** — checks for `.env`, builds and starts `docker compose up --build -d`,
  polls until the backend `/health` endpoint responds, then prints the app URLs.
- **`clear_data.bat`** — stops all containers, removes the postgres named volume
  (`docker compose down -v`), and empties the `logs/` directory.

No source files are modified. No new Python dependencies. No schema changes.
