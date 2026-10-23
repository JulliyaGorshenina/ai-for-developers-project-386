"""Contract-API tests for the owner's weekly schedule."""


def test_seeded_schedule_is_listed(client) -> None:
    windows = client.get("/api/schedule").json()
    assert len(windows) == 5  # Monday..Friday
    assert all(w["start_time"] == "10:00" and w["end_time"] == "18:00" for w in windows)


def test_update_schedule_replaces_windows(client) -> None:
    payload = {"windows": [{"weekday": 0, "start_time": "09:00", "end_time": "12:00"}]}
    response = client.put("/api/schedule", json=payload)
    assert response.status_code == 200
    assert response.json() == payload["windows"]


def test_overlapping_windows_are_rejected(client) -> None:
    payload = {
        "windows": [
            {"weekday": 0, "start_time": "10:00", "end_time": "14:00"},
            {"weekday": 0, "start_time": "13:00", "end_time": "18:00"},
        ]
    }
    assert client.put("/api/schedule", json=payload).status_code == 400


def test_inverted_window_is_rejected(client) -> None:
    payload = {"windows": [{"weekday": 0, "start_time": "18:00", "end_time": "10:00"}]}
    assert client.put("/api/schedule", json=payload).status_code == 400


def test_adjacent_windows_are_allowed(client) -> None:
    payload = {
        "windows": [
            {"weekday": 0, "start_time": "10:00", "end_time": "13:00"},
            {"weekday": 0, "start_time": "13:00", "end_time": "18:00"},
        ]
    }
    assert client.put("/api/schedule", json=payload).status_code == 200
