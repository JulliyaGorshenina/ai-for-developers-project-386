"""Unit tests for the pure slot-generation logic."""

from datetime import date, time
from zoneinfo import ZoneInfo

from app.slots import generate_slots, parse_hhmm

TZ = ZoneInfo("Europe/Moscow")
MONDAY = date(2026, 10, 19)
TUESDAY = date(2026, 10, 20)


def test_parse_hhmm() -> None:
    assert parse_hhmm("09:30") == time(9, 30)


def test_generates_half_hour_slots() -> None:
    windows = [(0, "10:00", "12:00")]
    slots = generate_slots(MONDAY, windows, 30, TZ)
    assert len(slots) == 4
    assert slots[0][0].hour == 10 and slots[0][0].minute == 0
    assert slots[-1][0].hour == 11 and slots[-1][0].minute == 30


def test_step_equals_duration() -> None:
    """A 45-minute type in a 10:00-18:00 window starts every 45 minutes."""
    windows = [(0, "10:00", "18:00")]
    slots = generate_slots(MONDAY, windows, 45, TZ)
    starts = [(start.hour, start.minute) for start, _ in slots]
    assert starts[:3] == [(10, 0), (10, 45), (11, 30)]
    assert starts[-1] == (16, 45)
    assert len(slots) == 10


def test_ignores_other_weekdays() -> None:
    windows = [(0, "10:00", "12:00")]
    assert generate_slots(TUESDAY, windows, 30, TZ) == []


def test_partial_window_is_dropped() -> None:
    windows = [(0, "10:00", "10:45")]
    assert len(generate_slots(MONDAY, windows, 30, TZ)) == 1


def test_slots_are_sorted_across_windows() -> None:
    windows = [(0, "14:00", "15:00"), (0, "10:00", "11:00")]
    slots = generate_slots(MONDAY, windows, 30, TZ)
    starts = [start for start, _ in slots]
    assert starts == sorted(starts)
    assert len(slots) == 4
