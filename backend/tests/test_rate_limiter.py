from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app
from app.services.rate_limiter import limiter, GlobalIPLimiter
from app.config import settings
from app.middleware.rate_limit_middleware import get_global_ip_limiter

@pytest.fixture(autouse=True)
def clean_rate_limiter():
    limiter.clear()
    get_global_ip_limiter().clear()
    yield
    limiter.clear()
    get_global_ip_limiter().clear()

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


# ---------- InMemoryRateLimiter unit tests ----------

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


def test_rate_limiter_get_remaining():
    """get_remaining() returns correct budget after a few requests."""
    user_id = "user_remaining"
    action = "test_remaining"

    info = limiter.get_remaining(user_id, action, limit_per_minute=3, limit_per_day=10)
    assert info["remaining_minute"] == 3
    assert info["remaining_daily"] == 10
    assert info["retry_after"] == 0

    # Use one slot
    limiter.is_rate_limited(user_id, action, limit_per_minute=3, limit_per_day=10)
    info = limiter.get_remaining(user_id, action, limit_per_minute=3, limit_per_day=10)
    assert info["remaining_minute"] == 2
    assert info["remaining_daily"] == 9

    # Exhaust minute limit
    limiter.is_rate_limited(user_id, action, limit_per_minute=3, limit_per_day=10)
    limiter.is_rate_limited(user_id, action, limit_per_minute=3, limit_per_day=10)
    info = limiter.get_remaining(user_id, action, limit_per_minute=3, limit_per_day=10)
    assert info["remaining_minute"] == 0
    assert info["retry_after"] > 0


def test_rate_limiter_different_users():
    """Rate limits are per-user: user A being limited doesn't block user B."""
    assert limiter.is_rate_limited("a", "x", limit_per_minute=1, limit_per_day=100) is False
    assert limiter.is_rate_limited("a", "x", limit_per_minute=1, limit_per_day=100) is True
    # User B should still be fine
    assert limiter.is_rate_limited("b", "x", limit_per_minute=1, limit_per_day=100) is False


# ---------- GlobalIPLimiter unit tests ----------

def test_global_ip_limiter():
    """GlobalIPLimiter blocks after max_requests within the window."""
    ip_limiter = GlobalIPLimiter(max_requests=3, window_seconds=60.0)

    blocked, _ = ip_limiter.is_blocked("1.2.3.4")
    assert blocked is False
    blocked, _ = ip_limiter.is_blocked("1.2.3.4")
    assert blocked is False
    blocked, _ = ip_limiter.is_blocked("1.2.3.4")
    assert blocked is False
    # 4th request -> blocked
    blocked, retry_after = ip_limiter.is_blocked("1.2.3.4")
    assert blocked is True
    assert retry_after > 0


def test_global_ip_limiter_different_ips():
    """Different IPs have independent limits."""
    ip_limiter = GlobalIPLimiter(max_requests=1, window_seconds=60.0)
    blocked, _ = ip_limiter.is_blocked("10.0.0.1")
    assert blocked is False
    blocked, _ = ip_limiter.is_blocked("10.0.0.1")
    assert blocked is True

    # Different IP is fine
    blocked, _ = ip_limiter.is_blocked("10.0.0.2")
    assert blocked is False


def test_global_ip_limiter_clear():
    """clear() resets all IP tracking."""
    ip_limiter = GlobalIPLimiter(max_requests=1, window_seconds=60.0)
    ip_limiter.is_blocked("1.2.3.4")
    ip_limiter.is_blocked("1.2.3.4")
    blocked, _ = ip_limiter.is_blocked("1.2.3.4")
    assert blocked is True

    ip_limiter.clear()
    blocked, _ = ip_limiter.is_blocked("1.2.3.4")
    assert blocked is False


# ---------- Socrates chat integration tests ----------

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
    # Should have rate limit headers
    assert "x-ratelimit-remaining" in r1.headers

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
    assert "retry-after" in r3.headers


# ---------- Login brute-force protection ----------

def test_login_brute_force_protection(client):
    """Rapid login attempts from the same IP are rate-limited."""
    settings.rate_limit_login_minute = 3

    _signup(client, email="brute@example.com")

    for _ in range(3):
        r = client.post("/api/auth/login", json={"email": "brute@example.com", "password": "wrong"})
        # Will be 401 (invalid password) but not 429 yet
        assert r.status_code in (401, 200)

    # 4th attempt should be rate-limited
    r = client.post("/api/auth/login", json={"email": "brute@example.com", "password": "wrong"})
    assert r.status_code == 429
    assert "too many login attempts" in r.json()["detail"].lower()


# ---------- Question gen rate limiting (existing test) ----------

def test_question_gen_rate_limiting_fallback():
    # Set limit low
    settings.rate_limit_question_gen_minute = 1
    settings.rate_limit_question_gen_daily = 5

    user_id = "user_2"
    # First request -> not rate limited
    assert limiter.is_rate_limited(user_id, "question_gen", 1, 5) is False
    # Second request -> rate limited
    assert limiter.is_rate_limited(user_id, "question_gen", 1, 5) is True
