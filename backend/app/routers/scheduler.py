from __future__ import annotations

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel

from app.routers.auth import verify_token
from app.scheduler import get_scheduler_status, pause_all, resume_all, run_all_now

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


class SchedulerStatus(BaseModel):
    running: bool
    paused: bool
    active_schedules: int
    running_jobs: int
    running_query_ids: list[int]


@router.get("/status", response_model=SchedulerStatus, dependencies=[Depends(verify_token)])
async def get_status():
    logger.debug("[ROUTER] GET /scheduler/status")
    running, paused, active_schedules, running_jobs, running_query_ids = await get_scheduler_status()
    return SchedulerStatus(
        running=running,
        paused=paused,
        active_schedules=active_schedules,
        running_jobs=running_jobs,
        running_query_ids=running_query_ids,
    )


@router.post("/pause", dependencies=[Depends(verify_token)])
async def pause():
    logger.info("[ROUTER] POST /scheduler/pause")
    await pause_all()
    return {"message": "Scheduler paused"}


@router.post("/resume", dependencies=[Depends(verify_token)])
async def resume():
    logger.info("[ROUTER] POST /scheduler/resume")
    await resume_all()
    return {"message": "Scheduler resumed"}


@router.post("/run-all", dependencies=[Depends(verify_token)])
async def trigger_all():
    logger.info("[ROUTER] POST /scheduler/run-all — triggering all enabled queries")
    await run_all_now()
    return {"message": "All enabled queries triggered"}
