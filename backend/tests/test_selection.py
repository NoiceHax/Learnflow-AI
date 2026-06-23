"""Tests for quiz/assessment selection wiring (services/selection.py)."""
from __future__ import annotations

from app.models import ConceptMastery, Mastery
from app.services import selection as S
from app.services.mastery import upsert_mastery


def _populate(make_question, chapters, per_chapter=3):
    for ch in chapters.values():
        for i in range(per_chapter):
            make_question(ch, difficulty=["Easy", "Medium", "Advanced"][i % 3], correct_answer=0)


def test_assessment_picks_one_per_chapter_within_cap(db, chapters, make_question):
    _populate(make_question, chapters)
    picked = S.assessment_questions(db, user_id=None, per_subject_cap=5)
    # One subject, 3 chapters, cap 5 -> one question from each chapter.
    assert len(picked) == 3
    assert len({q.chapter_id for q in picked}) == 3


def test_assessment_respects_per_subject_cap(db, chapters, make_question):
    _populate(make_question, chapters)
    picked = S.assessment_questions(db, user_id=None, per_subject_cap=2)
    assert len(picked) == 2  # capped before the third chapter


def test_assessment_skips_chapters_with_only_retired_questions(db, chapters, user, make_question):
    _populate(make_question, chapters)
    # Retire every question in the vectors chapter for this user.
    from app.services.adaptive import record_attempts

    vectors_qs = [q for q in db.query(S.Question).filter_by(chapter_id=chapters["vectors"].id)]
    record_attempts(db, user.id, vectors_qs, {q.id: False for q in vectors_qs}, mode="final")
    db.flush()

    picked = S.assessment_questions(db, user_id=user.id, per_subject_cap=5)
    chapter_ids = {q.chapter_id for q in picked}
    assert chapters["vectors"].id not in chapter_ids
    assert len(picked) == 2


def test_assessment_empty_db_returns_empty(db, chapters):
    assert S.assessment_questions(db, user_id=None) == []


def test_chapter_questions_anonymous_returns_sorted_sample(db, chapters, make_question):
    ch = chapters["vectors"]
    for diff in ("Advanced", "Easy", "Medium", "Easy"):
        make_question(ch, difficulty=diff, correct_answer=0)

    picked = S.chapter_questions(db, ch.id, user_id=None, count=3)
    assert len(picked) == 3
    ranks = [S._DIFF_ORDER.get(q.difficulty, 1) for q in picked]
    assert ranks == sorted(ranks)  # easy-first ordering


def test_chapter_questions_empty_chapter_returns_empty(db, chapters):
    assert S.chapter_questions(db, chapters["vectors"].id, user_id=None) == []


def test_effective_mastery_prefers_chapter_row(db, chapters, user):
    ch = chapters["vectors"]
    upsert_mastery(db, user.id, ch, 67.0)
    db.flush()
    eff = S._effective_mastery(db, user.id, ch.id, {"Dot Product"}, {})
    assert eff == 67.0


def test_effective_mastery_falls_back_to_concept_average(db, chapters, user):
    ch = chapters["vectors"]
    cm = {
        "Dot Product": ConceptMastery(user_id=user.id, concept="Dot Product", ema=40.0),
        "Magnitude": ConceptMastery(user_id=user.id, concept="Magnitude", ema=60.0),
    }
    eff = S._effective_mastery(db, user.id, ch.id, {"Dot Product", "Magnitude"}, cm)
    assert eff == 50.0  # average of 40 and 60


def test_effective_mastery_defaults_to_zero_with_no_data(db, chapters, user):
    eff = S._effective_mastery(db, user.id, chapters["vectors"].id, set(), {})
    assert eff == 0.0
