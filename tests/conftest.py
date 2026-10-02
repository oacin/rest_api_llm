"""Shared pytest fixtures: a TestClient backed by a temporary SQLite file."""

import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app


@pytest.fixture
def db_path(tmp_path, monkeypatch) -> str:
    """Point the app at a temporary database file and return its path."""
    path = str(tmp_path / "test_fruits.db")
    monkeypatch.setattr(database, "DB_PATH", path)
    return path


@pytest.fixture
def client(db_path):
    """A test client for an empty, temporary database. Fresh for every test."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def create_fruit(client):
    """Return a helper that POSTs a fruit and returns the created fruit."""

    def _create(**overrides) -> dict:
        payload = {"name": "Apple", "color": "red", "quantity": 12}
        payload.update(overrides)
        response = client.post("/fruits", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _create