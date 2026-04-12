# Tasks: Stop active polls and inline query enable toggle

- [x] 1. Add cooperative stop-signal support to the poll runner and expose running query IDs
- [x] 2. Add the query stop endpoint and extend scheduler status with `running_query_ids`
- [x] 3. Extend frontend API types and hooks for stop requests and refreshed scheduler status
- [x] 4. Update the query card to show inline enabled toggle and `Stop` while polling
- [ ] 5. Wire the Queries page to scheduler status, stop mutation, and inline enabled toggles
- [ ] 6. Run the app and verify the stop/toggle workflow visually
- [ ] 7. Run relevant tests and fix any regressions introduced by this change
- [ ] 8. Validate and archive the OpenSpec change