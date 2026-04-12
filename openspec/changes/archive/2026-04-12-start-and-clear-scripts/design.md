# Design: Start and Clear Data Scripts

## Files Created

### `start.bat`

Steps:
1. Check `docker` command is available — error + pause if not.
2. Check `.env` exists — if not, copy `.env.example` to `.env` and warn the user to edit it first.
3. `docker compose up --build -d` — builds images and starts all services detached.
4. Poll `http://localhost:8000/health` in a loop (max 60 s, 2 s intervals) until it returns 200.
5. Print the frontend (`http://localhost:3000`) and backend (`http://localhost:8000`) URLs.

### `clear_data.bat`

Steps:
1. Prompt the user for confirmation: "This will DELETE ALL DATA. Continue? (y/n)"
2. If not `y`, abort.
3. `docker compose down -v` — stops containers AND removes named volumes (drops Postgres data).
4. Delete contents of `logs\` directory (keep the folder).
5. Print "All data cleared. Run start.bat to bring the stack back up."

## Error Handling

- `start.bat` exits with code 1 if Docker is not found.
- `clear_data.bat` exits gracefully if the user declines.
- Both scripts `cd /d %~dp0` at the top to ensure they run from the repo root regardless of where they are invoked.

## Security

- `.env` is NOT created automatically with real secrets; it is copied verbatim from `.env.example` and the script explicitly tells the user to edit it.
- `clear_data.bat` requires explicit `y` confirmation before destructive action.
