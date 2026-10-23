"""SQLite connection helpers and schema management."""

import sqlite3
from collections.abc import Iterator
from datetime import datetime, timezone

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS event_types (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0)
);

CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type_id TEXT NOT NULL,
    slot_start TEXT NOT NULL,
    slot_end TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    comment TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'booked',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bookings_active
    ON bookings (status, slot_start, slot_end);
"""

# (id, name, description, duration_minutes)
DEFAULT_EVENT_TYPES: list[tuple[str, str, str, int]] = [
    ("consultation", "Консультация", "Короткий вводный звонок по проекту.", 30),
    ("deep-dive", "Подробный разбор", "Глубокий разбор задачи или кода.", 60),
]


def get_connection() -> sqlite3.Connection:
    """Open a new connection to the SQLite database.

    ``check_same_thread=False`` because FastAPI may run the dependency and the
    endpoint on different threadpool threads; each request still owns its own
    connection, so it is never used concurrently.
    """
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_db() -> Iterator[sqlite3.Connection]:
    """FastAPI dependency yielding a database connection."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if missing and seed default event types and schedule."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        _seed_event_types(conn)
        _seed_schedule(conn)
        conn.commit()
    finally:
        conn.close()


def _seed_event_types(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) AS c FROM event_types").fetchone()["c"]
    if count:
        return
    conn.executemany(
        "INSERT INTO event_types (id, name, description, duration_minutes) VALUES (?, ?, ?, ?)",
        DEFAULT_EVENT_TYPES,
    )


def _seed_schedule(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) AS c FROM schedule").fetchone()["c"]
    if count:
        return
    for weekday in range(5):  # Monday..Friday
        conn.execute(
            "INSERT INTO schedule (weekday, start_time, end_time) VALUES (?, ?, ?)",
            (weekday, "10:00", "18:00"),
        )


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
