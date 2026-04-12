# Tasks: eBay Global Site Selector

- [ ] 1. Create `backend/app/services/ebay_sites.py` with canonical EBAY_SITES dict
- [ ] 2. Add `GET /config/ebay-sites` and `PUT /config/ebay-site` endpoints to config_router.py
- [ ] 3. Add `tomli_w` dependency for TOML writing (or use string replacement)
- [ ] 4. Update frontend API client with `sites()` and `updateSite()` methods + hooks
- [ ] 5. Update Settings page with eBay marketplace dropdown selector
- [ ] 6. Update Queries form: replace free-text site_id with dropdown
- [ ] 7. Rebuild Docker, verify Settings UI shows dropdown and saves correctly
- [ ] 8. Test with EBAY-DE: create query, run it, check logs for successful fetch
- [ ] 9. Run full backend test suite and fix any failures
