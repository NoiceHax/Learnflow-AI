"""Personalised learning-path generation.

Orders every chapter respecting prerequisites (topological), then assigns a
status from the student's mastery:

  mastered   -> mastery >= 80 (can be skipped)
  available  -> prerequisite satisfied, not yet mastered
  in_progress-> the first available chapter (the student's current focus)
  locked     -> prerequisite not yet satisfied

Weak chapters (mastery < 60) are flagged so the UI/lessons can add extra
practice. Two students with different assessments therefore get genuinely
different paths.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Chapter, LearningPathItem, Mastery
from .mastery import MASTER_THRESHOLD, PASS_THRESHOLD, WEAK_THRESHOLD


def _topo_order(chapters: list[Chapter]) -> list[Chapter]:
    by_id = {c.id: c for c in chapters}
    ordered: list[Chapter] = []
    placed: set[str] = set()
    # Stable base order: subject then chapter order.
    base = sorted(
        chapters,
        key=lambda c: (c.subject.order_index if c.subject else 0, c.order_index),
    )

    def place(ch: Chapter, guard: set[str]):
        if ch.id in placed or ch.id in guard:
            return
        guard.add(ch.id)
        prereq = by_id.get(ch.prerequisite_id) if ch.prerequisite_id else None
        if prereq is not None:
            place(prereq, guard)
        if ch.id not in placed:
            ordered.append(ch)
            placed.add(ch.id)

    for ch in base:
        place(ch, set())
    return ordered


def generate(db: Session, user_id: str) -> list[LearningPathItem]:
    chapters = db.query(Chapter).all()
    mastery_rows = {
        m.chapter_id: m.mastery_score
        for m in db.query(Mastery).filter(Mastery.user_id == user_id).all()
    }
    ordered = _topo_order(chapters)

    db.query(LearningPathItem).filter(LearningPathItem.user_id == user_id).delete()

    first_focus_assigned = False
    items: list[LearningPathItem] = []
    for pos, ch in enumerate(ordered):
        mastery = mastery_rows.get(ch.id, 0.0)
        prereq_mastery = mastery_rows.get(ch.prerequisite_id, 100.0) if ch.prerequisite_id else 100.0
        is_weak = mastery < WEAK_THRESHOLD

        if mastery >= MASTER_THRESHOLD:
            status = "mastered"
            reason = "Strong. You can skip ahead."
        elif prereq_mastery < PASS_THRESHOLD:
            status = "locked"
            reason = "Locked until the prerequisite is cleared."
        elif not first_focus_assigned:
            status = "in_progress"
            first_focus_assigned = True
            reason = (
                "Focus here next. Needs work." if is_weak else "Continue building on your strengths."
            )
        else:
            status = "available"
            reason = "Extra practice recommended." if is_weak else "Ready when you are."

        item = LearningPathItem(
            user_id=user_id,
            chapter_id=ch.id,
            position=pos,
            status=status,
            is_weak=is_weak,
            reason=reason,
        )
        db.add(item)
        items.append(item)

    db.flush()
    _bubble_weak_to_front(db, user_id, items, mastery_rows)
    db.commit()
    return items


def _bubble_weak_to_front(
    db: Session,
    user_id: str,
    items: list[LearningPathItem],
    mastery_rows: dict[str, float],
) -> None:
    """Dynamic syllabus: weak unlocked chapters move to the front of the path."""
    weak_unlocked = [
        i for i in items if i.is_weak and i.status in ("in_progress", "available", "mastered")
    ]
    if not weak_unlocked:
        return

    weak_unlocked.sort(key=lambda i: mastery_rows.get(i.chapter_id, 0.0))
    prev_focus = next((i for i in items if i.status == "in_progress"), None)
    others = [i for i in items if i not in weak_unlocked]
    locked = [i for i in others if i.status == "locked"]
    unlocked_rest = [i for i in others if i.status != "locked"]

    reordered = weak_unlocked + unlocked_rest + locked
    focus = weak_unlocked[0]
    if prev_focus and prev_focus is not focus:
        prev_focus.status = "available"
    focus.status = "in_progress"
    focus.reason = "Syllabus adjusted. Weak area surfaced for practice."

    for pos, item in enumerate(reordered):
        item.position = pos
