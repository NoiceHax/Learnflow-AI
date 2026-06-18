"""Adaptive learning engine: retire missed questions, spawn similar replacements,
and reshape the syllabus after every quiz."""
from __future__ import annotations

import logging
import random
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from ..models import Chapter, ConceptMastery, Question, Subject, UserQuestionState
from .gemini import gemini_enabled, generate_questions
from .question_gen import AI_CONCEPT_PREFIX, persist_generated, trim_old_ai

logger = logging.getLogger(__name__)

_DIFF_ORDER = {"Easy": 0, "Medium": 1, "Advanced": 2}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _clean_concept(concept: str) -> str:
    return concept.replace(AI_CONCEPT_PREFIX, "").strip()


def retired_ids(db: Session, user_id: str) -> set[str]:
    return {
        r.question_id
        for r in db.query(UserQuestionState)
        .filter(UserQuestionState.user_id == user_id, UserQuestionState.retired.is_(True))
        .all()
    }


def record_attempts(
    db: Session,
    user_id: str,
    questions: list[Question],
    correct_by_qid: dict[str, bool],
    *,
    mode: str = "adaptive",
) -> list[Question]:
    """Record outcomes.

    final: retire wrong answers (excluded from future final quizzes).
    practice: keep wrong in the practice pool; drop questions once answered correctly.
    """
    retired_rows: list[Question] = []
    for q in questions:
        ok = bool(correct_by_qid.get(q.id))
        row = (
            db.query(UserQuestionState)
            .filter(UserQuestionState.user_id == user_id, UserQuestionState.question_id == q.id)
            .one_or_none()
        )
        if row is None:
            row = UserQuestionState(
                user_id=user_id,
                question_id=q.id,
                chapter_id=q.chapter_id,
                seen_count=0,
                wrong_count=0,
                retired=False,
            )
            db.add(row)
        row.seen_count = (row.seen_count or 0) + 1
        row.last_correct = ok

        if mode == "practice":
            if ok:
                row.retired = False
            else:
                row.wrong_count = (row.wrong_count or 0) + 1
                row.retired = True
                retired_rows.append(q)
            continue

        if not ok:
            row.wrong_count = (row.wrong_count or 0) + 1
            row.retired = True
            retired_rows.append(q)
    return retired_rows


def _reference_payload(q: Question) -> dict[str, Any]:
    return {
        "prompt": q.prompt,
        "difficulty": q.difficulty,
        "concept": _clean_concept(q.concept),
        "type": q.type,
    }


def _pick_pool_replacements(
    db: Session,
    chapter: Chapter,
    references: list[Question],
    *,
    user_id: str,
) -> list[Question]:
    """DB-only replacement picks. Never calls Gemini (safe for quiz load)."""
    if not references:
        return []

    retired = retired_ids(db, user_id)
    pool = db.query(Question).filter(Question.chapter_id == chapter.id).all()
    created: list[Question] = []
    used_ids: set[str] = set()

    for ref in references:
        concept = _clean_concept(ref.concept)
        candidates = [
            q
            for q in pool
            if q.id not in retired
            and q.id not in used_ids
            and q.difficulty == ref.difficulty
            and _clean_concept(q.concept).lower() == concept.lower()
        ]
        if not candidates:
            candidates = [
                q
                for q in pool
                if q.id not in retired and q.id not in used_ids and q.difficulty == ref.difficulty
            ]
        if not candidates:
            candidates = [q for q in pool if q.id not in retired and q.id not in used_ids]
        if candidates:
            pick = random.choice(candidates)
            created.append(pick)
            used_ids.add(pick.id)

    return created


