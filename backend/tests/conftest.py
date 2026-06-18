"""Shared pytest fixtures.

The whole suite runs fully offline and against an isolated in-memory SQLite
database — no network, no Gemini/NVIDIA calls, no touching the dev `astra.db`.

Two things make that guaranteed:

  1. We set ``DATABASE_URL`` / ``USE_GEMINI`` in the environment *before* the
     ``app`` package is imported, so the module-level engine is in-memory.
  2. We also mutate the imported ``settings`` singleton directly. This app
     gives ``backend/.env`` precedence over OS env vars, so on a machine that
     has a real ``.env`` (with an API key) the env approach alone wouldn't be
     enough — mutating the singleton is the belt-and-braces guarantee.
"""
from __future__ import annotations

import os

# Must run before any `from app...` import below.
os.environ["DATABASE_URL"] = "sqlite://"  # in-memory: never writes astra.db
os.environ["USE_GEMINI"] = "false"
os.environ["AI_PROVIDER"] = "nvidia"
os.environ["NVIDIA_API_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""
os.environ["JWT_SECRET"] = "test-secret-do-not-use-in-production-environments"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base
from app import models  # noqa: F401  (registers all tables on Base.metadata)

# Belt-and-braces: force offline + deterministic auth regardless of any .env.
settings.use_gemini = False
settings.ai_provider = "nvidia"
settings.nvidia_api_key = ""
settings.gemini_api_key = ""
settings.jwt_secret = "test-secret-do-not-use-in-production-environments"


@pytest.fixture
def engine():
    """A fresh in-memory SQLite engine per test (full isolation)."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # one shared connection so :memory: persists across sessions
        future=True,
    )
    Base.metadata.create_all(bind=eng)
    try:
        yield eng
    finally:
        Base.metadata.drop_all(bind=eng)
        eng.dispose()


@pytest.fixture
def db(engine) -> Session:
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()


# --------------------------------------------------------------------------- #
# Data factories
# --------------------------------------------------------------------------- #
@pytest.fixture
def make_question(db):
    """Returns a factory that builds + persists a Question in a chapter."""
    counter = {"n": 0}

    def _make(
        chapter,
        *,
        type: str = "single_correct",
        difficulty: str = "Medium",
        concept: str = "Concept A",
        correct_answer=0,
        options=None,
        tolerance=None,
        prompt: str | None = None,
    ) -> models.Question:
        counter["n"] += 1
        q = models.Question(
            subject=chapter.subject.name if chapter.subject else "Physics",
            chapter=chapter.chapter_name,
            chapter_id=chapter.id,
            difficulty=difficulty,
            concept=concept,
            type=type,
            prompt=prompt or f"{concept} / {difficulty} #{counter['n']}",
            options=options,
            correct_answer=correct_answer,
            tolerance=tolerance,
            solution="Because.",
        )
        db.add(q)
        db.flush()
        return q

    return _make


@pytest.fixture
def physics(db) -> models.Subject:
    s = models.Subject(name="Physics", slug="physics", order_index=0)
    db.add(s)
    db.flush()
    return s


@pytest.fixture
def chapters(db, physics):
    """A 3-chapter prerequisite chain: vectors -> electrostatics -> current."""
    vectors = models.Chapter(
        subject_id=physics.id, chapter_name="Vectors", slug="vectors",
        order_index=0, jee_weightage=4, prerequisite_id=None,
    )
    db.add(vectors)
    db.flush()
    electro = models.Chapter(
        subject_id=physics.id, chapter_name="Electrostatics", slug="electrostatics",
        order_index=1, jee_weightage=5, prerequisite_id=vectors.id,
    )
    db.add(electro)
    db.flush()
    current = models.Chapter(
        subject_id=physics.id, chapter_name="Current Electricity", slug="current-electricity",
        order_index=2, jee_weightage=3, prerequisite_id=electro.id,
    )
    db.add(current)
    db.flush()
    return {"vectors": vectors, "electrostatics": electro, "current": current}


@pytest.fixture
def user(db) -> models.User:
    u = models.User(name="Test Student", email="student@example.com", password_hash="x")
    db.add(u)
    db.flush()
    return u
