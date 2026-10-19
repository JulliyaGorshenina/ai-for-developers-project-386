"""Booking creation endpoint."""

import sqlite3
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException

from .. import config, db
from ..repository import is_within_schedule, load_windows
from ..schemas import Booking, BookingCreate

router = APIRouter(prefix="/api", tags=["bookings"])


@router.post("/bookings", response_model=Booking, status_code=201)
def create_booking(
    payload: BookingCreate,
    conn: sqlite3.Connection = Depends(db.get_db),
) -> Booking:
    """Book a slot for a guest."""
    try:
        parsed = datetime.fromisoformat(payload.slot_start)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="slot_start must be ISO-8601") from exc

    if parsed.tzinfo is None:
        raise HTTPException(status_code=400, detail="slot_start must include a timezone")

    start_utc = parsed.astimezone(timezone.utc)
    if start_utc.second or start_utc.microsecond or start_utc.minute % config.SLOT_MINUTES:
        raise HTTPException(status_code=400, detail="slot_start is not aligned to the slot grid")

    if start_utc <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="slot_start is in the past")

    tz = ZoneInfo(config.BOOKING_TZ)
    local_start = start_utc.astimezone(tz)
    if not is_within_schedule(local_start, load_windows(conn), config.SLOT_MINUTES):
        raise HTTPException(status_code=400, detail="slot_start is outside availability")

    slot_end = start_utc + timedelta(minutes=config.SLOT_MINUTES)
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        cursor = conn.execute(
            """
            INSERT INTO bookings (slot_start, slot_end, name, email, comment, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'booked', ?)
            """,
            (
                start_utc.isoformat(),
                slot_end.isoformat(),
                payload.name,
                payload.email,
                payload.comment,
                created_at,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="This slot is already booked") from exc

    row = conn.execute("SELECT * FROM bookings WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return Booking(**dict(row))
