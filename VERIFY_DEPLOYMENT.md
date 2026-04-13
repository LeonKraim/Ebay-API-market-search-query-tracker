# ✅ DEPLOYMENT VERIFICATION CHECKLIST

**Fix Deployed**: Commit `9809e29` - Settings now persist correctly to new query form defaults

## 🔍 Step 1: Wait for Coolify to Deploy
- Coolify auto-detects git commits every 1-5 minutes
- Latest commit: `9809e29` (pushed just now)
- Deployment should start within 5 minutes automatically
- Check Coolify dashboard for deployment status

## ⚙️ Step 2: Verify Deployment Succeeded (CRITICAL)

**In Coolify Dashboard:**
1. Navigate to your application
2. Look for the latest deployment status
3. Both backend and frontend containers should show: ✅ **RUNNING**
4. Backend logs should show:
   ```
   [ALEMBIC] Running migration...
   [DB] All tables verified / created
   [SCHEDULER] Background scheduler started
   [APP] Startup complete — auth_enabled=False
   ```

**If deployment failed:**
- Check backend logs for errors
- If postgres failed, wait 30s for health check and retry
- If build failed, check compiler errors

## 🧪 Step 3: Functional Test (This is the REAL verification)

### Test A: Verify Settings Persist
1. Open your deployed app in browser
2. Go to **Settings** tab
3. Change "Default Poll Interval" to a custom value (example: **1500** minutes)
4. Click **Save**
5. Observe: Button should show "Save" → click → "Saving..." → "Save" (reset)
   - This confirms the value was saved to the database ✅

### Test B: Verify New Query Uses Custom Default
1. Go to **Queries** tab
2. Click **"+ New Query"** button
3. Look at the "Interval (minutes)" field
4. **EXPECTED**: Shows **1500** (the value you set in Step A3)
5. **BUG (if not fixed)**: Shows **1440** (hardcoded default)

### ✅ SUCCESS CRITERIA
- **Test A**: Save button works and resets after click
- **Test B**: Interval field shows custom value (not 1440)

**If both tests pass**: 🎉 **Deployment is SUCCESSFUL - Bug is FIXED**

---

## 🔧 If Test B Still Shows 1440

**Cause**: App is serving old version (hasn't redeployed yet)

**Solution**:
1. Hard refresh browser: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. Wait another 2-5 minutes for Coolify to finish deployment
3. Check Coolify dashboard to confirm "DEPLOYED" status
4. Try again

**If still shows 1440 after 10+ minutes:**
- Check Coolify deployment logs for errors
- Redeploy manually from Coolify dashboard
- Contact support if frontend still loading old code

---

## 📊 What the Fix Does

| Setting | Before (Bug) | After (Fixed) |
|---------|------------|---------------|
| You save 1442 in Settings | ✅ Saves to DB | ✅ Saves to DB |
| API `/config` returns | ❌ Nested structure | ✅ Flat structure |
| New query form gets default | ❌ Shows 1440 | ✅ Shows 1442 |

---

## 🎯 Final Verification

**Once `Test B` shows your custom interval (not 1440):**
- ✅ Everything is working
- ✅ Settings persist across app restarts  
- ✅ New queries use your configured default
- ✅ Issue RESOLVED

---

**Current Status**: ✅ Code fixed, committed, pushed to main  
**Next Action**: Coolify will auto-deploy within 5 minutes - Run the tests above

Run `/config` API test if you want early confirmation (before full UI test):
```bash
curl http://<your-domain>:47821/config
# Should return: "scheduler_default_interval_minutes": 1442
```
