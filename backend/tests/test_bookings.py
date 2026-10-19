"""API tests for the booking flow and admin access."""

from fastapi.testclient import TestClient

from app.main import app


def test_book_first_available_slot_and_reject_double_booking() -> None:
    with TestClient(app) as client:
        days = client.get("/api/availability").json()
        assert days, "expected at least one day with free slots"
        slot = days[0]["slots"][0]
        payload = {
            "slot_start": slot["start"],
            "name": "Guest",
            "email": "guest@example.com",
            "comment": "hello",
        }
        created = client.post("/api/bookings", json=payload)
        assert created.status_code == 201
        assert created.json()["status"] == "booked"

        conflict = client.post("/api/bookings", json=payload)
        assert conflict.status_code == 409


def test_booking_rejects_invalid_email() -> None:
    with TestClient(app) as client:
        days = client.get("/api/availability").json()
        slot = days[0]["slots"][0]
        response = client.post(
            "/api/bookings",
            json={"slot_start": slot["start"], "name": "X", "email": "not-an-email"},
        )
    assert response.status_code == 422


def test_admin_endpoints_require_token() -> None:
    with TestClient(app) as client:
        assert client.get("/api/admin/bookings").status_code == 401
        authorized = client.get("/api/admin/bookings", headers={"X-Admin-Token": "test-token"})
        assert authorized.status_code == 200
