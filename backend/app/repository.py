"""Database access helpers shared by the routers."""

import sqlite3
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from .generated.models import EventType, Slot
from .slots import Window, generate_slots


def load_windows(conn: sqlite3.Connection) -> list[Window]:
    rows = conn.execute(
        "SELECT weekday, start_time, end_time FROM schedule ORDER BY weekday, start_time"
    ).fetchall()
    return [(row["weekday"], row["start_time"], row["end_time"]) for row in rows]


def load_event_types(conn: sqlite3.Connection) -> list[EventType]:
    rows = conn.execute(
        "SELECT id, name, description, duration_minutes FROM event_types"
    ).fetchall()
    return [EventType(**dict(row)) for row in rows]


def get_event_type(conn: sqlite3.Connection, event_type_id: str) -> EventType | None:
    row = conn.execute(
        "SELECT id, name, description, duration_minutes FROM event_types WHERE id = ?",
        (event_type_id,),
    ).fetchone()
    return EventType(**dict(row)) if row else None


def active_intervals(conn: sqlite3.Connection) -> list[tuple[datetime, datetime]]:
    """Return the ``[start, end)`` intervals of all active bookings."""
    rows = conn.execute(
        "SELECT slot_start, slot_end FROM bookings WHERE status = 'booked'"
    ).fetchall()
    return [
        (datetime.fromisoformat(row["slot_start"]), datetime.fromisoformat(row["slot_end"]))
        for row in rows
    ]


def overlaps(
    intervals: list[tuple[datetime, datetime]],
    start: datetime,
    end: datetime,
) -> bool:
    """True if ``[start, end)`` intersects any interval. Back-to-back is allowed."""
    return any(
        existing_start < end and start < existing_end for existing_start, existing_end in intervals
    )


def is_within_schedule(
    local_start: datetime,
    windows: list[Window],
    duration_minutes: int,
) -> bool:
    """Return True if ``local_start`` matches a generated slot start on its weekday."""
    slots = generate_slots(local_start.date(), windows, duration_minutes, local_start.tzinfo)
    return any(start == local_start for start, _ in slots)


def free_slots_for_day(
    conn: sqlite3.Connection,
    duration_minutes: int,
    day: date,
    now: datetime,
    tz: ZoneInfo,
) -> list[Slot]:
    """Free slots of ``day`` for a type: inside the schedule and conflict-free."""
    windows = load_windows(conn)
    booked = active_intervals(conn)
    slots: list[Slot] = []
    for start, end in generate_slots(day, windows, duration_minutes, tz):
        if start <= now or overlaps(booked, start, end):
            continue
        slots.append(Slot(start=start.astimezone(timezone.utc), end=end.astimezone(timezone.utc)))
    return slots
