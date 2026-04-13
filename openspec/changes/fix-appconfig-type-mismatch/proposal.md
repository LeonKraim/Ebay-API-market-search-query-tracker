# Fix: AppConfig Type Mismatch in QueriesPage

## Problem
The frontend build fails with TypeScript error:
```
src/pages/Queries.tsx:34:45 - error TS2339: Property 'scheduler' does not exist on type 'AppConfig'.
```

The code tries to access `appConfig?.scheduler?.default_interval_minutes`, but the `AppConfig` interface defines flat, non-nested properties like `scheduler_default_interval_minutes`.

## Root Cause
When implementing dynamic default interval in QueriesPage, the code incorrectly assumed a nested object structure that doesn't exist in the AppConfig type definition.

## Solution
Update the property access in Queries.tsx to match the flat AppConfig interface structure: use `appConfig?.scheduler_default_interval_minutes` instead of `appConfig?.scheduler?.default_interval_minutes`.

## Impact
- **Scope**: Frontend only, 1 file, 2 line changes
- **Risk**: Low — fixes broken TypeScript compilation, enables successful deployment
- **User Impact**: None negative; enables the new feature (default interval applied to new queries)

## Acceptance Criteria
1. Frontend TypeScript compiles without errors
2. Frontend builds successfully with `npm run build`
3. Deployment to Coolify succeeds
4. New query form defaults to 1440 minutes (1 day) from config
