# Design: Fix Docker DB Config Override

## Approach
Add an `_apply_env_overrides()` method to `Settings` that reads `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME` from `os.environ` and overrides the respective fields if present.

Call this method in `get_settings()` after `_apply_toml()`.

## Changes
- `backend/app/config.py`: Add `_apply_env_overrides()` method and call it in `get_settings()`.

## No other files change.
