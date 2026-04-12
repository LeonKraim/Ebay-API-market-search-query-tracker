"""Integration tests for the /config endpoint."""
from __future__ import annotations

import importlib

import pytest

from app.services.ebay_taxonomy import CategorySuggestion

pytestmark = pytest.mark.asyncio


class TestConfigEndpoint:
    async def test_config_returns_200(self, client):
        resp = await client.get("/api/v1/config")
        assert resp.status_code == 200

    async def test_config_has_app_title(self, client):
        resp = await client.get("/api/v1/config")
        data = resp.json()
        assert "app" in data
        assert "title" in data["app"]

    async def test_config_excludes_secrets(self, client):
        data = (await client.get("/api/v1/config")).json()
        all_text = str(data)
        for secret_val_marker in ("fake-app-id", "fake-cert-id"):
            assert secret_val_marker not in all_text, f"Secret value must not appear in /config response"


class TestCategorySuggestionsEndpoint:
    async def test_blank_query_returns_empty_list(self, client):
        resp = await client.get(
            "/api/v1/config/ebay-category-suggestions",
            params={"site_id": "EBAY-DE", "q": "   "},
        )
        assert resp.status_code == 200
        assert resp.json() == {"items": []}

    async def test_category_suggestions_return_service_results(self, client, monkeypatch):
        config_router_module = importlib.import_module("app.routers.config_router")

        async def fake_get_category_suggestions(site_id: str, query: str) -> list[CategorySuggestion]:
            assert site_id == "EBAY-DE"
            assert query == "nintendo switch"
            return [
                CategorySuggestion(
                    category_id="139971",
                    category_name="Consoles",
                    category_path="Video Games & Consoles > Consoles",
                )
            ]

        monkeypatch.setattr(config_router_module, "get_category_suggestions", fake_get_category_suggestions)

        resp = await client.get(
            "/api/v1/config/ebay-category-suggestions",
            params={"site_id": "EBAY-DE", "q": "nintendo switch"},
        )
        assert resp.status_code == 200
        assert resp.json() == {
            "items": [
                {
                    "category_id": "139971",
                    "category_name": "Consoles",
                    "category_path": "Video Games & Consoles > Consoles",
                }
            ]
        }

    async def test_invalid_site_returns_400(self, client):
        resp = await client.get(
            "/api/v1/config/ebay-category-suggestions",
            params={"site_id": "BAD-SITE", "q": "nintendo switch"},
        )
        assert resp.status_code == 400
