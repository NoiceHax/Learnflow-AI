"""Tests for password hashing + JWT helpers (security.py)."""
from __future__ import annotations

import jwt

from app.config import settings
from app.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_is_salted_and_verifies():
    h1 = hash_password("hunter2")
    h2 = hash_password("hunter2")
    assert h1 != h2            # random salt -> different hashes
    assert h1 != "hunter2"     # never stored in clear
    assert verify_password("hunter2", h1) is True
    assert verify_password("hunter2", h2) is True


def test_verify_password_rejects_wrong_password():
    h = hash_password("correct horse battery staple")
    assert verify_password("Tr0ub4dor&3", h) is False


def test_verify_password_handles_garbage_hash_without_raising():
    # A corrupted/non-bcrypt hash must return False, not blow up.
    assert verify_password("anything", "not-a-real-hash") is False
    assert verify_password("anything", "") is False


def test_token_round_trips_subject():
    token = create_access_token("user-123")
    assert decode_token(token) == "user-123"


def test_decode_rejects_tampered_token():
    token = create_access_token("user-123")
    tampered = token[:-2] + ("aa" if not token.endswith("aa") else "bb")
    assert decode_token(tampered) is None


def test_decode_rejects_token_signed_with_other_secret():
    forged = jwt.encode({"sub": "intruder"}, "some-other-secret", algorithm=settings.jwt_algorithm)
    assert decode_token(forged) is None


def test_decode_rejects_garbage():
    assert decode_token("not.a.jwt") is None
    assert decode_token("") is None
