# Immediate Verification Steps - Settings Persistence Fix

**CRITICAL:** Coolify has received the fix via GitHub webhook. Follow these steps to verify it's working:

## Quick Test (Do This Now)

### Step 1: Save a Setting
1. Open http://192.168.31.92:3001 in browser
2. Go to **Settings**
3. Change **"Default Poll Interval"** from `60` to `120` minutes
4. Click **Save**
5. Confirm you see success message

### Step 2: Check Settings with Diagnostic Endpoint
```bash
curl http://192.168.31.92:3001/api/v1/config/persistence-check
```

**Expected output (formatted):**
```json
{
  "timestamp": "2026-04-13T...",
  "app_settings_count": 1,
  "saved_queries_count": ...,
  "settings": {
    "scheduler_default_interval_minutes": "120"
  },
  "persistence_status": "✅ Data persisting"
}
```

### Step 3: Trigger a New Deployment (Wait 2-3 minutes for redeploy)
- Push any small commit to GitHub (e.g., add a comment)
- Or manually redeploy in Coolify dashboard

### Step 4: Verify Settings Persisted After Redeploy
1. Go back to Settings page on http://192.168.31.92:3001
2. Check if **"Default Poll Interval"** is still `120` (NOT reset to `60`)
3. Run diagnostic endpoint again:
   ```bash
   curl http://192.168.31.92:3001/api/v1/config/persistence-check
   ```

### Expected Result ✅
- **Before fix:** Settings reset to 60 after deployment ❌
- **After fix:** Settings stay at 120 after deployment ✅
- **Diagnostic shows:** `"persistence_status": "✅ Data persisting"` ✅

## If Settings Are STILL Resetting

If after following these steps settings are still reset, the volume may not be persisting on Coolify. Check:

### SSH into Coolify Server
```bash
# List Docker volumes
docker volume ls | grep postgres

# Check if volume has data
docker exec <postgres-container-id> psql -U ebay -d ebay_market_intel -c "SELECT * FROM app_settings;"

# Check Docker logs
docker logs <backend-container-id> | grep -i "persistence\|volume\|mount"
```

### Common Issues & Fixes

**Issue:** Volume shows as empty after redeploy
- **Cause:** Coolify not mounting volumes correctly
- **Fix:** SSH to Coolify, check docker-compose.yml is using the updated version:
  ```bash
  cat docker-compose.yml | grep -A3 "postgres_data:"
  ```

**Issue:** Container restarting constantly
- **Cause:** PostgreSQL not initializing properly
- **Fix:** Check PostgreSQL logs:
  ```bash
  docker logs <postgres-container-id>
  ```

## What Was Changed

### File: docker-compose.yml
```yaml
# BEFORE (data lost on restart):
volumes:
  postgres_data:
  backend_logs:

# AFTER (data persists):
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./postgres_data
  backend_logs:
    driver: local
```

### File: backend/app/routers/config_router.py
- Added new endpoint: `/api/v1/config/persistence-check`
- Endpoint returns database state to verify persistence

## GitHub Commits
- `bbecbc2` - Documentation and verification guide
- `a28956c` - Volume persistence fix in docker-compose.yml
- Both are on main branch and deployed to Coolify

---

**⏱️ Timeline:**
1. ✅ Fix committed to GitHub
2. ⏳ Coolify webhook auto-deploys (check Coolify dashboard for deployment status)
3. ⏳ **YOU TEST** - Follow verification steps above
4. ✅ Confirm settings persist after redeploy

**Report back with the diagnostic endpoint output and whether settings persisted after redeploy!**
