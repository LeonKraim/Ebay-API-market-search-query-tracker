from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.models.listing import ListingRecord
from app.models.query import SearchQuery
from app.models.snapshot import Snapshot
from app.models.sold import SoldRecord


pytestmark = pytest.mark.asyncio


def _parsed_utc(value: str) -> datetime:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)


async def test_items_evaluated_counts_unique_item_ids_across_live_and_sold(client, db_session):
    base_time = datetime.now(timezone.utc)
    query = SearchQuery(name='switch', keyword='switch', site_id='EBAY-DE', interval_minutes=60)
    db_session.add(query)
    await db_session.flush()

    snapshot = Snapshot(query_id=query.id, started_at=base_time, status='complete')
    second_snapshot = Snapshot(query_id=query.id, started_at=base_time + timedelta(minutes=5), status='complete')
    db_session.add_all([snapshot, second_snapshot])
    await db_session.flush()

    db_session.add_all([
        ListingRecord(
            snapshot_id=snapshot.id,
            query_id=query.id,
            item_id='A-1',
            title='Duplicate live 1',
            first_seen_at=base_time + timedelta(minutes=10),
            last_seen_at=base_time + timedelta(minutes=10),
        ),
        ListingRecord(
            snapshot_id=snapshot.id,
            query_id=query.id,
            item_id='B-2',
            title='Unique live',
            first_seen_at=base_time + timedelta(minutes=20),
            last_seen_at=base_time + timedelta(minutes=20),
        ),
        ListingRecord(
            snapshot_id=second_snapshot.id,
            query_id=query.id,
            item_id='A-1',
            title='Duplicate live 2',
            first_seen_at=base_time + timedelta(minutes=25),
            last_seen_at=base_time + timedelta(minutes=25),
        ),
    ])
    db_session.add_all([
        SoldRecord(
            query_id=query.id,
            item_id='A-1',
            title='Duplicate across sold',
            sold_date=base_time + timedelta(days=1),
            scraped_at=base_time - timedelta(days=1),
        ),
        SoldRecord(
            query_id=query.id,
            item_id='C-3',
            title='Unique sold',
            sold_date=base_time + timedelta(days=2),
            scraped_at=base_time + timedelta(minutes=30),
        ),
    ])
    await db_session.commit()

    response = await client.get('/api/v1/stats/items-evaluated')

    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 3
    assert _parsed_utc(body['since']) == base_time - timedelta(days=1)


async def test_items_evaluated_ignores_null_item_ids_and_uses_available_observation_timestamp(client, db_session):
    base_time = datetime.now(timezone.utc)
    query = SearchQuery(name='deck', keyword='steam deck', site_id='EBAY-DE', interval_minutes=60)
    db_session.add(query)
    await db_session.flush()

    db_session.add(
        SoldRecord(
            query_id=query.id,
            item_id=None,
            title='Null id should not count',
            sold_date=base_time,
            scraped_at=base_time,
        )
    )
    db_session.add(
        SoldRecord(
            query_id=query.id,
            item_id='Z-9',
            title='Only counted item',
            sold_date=base_time + timedelta(hours=1),
            scraped_at=base_time + timedelta(hours=1),
        )
    )
    await db_session.commit()

    response = await client.get('/api/v1/stats/items-evaluated')

    assert response.status_code == 200
    body = response.json()
    assert body['total'] == 1
    assert _parsed_utc(body['since']) == base_time + timedelta(hours=1)