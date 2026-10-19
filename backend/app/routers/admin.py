"""Owner/admin endpoints: weekly schedule and meetings."""

import sqlite3
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import db
from ..auth import require_admin
from ..schemas import Booking, ScheduleUpdate, Window

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


def _read_schedule(conn: sqlite3.Connection) -> list[Window]:
    rows = conn.execute(
        "SELECT weekday, start_time, end_time FROM schedule ORDER BY weekday, start_time"
    ).fetchall()
    return [Window(**dict(row)) for row in rows]


@router.get("/schedule", response_model=list[Window])
def get_schedule(conn: sqlite3.Connection = Depends(db.get_db)) -> list[Window]:
    """Return the current weekly availability."""
    return _read_schedule(conn)


@router.put("/schedule", response_model=list[Window])
def update_schedule(
    payload: ScheduleUpdate,
    conn: sqlite3.Connection = Depends(db.get_db),
) -> list[Window]:
    """Replace the weekly availability."""
    for window in payload.windows:
        if window.end_time <= window.start_time:
            raise HTTPException(
                status_code=400,
                detail=f"window end must be after start (weekday {window.weekday})",
            )
    conn.execute("DELETE FROM schedule")
    conn.executemany(
        "INSERT INTO schedule (weekday, start_time, end_time) VALUES (?, ?, ?)",
        [(w.weekday, w.start_time, w.end_time) for w in payload.windows],
    )
    conn.commit()
    return _read_schedule(conn)


@router.get("/bookings", response_model=list[Booking])
def list_bookings(
    upcoming: bool = Query(True),
    conn: sqlite3.Connection = Depends(db.get_db),
) -> list[Booking]:
    """List meetings; by default only the upcoming ones."""
    query = "SELECT * FROM bookings WHERE status = 'booked'"
    params: tuple[str, ...] = ()
    if upcoming:
        query += " AND slot_start >= ?"
        params = (datetime.now(timezone.utc).isoformat(),)
    query += " ORDER BY slot_start"
    rows = conn.execute(query, params).fetchall()
    return [Booking(**dict(row)) for row in rows]


@router.delete("/bookings/{booking_id}", response_model=Booking)
def cancel_booking(
    booking_id: int,
    conn: sqlite3.Connection = Depends(db.get_db),
) -> Booking:
    """Cancel a booking, freeing its slot."""
    row = conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    conn.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
    conn.commit()
    row = conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    return Booking(**dict(row))
