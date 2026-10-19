"""Pure helpers for turning a weekly schedule into 30-minute slots."""

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

Window = tuple[int, str, str]  # (weekday, "HH:MM", "HH:MM")


def parse_hhmm(value: str) -> time:
    """Parse a ``HH:MM`` string into a :class:`datetime.time`."""
    hour, minute = value.split(":")
    return time(int(hour), int(minute))


def generate_slots(
    day: date,
    windows: list[Window],
    slot_minutes: int,
    tz: ZoneInfo,
) -> list[tuple[datetime, datetime]]:
    """Return the timezone-aware slots of ``day`` within ``windows``.

    Each window is ``(weekday, start, end)`` where ``weekday`` is 0 (Monday) to
    6 (Sunday). Slots are ``slot_minutes`` long and only fully inside a window.
    """
    step = timedelta(minutes=slot_minutes)
    result: list[tuple[datetime, datetime]] = []
    for weekday, start_str, end_str in windows:
        if weekday != day.weekday():
            continue
        start = datetime.combine(day, parse_hhmm(start_str), tzinfo=tz)
        end = datetime.combine(day, parse_hhmm(end_str), tzinfo=tz)
        current = start
        while current + step <= end:
            result.append((current, current + step))
            current += step
    result.sort(key=lambda pair: pair[0])
    return result


def to_utc_iso(value: datetime) -> str:
    """Render a datetime as an ISO-8601 string in UTC."""
    return value.astimezone(timezone.utc).isoformat()
