"""API tests for meeting-type management (contract-API layer)."""


def test_lists_seeded_types(client) -> None:
    response = client.get("/api/event-types")
    assert response.status_code == 200
    ids = {event_type["id"] for event_type in response.json()}
    assert {"consultation", "deep-dive"} <= ids


def test_create_event_type(client) -> None:
    payload = {
        "id": "intro-call",
        "name": "Знакомство",
        "description": "Короткий звонок.",
        "duration_minutes": 15,
    }
    created = client.post("/api/event-types", json=payload)
    assert created.status_code == 201
    assert created.json() == payload
    assert any(t["id"] == "intro-call" for t in client.get("/api/event-types").json())


def test_create_duplicate_is_conflict(client) -> None:
    payload = {
        "id": "consultation",
        "name": "Дубль",
        "description": "",
        "duration_minutes": 30,
    }
    assert client.post("/api/event-types", json=payload).status_code == 409


def test_rejects_invalid_slug(client) -> None:
    payload = {
        "id": "Bad Slug",
        "name": "Плохой",
        "description": "",
        "duration_minutes": 30,
    }
    assert client.post("/api/event-types", json=payload).status_code == 422


def test_update_event_type(client) -> None:
    payload = {
        "id": "consultation",
        "name": "Консультация 45",
        "description": "Обновлено.",
        "duration_minutes": 45,
    }
    updated = client.put("/api/event-types/consultation", json=payload)
    assert updated.status_code == 200
    assert updated.json()["duration_minutes"] == 45


def test_update_missing_type_is_not_found(client) -> None:
    payload = {"id": "nope", "name": "Нет", "description": "", "duration_minutes": 30}
    assert client.put("/api/event-types/nope", json=payload).status_code == 404


def test_delete_event_type(client) -> None:
    assert client.delete("/api/event-types/deep-dive").status_code == 204
    ids = {t["id"] for t in client.get("/api/event-types").json()}
    assert "deep-dive" not in ids


def test_delete_missing_type_is_not_found(client) -> None:
    assert client.delete("/api/event-types/nope").status_code == 404
