"""End-to-end auth API tests through FastAPI's TestClient.

Runs against the in-memory test DB via a dependency override; the lifespan
startup makes no network calls because USE_GEMINI is forced off in conftest.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app


@pytest.fixture
def client(engine):
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    def _override():
        s = TestingSession()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _signup(client, email="alice@example.com", password="secret123", name="Alice"):
    return client.post("/api/auth/signup", json={"name": name, "email": email, "password": password})


def test_signup_creates_user_and_returns_token(client):
    r = _signup(client)
    assert r.status_code == 201
    body = r.json()
    assert body["token"]
    assert body["user"]["email"] == "alice@example.com"
    assert body["user"]["onboarded"] is False


def test_signup_normalises_email_case(client):
    r = _signup(client, email="Alice@Example.COM")
    assert r.status_code == 201
    assert r.json()["user"]["email"] == "alice@example.com"


def test_signup_duplicate_email_conflicts(client):
    _signup(client)
    r = _signup(client, name="Alice2")
    assert r.status_code == 409


def test_signup_rejects_short_password(client):
    r = _signup(client, password="123")  # min_length=6
    assert r.status_code == 422


def test_login_succeeds_with_correct_credentials(client):
    _signup(client)
    r = client.post("/api/auth/login", json={"email": "alice@example.com", "password": "secret123"})
    assert r.status_code == 200
    assert r.json()["token"]


def test_login_wrong_password_is_401(client):
    _signup(client)
    r = client.post("/api/auth/login", json={"email": "alice@example.com", "password": "wrong"})
    assert r.status_code == 401


def test_login_unknown_email_is_401(client):
    r = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "secret123"})
    assert r.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_me_returns_current_user_with_token(client):
    token = _signup(client).json()["token"]
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "alice@example.com"


def test_health_endpoint_reports_offline_mode(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["llm"]["use_ai"] is False
    assert body["llm"]["connected"] is False
