"""Smoke test: the application starts up and responds."""

from fastapi.testclient import TestClient

from app.main import app


def test_app_starts_and_responds() -> None:
    with TestClient(app) as client:
        response = client.get("/api/availability")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
