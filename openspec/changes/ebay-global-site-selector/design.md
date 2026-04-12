# Design: eBay Global Site Selector

## Approach
Since the app already reads `ebay.site_id` from `config.toml` and uses it as the default for new queries, we need:

1. A **canonical list of eBay site IDs** shared between backend and frontend
2. A **Settings API endpoint** to read and update the global site
3. A **Settings UI dropdown** to pick the global site
4. A **Query form dropdown** to replace the free-text site ID input

## Backend Changes

### 1. eBay Sites Constant (new: `backend/app/services/ebay_sites.py`)
A simple dictionary mapping GLOBAL-ID → display name:
```python
EBAY_SITES = {
    "EBAY-US": "United States",
    "EBAY-GB": "United Kingdom", 
    "EBAY-DE": "Germany",
    "EBAY-FR": "France",
    "EBAY-AU": "Australia",
    "EBAY-CA": "Canada",
    "EBAY-AT": "Austria",
    "EBAY-CH": "Switzerland",
    "EBAY-IT": "Italy",
    "EBAY-ES": "Spain",
    "EBAY-NL": "Netherlands",
    "EBAY-BE-FR": "Belgium (French)",
    "EBAY-BE-NL": "Belgium (Dutch)",
    "EBAY-IE": "Ireland",
    "EBAY-PL": "Poland",
    "EBAY-MOTOR": "eBay Motors",
}
```

### 2. Config Router Update (`backend/app/routers/config_router.py`)
- Add `GET /config/ebay-sites` → returns list of `{id, name}` objects
- Add `PUT /config/ebay-site` → accepts `{site_id: str}`, validates against known sites, updates `config.toml`, clears settings cache
- The PUT endpoint writes to `config.toml` using `tomli_w` (or manual write) and calls `get_settings.cache_clear()` to reload

### 3. Config.py
- Clear `lru_cache` when site changes so new settings are picked up

## Frontend Changes

### 4. Settings Page (`frontend/src/pages/Settings.tsx`)
- Add a "Default eBay Marketplace" section with a `<select>` dropdown
- Fetch available sites from `GET /config/ebay-sites`
- On change, call `PUT /config/ebay-site` with the selected site ID
- Show success/error feedback

### 5. Queries Form (`frontend/src/pages/Queries.tsx`)
- Replace the free-text `site_id` input with a `<select>` dropdown using the same site list
- Pre-populate with the global default

### 6. API Client + Hooks
- Add `api.config.sites()` and `api.config.updateSite()` methods
- Add `useEbaySites()` and `useUpdateEbaySite()` hooks

## No DB Migration Needed
The `search_queries.site_id` column already stores the GLOBAL-ID string. No schema change required.
