"""Scheduler lifecycle helpers for per-query polling jobs."""
from __future__ import annotations

import asyncio
import os
import random

from apscheduler import AsyncScheduler, ConflictPolicy
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from app.config import get_settings
from app.services.poll_runner import run_poll

_scheduler: AsyncScheduler | None = None
_scheduler_started: bool = False
_scheduler_lock = asyncio.Lock()
_paused: bool = False
_semaphore: asyncio.Semaphore | None = None
_testing_schedule_ids: set[str] = set()
_TESTING = os.environ.get("TESTING", "").lower() == "true"


def _schedule_id(query_id: int) -> str:
    return f"poll_query_{query_id}"


def get_scheduler() -> AsyncScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncScheduler()
        logger.info("[SCHEDULER] AsyncScheduler instance created")
    return _scheduler


def get_semaphore() -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        settings = get_settings()
        _semaphore = asyncio.Semaphore(settings.scheduler_max_concurrent_polls)
        logger.info(
            "[SCHEDULER] Semaphore created — max_concurrent_polls={n}",
            n=settings.scheduler_max_concurrent_polls,
        )
    return _semaphore


async def _guarded_poll(query_id: int) -> None:
    sem = get_semaphore()
    async with sem:
        await run_poll(query_id)


async def _start_scheduler_unlocked() -> AsyncScheduler:
    global _scheduler_started

    sched = get_scheduler()
    if _scheduler_started:
        return sched

    await sched.__aenter__()
    try:
        await sched.start_in_background()
    except Exception:
        sched.stop()
        raise

    _scheduler_started = True
    logger.info("[SCHEDULER] Background scheduler started")
    return sched


async def _stop_scheduler_unlocked(reset_paused: bool = False) -> None:
    global _scheduler, _scheduler_started, _paused

    sched = _scheduler
    was_started = _scheduler_started
    _scheduler = None
    _scheduler_started = False

    if was_started and sched is not None:
        logger.info("[SCHEDULER] Stopping background scheduler")
        sched.stop()

    if reset_paused:
        _paused = False


async def _get_schedules_unlocked() -> list:
    global _scheduler, _scheduler_started

    if not _scheduler_started or _scheduler is None:
        return []
    try:
        return await _scheduler.get_schedules()
    except RuntimeError as exc:
        if "not been initialized yet" in str(exc):
            _scheduler = None
            _scheduler_started = False
            logger.warning("[SCHEDULER] get_schedules() called before scheduler initialization completed; treating as idle")
            return []
        raise


async def _stop_if_idle_unlocked() -> None:
    schedules = await _get_schedules_unlocked()
    if not schedules:
        await _stop_scheduler_unlocked(reset_paused=True)


async def _add_job_unlocked(sched: AsyncScheduler, query_id: int, interval_minutes: int) -> None:
    settings = get_settings()
    jitter_seconds = random.randint(0, settings.scheduler_jitter_seconds)
    schedule_id = _schedule_id(query_id)

    await sched.add_schedule(
        _guarded_poll,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id=schedule_id,
        args=[query_id],
        paused=_paused,
        max_jitter=jitter_seconds,
        conflict_policy=ConflictPolicy.replace,
    )
    logger.info(
        "[SCHEDULER] Schedule {schedule_id} active — every {interval}min (max_jitter={j}s paused={paused})",
        schedule_id=schedule_id,
        interval=interval_minutes,
        j=jitter_seconds,
        paused=_paused,
    )


async def sync_scheduler_from_db() -> None:
    from sqlalchemy import select

    from app.database import get_session
    from app.models.query import SearchQuery

    async with get_session() as session:
        result = await session.execute(select(SearchQuery).where(SearchQuery.enabled == True))
        queries = result.scalars().all()

    if _TESTING:
        _testing_schedule_ids.clear()
        _testing_schedule_ids.update(_schedule_id(query.id) for query in queries)
        if not _testing_schedule_ids:
            global _paused
            _paused = False
        return

    async with _scheduler_lock:
        if not queries:
            await _stop_scheduler_unlocked(reset_paused=True)
            logger.info("[SCHEDULER] No enabled queries found at sync time")
            return

        sched = await _start_scheduler_unlocked()
        existing_ids = {schedule.id for schedule in await _get_schedules_unlocked()}
        desired_ids = {_schedule_id(query.id) for query in queries}

        for query in queries:
            await _add_job_unlocked(sched, query.id, query.interval_minutes)

        for schedule_id in existing_ids - desired_ids:
            await sched.remove_schedule(schedule_id)
            logger.info("[SCHEDULER] Removed stale schedule {schedule_id}", schedule_id=schedule_id)


