"""Integration tests for the /queries endpoints."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


pytestmark = pytest.mark.asyncio


class TestCreateQuery:
    async def test_create_minimal(self, client, sample_query_payload_minimal):
        resp = await client.post("/api/v1/queries", json=sample_query_payload_minimal)
        assert resp.status_code == 201
        data = resp.json()
        assert data["keyword"] == "ps5"
        assert data["name"] == "ps5"
        assert data["id"] > 0

    async def test_create_full_payload(self, client, sample_query_payload):
        resp = await client.post("/api/v1/queries", json=sample_query_payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Nintendo Switch"
        assert data["interval_minutes"] == 60

    async def test_create_with_category_id(self, client):
        resp = await client.post(
            "/api/v1/queries",
            json={"keyword": "nintendo switch", "category_id": "139971"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["category_id"] == "139971"
        assert data["name"] == "nintendo switch"

    async def test_create_missing_keyword_returns_422(self, client):
        resp = await client.post("/api/v1/queries", json={"name": "No keyword"})
        assert resp.status_code == 422

    async def test_create_empty_keyword_returns_422(self, client):
        resp = await client.post("/api/v1/queries", json={"name": "X", "keyword": ""})
        assert resp.status_code == 422

    async def test_create_interval_too_small_returns_422(self, client):
        resp = await client.post(
            "/api/v1/queries", json={"name": "X", "keyword": "x", "interval_minutes": 4}
        )
        assert resp.status_code == 422

    async def test_create_interval_too_large_returns_422(self, client):
        resp = await client.post(
            "/api/v1/queries",
            json={"name": "X", "keyword": "x", "interval_minutes": 10081},
        )
        assert resp.status_code == 422


class TestGetQuery:
    async def test_get_nonexistent_returns_404(self, client):
        resp = await client.get("/api/v1/queries/9999")
        assert resp.status_code == 404

    async def test_get_created_query(self, client, sample_query_payload_minimal):
        create = await client.post("/api/v1/queries", json=sample_query_payload_minimal)
        qid = create.json()["id"]
        resp = await client.get(f"/api/v1/queries/{qid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == qid


class TestListQueries:
    async def test_empty_list(self, client):
        resp = await client.get("/api/v1/queries")
        assert resp.status_code == 200
        body = resp.json()
        assert body["items"] == []
        assert body["total"] == 0

    async def test_list_returns_created(self, client, sample_query_payload_minimal):
        await client.post("/api/v1/queries", json=sample_query_payload_minimal)
        resp = await client.get("/api/v1/queries")
        assert resp.json()["total"] == 1


class TestPatchQuery:
    async def test_patch_name(self, client, sample_query_payload_minimal):
        create = await client.post("/api/v1/queries", json=sample_query_payload_minimal)
        qid = create.json()["id"]
        resp = await client.patch(f"/api/v1/queries/{qid}", json={"name": "Updated"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"

    async def test_patch_nonexistent_returns_404(self, client):
        resp = await client.patch("/api/v1/queries/9999", json={"name": "X"})
        assert resp.status_code == 404

    async def test_patch_keyword_without_name_keeps_name_synced(self, client, sample_query_payload_minimal):
        create = await client.post("/api/v1/queries", json=sample_query_payload_minimal)
        qid = create.json()["id"]
        resp = await client.patch(f"/api/v1/queries/{qid}", json={"keyword": "steam deck"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["keyword"] == "steam deck"
        assert data["name"] == "steam deck"

    async def test_patch_category_id_to_null(self, client):
        create = await client.post(
            "/api/v1/queries",
            json={"keyword": "steam deck", "category_id": "139971"},
        )
        qid = create.json()["id"]
        resp = await client.patch(f"/api/v1/queries/{qid}", json={"category_id": None})
        assert resp.status_code == 200
        assert resp.json()["category_id"] is None


class TestDeleteQuery:
    async def test_delete_removes_query(self, client, sample_query_payload_minimal):
        create = await client.post("/api/v1/queries", json=sample_query_payload_minimal)
        qid = create.json()["id"]
        del_resp = await client.delete(f"/api/v1/queries/{qid}")
        assert del_resp.status_code == 204
        get_resp = await client.get(f"/api/v1/queries/{qid}")
        assert get_resp.status_code == 404

    async def test_delete_nonexistent_returns_404(self, client):
        resp = await client.delete("/api/v1/queries/9999")
        assert resp.status_code == 404


class TestStopQuery:
    async def test_stop_active_query_requests_cancellation(self, client):
        mock_cancel = AsyncMock(return_value=True)
        with (
            patch("app.routers.queries.is_running", new=AsyncMock(return_value=True)),
            patch("app.routers.queries.cancel_poll", new=mock_cancel),
        ):
            resp = await client.post("/api/v1/queries/123/stop")

        assert resp.status_code == 200
        assert resp.json() == {"message": "Stop requested for query #123", "query_id": 123}
        mock_cancel.assert_awaited_once_with(123)

    async def test_stop_idle_query_returns_404(self, client):
        with patch("app.routers.queries.is_running", new=AsyncMock(return_value=False)):
            resp = await client.post("/api/v1/queries/123/stop")

        assert resp.status_code == 404
        assert resp.json()["detail"] == "No active poll found for this query"
