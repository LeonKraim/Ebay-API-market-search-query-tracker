# Settings Persistence Fix — Deployment Issue Resolution

## Problem
User settings (poll interval, concurrent polls, max pages, scraper settings, etc.) were resetting to default values on every Coolify deployment. This was caused by PostgreSQL volume not persisting data across container restarts.

## Root Cause
When Coolify redeployed containers, the PostgreSQL data volume was being recreated/lost, causing all application settings stored in the `app_settings` database table to be wiped out.

## Solution Implemented

### 1. Docker Compose Volume Persistence (docker-compose.yml)
Updated the volume configuration to use explicit local binding:
```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./postgres_data
```

This ensures that:
- PostgreSQL data persists in a local `./postgres_data` directory
- Data survives container restarts and redeployments
- Coolify can access and preserve the volume

### 2. Diagnostic Endpoint (backend/app/routers/config_router.py)
Added `/api/v1/config/persistence-check` endpoint that returns:
- Current count of stored app settings
- List of all persisted settings with their values
- Count of saved queries in the database
- Timestamp to track when persistence was last verified

## How to Verify the Fix

### On Coolify Deployment (192.168.31.92)

1. **Save a custom setting in the UI** (e.g., change Poll Interval to 120 minutes)
2. **Wait for the save confirmation**
3. **Trigger a new deployment** by pushing a commit to GitHub (Coolify webhook auto-deploys)
4. **After deployment completes** (wait 2-3 minutes)
5. **Check the persistence endpoint**:
   ```bash
   curl http://192.168.31.92:3001/api/v1/config/persistence-check
   ```
   
   Expected response:
   ```json
   {
     "timestamp": "2026-04-13T...",
     "app_settings_count": 1,
     "saved_queries_count": 42,
     "settings": {
       "scheduler_default_interval_minutes": "120"
     },
     "persistence_status": "✅ Data persisting"
   }
   ```

### If Settings Are Still Resetting

If the `persistence_check` endpoint shows `"persistence_status": "❌ No persistent data"` after a fresh deployment:

1. **Coolify volume may not be mounted correctly** — Check Coolify dashboard for volume mount errors
2. **PostgreSQL container may be restarting** — Check Docker logs: `docker logs <postgres-container-id>`
3. **Volume may be recreated on each deploy** — Verify in Coolify that persistence volumes are enabled

### Commands to Debug

```bash
# SSH into Coolify server and check volume
docker volume ls | grep postgres

# Inspect PostgreSQL volume
docker volume inspect postgres_data

# Check if data persists
docker exec <postgres-container> psql -U ebay -d ebay_market_intel -c "SELECT * FROM app_settings;"
```

## Files Modified
- `docker-compose.yml` — Added explicit local volume binding
- `backend/app/routers/config_router.py` — Added persistence-check endpoint with SearchQuery import

## Commit
- SHA: `a28956cae72205512214622b6c0c9a54840c2ec0`
- Message: "Fix: Ensure PostgreSQL volume persists across deployments"

## Testing Timeline
1. ✅ Code changes committed and pushed to GitHub
2. ⏳ Coolify webhook triggers automatic redeploy
3. ⏳ After deployment: Save a setting and trigger another deploy to verify persistence
4. ⏳ Use `/config/persistence-check` endpoint to confirm data survives redeployment
