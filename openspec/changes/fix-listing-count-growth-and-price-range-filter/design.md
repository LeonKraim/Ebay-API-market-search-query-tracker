# Design: Fix listing count growth and add price range filter

## 1. Reduce max_pages: config.toml

Change one line:
```toml
# before
max_pages = 10
# after
max_pages = 3
```
This is a config-only change with no code or schema impact. The value flows through
`Settings.ebay_max_pages` → `fetch_all_listings` → loop guard `while page <= min(total_pages, settings.ebay_max_pages)`.

## 2. Database schema — new columns on `search_queries`

Add two nullable `NUMERIC(12,2)` columns:
- `min_price` — minimum item price filter (inclusive lower bound for Browse API)
- `max_price` — maximum item price filter (inclusive upper bound for Browse API)

Both default to `NULL` (no filter applied).

### Alembic migration `0002`

```python
op.add_column("search_queries", sa.Column("min_price", sa.Numeric(12, 2), nullable=True))
op.add_column("search_queries", sa.Column("max_price", sa.Numeric(12, 2), nullable=True))
```

No data migration needed (existing rows get NULL, which means no filter — backward compatible).

## 3. SQLAlchemy model update

In `app/models/query.py` import `Numeric` and add:
```python
from decimal import Decimal
from sqlalchemy import Numeric

min_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
max_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
```

## 4. Pydantic schemas update

In `app/schemas/query.py`:
- `QueryCreate`: add `min_price: Decimal | None = None`, `max_price: Decimal | None = None`
- `QueryUpdate`: same (both optional)
- `QueryRead`: add both fields

Use `Decimal` from stdlib. Pydantic handles JSON serialisation automatically.

## 5. eBay Browse API price filter

The Browse API `filter` parameter accepts compound filters separated by commas.
Current default filter: `buyingOptions:{AUCTION|FIXED_PRICE}`

When `price_min` or `price_max` is set, append:
`price:[MIN..MAX],priceCurrency:CURRENCY`

Where `MIN` and `MAX` default to `*` if not provided (open-ended):
- Only min: `price:[100..],priceCurrency:EUR`  (actually Browse API uses `price:[100..*]` but eBay accepts `price:[100..]` too)
- Only max: `price:[..300],priceCurrency:EUR`
- Both:     `price:[100..300],priceCurrency:EUR`

The currency for the price filter must match the site's currency:
- EBAY-DE → EUR, EBAY-GB → GBP, EBAY-US → USD, EBAY-AU → AUD, EBAY-FR → EUR, etc.

### `_fetch_page` signature addition

Add `price_min: Decimal | None = None` and `price_max: Decimal | None = None` parameters.

Build the filter string:
```python
filter_parts = ["buyingOptions:{AUCTION|FIXED_PRICE}"]
if price_min is not None or price_max is not None:
    lo = str(price_min) if price_min is not None else ""
    hi = str(price_max) if price_max is not None else ""
    currency = _site_currency(site_id)
    filter_parts.append(f"price:[{lo}..{hi}],priceCurrency:{currency}")
params["filter"] = ",".join(filter_parts)
```

### Site → currency mapping helper

```python
_SITE_CURRENCY: dict[str, str] = {
    "EBAY-US": "USD", "EBAY-GB": "GBP", "EBAY-DE": "EUR",
    "EBAY-AU": "AUD", "EBAY-CA": "CAD", "EBAY-FR": "EUR",
    "EBAY-IT": "EUR", "EBAY-ES": "EUR",
}
def _site_currency(site_id: str) -> str:
    return _SITE_CURRENCY.get(site_id.upper(), "USD")
```

### `fetch_all_listings` signature addition

Add `price_min: Decimal | None = None`, `price_max: Decimal | None = None` and forward to `_fetch_page`.

## 6. Poll runner — pass price fields from query

```python
raw_listings = await fetch_all_listings(
    keyword=query.keyword,
    category_id=query.category_id,
    site_id=query.site_id,
    price_min=query.min_price,
    price_max=query.max_price,
)
```

## 7. Frontend — client types

In `frontend/src/api/client.ts`:
```typescript
export interface SearchQuery {
  ...
  min_price: number | null
  max_price: number | null
}

export interface QueryCreate {
  ...
  min_price?: number | null
  max_price?: number | null
}
```

## 8. Frontend — query form

In `frontend/src/pages/Queries.tsx`, add two optional number inputs after the existing fields:
- "Min Price" and "Max Price" in a row (side by side)
- Both `type="number"` with `min="0"` and `step="0.01"` for decimal entry
- Empty string maps to `null` in form state

## Verification plan

1. Run Alembic migration in the Postgres container.
2. Run `backend/.venv/Scripts/python.exe -m pytest` → all tests pass.
3. `docker compose up --build -d backend frontend`
4. In the UI, edit the "nintendo switch" query to set Min Price=50, Max Price=300.
5. Trigger a manual run; check backend logs for `price:[50..300],priceCurrency:EUR` in the Browse API filter line.
6. Check the number of new items found in the snapshot is reduced.
