"""Booking endpoints: create, list and cancel."""

import sqlite3
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import config, db
from ..generated.models import Booking, BookingCreate
from ..repository import (
    active_intervals,
    get_event_type,
    is_within_schedule,
    load_windows,
    overlaps,
)

router = APIRouter(prefix="/api", tags=["bookings"])


def _row_to_booking(row: sqlite3.Row) -> Booking:
    return Booking(**dict(row))


@router.post("/bookings", response_model=Booking, status_code=201)
def create_booking(
    payload: BookingCreate,
    conn: sqlite3.Connection = Depends(db.get_db),
) -> Booking:
    """Book a slot for a guest; conflicts are rejected server-side."""
    event_type = get_event_type(conn, payload.event_type_id)
    if event_type is None:
        raise HTTPException(status_code=404, detail="Event type not found")

    start_utc = payload.slot_start.astimezone(timezone.utc)
    if start_utc <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="slot_start is in the past")

    tz = ZoneInfo(config.BOOKING_TZ)
    local_start = start_utc.astimezone(tz)
    if not is_within_schedule(local_start, load_windows(conn), event_type.duration_minutes):
        raise HTTPException(status_code=400, detail="slot_start is outside availability")

    end_utc = start_utc + timedelta(minutes=event_type.duration_minutes)
    created_at = datetime.now(timezone.utc)

    conn.execute("BEGIN IMMEDIATE")
    try:
        if overlaps(active_intervals(conn), start_utc, end_utc):
            raise HTTPException(status_code=409, detail="This slot is already booked")
        cursor = conn.execute(
            """
            INSERT INTO bookings
                (event_type_id, slot_start, slot_end, name, email, comment, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'booked', ?)
            """,
            (
                event_type.id,
                start_utc.isoformat(),
                end_utc.isoformat(),
                payload.name,
                payload.email,
                payload.comment or "",
                created_at.isoformat(),
            ),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise

    row = conn.execute("SELECT * FROM bookings WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _row_to_booking(row)


@router.get("/bookings", response_model=list[Booking])
def list_bookings(
    upcoming: bool = Query(True),
    conn: sqlite3.Connection = Depends(db.get_db),
) -> list[Booking]:
    """List meetings of all types; by default only the upcoming ones."""
    query = "SELECT * FROM bookings WHERE status = 'booked'"
    params: tuple[str, ...] = ()
    if upcoming:
        query += " AND slot_start > ?"
        params = (datetime.now(timezone.utc).isoformat(),)
    query += " ORDER BY slot_start"
    rows = conn.execute(query, params).fetchall()
    return [_row_to_booking(row) for row in rows]


@router.delete("/bookings/{id}", response_model=Booking)
def cancel_booking(
    id: int,
    conn: sqlite3.Connection = Depends(db.get_db),
) -> Booking:
    """Cancel a meeting, freeing its slot."""
    row = conn.execute("SELECT * FROM bookings WHERE id = ?", (id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    conn.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (id,))
    conn.commit()
    row = conn.execute("SELECT * FROM bookings WHERE id = ?", (id,)).fetchone()
    return _row_to_booking(row)