def generate_similar_replacements(
    db: Session,
    chapter: Chapter,
    references: list[Question],
    *,
    user_id: str,
) -> list[Question]:
    """Create same-difficulty replacement questions for retired items."""
    if not references:
        return []

    subject = db.get(Subject, chapter.subject_id)
    if subject is None:
        return []

    retired = retired_ids(db, user_id)
    pool = db.query(Question).filter(Question.chapter_id == chapter.id).all()
    exclude = list({q.prompt for q in pool})

    created: list[Question] = []
    by_difficulty: dict[str, list[Question]] = {}
    for ref in references:
        by_difficulty.setdefault(ref.difficulty, []).append(ref)

    for difficulty, refs in by_difficulty.items():
        concepts = list({_clean_concept(r.concept) for r in refs})
        ref_payloads = [_reference_payload(r) for r in refs]

        from .gemini_cache import fetch_db_question_cache

        cached = fetch_db_question_cache(
            db,
            chapter.id,
            difficulty=difficulty,
            concepts=concepts,
            count=len(refs),
            exclude_prompts=set(exclude),
            retired_ids=retired,
        )
        if len(cached) >= len(refs):
            created.extend(cached[: len(refs)])
            exclude.extend(q.prompt for q in cached[: len(refs)])
            continue

        if gemini_enabled():
            raw, err = generate_questions(
                subject_name=subject.name,
                chapter_name=chapter.chapter_name,
                chapter_description=chapter.description or "",
                difficulty=difficulty,
                concepts=concepts,
                count=len(refs),
                exclude_prompts=exclude,
                reference_questions=ref_payloads,
            )
            if raw:
                trim_old_ai(db, chapter.id)
                batch = persist_generated(db, chapter, subject, raw)
                created.extend(batch)
                exclude.extend(q.prompt for q in batch)
                continue
            if err:
                logger.warning("AI replacement failed (%s); using pool fallback", err)

        pool_picks = _pick_pool_replacements(db, chapter, refs, user_id=user_id)
        created.extend(pool_picks)
        exclude.extend(q.prompt for q in pool_picks)

    return created


def replenish_pool(
    db: Session,
    user_id: str,
    chapter_id: str,
    retired_questions: list[Question],
) -> int:
    chapter = db.get(Chapter, chapter_id)
    if chapter is None or not retired_questions:
        return 0
    return len(generate_similar_replacements(db, chapter, retired_questions, user_id=user_id))


def weak_concepts_for_user(db: Session, user_id: str, chapter_id: str) -> list[str]:
    rows = (
        db.query(ConceptMastery)
        .filter(ConceptMastery.user_id == user_id, ConceptMastery.chapter_id == chapter_id)
        .all()
    )
    weak = sorted(rows, key=lambda r: (r.ema, -r.fail_streak))
    return [_clean_concept(r.concept) for r in weak if r.ema < 70 or r.fail_streak >= 1]


def seen_question_ids(db: Session, user_id: str, chapter_id: str) -> set[str]:
    """Questions this user has already attempted in practice or final quizzes."""
    return {
        r.question_id
        for r in db.query(UserQuestionState)
        .filter(
            UserQuestionState.user_id == user_id,
            UserQuestionState.chapter_id == chapter_id,
            UserQuestionState.seen_count > 0,
        )
        .all()
    }


def final_quiz_difficulty(effective_mastery: float) -> str:
    """Final quizzes are always at least Medium and one step harder than adaptive target."""
    order = ["Easy", "Medium", "Advanced"]
    base = target_difficulty(effective_mastery)
    idx = min(order.index(base) + 1, len(order) - 1)
    return order[idx]


def _ensure_pool_for_user(db: Session, user_id: str, chapter: Chapter) -> list[Question]:
    """Return a usable question pool, replenishing or recycling when all are retired."""
    chapter_id = chapter.id
    all_qs = db.query(Question).filter(Question.chapter_id == chapter_id).all()
    if not all_qs:
        return []

    retired = retired_ids(db, user_id)
    pool = [q for q in all_qs if q.id not in retired]
    if pool:
        return pool

    retired_qs = [q for q in all_qs if q.id in retired]
    logger.info(
        "Adaptive pool exhausted: user=%s chapter=%s (%d/%d retired); replenishing",
        user_id,
        chapter.slug,
        len(retired_qs),
        len(all_qs),
    )

    replacements = _pick_pool_replacements(db, chapter, retired_qs, user_id=user_id)
    if replacements:
        db.flush()
        retired = retired_ids(db, user_id)
        pool = [
            q
            for q in db.query(Question).filter(Question.chapter_id == chapter_id).all()
            if q.id not in retired
        ]
        if pool:
            logger.info("Replenished adaptive pool: chapter=%s now has %d available", chapter.slug, len(pool))
            return pool

    # Gemini off or chapter too small: recycle retired questions so quizzes never 404
    logger.warning(
        "Recycling retired questions: user=%s chapter=%s (no new replacements available)",
        user_id,
        chapter.slug,
    )
    (
        db.query(UserQuestionState)
        .filter(
            UserQuestionState.user_id == user_id,
            UserQuestionState.chapter_id == chapter_id,
            UserQuestionState.retired.is_(True),
        )
        .update({UserQuestionState.retired: False}, synchronize_session=False)
    )
    db.flush()
    return all_qs


