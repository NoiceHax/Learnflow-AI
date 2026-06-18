"""Tests for the answer-grading core (services/grading.py).

This is the shared evaluation engine for both assessments and chapter quizzes,
so its correctness is load-bearing for every mastery/learning-path decision
downstream. We build transient Question objects (no DB needed) since
``is_correct`` only reads attributes.
"""
from __future__ import annotations

from app.models import Question
from app.services.grading import grade_questions, is_correct


def _q(**kw) -> Question:
    base = dict(
        subject="Physics", chapter="Vectors", chapter_id="c1",
        difficulty="Medium", concept="Dot Product", type="single_correct",
        prompt="?", correct_answer=0,
    )
    base.update(kw)
    return Question(**base)


# --- single_correct ---------------------------------------------------------
def test_single_correct_right_and_wrong():
    q = _q(type="single_correct", correct_answer=2)
    assert is_correct(q, 2) is True
    assert is_correct(q, "2") is True  # string index coerced
    assert is_correct(q, 1) is False


def test_single_correct_none_is_wrong_not_error():
    q = _q(type="single_correct", correct_answer=2)
    assert is_correct(q, None) is False


def test_single_correct_garbage_answer_is_wrong():
    q = _q(type="single_correct", correct_answer=2)
    assert is_correct(q, "banana") is False
    assert is_correct(q, "") is False


# --- multiple_correct -------------------------------------------------------
def test_multiple_correct_order_independent():
    q = _q(type="multiple_correct", correct_answer=[0, 2])
    assert is_correct(q, [2, 0]) is True
    assert is_correct(q, [0, 2]) is True


def test_multiple_correct_partial_is_wrong():
    q = _q(type="multiple_correct", correct_answer=[0, 2])
    assert is_correct(q, [0]) is False
    assert is_correct(q, [0, 1, 2]) is False


def test_multiple_correct_non_list_is_wrong():
    q = _q(type="multiple_correct", correct_answer=[0, 2])
    assert is_correct(q, 0) is False
    assert is_correct(q, "0,2") is False


# --- integer ----------------------------------------------------------------
def test_integer_exact_match():
    q = _q(type="integer", correct_answer=42)
    assert is_correct(q, 42) is True
    assert is_correct(q, "42") is True
    assert is_correct(q, 42.0) is True
    assert is_correct(q, 41) is False


# --- numerical (tolerance) --------------------------------------------------
def test_numerical_within_default_tolerance():
    q = _q(type="numerical", correct_answer=9.8, tolerance=None)  # default 0.01
    assert is_correct(q, 9.805) is True
    assert is_correct(q, 9.8) is True
    assert is_correct(q, 9.83) is False


def test_numerical_respects_custom_tolerance():
    q = _q(type="numerical", correct_answer=100.0, tolerance=1.0)
    assert is_correct(q, 100.7) is True
    assert is_correct(q, 101.5) is False


def test_numerical_none_answer_is_wrong():
    q = _q(type="numerical", correct_answer=9.8)
    assert is_correct(q, None) is False


# --- unknown type -----------------------------------------------------------
def test_unknown_type_is_wrong():
    q = _q(type="essay", correct_answer="anything")
    assert is_correct(q, "anything") is False


# --- grade_questions aggregation -------------------------------------------
def test_grade_questions_scores_and_weak_concepts():
    qs = [
        _q(type="single_correct", correct_answer=0, concept="Dot Product"),
        _q(type="single_correct", correct_answer=1, concept="Dot Product"),
        _q(type="integer", correct_answer=5, concept="Magnitude"),
        _q(type="numerical", correct_answer=2.0, concept="Cross Product"),
    ]
    for i, q in enumerate(qs):
        q.id = f"q{i}"

    answers = {
        "q0": 0,      # correct
        "q1": 0,      # wrong (Dot Product)
        "q2": None,   # skipped -> wrong, not attempted
        "q3": 2.0,    # correct
    }
    result = grade_questions(qs, answers)

    assert result["total_questions"] == 4
    assert result["correct_count"] == 2
    assert result["score"] == 50.0  # 2/4
    # accuracy is over *attempted* (3 attempted, 2 correct)
    assert result["accuracy"] == round(100 * 2 / 3, 1)
    # weak concepts: Dot Product (1 miss) and Magnitude (1 miss); Cross Product was correct
    assert set(result["weak_concepts"]) == {"Dot Product", "Magnitude"}


def test_grade_questions_empty_is_safe():
    result = grade_questions([], {})
    assert result["total_questions"] == 0
    assert result["score"] == 0.0
    assert result["accuracy"] == 0.0
    assert result["weak_concepts"] == []


def test_grade_questions_all_skipped_zero_accuracy():
    qs = [_q(type="single_correct", correct_answer=0)]
    qs[0].id = "q0"
    result = grade_questions(qs, {"q0": None})
    assert result["correct_count"] == 0
    assert result["accuracy"] == 0.0  # nothing attempted -> no div-by-zero
