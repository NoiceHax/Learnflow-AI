"""Seed runner: loads the JEE catalog, question bank and lessons.

Idempotent: it clears existing content (and any progress that references it)
and rebuilds from the data modules. Run with:  python -m app.seed
"""
import random

from sqlalchemy.orm import Session

from ..database import Base, SessionLocal, engine
from ..models import (
    Assessment,
    Chapter,
    LearningPathItem,
    Lesson,
    Mastery,
    Question,
    QuizAttempt,
    Subject,
)
from .data_catalog import CATALOG
from .data_lessons_inorganic import LESSONS as L_INORG
from .data_lessons_math import LESSONS as L_MATH
from .data_lessons_organic import LESSONS as L_ORG
from .data_lessons_physics import LESSONS as L_PHY
from .data_q_inorganic import QUESTIONS as Q_INORG
from .data_q_math import QUESTIONS as Q_MATH
from .data_q_organic import QUESTIONS as Q_ORG
from .data_q_physics import QUESTIONS as Q_PHY

ALL_QUESTIONS = Q_PHY + Q_MATH + Q_ORG + Q_INORG
ALL_LESSONS = L_PHY + L_MATH + L_ORG + L_INORG


def _reset_content(db: Session) -> None:
    # Delete in FK-safe order. Progress tables are cleared because chapter ids
    # are regenerated on each reseed.
    for model in (Lesson, Question, LearningPathItem, Mastery, QuizAttempt, Assessment, Chapter, Subject):
        db.query(model).delete()
    db.commit()


def _seed_catalog(db: Session) -> dict[str, Chapter]:
    chapters: dict[str, Chapter] = {}
    prereqs: dict[str, str | None] = {}

    for s_idx, subj in enumerate(CATALOG):
        subject = Subject(name=subj["name"], slug=subj["slug"], icon=subj["icon"], order_index=s_idx)
        db.add(subject)
        db.flush()
        for c_idx, (name, slug, prereq_slug, weight, desc) in enumerate(subj["chapters"]):
            chapter = Chapter(
                subject_id=subject.id,
                chapter_name=name,
                slug=slug,
                order_index=c_idx,
                jee_weightage=weight,
                description=desc,
            )
            db.add(chapter)
            db.flush()
            chapters[slug] = chapter
            prereqs[slug] = prereq_slug

    for slug, prereq_slug in prereqs.items():
        if prereq_slug:
            if prereq_slug not in chapters:
                raise ValueError(f"Chapter '{slug}' references unknown prerequisite '{prereq_slug}'")
            chapters[slug].prerequisite_id = chapters[prereq_slug].id
    db.commit()
    return chapters


def _shuffle_options(texts: list[str], correct, qtype: str, seed: str):
    """Randomise option order (so the answer isn't always 'A') and remap indices.

    Deterministic per-question seed keeps it stable across reseeds.
    """
    rng = random.Random(seed)
    order = list(range(len(texts)))
    rng.shuffle(order)
    new_texts = [texts[i] for i in order]
    new_pos = {old: new for new, old in enumerate(order)}
    if qtype == "single_correct":
        new_correct = new_pos[int(correct)]
    elif qtype == "multiple_correct":
        new_correct = sorted(new_pos[int(c)] for c in correct)
    else:
        new_correct = correct
    return new_texts, new_correct


def _seed_questions(db: Session, chapters: dict[str, Chapter]) -> int:
    count = 0
    for q in ALL_QUESTIONS:
        slug = q["chapter"]
        if slug not in chapters:
            raise ValueError(f"Question references unknown chapter slug '{slug}'")
        chapter = chapters[slug]
        options = None
        correct = q["correct"]
        if q.get("options") is not None:
            texts, correct = _shuffle_options(q["options"], correct, q["type"], q["prompt"])
            options = [{"id": str(i), "text": text} for i, text in enumerate(texts)]
        db.add(
            Question(
                subject=chapter.subject.name,
                chapter=chapter.chapter_name,
                chapter_id=chapter.id,
                difficulty=q["difficulty"],
                concept=q["concept"],
                jee_weightage=chapter.jee_weightage,
                type=q["type"],
                prompt=q["prompt"],
                options=options,
                correct_answer=correct,
                tolerance=q.get("tolerance"),
                unit=q.get("unit"),
                solution=q.get("solution", ""),
                is_pyq=q.get("is_pyq", False),
                pyq_year=q.get("pyq_year"),
                pyq_exam=q.get("pyq_exam"),
            )
        )
        count += 1
    db.commit()
    return count


def _seed_lessons(db: Session, chapters: dict[str, Chapter]) -> int:
    count = 0
    for lesson in ALL_LESSONS:
        slug = lesson["chapter"]
        if slug not in chapters:
            raise ValueError(f"Lesson references unknown chapter slug '{slug}'")
        chapter = chapters[slug]
        content = {k: v for k, v in lesson.items() if k != "chapter"}
        db.add(Lesson(chapter_id=chapter.id, chapter=chapter.chapter_name, content=content, generated_by_ai=False))
        count += 1
    db.commit()
    return count


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _reset_content(db)
        chapters = _seed_catalog(db)
        n_q = _seed_questions(db, chapters)
        n_l = _seed_lessons(db, chapters)
        n_subjects = len(CATALOG)
        print("Astra database seeded:")
        print(f"  subjects : {n_subjects}")
        print(f"  chapters : {len(chapters)}")
        print(f"  questions: {n_q}")
        print(f"  lessons  : {n_l}")
    finally:
        db.close()


def run_if_empty() -> None:
    """Seed only when the catalog is empty (safe for Render release command)."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Subject).count() > 0:
            print("Database already seeded. Skipping.")
            return
        print("Empty database — seeding catalog, questions, and lessons…")
    finally:
        db.close()
    run()


if __name__ == "__main__":
    run()
