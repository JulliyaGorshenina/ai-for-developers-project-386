"""Availability endpoints, scoped to a meeting type."""

import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import config, db
from ..generated.models import DaySlots, Slot
from ..repository import free_slots_for_day, get_event_type

router = APIRouter(prefix="/api", tags=["availability"])


def _load_type_or_404(conn: sqlite3.Connection, event_type_id: str):
    event_type = get_event_type(conn, event_type_id)
    if event_type is None:
        raise HTTPException(status_code=404, detail="Event type not found")
    return event_type


@router.get("/event-types/{id}/availability", response_model=list[DaySlots])
def availability(
    id: str,
    days: int = Query(config.DEFAULT_AVAILABILITY_DAYS, ge=1, le=60),
    conn: sqlite3.Connection = Depends(db.get_db),
) -> list[DaySlots]:
    """Return the next ``days`` days with at least one free slot of this type."""
    event_type = _load_type_or_404(conn, id)
    tz = ZoneInfo(config.BOOKING_TZ)
    now = datetime.now(tz)
    today = now.date()

    result: list[DaySlots] = []
    for offset in range(days):
        day = today + timedelta(days=offset)
        slots = free_slots_for_day(conn, event_type.duration_minutes, day, now, tz)
        if slots:
            result.append(DaySlots(date=day, weekday=day.weekday(), slots=slots))
    return result


@router.get("/event-types/{id}/slots", response_model=list[Slot])
def slots_for_date(
    id: str,
    date: str = Query(..., description="ISO date, e.g. 2026-10-20"),
    conn: sqlite3.Connection = Depends(db.get_db),
) -> list[Slot]:
    """Return the free slots of a meeting type on a single day."""
    event_type = _load_type_or_404(conn, id)
    try:
        day = datetime.fromisoformat(date).date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="date must be ISO-8601 (YYYY-MM-DD)") from exc
    tz = ZoneInfo(config.BOOKING_TZ)
    now = datetime.now(tz)
    return free_slots_for_day(conn, event_type.duration_minutes, day, now, tz)
