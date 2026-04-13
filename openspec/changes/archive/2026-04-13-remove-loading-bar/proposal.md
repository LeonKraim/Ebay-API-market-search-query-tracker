# Proposal: Remove Loading Bar

## Why
User wants a cleaner UI without the blue NProgress loading bar.

## What Changes
- Remove the blue NProgress top loading bar that appears during API requests.
- Remove NProgress import and start/done calls from `client.ts`
- Remove `#nprogress` CSS rules from `index.css`
- Delete unused `TopLoadingBar.tsx` component

## Files Affected
- `frontend/src/api/client.ts` — remove NProgress import and start/done calls
- `frontend/src/index.css` — remove #nprogress CSS rules
- `frontend/src/components/layout/TopLoadingBar.tsx` — deleted (unused component)

## Acceptance Criteria
1. No blue bar appears at the top during any page load or data fetch
2. All other UI elements remain unaffected
3. No console errors related to NProgress
