"""Persist Gemini-generated questions and blend them into quiz/assessment selection."""
from __future__ import annotations

import logging
import random

from sqlalchemy import not_
from sqlalchemy.orm import Session

from ..models import Chapter, Question, Subject
from .gemini import gemini_enabled, generate_questions

logger = logging.getLogger(__name__)

AI_CONCEPT_PREFIX = "[AI] "


def _is_ai(q: Question) -> bool:
    return q.concept.startswith(AI_CONCEPT_PREFIX)


def trim_old_ai(db: Session, chapter_id: str, keep: int = 40) -> None:
    rows = (
        db.query(Question)
        .filter(Question.chapter_id == chapter_id, Question.concept.like(f"{AI_CONCEPT_PREFIX}%"))
        .order_by(Question.id.desc())
        .all()
    )
    for row in rows[keep:]:
        db.delete(row)
    if len(rows) > keep:
        db.commit()


def persist_generated(db: Session, chapter: Chapter, subject: Subject, raw: list[dict]) -> list[Question]:
    saved: list[Question] = []
    for q in raw:
        options = None
        correct = q["correct"]
        qtype = q["type"]
        if q.get("options"):
            texts = list(q["options"])
            if qtype == "single_correct":
                correct = int(correct)
            elif qtype == "multiple_correct":
                correct = [int(c) for c in correct]
            options = [{"id": str(i), "text": text} for i, text in enumerate(texts)]

        row = Question(
            subject=subject.name,
            chapter=chapter.chapter_name,
            chapter_id=chapter.id,
            difficulty=q.get("difficulty") or "Medium",
            concept=f"{AI_CONCEPT_PREFIX}{q.get('concept') or chapter.chapter_name}",
            jee_weightage=chapter.jee_weightage,
            type=qtype,
            prompt=q["prompt"],
            options=options,
            correct_answer=correct,
            tolerance=q.get("tolerance"),
            unit=q.get("unit"),
            solution=(q.get("solution") or "") + " [[ai]]",
        )
        db.add(row)
        saved.append(row)
    db.commit()
    for row in saved:
        db.refresh(row)
    return saved


def generate_for_chapter(
    db: Session,
    chapter: Chapter,
    *,
    count: int,
    difficulty: str,
    concepts: list[str],
    user_id: str | None = None,
    exclude_question_ids: set[str] | None = None,
) -> list[Question]:
    """Generate and persist fresh AI questions for a chapter. Returns [] if Gemini disabled."""
    if not gemini_enabled() or count < 1:
        return []

    subject = db.get(Subject, chapter.subject_id)
    if subject is None:
        return []

    exclude: list[str] = []
    blocked: set[str] = set(exclude_question_ids or ())
    pool = db.query(Question).filter(Question.chapter_id == chapter.id).all()
    if user_id:
        from ..models import UserQuestionState

        states = (
            db.query(UserQuestionState)
            .filter(UserQuestionState.user_id == user_id, UserQuestionState.chapter_id == chapter.id)
            .all()
        )
        seen = {r.question_id for r in states if (r.seen_count or 0) > 0}
        retired = {r.question_id for r in states if r.retired}
        blocked |= seen | retired
        exclude = [q.prompt for q in pool if q.id in blocked]
    else:
        exclude = [q.prompt for q in pool if not _is_ai(q)][:12]

    from .gemini_cache import fetch_db_question_cache

    cached = fetch_db_question_cache(
        db,
        chapter.id,
        difficulty=difficulty,
        concepts=concepts,
        count=count,
        exclude_prompts=set(exclude),
        retired_ids=blocked,
    )
    cached = [q for q in cached if q.id not in blocked]
    if len(cached) >= count:
        logger.info("Reused %d cached AI question(s) for chapter %s", len(cached[:count]), chapter.slug)
        return cached[:count]

    raw, err = generate_questions(
        subject_name=subject.name,
        chapter_name=chapter.chapter_name,
        chapter_description=chapter.description or "",
        difficulty=difficulty,
        concepts=concepts,
        count=count,
        exclude_prompts=exclude,
    )
    if err:
        logger.warning("AI question generation failed for %s: %s", chapter.slug, err)
        return cached

    trim_old_ai(db, chapter.id)
    saved = persist_generated(db, chapter, subject, raw)
    saved = [q for q in saved if q.id not in blocked]
    logger.info("Generated %d AI question(s) for chapter %s", len(saved), chapter.slug)
    if saved:
        return saved[:count]
    return cached[:count]


def blend_ai_questions(
    db: Session,
    chapter: Chapter,
    selected: list[Question],
    *,
    user_id: str | None,
    target_count: int,
    effective_mastery: float,
    weak_concepts: list[str] | None = None,
) -> list[Question]:
    """Replace part of the static selection with freshly generated AI questions."""
    if not gemini_enabled():
        return selected

    ai_count = 2 if effective_mastery < 75 else 1
    ai_count = min(ai_count, max(1, target_count // 2))

    if effective_mastery < 50:
        difficulty = "Easy"
    elif effective_mastery < 75:
        difficulty = "Medium"
    else:
        difficulty = "Advanced"

    concepts = weak_concepts or list({_clean_concept(q.concept) for q in selected})
    if not concepts:
        concepts = [chapter.chapter_name]

    fresh = generate_for_chapter(
        db, chapter, count=ai_count, difficulty=difficulty, concepts=concepts, user_id=user_id
    )
    if not fresh:
        return selected

    static = [q for q in selected if not _is_ai(q)]
    return (fresh + static)[:target_count]


def _clean_concept(concept: str) -> str:
    return concept.replace(AI_CONCEPT_PREFIX, "").strip()
