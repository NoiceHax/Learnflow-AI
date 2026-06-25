from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app
from app.services.rate_limiter import limiter
from app.config import settings

@pytest.fixture(autouse=True)
def clean_rate_limiter():
    limiter.clear()
    yield
    limiter.clear()

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


def test_rate_limiter_logic():
    # Test rate limiter directly
    # limit: 2 per minute, 5 per day
    user_id = "user_1"
    action = "test_action"

    # First request
    assert limiter.is_rate_limited(user_id, action, limit_per_minute=2, limit_per_day=5) is False
    # Second request
    assert limiter.is_rate_limited(user_id, action, limit_per_minute=2, limit_per_day=5) is False
    # Third request -> blocked by per-minute limit
    assert limiter.is_rate_limited(user_id, action, limit_per_minute=2, limit_per_day=5) is True


def test_socrates_chat_rate_limiting(client):
    # Set limit very low for testing
    settings.rate_limit_socrates_minute = 2
    settings.rate_limit_socrates_daily = 10

    signup_res = _signup(client)
    token = signup_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # First chat request
    r1 = client.post(
        "/api/socrates/chat",
        headers=headers,
        json={"message": "What is 1+1?", "chapter_context": "Basic Math"}
    )
    # The LLM is disabled in test mode so we expect Socrates tutoring chat response to be mock/fallback
    assert r1.status_code == 200

    # Second chat request
    r2 = client.post(
        "/api/socrates/chat",
        headers=headers,
        json={"message": "What is 2+2?", "chapter_context": "Basic Math"}
    )
    assert r2.status_code == 200

    # Third chat request -> should fail with 429
    r3 = client.post(
        "/api/socrates/chat",
        headers=headers,
        json={"message": "What is 3+3?", "chapter_context": "Basic Math"}
    )
    assert r3.status_code == 429
    assert r3.json()["detail"] == "Too many requests to Socrates tutoring chat. Please wait a bit or try again tomorrow."


def test_question_gen_rate_limiting_fallback():
    # Set limit low
    settings.rate_limit_question_gen_minute = 1
    settings.rate_limit_question_gen_daily = 5

    user_id = "user_2"
    # First request -> not rate limited
    assert limiter.is_rate_limited(user_id, "question_gen", 1, 5) is False
    # Second request -> rate limited
    assert limiter.is_rate_limited(user_id, "question_gen", 1, 5) is True
