"""Unit tests for the deduplication service."""
from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.dedup import DeduplicationResult, classify
from app.services.ebay_finding import RawListing


def _make_listing(item_id: str, price: float | None = 9.99) -> RawListing:
    return RawListing(
        item_id=item_id,
        title=f"Item {item_id}",
        current_price=Decimal(str(price)) if price is not None else None,
        currency="GBP",
        buy_it_now=True,
        listing_type="FixedPrice",
        watch_count=None,
        bid_count=None,
        selling_state="Active",
        country="GB",
        postal_code=None,
        end_time=None,
        item_url=f"https://ebay.co.uk/itm/{item_id}",
        gallery_url=None,
        image_url=None,
        description=None,
    )


class TestClassify:
    def test_all_new_when_existing_is_empty(self):
        items = [_make_listing("A"), _make_listing("B")]
        result = classify(items, {})
        assert len(result.new) == 2
        assert result.updated == []
        assert result.unchanged == []
        assert result.total == 2


    def test_unchanged_when_price_identical(self):
        existing = {"A": Decimal("9.99")}
        items = [_make_listing("A", price=9.99)]
        result = classify(items, existing)
        assert [r.item_id for r in result.unchanged] == ["A"]
        assert result.new == []
        assert result.updated == []

    def test_updated_when_price_differs(self):
        existing = {"A": Decimal("9.99")}
        items = [_make_listing("A", price=7.50)]
        result = classify(items, existing)
        assert [r.item_id for r in result.updated] == ["A"]
        assert result.new == []
        assert result.unchanged == []

    def test_new_item_not_in_existing(self):
        existing = {"KNOWN": Decimal("5.00")}
        items = [_make_listing("KNOWN", price=5.00), _make_listing("NEW")]  # KNOWN price matches existing
        result = classify(items, existing)
        assert [r.item_id for r in result.new] == ["NEW"]
        assert [r.item_id for r in result.unchanged] == ["KNOWN"]

    def test_price_none_existing_price_none_counts_as_unchanged(self):
        existing: dict = {"A": None}
        items = [_make_listing("A", price=None)]
        result = classify(items, existing)
        assert [r.item_id for r in result.unchanged] == ["A"]

    def test_price_none_to_value_counts_as_updated(self):
        existing: dict = {"A": None}
        items = [_make_listing("A", price=5.00)]
        result = classify(items, existing)
        assert [r.item_id for r in result.updated] == ["A"]

    def test_total_equals_sum_of_buckets(self):
        existing = {"X": Decimal("1.00"), "Y": Decimal("2.00")}
        items = [
            _make_listing("X", price=1.00),   # unchanged
            _make_listing("Y", price=3.00),   # updated
            _make_listing("Z", price=0.50),   # new
        ]
        result = classify(items, existing)
        assert result.total == 3
        assert len(result.new) + len(result.updated) + len(result.unchanged) == 3

    def test_empty_input_returns_empty_result(self):
        result = classify([], {})
        assert result.total == 0
        assert isinstance(result, DeduplicationResult)

    def test_large_batch_all_new(self):
        items = [_make_listing(str(i)) for i in range(500)]
        result = classify(items, {})
        assert len(result.new) == 500
        assert result.total == 500

    def test_decimal_precision_not_float_error(self):
        """Ensure 0.1 + 0.2 == 0.3 style float traps do not cause false updates."""
        existing = {"A": Decimal("0.30")}
        listing = _make_listing("A", price=None)
        # Set price manually to simulate 0.1+0.2 which in float != 0.3
        listing = RawListing(
            item_id="A",
            title="A",
            current_price=Decimal("0.1") + Decimal("0.2"),  # exactly 0.3 in Decimal
            currency="GBP",
            buy_it_now=True,
            listing_type="FixedPrice",
            watch_count=None,
            bid_count=None,
            selling_state="Active",
            country="GB",
            postal_code=None,
            end_time=None,
            item_url="https://ebay.co.uk/itm/A",
            gallery_url=None,
            image_url=None,
            description=None,
        )
        result = classify([listing], existing)
        assert [r.item_id for r in result.unchanged] == ["A"], "Decimal arithmetic should match exactly"
