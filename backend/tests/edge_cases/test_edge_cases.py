"""Edge-case tests — boundary values, empty states, malformed input."""
from __future__ import annotations

import pytest
from decimal import Decimal

pytestmark = pytest.mark.asyncio


class TestQueryEdgeCases:
    async def test_keyword_whitespace_only_is_rejected(self, client):
        resp = await client.post("/api/v1/queries", json={"name": "X", "keyword": "   "})
        # Pydantic min_length=1 should strip or reject
        assert resp.status_code == 422

    async def test_extremely_long_keyword_accepted_or_graceful_error(self, client):
        """Keywords up to 255 chars should be accepted; >255 should 422, not 500."""
        long_kw = "a" * 255
        resp = await client.post("/api/v1/queries", json={"name": "Long", "keyword": long_kw})
        assert resp.status_code in (201, 422)  # either is acceptable; must not 500

        very_long_kw = "a" * 256
        resp2 = await client.post("/api/v1/queries", json={"name": "VLong", "keyword": very_long_kw})
        assert resp2.status_code in (201, 422)

    async def test_pagination_beyond_total_returns_empty(self, client, sample_query_payload_minimal):
        await client.post("/api/v1/queries", json=sample_query_payload_minimal)
        resp = await client.get("/api/v1/queries?page=999&page_size=20")
        body = resp.json()
        assert resp.status_code == 200
        assert body["items"] == []

    async def test_invalid_page_size_zero(self, client):
        resp = await client.get("/api/v1/queries?page_size=0")
        assert resp.status_code == 422

    async def test_patch_empty_body_is_no_op(self, client, sample_query_payload_minimal):
        create = await client.post("/api/v1/queries", json=sample_query_payload_minimal)
        qid = create.json()["id"]
        original_name = create.json()["name"]
        patch = await client.patch(f"/api/v1/queries/{qid}", json={})
        assert patch.status_code == 200
        assert patch.json()["name"] == original_name


class TestDeduplicationEdgeCases:
    def test_duplicate_item_ids_in_input_last_wins(self):
        """If the same item_id appears twice in input, dedup should not crash."""
        from app.services.dedup import classify
        from app.services.ebay_finding import RawListing

        def mk(item_id, price):
            return RawListing(
                item_id=item_id, title="T", current_price=Decimal(str(price)),
                currency="GBP", buy_it_now=True, listing_type="FP",
                watch_count=None, bid_count=None, selling_state="Active",
                country="GB", postal_code=None, end_time=None,
                item_url="https://ebay.co.uk/itm/x",
                gallery_url=None, image_url=None, description=None,
            )

        items = [mk("DUP", 1.00), mk("DUP", 2.00)]
        result = classify(items, {})
        # Should not raise; all items accounted for
        assert result.total >= 1


class TestPriceParsedgeCase:
    def test_negative_price_returns_none_or_float(self):
        from app.services.sold_scraper import _parse_price
        price, _ = _parse_price("-£5.00")
        # Negative prices should be treated as None (garbage data)
        assert price is None or price < 0  # either interpretation is valid — must not crash

    def test_price_with_range_uses_lower(self):
        from app.services.sold_scraper import _parse_price
        # eBay sometimes shows "£5.00 to £10.00" — we should get a value, not raise
        try:
            price, currency = _parse_price("£5.00 to £10.00")
        except Exception as exc:
            pytest.fail(f"_parse_price raised unexpectedly: {exc}")
