"""Shared pytest fixtures and test environment setup."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("BOOKING_TZ", "Europe/Moscow")


@pytest.fixture(autouse=True)
def fresh_db(monkeypatch, tmp_path):
    """Give every test its own seeded SQLite database."""
    from app import config

    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")


@pytest.fixture()
def client():
    """A TestClient whose lifespan seeds the fresh database."""
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
