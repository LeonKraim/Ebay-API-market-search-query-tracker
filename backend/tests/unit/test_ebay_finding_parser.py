"""Unit tests for the eBay Browse API JSON parser."""
from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.ebay_finding import _parse_listing

# Minimal valid Browse API itemSummary dict
MINIMAL_ITEM = {
    "itemId": "v1|123456789|0",
    "legacyItemId": "123456789",
    "title": "Nintendo Switch OLED",
    "itemWebUrl": "https://www.ebay.co.uk/itm/123456789",
    "price": {"value": "249.99", "currency": "GBP"},
    "buyingOptions": ["FIXED_PRICE"],
    "itemEndDate": "2025-12-31T23:59:59.000Z",
    "image": {"imageUrl": "https://i.ebayimg.com/images/g/123/s-l140.jpg"},
    "itemLocation": {"country": "GB", "postalCode": "SW1A"},
}

AUCTION_ITEM = {
    "itemId": "v1|999|0",
    "legacyItemId": "999",
    "title": "Item at auction",
    "itemWebUrl": "https://www.ebay.co.uk/itm/999",
    "buyingOptions": ["AUCTION"],
    "bidCount": 5,
}

ITEM_MISSING_PRICE = {
    "itemId": "v1|888|0",
    "legacyItemId": "888",
    "title": "Item without price",
    "itemWebUrl": "https://www.ebay.co.uk/itm/888",
    "buyingOptions": ["AUCTION"],
}


class TestParseListingJSON:
    def test_parses_item_id(self):
        listing = _parse_listing(MINIMAL_ITEM)
        assert listing.item_id == "123456789"

    def test_parses_title(self):
        listing = _parse_listing(MINIMAL_ITEM)
        assert listing.title == "Nintendo Switch OLED"

    def test_parses_price(self):
        listing = _parse_listing(MINIMAL_ITEM)
        assert listing.current_price == Decimal("249.99")
        assert listing.currency == "GBP"

    def test_parses_buy_it_now(self):
        listing = _parse_listing(MINIMAL_ITEM)
        assert listing.buy_it_now is True

    def test_parses_listing_type(self):
        listing = _parse_listing(MINIMAL_ITEM)
        assert listing.listing_type == "FixedPrice"

    def test_parses_item_url(self):
        listing = _parse_listing(MINIMAL_ITEM)
        assert "123456789" in listing.item_url

    def test_parses_image_url(self):
        listing = _parse_listing(MINIMAL_ITEM)
        assert listing.image_url == "https://i.ebayimg.com/images/g/123/s-l140.jpg"

    def test_parses_location(self):
        listing = _parse_listing(MINIMAL_ITEM)
        assert listing.country == "GB"
        assert listing.postal_code == "SW1A"

    def test_auction_listing_type(self):
        listing = _parse_listing(AUCTION_ITEM)
        assert listing.listing_type == "Auction"
        assert listing.buy_it_now is False
        assert listing.bid_count == 5

    def test_missing_price_returns_none(self):
        listing = _parse_listing(ITEM_MISSING_PRICE)
        assert listing.current_price is None

    def test_selling_state_always_active(self):
        listing = _parse_listing(MINIMAL_ITEM)
        assert listing.selling_state == "Active"

    def test_end_time_parsed(self):
        listing = _parse_listing(MINIMAL_ITEM)
        assert listing.end_time is not None
        assert listing.end_time.year == 2025
        assert listing.end_time.month == 12

    def test_missing_price_item_id_still_parsed(self):
        listing = _parse_listing(ITEM_MISSING_PRICE)
        assert listing.item_id == "888"

    def test_buy_it_now_false_for_auction(self):
        listing = _parse_listing(AUCTION_ITEM)
        assert listing.buy_it_now is False
