"""Smoke tests: the application starts up and responds."""

from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_seeded_event_types_are_listed() -> None:
    with TestClient(app) as client:
        response = client.get("/api/event-types")
    assert response.status_code == 200
    ids = {event_type["id"] for event_type in response.json()}
    assert "consultation" in ids
