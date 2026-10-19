"""Database access helpers shared by the routers."""

import sqlite3
from datetime import datetime

from .slots import Window, generate_slots


def load_windows(conn: sqlite3.Connection) -> list[Window]:
    rows = conn.execute(
        "SELECT weekday, start_time, end_time FROM schedule ORDER BY weekday, start_time"
    ).fetchall()
    return [(row["weekday"], row["start_time"], row["end_time"]) for row in rows]


def booked_slot_starts(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT slot_start FROM bookings WHERE status = 'booked'").fetchall()
    return {row["slot_start"] for row in rows}


def is_within_schedule(
    local_start: datetime,
    windows: list[Window],
    slot_minutes: int,
) -> bool:
    """Return True if ``local_start`` matches a generated slot on its weekday."""
    slots = generate_slots(local_start.date(), windows, slot_minutes, local_start.tzinfo)
    return any(start == local_start for start, _ in slots)
