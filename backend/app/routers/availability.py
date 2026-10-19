"""Public availability endpoints."""

import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import config, db
from ..repository import booked_slot_starts, load_windows
from ..schemas import DaySlots, Slot
from ..slots import generate_slots, to_utc_iso

router = APIRouter(prefix="/api", tags=["availability"])


def _free_slots_for_day(
    day,
    now: datetime,
    tz: ZoneInfo,
    windows,
    booked: set[str],
) -> list[Slot]:
    slots: list[Slot] = []
    for start, end in generate_slots(day, windows, config.SLOT_MINUTES, tz):
        start_iso = to_utc_iso(start)
        if start <= now or start_iso in booked:
            continue
        slots.append(Slot(start=start_iso, end=to_utc_iso(end)))
    return slots


@router.get("/availability", response_model=list[DaySlots])
def availability(
    days: int = Query(config.DEFAULT_AVAILABILITY_DAYS, ge=1, le=60),
    conn: sqlite3.Connection = Depends(db.get_db),
) -> list[DaySlots]:
    """Return the next ``days`` days that have at least one free slot."""
    tz = ZoneInfo(config.BOOKING_TZ)
    now = datetime.now(tz)
    windows = load_windows(conn)
    booked = booked_slot_starts(conn)

    result: list[DaySlots] = []
    today = now.date()
    for offset in range(days):
        day = today + timedelta(days=offset)
        slots = _free_slots_for_day(day, now, tz, windows, booked)
        if slots:
            result.append(DaySlots(date=day.isoformat(), weekday=day.weekday(), slots=slots))
    return result


@router.get("/slots", response_model=list[Slot])
def slots_for_date(
    date: str = Query(..., description="ISO date, e.g. 2026-10-20"),
    conn: sqlite3.Connection = Depends(db.get_db),
) -> list[Slot]:
    """Return the free slots for a single day."""
    tz = ZoneInfo(config.BOOKING_TZ)
    try:
        day = datetime.fromisoformat(date).date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="date must be ISO-8601 (YYYY-MM-DD)") from exc
    now = datetime.now(tz)
    windows = load_windows(conn)
    booked = booked_slot_starts(conn)
    return _free_slots_for_day(day, now, tz, windows, booked)
