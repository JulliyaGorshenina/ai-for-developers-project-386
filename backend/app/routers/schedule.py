"""Owner schedule endpoints."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from .. import db
from ..generated.models import Window, WindowList

router = APIRouter(prefix="/api", tags=["schedule"])


def _read_schedule(conn: sqlite3.Connection) -> list[Window]:
    rows = conn.execute(
        "SELECT weekday, start_time, end_time FROM schedule ORDER BY weekday, start_time"
    ).fetchall()
    return [Window(**dict(row)) for row in rows]


def _to_minutes(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


@router.get("/schedule", response_model=list[Window])
def get_schedule(conn: sqlite3.Connection = Depends(db.get_db)) -> list[Window]:
    """Read the owner's weekly availability."""
    return _read_schedule(conn)


@router.put("/schedule", response_model=list[Window])
def update_schedule(
    payload: WindowList,
    conn: sqlite3.Connection = Depends(db.get_db),
) -> list[Window]:
    """Replace the weekly availability; overlapping or inverted windows are rejected."""
    for window in payload.windows:
        if _to_minutes(window.end_time) <= _to_minutes(window.start_time):
            raise HTTPException(
                status_code=400,
                detail=f"window end must be after start (weekday {window.weekday})",
            )
    for weekday in range(7):
        day_windows = sorted(
            (w for w in payload.windows if w.weekday == weekday),
            key=lambda w: _to_minutes(w.start_time),
        )
        for earlier, later in zip(day_windows, day_windows[1:], strict=False):
            if _to_minutes(later.start_time) < _to_minutes(earlier.end_time):
                raise HTTPException(
                    status_code=400,
                    detail=f"windows overlap (weekday {weekday})",
                )
    conn.execute("DELETE FROM schedule")
    conn.executemany(
        "INSERT INTO schedule (weekday, start_time, end_time) VALUES (?, ?, ?)",
        [(w.weekday, w.start_time, w.end_time) for w in payload.windows],
    )
    conn.commit()
    return _read_schedule(conn)
