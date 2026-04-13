# Design: AppConfig Type Mismatch Fix

## Architecture
No architectural changes. This is a type correction in existing code.

## Changes Required

### Frontend: src/pages/Queries.tsx
**Current (broken):**
```typescript
const defaultIntervalMinutes = appConfig?.scheduler?.default_interval_minutes ?? 1440
```

**Fixed:**
```typescript
const defaultIntervalMinutes = appConfig?.scheduler_default_interval_minutes ?? 1440
```

Also fix the fallback usage in the onChange handler:
```typescript
// Current (works but wrong):
onChange={(e) => setForm((f) => ({ ...f, interval_minutes: parseInt(e.target.value) || 60 }))}

// Fixed (uses new default):
onChange={(e) => setForm((f) => ({ ...f, interval_minutes: parseInt(e.target.value) || defaultIntervalMinutes }))}
```

Already updated but needs to use correct property name.

## Type Safety
- The `AppConfig` interface is the source of truth (frontend/src/api/client.ts)
- AppConfig structure: flat properties, no nested `scheduler` object
- This fix aligns the code with the actual API response type

## No Database Changes
- No migrations needed
- No model changes needed
- No API changes needed

## Build & Deploy
- TypeScript will validate the fix
- Frontend build will pass
- Backend unaffected
- Coolify deployment will succeed
