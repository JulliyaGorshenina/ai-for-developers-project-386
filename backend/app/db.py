"""SQLite connection helpers and schema management."""

import sqlite3
from collections.abc import Iterator
from datetime import timezone

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_start TEXT NOT NULL,
    slot_end TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    comment TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'booked',
    created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_bookings_active_slot
    ON bookings (slot_start) WHERE status = 'booked';
"""


def get_connection() -> sqlite3.Connection:
    """Open a new connection to the SQLite database."""
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
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
    """Create tables if missing and seed a default weekly schedule."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        _seed_schedule(conn)
        conn.commit()
    finally:
        conn.close()


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
    from datetime import datetime

    return datetime.now(timezone.utc).isoformat()
