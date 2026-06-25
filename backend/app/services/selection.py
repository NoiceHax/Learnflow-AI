"""Adaptive question selection for quizzes and assessments.

The engine:
  * excludes questions the student already got wrong (retired per-user)
  * generates same-difficulty replacements after misses (LLM on submit only, never on quiz load)
  * prioritises weak concepts and reshapes the learning path after each quiz
"""
from __future__ import annotations

import logging
import random
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models import Chapter, ConceptMastery, Mastery, Question
from ..config import settings
from .adaptive import retired_ids, select_final_quiz, select_practice_quiz
from .quiz_rules import accept_quiz_questions

_DIFF_ORDER = {"Easy": 0, "Medium": 1, "Advanced": 2}
logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _days_since(dt: datetime | None) -> float:
    if dt is None:
        return 999.0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0.0, (_now() - dt).total_seconds() / 86400.0)


def assessment_questions(db: Session, user_id: str | None = None, per_subject_cap: int = 5) -> list[Question]:
    """Balanced diagnostic from the seeded question bank. Never calls the LLM on load."""
    chapters = (
        db.query(Chapter)
        .order_by(Chapter.subject_id, Chapter.jee_weightage.desc(), Chapter.order_index)
        .all()
    )
    retired = retired_ids(db, user_id) if user_id else set()
    picked: list[Question] = []
    per_subject: dict[str, int] = {}

    for ch in chapters:
        if per_subject.get(ch.subject_id, 0) >= per_subject_cap:
            continue
        pool = [q for q in db.query(Question).filter(Question.chapter_id == ch.id).all() if q.id not in retired]
        if not pool:
            continue
        weights = [1.0 / (1 + abs(_DIFF_ORDER.get(q.difficulty, 1) - 1)) for q in pool]
        picked.append(random.choices(pool, weights=weights, k=1)[0])
        per_subject[ch.subject_id] = per_subject.get(ch.subject_id, 0) + 1

    random.shuffle(picked)
    return picked


def _concept_rows(db: Session, user_id: str | None) -> dict[str, ConceptMastery]:
    if not user_id:
        return {}
    return {
        r.concept: r
        for r in db.query(ConceptMastery).filter(ConceptMastery.user_id == user_id).all()
    }


def _effective_mastery(
    db: Session, user_id: str | None, chapter_id: str, concepts: set[str], cm: dict[str, ConceptMastery]
) -> float:
    if user_id:
        row = (
            db.query(Mastery)
            .filter(Mastery.user_id == user_id, Mastery.chapter_id == chapter_id)
            .one_or_none()
        )
        if row is not None:
            return row.mastery_score
    emas = [cm[c].ema for c in concepts if c in cm]
    return sum(emas) / len(emas) if emas else 0.0


def chapter_questions(
    db: Session,
    chapter_id: str,
    user_id: str | None = None,
    count: int = 6,
    *,
    mode: str = "final",
    is_pyq: bool | None = None,
    pyq_year: int | None = None,
    pyq_exam: str | None = None,
) -> list[Question]:
    query = db.query(Question).filter(Question.chapter_id == chapter_id)
    if is_pyq is not None:
        query = query.filter(Question.is_pyq == is_pyq)
    if pyq_year is not None:
        query = query.filter(Question.pyq_year == pyq_year)
    if pyq_exam is not None:
        query = query.filter(Question.pyq_exam == pyq_exam)

    pool = query.all()

    if is_pyq is not None or pyq_year is not None or pyq_exam is not None:
        random.shuffle(pool)
        return accept_quiz_questions(pool[:count])

    if len(pool) < settings.min_quiz_questions:
        return []

    if not user_id:
        picked = sorted(
            random.sample(pool, min(count, len(pool))),
            key=lambda q: _DIFF_ORDER.get(q.difficulty, 1),
        )
        return accept_quiz_questions(picked)

    if mode == "practice":
        selected = select_practice_quiz(db, user_id, chapter_id, count)
        if selected:
            return accept_quiz_questions(selected)
        logger.warning("Practice selection empty for chapter=%s user=%s", chapter_id, user_id)
        return []

    # final quiz: fresh, harder questions never shown in practice or prior finals
    cm = _concept_rows(db, user_id)
    concepts = {q.concept for q in pool}
    eff = _effective_mastery(db, user_id, chapter_id, concepts, cm)
    selected = select_final_quiz(
        db, user_id, chapter_id, count, effective_mastery=eff, concept_mastery=cm
    )
    if selected:
        return accept_quiz_questions(selected)

    logger.warning(
        "Final quiz selection empty for chapter=%s user=%s (pool=%d)",
        chapter_id,
        user_id,
        len(pool),
    )
    return []
