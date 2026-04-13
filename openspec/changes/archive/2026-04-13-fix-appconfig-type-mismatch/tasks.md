# Tasks: AppConfig Type Mismatch Fix

## Implementation Tasks

- [ ] Fix property access in src/pages/Queries.tsx line 34: change `appConfig?.scheduler?.default_interval_minutes` to `appConfig?.scheduler_default_interval_minutes`
- [ ] Update defaultIntervalMinutes variable initialization to use corrected property path
- [ ] Run TypeScript compiler to verify no errors
- [ ] Build frontend with `npm run build` to verify build succeeds
- [ ] Commit changes to git
- [ ] Push to main branch for Coolify deployment
- [ ] Verify Coolify deployment succeeds
- [ ] Verify new query form shows 1440 minutes default
- [ ] Archive change in OpenSpec
