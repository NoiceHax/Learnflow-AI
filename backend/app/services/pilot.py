"""Pilot syllabus: first wave of content for multi-user testing (DB-backed AI bank)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..config import settings
from ..models import Chapter, Subject

# First 3 chapters per subject — matches catalog order_index 0..2.
DEFAULT_PILOT_SLUGS: tuple[str, ...] = (
    "mechanics",
    "waves",
    "thermodynamics",
    "algebra",
    "trigonometry",
    "coordinate-geometry",
    "goc",
    "hydrocarbons",
    "haloalkanes",
    "chemical-bonding",
    "coordination-compounds",
    "p-block",
)


def pilot_mode_enabled() -> bool:
    return settings.pilot_mode


def _configured_slugs() -> list[str]:
    if settings.pilot_chapter_slugs.strip():
        return [s.strip() for s in settings.pilot_chapter_slugs.split(",") if s.strip()]
    if DEFAULT_PILOT_SLUGS:
        return list(DEFAULT_PILOT_SLUGS)
    return []


def pilot_chapters(db: Session) -> list[Chapter]:
    """Chapters included in the pilot (lessons + quizzes + AI pregenerate)."""
    if not pilot_mode_enabled():
        return db.query(Chapter).order_by(Chapter.order_index).all()

    slugs = _configured_slugs()
    if slugs:
        by_slug = {c.slug: c for c in db.query(Chapter).all()}
        return [by_slug[s] for s in slugs if s in by_slug]

    per = max(1, settings.pilot_chapters_per_subject)
    subjects = db.query(Subject).order_by(Subject.order_index).all()
    out: list[Chapter] = []
    for subj in subjects:
        rows = (
            db.query(Chapter)
            .filter(Chapter.subject_id == subj.id)
            .order_by(Chapter.order_index)
            .limit(per)
            .all()
        )
        out.extend(rows)
    return out


def pilot_chapter_ids(db: Session) -> set[str]:
    return {c.id for c in pilot_chapters(db)}


def is_pilot_chapter(db: Session, chapter_id: str) -> bool:
    if not pilot_mode_enabled():
        return True
    return chapter_id in pilot_chapter_ids(db)


def assert_pilot_chapter_access(db: Session, chapter_id: str) -> None:
    from fastapi import HTTPException

    if pilot_mode_enabled() and chapter_id not in pilot_chapter_ids(db):
        raise HTTPException(
            403,
            "This chapter is not in the current pilot. Complete the available topics first.",
        )
