"""Adaptive learning engine: retire missed questions, spawn similar replacements,
and reshape the syllabus after every quiz."""
from __future__ import annotations

import logging
import random
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from ..models import Chapter, ConceptMastery, Mastery, Question, Subject, UserQuestionState
from ..config import settings
from ..database import release_db_transaction
from .llm import ai_enabled, generate_questions
from .quiz_rules import accept_quiz_questions
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
    """DB-only replacement picks. Never calls the LLM (safe for quiz load)."""
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
    allow_live_api: bool = True,
) -> list[Question]:
    """Create same-difficulty replacement questions for retired items."""
    if not references:
        return []

    subject = db.get(Subject, chapter.subject_id)
    if subject is None:
        return []

    if user_id:
        from ..config import settings
        from .rate_limiter import limiter
        if limiter.is_rate_limited(
            user_id=user_id,
            action="question_gen",
            limit_per_minute=settings.rate_limit_question_gen_minute,
            limit_per_day=settings.rate_limit_question_gen_daily,
        ):
            logger.warning(
                "User %s is rate-limited for live question generation. Disallowing live API call for replacements.",
                user_id,
            )
            allow_live_api = False

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

        from .llm_cache import fetch_db_question_cache

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

        if ai_enabled() and allow_live_api:
            release_db_transaction(db)
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
    *,
    allow_live_api: bool = True,
) -> int:
    chapter = db.get(Chapter, chapter_id)
    if chapter is None or not retired_questions:
        return 0
    return len(
        generate_similar_replacements(
            db, chapter, retired_questions, user_id=user_id, allow_live_api=allow_live_api
        )
    )


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

    # AI off or chapter too small: recycle retired questions so quizzes never 404
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
    """Fresh final-quiz set from DB only on load — never blocks on live LLM (see submit replenish)."""
    from .question_gen import generate_for_chapter

    chapter = db.get(Chapter, chapter_id)
    if chapter is None:
        return []

    seen = seen_question_ids(db, user_id, chapter_id)
    retired = retired_ids(db, user_id)
    blocked = seen | retired

    weak = weak_concepts_for_user(db, user_id, chapter_id)
    diff = final_quiz_difficulty(effective_mastery)
    all_chapter_qs = db.query(Question).filter(Question.chapter_id == chapter_id).all()
    concepts = weak or list({_clean_concept(q.concept) for q in all_chapter_qs})
    if not concepts:
        concepts = [chapter.chapter_name]

    diff_rank = _DIFF_ORDER.get(diff, 1)
    pool = [q for q in all_chapter_qs if q.id not in blocked]
    harder = [q for q in pool if _DIFF_ORDER.get(q.difficulty, 1) >= diff_rank]
    candidates = harder or pool

    def score(q: Question) -> float:
        concept = _clean_concept(q.concept)
        base = 3.0 if concept in weak else 1.0
        cm = concept_mastery.get(q.concept)
        if cm:
            base += (100 - cm.ema) / 40
        return base + _DIFF_ORDER.get(q.difficulty, 1) * 0.5 + random.random() * 0.2

    selected: list[Question] = []
    seen_ids: set[str] = set()
    if candidates:
        picked = sorted(candidates, key=score, reverse=True)[:count]
        picked.sort(key=lambda q: _DIFF_ORDER.get(q.difficulty, 1), reverse=True)
        selected = picked
        seen_ids = {q.id for q in selected}

    # Unseen AI questions already in DB (from prior submit replenishment) — no live API.
    if len(selected) < count and ai_enabled():
        need = count - len(selected)
        cached = generate_for_chapter(
            db,
            chapter,
            count=need,
            difficulty=diff,
            concepts=concepts,
            user_id=user_id,
            exclude_question_ids=blocked | seen_ids,
            allow_live_api=False,
        )
        for q in cached:
            if q.id not in seen_ids and q.id not in blocked:
                selected.append(q)
                seen_ids.add(q.id)
            if len(selected) >= count:
                break

    # Any remaining unseen questions (e.g. easier seed bank) before giving up.
    if len(selected) < count:
        remainder = [q for q in pool if q.id not in seen_ids]
        random.shuffle(remainder)
        for q in remainder:
            selected.append(q)
            seen_ids.add(q.id)
            if len(selected) >= count:
                break

    min_q = settings.min_quiz_questions
    if 0 < len(selected) < min_q and ai_enabled():
        need = min_q - len(selected)
        cached = generate_for_chapter(
            db,
            chapter,
            count=need,
            difficulty=diff,
            concepts=concepts,
            user_id=user_id,
            exclude_question_ids=blocked | seen_ids,
            allow_live_api=False,
        )
        for q in cached:
            if q.id not in seen_ids and q.id not in blocked:
                selected.append(q)
                seen_ids.add(q.id)
            if len(selected) >= min_q:
                break

    if selected:
        return accept_quiz_questions(selected[:count])

    logger.warning(
        "Final quiz pool empty after DB selection: user=%s chapter=%s blocked=%d",
        user_id,
        chapter_id,
        len(blocked),
    )
    return []


