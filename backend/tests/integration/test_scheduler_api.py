from __future__ import annotations

import pytest


pytestmark = pytest.mark.asyncio


class TestSchedulerStatus:
    async def test_status_is_idle_without_enabled_queries(self, client):
        resp = await client.get("/api/v1/scheduler/status")
        assert resp.status_code == 200
        assert resp.json() == {
            "running": False,
            "paused": False,
            "active_schedules": 0,
            "running_jobs": 0,
            "running_query_ids": [],
        }

    async def test_status_is_idle_but_scheduled_after_enabled_query_created(self, client):
        create = await client.post(
            "/api/v1/queries",
            json={"keyword": "nintendo switch", "enabled": True, "interval_minutes": 60},
        )
        assert create.status_code == 201

        resp = await client.get("/api/v1/scheduler/status")
        assert resp.status_code == 200
        assert resp.json() == {
            "running": False,
            "paused": False,
            "active_schedules": 1,
            "running_jobs": 0,
            "running_query_ids": [],
        }

    async def test_status_returns_idle_after_last_enabled_query_deleted(self, client):
        create = await client.post(
            "/api/v1/queries",
            json={"keyword": "steam deck", "enabled": True, "interval_minutes": 60},
        )
        qid = create.json()["id"]

        delete_resp = await client.delete(f"/api/v1/queries/{qid}")
        assert delete_resp.status_code == 204

        resp = await client.get("/api/v1/scheduler/status")
        assert resp.status_code == 200
        assert resp.json() == {
            "running": False,
            "paused": False,
            "active_schedules": 0,
            "running_jobs": 0,
            "running_query_ids": [],
        }

    async def test_pause_and_resume_reflect_status(self, client):
        create = await client.post(
            "/api/v1/queries",
            json={"keyword": "xbox", "enabled": True, "interval_minutes": 60},
        )
        assert create.status_code == 201

        pause_resp = await client.post("/api/v1/scheduler/pause")
        assert pause_resp.status_code == 200
        paused_status = await client.get("/api/v1/scheduler/status")
        assert paused_status.json() == {
            "running": False,
            "paused": True,
            "active_schedules": 1,
            "running_jobs": 0,
            "running_query_ids": [],
        }

        resume_resp = await client.post("/api/v1/scheduler/resume")
        assert resume_resp.status_code == 200
        running_status = await client.get("/api/v1/scheduler/status")
        assert running_status.json() == {
            "running": False,
            "paused": False,
            "active_schedules": 1,
            "running_jobs": 0,
            "running_query_ids": [],
        }