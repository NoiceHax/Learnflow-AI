"""Adaptive mastery scoring.

Mastery is an exponential moving average of quiz performance so that recent
results matter most while history still counts. Thresholds drive the adaptive
behaviour described in the spec:

  >= 80  -> mastered, move forward
  < 60   -> weak, revisit with extra practice
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models import Chapter, ConceptMastery, Mastery, Question

MASTER_THRESHOLD = 80.0
PASS_THRESHOLD = 60.0
WEAK_THRESHOLD = 60.0
EMA_ALPHA = 0.45  # weight on the newest score


def _now() -> datetime:
    return datetime.now(timezone.utc)


def blend(old: float, new: float, attempts: int) -> float:
    if attempts <= 0:
        return round(new, 1)
    return round((1 - EMA_ALPHA) * old + EMA_ALPHA * new, 1)


def upsert_mastery(db: Session, user_id: str, chapter: Chapter, score: float) -> Mastery:
    row = (
        db.query(Mastery)
        .filter(Mastery.user_id == user_id, Mastery.chapter_id == chapter.id)
        .one_or_none()
    )
    if row is None:
        row = Mastery(
            user_id=user_id,
            chapter_id=chapter.id,
            chapter=chapter.chapter_name,
            subject=chapter.subject.name if chapter.subject else "",
            mastery_score=round(score, 1),
            attempts=1,
        )
        db.add(row)
    else:
        row.mastery_score = blend(row.mastery_score or 0, score, row.attempts or 0)
        row.attempts = (row.attempts or 0) + 1
    return row


def mark_chapter_mastered(db: Session, user_id: str, chapter: Chapter) -> Mastery:
    """Final quiz perfect score: chapter is solved (100% mastery)."""
    row = (
        db.query(Mastery)
        .filter(Mastery.user_id == user_id, Mastery.chapter_id == chapter.id)
        .one_or_none()
    )
    if row is None:
        row = Mastery(
            user_id=user_id,
            chapter_id=chapter.id,
            chapter=chapter.chapter_name,
            subject=chapter.subject.name if chapter.subject else "",
            mastery_score=100.0,
            attempts=1,
        )
        db.add(row)
    else:
        row.mastery_score = 100.0
        row.attempts = (row.attempts or 0) + 1
    return row


def update_concept_mastery(
    db: Session, user_id: str, questions: list[Question], correct_by_qid: dict[str, bool]
) -> None:
    """Update per-concept EMA, attempts, fail-streak and last-seen after grading."""
    rows = {
        r.concept: r
        for r in db.query(ConceptMastery).filter(ConceptMastery.user_id == user_id).all()
    }
    for q in questions:
        correct = bool(correct_by_qid.get(q.id))
        sample = 100.0 if correct else 0.0
        row = rows.get(q.concept)
        if row is None:
            row = ConceptMastery(
                user_id=user_id,
                concept=q.concept,
                chapter_id=q.chapter_id,
                subject=q.subject,
                ema=sample,
                attempts=1,
                correct=1 if correct else 0,
                fail_streak=0 if correct else 1,
                last_seen=_now(),
            )
            db.add(row)
            rows[q.concept] = row
        else:
            row.ema = blend(row.ema or 0, sample, row.attempts or 0)
            row.attempts = (row.attempts or 0) + 1
            row.correct = (row.correct or 0) + (1 if correct else 0)
            row.fail_streak = 0 if correct else (row.fail_streak or 0) + 1
            row.chapter_id = q.chapter_id
            row.subject = q.subject
            row.last_seen = _now()


def concept_ema_map(db: Session, user_id: str) -> dict[str, float]:
    return {
        r.concept: r.ema
        for r in db.query(ConceptMastery).filter(ConceptMastery.user_id == user_id).all()
    }


def seed_mastery_from_assessment(
    db: Session, user_id: str, chapter_scores: dict[str, float]
) -> None:
    """Initialise mastery rows from the initial assessment (keyed by chapter slug)."""
    chapters = {c.slug: c for c in db.query(Chapter).all()}
    for slug, score in chapter_scores.items():
        chapter = chapters.get(slug)
        if chapter is None:
            continue
        existing = (
            db.query(Mastery)
            .filter(Mastery.user_id == user_id, Mastery.chapter_id == chapter.id)
            .one_or_none()
        )
        if existing is None:
            db.add(
                Mastery(
                    user_id=user_id,
                    chapter_id=chapter.id,
                    chapter=chapter.chapter_name,
                    subject=chapter.subject.name if chapter.subject else "",
                    mastery_score=round(score, 1),
                    attempts=1,
                )
            )
        else:
            existing.mastery_score = round(score, 1)
