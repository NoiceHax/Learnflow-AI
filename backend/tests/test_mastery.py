"""Tests for adaptive mastery scoring (services/mastery.py).

Mastery is an exponential moving average (alpha=0.45) of quiz performance. The
80/60 thresholds gate the entire learning path, so the EMA arithmetic and the
upsert/concept bookkeeping need to be pinned down.
"""
from __future__ import annotations

import pytest

from app.models import ConceptMastery, Mastery, Question
from app.services import mastery as M


# --- blend (the EMA primitive) ---------------------------------------------
def test_blend_first_sample_takes_value_directly():
    # No prior attempts -> the new score is the EMA.
    assert M.blend(0.0, 73.0, attempts=0) == 73.0


def test_blend_weights_recent_more_via_alpha():
    # 0.55*old + 0.45*new
    assert M.blend(40.0, 80.0, attempts=1) == pytest.approx(58.0)
    assert M.blend(100.0, 0.0, attempts=3) == pytest.approx(55.0)


def test_thresholds_match_spec():
    assert M.MASTER_THRESHOLD == 80.0
    assert M.PASS_THRESHOLD == 60.0
    assert M.WEAK_THRESHOLD == 60.0


# --- upsert_mastery ---------------------------------------------------------
def test_upsert_creates_then_blends(db, chapters, user):
    ch = chapters["vectors"]

    row = M.upsert_mastery(db, user.id, ch, 40.0)
    db.flush()
    assert row.mastery_score == 40.0
    assert row.attempts == 1
    assert row.chapter == "Vectors"
    assert row.subject == "Physics"

    row2 = M.upsert_mastery(db, user.id, ch, 80.0)
    db.flush()
    assert row2.id == row.id  # same row, not a duplicate
    assert row2.mastery_score == pytest.approx(58.0)  # blend(40, 80)
    assert row2.attempts == 2


def test_mark_chapter_mastered_pins_to_100(db, chapters, user):
    ch = chapters["electrostatics"]
    M.upsert_mastery(db, user.id, ch, 30.0)
    db.flush()

    row = M.mark_chapter_mastered(db, user.id, ch)
    db.flush()
    assert row.mastery_score == 100.0


def test_seed_mastery_from_assessment_keys_by_slug(db, chapters, user):
    M.seed_mastery_from_assessment(
        db, user.id, {"vectors": 72.0, "electrostatics": 35.0, "nonexistent-slug": 99.0}
    )
    db.flush()
    rows = {r.chapter: r.mastery_score for r in db.query(Mastery).filter(Mastery.user_id == user.id)}
    assert rows == {"Vectors": 72.0, "Electrostatics": 35.0}  # bogus slug ignored


# --- per-concept mastery ----------------------------------------------------
def test_update_concept_mastery_tracks_streak_and_ema(db, chapters, user):
    ch = chapters["vectors"]
    q1 = Question(subject="Physics", chapter="Vectors", chapter_id=ch.id,
                  difficulty="Easy", concept="Dot Product", type="single_correct",
                  prompt="?", correct_answer=0)
    db.add(q1)
    db.flush()

    # First attempt: wrong -> ema 0, fail_streak 1
    M.update_concept_mastery(db, user.id, [q1], {q1.id: False})
    db.flush()
    row = db.query(ConceptMastery).filter_by(user_id=user.id, concept="Dot Product").one()
    assert row.ema == 0.0
    assert row.fail_streak == 1
    assert row.attempts == 1

    # Second attempt: correct -> ema blends up, fail_streak resets
    M.update_concept_mastery(db, user.id, [q1], {q1.id: True})
    db.flush()
    db.refresh(row)
    assert row.fail_streak == 0
    assert row.correct == 1
    assert row.attempts == 2
    assert row.ema == pytest.approx(45.0)  # blend(0, 100) = 0.45*100