def target_difficulty(effective_mastery: float) -> str:
    if effective_mastery < 50:
        return "Easy"
    if effective_mastery < 75:
        return "Medium"
    return "Advanced"


def select_final_quiz(
    db: Session,
    user_id: str,
    chapter_id: str,
    count: int,
    *,
    effective_mastery: float,
    concept_mastery: dict[str, ConceptMastery],
) -> list[Question]:
    """Fresh final-quiz set: harder difficulty, never reuses practice or prior attempts."""
    from .question_gen import generate_for_chapter

    chapter = db.get(Chapter, chapter_id)
    if chapter is None:
        return []

    seen = seen_question_ids(db, user_id, chapter_id)
    retired = retired_ids(db, user_id)
    blocked = seen | retired

    weak = weak_concepts_for_user(db, user_id, chapter_id)
    diff = final_quiz_difficulty(effective_mastery)
    concepts = weak or list({_clean_concept(q.concept) for q in db.query(Question).filter(Question.chapter_id == chapter_id).all()})
    if not concepts:
        concepts = [chapter.chapter_name]

    # Prefer a full freshly generated set (never shown to this user before).
    if gemini_enabled():
        fresh = generate_for_chapter(
            db,
            chapter,
            count=count,
            difficulty=diff,
            concepts=concepts,
            user_id=user_id,
            exclude_question_ids=blocked,
        )
        fresh = [q for q in fresh if q.id not in blocked]
        if len(fresh) >= count:
            random.shuffle(fresh)
            fresh.sort(key=lambda q: _DIFF_ORDER.get(q.difficulty, 1), reverse=True)
            return fresh[:count]

    pool = [
        q
        for q in db.query(Question).filter(Question.chapter_id == chapter_id).all()
        if q.id not in blocked
    ]
    if not pool:
        return []

    diff_rank = _DIFF_ORDER.get(diff, 1)
    harder = [q for q in pool if _DIFF_ORDER.get(q.difficulty, 1) >= diff_rank]
    candidates = harder or pool

    def score(q: Question) -> float:
        concept = _clean_concept(q.concept)
        base = 3.0 if concept in weak else 1.0
        cm = concept_mastery.get(q.concept)
        if cm:
            base += (100 - cm.ema) / 40
        return base + _DIFF_ORDER.get(q.difficulty, 1) * 0.5 + random.random() * 0.2

    selected = sorted(candidates, key=score, reverse=True)[:count]
    selected.sort(key=lambda q: _DIFF_ORDER.get(q.difficulty, 1), reverse=True)
    return selected


def select_practice_quiz(
    db: Session,
    user_id: str,
    chapter_id: str,
    count: int,
) -> list[Question]:
    """Practice quiz: missed questions only; excludes ones already answered correctly."""
    all_qs = db.query(Question).filter(Question.chapter_id == chapter_id).all()
    if not all_qs:
        return []

    states = {
        r.question_id: r
        for r in db.query(UserQuestionState)
        .filter(UserQuestionState.user_id == user_id, UserQuestionState.chapter_id == chapter_id)
        .all()
    }

    missed: list[tuple[Question, float]] = []
    unseen: list[Question] = []

    for q in all_qs:
        row = states.get(q.id)
        if row is None:
            unseen.append(q)
        elif row.last_correct is True:
            continue
        else:
            weight = float(row.wrong_count or 0) + (2.0 if row.retired else 0.0)
            missed.append((q, weight))

    if missed:
        missed.sort(key=lambda t: t[1], reverse=True)
        pool = [q for q, _ in missed]
    else:
        pool = unseen

    if not pool:
        return []

    selected = pool[:count]
    random.shuffle(selected)
    selected.sort(key=lambda q: _DIFF_ORDER.get(q.difficulty, 1))
    return selected


def process_after_quiz(
    db: Session,
    user_id: str,
    chapter_id: str,
    questions: list[Question],
    graded: list[dict[str, Any]],
    *,
    mode: str = "adaptive",
) -> dict[str, Any]:
    """Update per-user question state; adaptive mode also replenishes the pool."""
    correct_by_qid = {g["question_id"]: g["correct"] for g in graded}
    retired = record_attempts(db, user_id, questions, correct_by_qid, mode=mode)
    replacements = 0
    if mode == "final" or mode == "adaptive":
        replacements = replenish_pool(db, user_id, chapter_id, retired)

    weak = list({g["concept"] for g in graded if not g["correct"]})
    return {
        "retired_count": len(retired),
        "replacements_generated": replacements,
        "weak_concepts_hit": weak,
        "mode": mode,
    }
