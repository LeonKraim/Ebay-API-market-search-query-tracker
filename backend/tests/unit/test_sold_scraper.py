"""Unit tests for the eBay sold listing scraper."""
from __future__ import annotations

import pytest

from app.services.sold_scraper import _parse_date, _parse_price


class TestParsePrice:
    def test_gbp_symbol(self):
        price, currency = _parse_price("£12.99")
        assert price == pytest.approx(12.99)
        assert currency == "GBP"

    def test_usd_symbol(self):
        price, currency = _parse_price("$9.50")
        assert price == pytest.approx(9.50)
        assert currency == "USD"

    def test_eur_symbol(self):
        price, currency = _parse_price("€7.00")
        assert price == pytest.approx(7.00)
        assert currency == "EUR"

    def test_price_with_commas_thousands(self):
        price, currency = _parse_price("£1,299.00")
        assert price == pytest.approx(1299.00)
        assert currency == "GBP"

    def test_price_with_trailing_text(self):
        price, currency = _parse_price("£5.00 postage")
        assert price == pytest.approx(5.00)
        assert currency == "GBP"

    def test_price_no_decimal(self):
        price, currency = _parse_price("$10")
        assert price == pytest.approx(10.0)

    def test_empty_string_returns_none(self):
        price, currency = _parse_price("")
        assert price is None
        assert currency is None

    def test_non_price_string_returns_none(self):
        price, currency = _parse_price("Best offer")
        assert price is None

    def test_zero_price(self):
        price, currency = _parse_price("£0.00")
        assert price == pytest.approx(0.0)
        assert currency == "GBP"

    def test_negative_price_returns_none(self):
        price, currency = _parse_price("-£5.00")
        assert price is None
        assert currency is None


class TestParseDate:
    def test_sold_dd_mon_yyyy(self):
        from datetime import date
        d = _parse_date("Sold 15 Jan 2024")
        assert d == date(2024, 1, 15)

    def test_dd_mon_yyyy_no_prefix(self):
        from datetime import date
        d = _parse_date("20 Mar 2023")
        assert d == date(2023, 3, 20)

    def test_yyyy_mm_dd_iso(self):
        from datetime import date
        d = _parse_date("2024-06-01")
        assert d == date(2024, 6, 1)

    def test_empty_string_returns_none(self):
        result = _parse_date("")
        assert result is None

    def test_unrecognised_format_returns_none(self):
        result = _parse_date("not a date at all")
        assert result is None

    def test_whitespace_only_returns_none(self):
        result = _parse_date("   ")
        assert result is None