async def stop_scheduler() -> None:
    if _TESTING:
        global _paused
        _testing_schedule_ids.clear()
        _paused = False
        return

    async with _scheduler_lock:
        await _stop_scheduler_unlocked(reset_paused=True)


async def sync_query_schedule(query_id: int, enabled: bool, interval_minutes: int | None = None) -> None:
    if _TESTING:
        schedule_id = _schedule_id(query_id)
        if enabled:
            _testing_schedule_ids.add(schedule_id)
        else:
            _testing_schedule_ids.discard(schedule_id)
            if not _testing_schedule_ids:
                global _paused
                _paused = False
        return

    async with _scheduler_lock:
        if enabled:
            if interval_minutes is None:
                raise ValueError("interval_minutes is required when enabling a schedule")
            sched = await _start_scheduler_unlocked()
            await _add_job_unlocked(sched, query_id, interval_minutes)
            return

        if _scheduler_started and _scheduler is not None:
            schedule_id = _schedule_id(query_id)
            existing_ids = {schedule.id for schedule in await _get_schedules_unlocked()}
            if schedule_id in existing_ids:
                await _scheduler.remove_schedule(schedule_id)
                logger.info("[SCHEDULER] Removed schedule {schedule_id}", schedule_id=schedule_id)
        await _stop_if_idle_unlocked()


async def pause_all() -> None:
    global _paused

    if _TESTING:
        _paused = bool(_testing_schedule_ids)
        return

    async with _scheduler_lock:
        schedules = await _get_schedules_unlocked()
        if not schedules:
            _paused = False
            logger.info("[SCHEDULER] Pause requested with no active schedules")
            return

        for schedule in schedules:
            await _scheduler.pause_schedule(schedule.id)
        _paused = True
        logger.info("[SCHEDULER] All schedules paused")


async def resume_all() -> None:
    global _paused

    if _TESTING:
        _paused = False
        return

    async with _scheduler_lock:
        schedules = await _get_schedules_unlocked()
        if not schedules:
            _paused = False
            logger.info("[SCHEDULER] Resume requested with no active schedules")
            return

        for schedule in schedules:
            await _scheduler.unpause_schedule(schedule.id, resume_from="now")
        _paused = False
        logger.info("[SCHEDULER] All schedules resumed")


async def get_scheduler_status() -> tuple[bool, bool, int, int, list[int]]:
    from app.services.poll_runner import _running_jobs, get_running_query_ids

    if _TESTING:
        active_schedules = len(_testing_schedule_ids)
        running_ids = await get_running_query_ids()
        if active_schedules == 0:
            return False, False, 0, 0, running_ids
        return (len(_running_jobs) > 0, _paused, active_schedules, len(_running_jobs), running_ids)

    async with _scheduler_lock:
        schedules = await _get_schedules_unlocked()
        active_schedules = len(schedules)
        running_ids = await get_running_query_ids()
        if active_schedules == 0:
            return False, False, 0, 0, running_ids
        return (len(_running_jobs) > 0, _paused, active_schedules, len(_running_jobs), running_ids)


async def run_all_now() -> None:
    """Immediately trigger all enabled queries outside of the scheduler."""
    from sqlalchemy import select

    from app.database import get_session
    from app.models.query import SearchQuery

    async with get_session() as session:
        result = await session.execute(select(SearchQuery).where(SearchQuery.enabled == True))
        queries = result.scalars().all()

    logger.info("[SCHEDULER] run_all_now — triggering {n} queries immediately", n=len(queries))
    tasks = [asyncio.create_task(_guarded_poll(query.id)) for query in queries]
    _ = tasks
