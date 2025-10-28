"""Smoke test for the FastAPI health endpoint."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    """The API should return a 200 OK status for /health."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
