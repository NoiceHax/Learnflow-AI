"""Pre-generate AI backup questions so quiz loads stay fast (DB-only, no live LLM).

Run after seeding:
  python -m app.seed --pregenerate-backups

Uses CHAPTER_BACKUP_MULTIPLIER from settings (default 2): per chapter, targets
``multiplier × seeded_question_count`` AI-tagged questions in the bank.
"""
from __future__ import annotations

import logging
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from ..config import nvidia_api_keys_list, nvidia_question_model_chain, settings
from ..database import SessionLocal
from ..models import Chapter, Question
from ..services.llm import ai_enabled
from ..services.question_gen import AI_CONCEPT_PREFIX, generate_for_chapter

logger = logging.getLogger(__name__)


def _safe_console(text: str) -> str:
    """Avoid UnicodeEncodeError on Windows cp1252 terminals."""
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        text.encode(enc)
        return text
    except UnicodeEncodeError:
        return text.encode(enc, errors="replace").decode(enc)


def _progress(msg: str) -> None:
    """Immediate stdout progress (seed CLI may not show logger output)."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {_safe_console(msg)}", flush=True)


def _is_seed_question(q: Question) -> bool:
    return not (q.concept or "").startswith(AI_CONCEPT_PREFIX)


def _clean_concept(concept: str) -> str:
    return concept.replace(AI_CONCEPT_PREFIX, "").strip()


def pregenerate_chapter_to_target(
    db: Session,
    chapter: Chapter,
    target_ai: int,
    *,
    chapter_index: int | None = None,
    chapter_total: int | None = None,
) -> int:
    """Generate AI questions until the chapter has ``target_ai`` AI-tagged rows."""
    if target_ai <= 0:
        return 0

    pool = db.query(Question).filter(Question.chapter_id == chapter.id).all()
    seed_qs = [q for q in pool if _is_seed_question(q)]
    ai_qs = [q for q in pool if not _is_seed_question(q)]

    if not seed_qs:
        _progress(f"SKIP {chapter.slug}: no seed questions")
        logger.warning("Chapter %s has no seed questions; skipping", chapter.slug)
        return 0

    if len(ai_qs) >= target_ai:
        prefix = f"[{chapter_index}/{chapter_total}] " if chapter_index else ""
        _progress(f"{prefix}{chapter.slug}: already at {len(ai_qs)}/{target_ai} AI questions")
        logger.info(
            "Chapter %s: already has %d AI backups (target %d)",
            chapter.slug,
            len(ai_qs),
            target_ai,
        )
        return 0

    need = target_ai - len(ai_qs)
    prefix = f"[{chapter_index}/{chapter_total}] " if chapter_index else ""
    _progress(f"{prefix}{chapter.slug}: need {need} AI question(s) (have {len(ai_qs)}/{target_ai})")

    by_difficulty: dict[str, list[Question]] = defaultdict(list)
    for q in seed_qs:
        by_difficulty[q.difficulty].append(q)

    diff_counts = Counter({d: len(qs) for d, qs in by_difficulty.items()})
    total_seed = sum(diff_counts.values())
    diffs_ordered = sorted(diff_counts.items(), key=lambda x: -x[1])
    planned: dict[str, int] = {}
    left = need
    for i, (diff, seed_count) in enumerate(diffs_ordered):
        if i == len(diffs_ordered) - 1:
            planned[diff] = left
        else:
            batch = max(1, round(need * seed_count / total_seed))
            batch = min(batch, left)
            planned[diff] = batch
            left -= batch

    plan_str = ", ".join(f"{d}={n}" for d, n in planned.items() if n > 0)
    _progress(f"  plan for {chapter.slug}: {plan_str}")

    created = 0
    for diff, batch in planned.items():
        if batch <= 0:
            continue
        concepts = list({_clean_concept(q.concept) for q in by_difficulty[diff]})
        exclude_ids = {q.id for q in pool}

        for q_num in range(1, batch + 1):
            overall = len(ai_qs) + created
            _progress(
                f"  {chapter.slug} ({diff}) question {q_num}/{batch} "
                f"[overall {overall + 1}/{target_ai}] - calling LLM..."
            )
            started = time.perf_counter()
            fresh = generate_for_chapter(
                db,
                chapter,
                count=1,
                difficulty=diff,
                concepts=concepts,
                allow_live_api=True,
                exclude_question_ids=exclude_ids,
            )
            elapsed = time.perf_counter() - started
            if not fresh:
                _progress(
                    f"  {chapter.slug} ({diff}): FAILED after {elapsed:.0f}s "
                    f"(saved {created}/{need} this chapter)"
                )
                logger.warning(
                    "Chapter %s (%s): generation stalled after %d/%d",
                    chapter.slug,
                    diff,
                    created,
                    need,
                )
                break
            created += len(fresh)
            exclude_ids.update(q.id for q in fresh)
            db.flush()
            pool = db.query(Question).filter(Question.chapter_id == chapter.id).all()
            preview = fresh[0].prompt[:70].replace("\n", " ")
            _progress(
                f"  {chapter.slug} ({diff}): saved in {elapsed:.0f}s "
                f"({len(ai_qs) + created}/{target_ai}) - {preview}..."
            )

    _progress(f"{prefix}{chapter.slug}: finished +{created} (now {len(ai_qs) + created}/{target_ai} AI)")
    logger.info(
        "Chapter %s: +%d AI backup(s) (seed=%d, ai now≈%d, target=%d)",
        chapter.slug,
        created,
        len(seed_qs),
        len(ai_qs) + created,
        target_ai,
    )
    return created


def pregenerate_chapter_backups(
    db: Session,
    *,
    multiplier: float | None = None,
    chapter_slug: str | None = None,
) -> dict[str, int]:
    """Generate AI backup questions for chapters. Returns {chapter_slug: created_count}."""
    if not ai_enabled():
        raise RuntimeError("AI is disabled or NVIDIA keys missing. Set USE_AI=true and NVIDIA_API_KEYS.")

    mult = multiplier if multiplier is not None else settings.chapter_backup_multiplier
    if mult <= 0:
        return {}

    query = db.query(Chapter).order_by(Chapter.order_index)
    if chapter_slug:
        query = query.filter(Chapter.slug == chapter_slug)
    chapters = query.all()
    if chapter_slug and not chapters:
        raise ValueError(f"Unknown chapter slug: {chapter_slug}")

    created_by_slug: dict[str, int] = {}

    for chapter in chapters:
        pool = db.query(Question).filter(Question.chapter_id == chapter.id).all()
        seed_qs = [q for q in pool if _is_seed_question(q)]
        ai_qs = [q for q in pool if not _is_seed_question(q)]

        if not seed_qs:
            logger.warning("Chapter %s has no seed questions; skipping", chapter.slug)
            continue

        target_ai = max(1, int(round(len(seed_qs) * mult)))
        if len(ai_qs) >= target_ai:
            logger.info(
                "Chapter %s: already has %d AI backups (target %d)",
                chapter.slug,
                len(ai_qs),
                target_ai,
            )
            created_by_slug[chapter.slug] = 0
            continue

        created = pregenerate_chapter_to_target(db, chapter, target_ai)
        created_by_slug[chapter.slug] = created

    db.commit()
    return created_by_slug


def pregenerate_pilot_chapters(
    db: Session,
    *,
    target_per_chapter: int | None = None,
) -> dict[str, int]:
    """Fill AI bank for pilot syllabus chapters only (for multi-user testing)."""
    if not ai_enabled():
        raise RuntimeError("AI is disabled or NVIDIA keys missing. Set USE_AI=true and NVIDIA_API_KEYS.")

    from ..services.pilot import pilot_chapters

    target = target_per_chapter if target_per_chapter is not None else settings.pilot_ai_questions_per_chapter
    created_by_slug: dict[str, int] = {}
    chapters = pilot_chapters(db)
    if not chapters:
        logger.warning("No pilot chapters resolved")
        return {}

    print(f"Pilot pregenerate: {len(chapters)} chapter(s), {target} AI questions each (~{len(chapters) * target} total).")
    _progress(f"API keys: {len(nvidia_api_keys_list())}, models: {', '.join(nvidia_question_model_chain())}")
    rpm = settings.nvidia_rpm_per_key
    keys = len(nvidia_api_keys_list())
    _progress(
        f"Rate limit: {rpm:.0f} RPM/key x {keys} keys (~{rpm * keys:.0f} RPM max). "
        "Each question is one LLM call (~30-90s)."
    )

    for idx, chapter in enumerate(chapters, start=1):
        created_by_slug[chapter.slug] = pregenerate_chapter_to_target(
            db,
            chapter,
            target,
            chapter_index=idx,
            chapter_total=len(chapters),
        )

    db.commit()
    return created_by_slug


def run_pregenerate(*, multiplier: float | None = None, chapter_slug: str | None = None) -> None:
    db = SessionLocal()
    try:
        totals = pregenerate_chapter_backups(db, multiplier=multiplier, chapter_slug=chapter_slug)
        total = sum(totals.values())
        done = sum(1 for n in totals.values() if n > 0)
        print(f"Backup generation complete: {total} new AI question(s) across {done} chapter(s).")
        for slug, n in sorted(totals.items()):
            if n:
                print(f"  {slug}: +{n}")
    finally:
        db.close()


def run_pregenerate_pilot(*, target_per_chapter: int | None = None) -> None:
    db = SessionLocal()
    try:
        totals = pregenerate_pilot_chapters(db, target_per_chapter=target_per_chapter)
        total = sum(totals.values())
        print(f"Pilot backup generation complete: {total} new AI question(s) across {len(totals)} pilot chapter(s).")
        for slug, n in sorted(totals.items()):
            print(f"  {slug}: +{n}")
    finally:
        db.close()