def _chapter_mastery_ema(db: Session, user_id: str, chapter_id: str) -> float:
    row = (
        db.query(Mastery)
        .filter(Mastery.user_id == user_id, Mastery.chapter_id == chapter_id)
        .one_or_none()
    )
    if row is not None:
        return float(row.mastery_score)
    rows = (
        db.query(ConceptMastery)
        .filter(ConceptMastery.user_id == user_id, ConceptMastery.chapter_id == chapter_id)
        .all()
    )
    return sum(r.ema for r in rows) / len(rows) if rows else 50.0


def cleared_question_ids(db: Session, user_id: str, chapter_id: str) -> set[str]:
    """Questions the user answered correctly — excluded from future practice rounds."""
    return {
        r.question_id
        for r in db.query(UserQuestionState)
        .filter(
            UserQuestionState.user_id == user_id,
            UserQuestionState.chapter_id == chapter_id,
            UserQuestionState.last_correct.is_(True),
        )
        .all()
    }


def top_up_practice_pool(
    db: Session,
    user_id: str,
    chapter_id: str,
    need: int,
    *,
    allow_live_api: bool = True,
    exclude_ids: set[str] | None = None,
) -> list[Question]:
    """Generate fresh AI questions when the practice pool is smaller than the target size."""
    if need < 1:
        return []
    chapter = db.get(Chapter, chapter_id)
    if chapter is None:
        return []

    weak = weak_concepts_for_user(db, user_id, chapter_id)
    concepts = weak or [chapter.chapter_name]
    diff = target_difficulty(_chapter_mastery_ema(db, user_id, chapter_id))

    from .question_gen import generate_for_chapter

    blocked = cleared_question_ids(db, user_id, chapter_id) | (exclude_ids or set())

    fresh = generate_for_chapter(
        db,
        chapter,
        count=need,
        difficulty=diff,
        concepts=concepts,
        user_id=user_id,
        exclude_question_ids=blocked,
        allow_live_api=allow_live_api,
        fresh_for_practice=True,
    )
    if fresh:
        logger.info(
            "Practice pool top-up: user=%s chapter=%s added=%d live=%s",
            user_id,
            chapter.slug,
            len(fresh),
            allow_live_api,
        )
    return fresh


