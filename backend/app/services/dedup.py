"""
Item deduplication service.

Classifies a batch of fetched RawListing items against the set of item IDs
already recorded for a query.  Returns three buckets:
  - new:       never seen before
  - updated:   seen before but price has changed
  - unchanged: seen before, price identical
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from loguru import logger

from app.services.ebay_finding import RawListing


@dataclass
class DeduplicationResult:
    new: list[RawListing]
    updated: list[RawListing]
    unchanged: list[RawListing]

    @property
    def total(self) -> int:
        return len(self.new) + len(self.updated) + len(self.unchanged)


def classify(
    raw_items: list[RawListing],
    existing: dict[str, Decimal | None],  # item_id → last known price
) -> DeduplicationResult:
    """
    Classify each item in `raw_items` against `existing` (a dict of known item IDs
    mapped to their last recorded price).

    Args:
        raw_items:  Items returned from the eBay API for this poll.
        existing:   Mapping of {item_id: current_price} already in the database.

    Returns:
        DeduplicationResult with new / updated / unchanged buckets.
    """
    new_items: list[RawListing] = []
    updated_items: list[RawListing] = []
    unchanged_items: list[RawListing] = []

    logger.debug("[DEDUP] Classifying {n} raw items against {e} existing", n=len(raw_items), e=len(existing))

    for item in raw_items:
        if item.item_id not in existing:
            new_items.append(item)
        else:
            stored_price = existing[item.item_id]
            fetched_price = Decimal(str(item.current_price)) if item.current_price is not None else None
            if stored_price != fetched_price:
                updated_items.append(item)
            else:
                unchanged_items.append(item)

    result = DeduplicationResult(new=new_items, updated=updated_items, unchanged=unchanged_items)
    logger.info(
        "[DEDUP] Batch {total}: {new} new / {upd} updated / {unc} unchanged",
        total=result.total,
        new=len(new_items),
        upd=len(updated_items),
        unc=len(unchanged_items),
    )
    return result
