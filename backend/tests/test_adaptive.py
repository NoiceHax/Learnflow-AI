"""Tests for the adaptive engine (services/adaptive.py).

All run offline (USE_GEMINI=false), so selection falls back to the seeded pool
and is fully deterministic in structure. We assert the adaptive *contracts*:
difficulty targeting, retiring missed questions, and never re-serving questions
the student has already seen on a final quiz.
"""
from __future__ import annotations

from app.models import UserQuestionState
from app.services import adaptive as A


# --- difficulty targeting ---------------------------------------------------
def test_target_difficulty_bands():
    assert A.target_difficulty(20) == "Easy"
    assert A.target_difficulty(49.9) == "Easy"
    assert A.target_difficulty(50) == "Medium"
    assert A.target_difficulty(74) == "Medium"
    assert A.target_difficulty(75) == "Advanced"
    assert A.target_difficulty(100) == "Advanced"


def test_final_quiz_difficulty_is_one_step_harder_min_medium():
    # Easy target -> Medium ; Medium target -> Advanced ; Advanced stays Advanced.
    assert A.final_quiz_difficulty(20) == "Medium"
    assert A.final_quiz_difficulty(60) == "Advanced"
    assert A.final_quiz_difficulty(95) == "Advanced"


# --- record_attempts --------------------------------------------------------
def test_record_attempts_final_retires_wrong_only(db, chapters, user, make_question):
    ch = chapters["vectors"]
    right = make_question(ch, correct_answer=0)
    wrong = make_question(ch, correct_answer=1)

    retired = A.record_attempts(
        db, user.id, [right, wrong], {right.id: True, wrong.id: False}, mode="final"
    )
    db.flush()

    assert [q.id for q in retired] == [wrong.id]
    states = {s.question_id: s for s in db.query(UserQuestionState).filter_by(user_id=user.id)}
    assert states[wrong.id].retired is True
    assert states[right.id].retired is False
    assert states[right.id].last_correct is True
    assert states[wrong.id].seen_count == 1


def test_record_attempts_practice_unretires_correct(db, chapters, user, make_question):
    ch = chapters["vectors"]
    q = make_question(ch, correct_answer=0)

    # Miss it in practice -> retired/in-pool
    A.record_attempts(db, user.id, [q], {q.id: False}, mode="practice")
    db.flush()
    st = db.query(UserQuestionState).filter_by(user_id=user.id, question_id=q.id).one()
    assert st.retired is True
    assert st.wrong_count == 1

    # Later get it right -> dropped from the practice pool
    A.record_attempts(db, user.id, [q], {q.id: True}, mode="practice")
    db.flush()
    db.refresh(st)
    assert st.retired is False
    assert st.last_correct is True


def test_retired_ids_reflects_recorded_misses(db, chapters, user, make_question):
    ch = chapters["vectors"]
    q = make_question(ch, correct_answer=0)
    A.record_attempts(db, user.id, [q], {q.id: False}, mode="final")
    db.flush()
    assert A.retired_ids(db, user.id) == {q.id}


# --- selection (offline pool path) -----------------------------------------
def test_select_practice_serves_missed_questions(db, chapters, user, make_question):
    ch = chapters["vectors"]
    missed = make_question(ch, concept="Dot Product", correct_answer=0)
    solved = make_question(ch, concept="Dot Product", correct_answer=0)
    # Fresh, never-seen questions so the pool clears the min_quiz_questions floor.
    [make_question(ch, concept="Dot Product", correct_answer=0) for _ in range(3)]

    A.record_attempts(db, user.id, [missed], {missed.id: False}, mode="final")
    A.record_attempts(db, user.id, [solved], {solved.id: True}, mode="practice")
    db.flush()

    picked = A.select_practice_quiz(db, user.id, ch.id, count=6)
    ids = {q.id for q in picked}
    assert missed.id in ids       # a recent miss is reinforced
    assert solved.id not in ids   # an already-correct (cleared) one is not re-served


def test_select_final_excludes_seen_and_retired(db, chapters, user, make_question):
    ch = chapters["electrostatics"]
    seen = make_question(ch, concept="Electric Field", difficulty="Advanced", correct_answer=0)
    fresh = [
        make_question(ch, concept="Electric Field", difficulty="Advanced", correct_answer=0)
        for _ in range(3)
    ]

    # Mark `seen` as already attempted (and wrong -> retired).
    A.record_attempts(db, user.id, [seen], {seen.id: False}, mode="final")
    db.flush()

    selected = A.select_final_quiz(
        db, user.id, ch.id, count=6, effective_mastery=80.0, concept_mastery={}
    )
    ids = {q.id for q in selected}
    assert seen.id not in ids                  # never re-serves a seen/retired question
    assert len(selected) >= 2                  # respects the min_quiz_questions floor
    assert any(q.id in ids for q in fresh)     # fresh, unseen questions are served


def test_process_after_quiz_returns_summary(db, chapters, user, make_question):
    ch = chapters["vectors"]
    q = make_question(ch, concept="Dot Product", correct_answer=0)
    graded = [{"question_id": q.id, "concept": "Dot Product", "correct": False}]

    summary = A.process_after_quiz(db, user.id, ch.id, [q], graded, mode="final")
    assert summary["retired_count"] == 1
    assert summary["weak_concepts_hit"] == ["Dot Product"]
    assert summary["mode"] == "final"
