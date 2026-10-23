"""Contract-API tests for the booking flow and its server-side rules."""

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Moscow")


def first_slot(client, event_type_id: str) -> str:
    days = client.get(f"/api/event-types/{event_type_id}/availability").json()
    assert days, f"expected a free day for {event_type_id}"
    return days[0]["slots"][0]["start"]


def book(client, event_type_id: str, slot_start: str, email: str = "guest@example.com"):
    return client.post(
        "/api/bookings",
        json={
            "event_type_id": event_type_id,
            "slot_start": slot_start,
            "name": "Гость",
            "email": email,
        },
    )


def test_book_free_slot_and_see_it_listed(client) -> None:
    slot = first_slot(client, "consultation")
    created = book(client, "consultation", slot)
    assert created.status_code == 201
    assert created.json()["status"] == "booked"

    meetings = client.get("/api/bookings").json()
    assert [m["id"] for m in meetings] == [created.json()["id"]]


def test_booked_slot_is_no_longer_offered(client) -> None:
    slot = first_slot(client, "consultation")
    assert book(client, "consultation", slot).status_code == 201

    days = client.get("/api/event-types/consultation/availability").json()
    offered = {s["start"] for day in days for s in day["slots"]}
    assert slot not in offered


def test_repeat_booking_is_conflict(client) -> None:
    slot = first_slot(client, "consultation")
    assert book(client, "consultation", slot).status_code == 201
    assert book(client, "consultation", slot).status_code == 409


def test_overlap_with_another_type_is_conflict(client) -> None:
    slot = first_slot(client, "deep-dive")
    assert book(client, "deep-dive", slot).status_code == 201
    # A 30-minute slot starting inside the 60-minute booking overlaps it.
    assert book(client, "consultation", slot).status_code == 409


def test_outside_schedule_is_rejected(client) -> None:
    now = datetime.now(TZ)
    days_ahead = (0 - now.weekday()) % 7  # next Monday
    monday = (now + timedelta(days=days_ahead)).date()
    start = datetime.combine(monday, time(9, 0), tzinfo=TZ)
    if start <= now:
        start += timedelta(days=7)
    response = book(client, "consultation", start.isoformat())
    assert response.status_code == 400


def test_unknown_event_type_is_not_found(client) -> None:
    response = book(client, "nope", first_slot(client, "consultation"))
    assert response.status_code == 404


def test_invalid_email_is_unprocessable(client) -> None:
    response = book(client, "consultation", first_slot(client, "consultation"), email="oops")
    assert response.status_code == 422


def test_cancel_frees_the_slot(client) -> None:
    slot = first_slot(client, "consultation")
    booking_id = book(client, "consultation", slot).json()["id"]

    cancelled = client.delete(f"/api/bookings/{booking_id}")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

    days = client.get("/api/event-types/consultation/availability").json()
    offered = {s["start"] for day in days for s in day["slots"]}
    assert slot in offered


def test_cancel_missing_booking_is_not_found(client) -> None:
    assert client.delete("/api/bookings/999").status_code == 404
