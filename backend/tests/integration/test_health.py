"""Integration tests for the /health endpoint."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


class TestHealth:
    async def test_health_returns_ok(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_health_has_title(self, client):
        resp = await client.get("/health")
        assert "title" in resp.json()
