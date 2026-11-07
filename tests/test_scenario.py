"""Shallow scenario smoke tests — intentionally weak."""

from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed


def setup_module() -> None:
    seed(reset=True)


client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["scenario"] == "career-advising"


def test_login_student():
    r = client.post(
        "/api/auth/login",
        json={"email": "student@example.com", "password": "stud-dev"},
    )
    assert r.status_code == 200
    assert r.json()["user"]["role"] == "student"
    assert "password" not in r.json()["user"]


def test_careers_listed():
    r = client.get("/api/careers")
    assert r.status_code == 200
    assert len(r.json()["careers"]) >= 1
