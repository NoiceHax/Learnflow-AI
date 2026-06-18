"""Tests for personalised learning-path generation (services/learning_path.py).

Covers the three behaviours that make two students' paths differ:
  * topological ordering (prerequisites always precede dependents)
  * prerequisite-gated locking + single in_progress focus
  * weak unlocked chapters bubbling to the front

Plus a regression guard that a malformed *cyclic* prerequisite chain does not
hang the topo sort (the shared `guard` set terminates the recursion).
"""
from __future__ import annotations

from app.models import Chapter, LearningPathItem, Subject
from app.services import learning_path as LP
from app.services.mastery import upsert_mastery


def _positions(items):
    return {i.chapter_id: i.position for i in items}


def _by_chapter(items):
    return {i.chapter_id: i for i in items}


def test_topo_order_places_prerequisites_first(chapters):
    ordered = LP._topo_order(list(chapters.values()))
    order = [c.slug for c in ordered]
    assert order.index("vectors") < order.index("electrostatics")
    assert order.index("electrostatics") < order.index("current-electricity")


def test_topo_order_survives_cycle_without_hanging():
    # Build a transient A -> B -> A cycle. _topo_order is pure (no DB).
    a = Chapter(id="a", subject_id="s", chapter_name="A", slug="a", order_index=0)
    b = Chapter(id="b", subject_id="s", chapter_name="B", slug="b", order_index=1)
    a.prerequisite_id = "b"
    b.prerequisite_id = "a"
    ordered = LP._topo_order([a, b])
    # Must return (not hang) and include every chapter exactly once.
    assert {c.id for c in ordered} == {"a", "b"}
    assert len(ordered) == 2


def test_no_mastery_data_leaves_everything_unlocked(db, chapters, user):
    # Design choice: an unseen prerequisite defaults to 100% mastery, so a brand
    # new student is never locked out — the first chapter is the focus.
    items = LP.generate(db, user.id)
    by = _by_chapter(items)

    assert by[chapters["vectors"].id].status == "in_progress"
    assert by[chapters["electrostatics"].id].status != "locked"
    assert by[chapters["current"].id].status != "locked"


def test_generate_locks_chapter_when_prerequisite_is_failing(db, chapters, user):
    # vectors attempted but weak (<60) -> electrostatics is locked behind it.
    upsert_mastery(db, user.id, chapters["vectors"], 30.0)
    db.flush()

    by = _by_chapter(LP.generate(db, user.id))
    assert by[chapters["electrostatics"].id].status == "locked"


def test_generate_unlocks_next_when_prerequisite_mastered(db, chapters, user):
    # Master vectors (>=80) -> electrostatics becomes the focus.
    upsert_mastery(db, user.id, chapters["vectors"], 90.0)
    db.flush()

    items = LP.generate(db, user.id)
    by = _by_chapter(items)

    assert by[chapters["vectors"].id].status == "mastered"
    assert by[chapters["electrostatics"].id].status == "in_progress"


def test_generate_bubbles_weak_unlocked_chapter_to_front(db, chapters, user):
    # vectors mastered (unlocks electrostatics) but electrostatics is weak (<60).
    upsert_mastery(db, user.id, chapters["vectors"], 95.0)
    upsert_mastery(db, user.id, chapters["electrostatics"], 30.0)
    db.flush()

    items = LP.generate(db, user.id)
    by = _by_chapter(items)
    pos = _positions(items)

    weak_item = by[chapters["electrostatics"].id]
    assert weak_item.is_weak is True
    assert weak_item.status == "in_progress"
    # The weak unlocked chapter is surfaced ahead of the mastered one.
    assert pos[chapters["electrostatics"].id] < pos[chapters["vectors"].id]


def test_generate_is_idempotent_one_row_per_chapter(db, chapters, user):
    LP.generate(db, user.id)
    LP.generate(db, user.id)  # regenerating must not duplicate rows
    rows = db.query(LearningPathItem).filter(LearningPathItem.user_id == user.id).all()
    assert len(rows) == len(chapters)


def test_two_students_get_different_paths(db, chapters):
    from app.models import User

    weak_student = User(name="A", email="a@x.com", password_hash="x")
    strong_student = User(name="B", email="b@x.com", password_hash="x")
    db.add_all([weak_student, strong_student])
    db.flush()

    # Weak student is failing vectors (locks electrostatics); strong student
    # has mastered it (unlocks electrostatics as the focus).
    upsert_mastery(db, weak_student.id, chapters["vectors"], 25.0)
    upsert_mastery(db, strong_student.id, chapters["vectors"], 92.0)
    db.flush()

    weak_items = _by_chapter(LP.generate(db, weak_student.id))
    strong_items = _by_chapter(LP.generate(db, strong_student.id))

    assert weak_items[chapters["electrostatics"].id].status == "locked"
    assert strong_items[chapters["electrostatics"].id].status == "in_progress"
