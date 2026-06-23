"""Persistent cache for LLM outputs. Reuse before calling the API."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..models import LlmCache, Question
from .question_gen import AI_CONCEPT_PREFIX

_SOCRATES_TTL = timedelta(days=30)
_QUESTIONS_TTL = timedelta(days=90)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_key(*parts: str) -> str:
    blob = "|".join(parts).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def cache_get(db: Session, cache_key: str, cache_type: str) -> str | None:
    row = (
        db.query(LlmCache)
        .filter(LlmCache.cache_key == cache_key, LlmCache.cache_type == cache_type)
        .one_or_none()
    )
    if row is None:
        return None
    if row.expires_at and row.expires_at < _now():
        db.delete(row)
        db.flush()
        return None
    return row.payload


def cache_set(
    db: Session,
    cache_key: str,
    cache_type: str,
    payload: str,
    *,
    ttl: timedelta,
) -> None:
    expires = _now() + ttl
    row = db.query(LlmCache).filter(LlmCache.cache_key == cache_key).one_or_none()
    if row is None:
        db.add(
            LlmCache(
                cache_key=cache_key,
                cache_type=cache_type,
                payload=payload,
                expires_at=expires,
            )
        )
    else:
        row.cache_type = cache_type
        row.payload = payload
        row.expires_at = expires
        row.created_at = _now()
    db.flush()


def socrates_cache_key(
    message: str,
    context: dict | None,
    history: list[dict[str, str]],
) -> str:
    ctx = json.dumps(context or {}, sort_keys=True, default=str)
    hist = json.dumps(history[-4:], default=str)
    return _hash_key("socrates", message.strip().lower(), ctx, hist)


def get_cached_socrates(db: Session, cache_key: str) -> str | None:
    return cache_get(db, cache_key, "socrates")


def set_cached_socrates(db: Session, cache_key: str, reply: str) -> None:
    cache_set(db, cache_key, "socrates", reply, ttl=_SOCRATES_TTL)


def fetch_db_question_cache(
    db: Session,
    chapter_id: str,
    *,
    difficulty: str,
    concepts: list[str],
    count: int,
    exclude_prompts: set[str] | None = None,
    retired_ids: set[str] | None = None,
) -> list[Question]:
    """Reuse AI-tagged questions already stored for this chapter (DB-first)."""
    exclude_prompts = exclude_prompts or set()
    retired_ids = retired_ids or set()
    concept_set = {c.lower() for c in concepts if c}

    pool = (
        db.query(Question)
        .filter(Question.chapter_id == chapter_id, Question.concept.like(f"{AI_CONCEPT_PREFIX}%"))
        .all()
    )
    matches: list[Question] = []
    for q in pool:
        if q.id in retired_ids:
            continue
        if q.prompt in exclude_prompts:
            continue
        if q.difficulty != difficulty:
            continue
        label = q.concept.replace(AI_CONCEPT_PREFIX, "").strip().lower()
        if concept_set and label not in concept_set:
            continue
        matches.append(q)

    if len(matches) < count:
        for q in pool:
            if q in matches or q.id in retired_ids or q.prompt in exclude_prompts:
                continue
            if q.difficulty == difficulty:
                matches.append(q)
            if len(matches) >= count:
                break

    return matches[:count]