def select_practice_quiz(
    db: Session,
    user_id: str,
    chapter_id: str,
    count: int,
) -> list[Question]:
    """Infinite practice: mostly fresh AI; at most one prior miss for reinforcement."""
    chapter = db.get(Chapter, chapter_id)
    if chapter is None:
        return []

    all_qs = db.query(Question).filter(Question.chapter_id == chapter_id).all()
    states = {
        r.question_id: r
        for r in db.query(UserQuestionState)
        .filter(UserQuestionState.user_id == user_id, UserQuestionState.chapter_id == chapter_id)
        .all()
    }
    cleared = cleared_question_ids(db, user_id, chapter_id)
    max_reinforce = max(0, settings.practice_reinforce_wrong)

    selected: list[Question] = []
    selected_ids: set[str] = set()

    # Optional: one recent miss for spaced reinforcement (not the whole stale pile).
    wrong: list[tuple[Question, float]] = []
    for q in all_qs:
        if q.id in cleared:
            continue
        row = states.get(q.id)
        if row and row.last_correct is not True and (row.wrong_count or 0) > 0:
            wrong.append((q, float(row.wrong_count or 0) + (1.0 if row.retired else 0.0)))
    wrong.sort(key=lambda t: t[1], reverse=True)
    for q, _ in wrong[:max_reinforce]:
        selected.append(q)
        selected_ids.add(q.id)

    # Unseen seeded / AI rows the user has never attempted.
    unseen = [q for q in all_qs if q.id not in states and q.id not in cleared]
    random.shuffle(unseen)
    for q in unseen:
        if len(selected) >= count:
            break
        if q.id not in selected_ids:
            selected.append(q)
            selected_ids.add(q.id)

    # Top up from DB backup bank; live API only if PRACTICE_LIVE_API_ON_LOAD=true.
    if len(selected) < count and ai_enabled():
        need = count - len(selected)
        extra = top_up_practice_pool(
            db,
            user_id,
            chapter_id,
            need,
            allow_live_api=settings.practice_live_api_on_load,
            exclude_ids=selected_ids | cleared,
        )
        for q in extra:
            if q.id not in selected_ids:
                selected.append(q)
                selected_ids.add(q.id)
            if len(selected) >= count:
                break

    min_q = settings.min_quiz_questions
    if 0 < len(selected) < min_q and ai_enabled():
        extra = top_up_practice_pool(
            db,
            user_id,
            chapter_id,
            min_q - len(selected),
            allow_live_api=settings.practice_live_api_on_load,
            exclude_ids=selected_ids | cleared,
        )
        for q in extra:
            if q.id not in selected_ids:
                selected.append(q)
                selected_ids.add(q.id)
            if len(selected) >= min_q:
                break

    if selected and len(selected) >= min_q:
        random.shuffle(selected)
        selected.sort(key=lambda q: _DIFF_ORDER.get(q.difficulty, 1))
        return selected[:count]

    if not all_qs and ai_enabled():
        fresh = top_up_practice_pool(
            db,
            user_id,
            chapter_id,
            max(count, min_q),
            allow_live_api=settings.practice_live_api_on_load,
            exclude_ids=cleared,
        )
        return accept_quiz_questions(fresh[:count])

    return []


def process_after_quiz(
    db: Session,
    user_id: str,
    chapter_id: str,
    questions: list[Question],
    graded: list[dict[str, Any]],
    *,
    mode: str = "adaptive",
) -> dict[str, Any]:
    """Update per-user question state; replenish pool after misses (final) or clears (practice)."""
    correct_by_qid = {g["question_id"]: g["correct"] for g in graded}
    retired = record_attempts(db, user_id, questions, correct_by_qid, mode=mode)
    replacements = 0
    # Never block submit on live LLM — use DB cache + pool; run pregenerate-backups to fill the bank.
    live_on_submit = False
    if mode == "practice":
        cleared = [q for q in questions if correct_by_qid.get(q.id)]
        if cleared:
            replacements = replenish_pool(
                db, user_id, chapter_id, cleared, allow_live_api=live_on_submit
            )
    elif mode == "final" or mode == "adaptive":
        replacements = replenish_pool(
            db, user_id, chapter_id, retired, allow_live_api=live_on_submit
        )

    weak = list({g["concept"] for g in graded if not g["correct"]})
    return {
        "retired_count": len(retired),
        "replacements_generated": replacements,
        "weak_concepts_hit": weak,
        "mode": mode,
    }
