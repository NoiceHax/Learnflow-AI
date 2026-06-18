"""Answer grading: the evaluation core shared by assessments and chapter quizzes.

Handles all four question types: single_correct, multiple_correct, integer,
numerical. A skipped answer (None) is always incorrect but never throws.
"""
from __future__ import annotations

from typing import Any

from ..models import Question


def _to_number(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def is_correct(question: Question, answer: Any) -> bool:
    if answer is None:
        return False

    qtype = question.type
    correct = question.correct_answer

    if qtype == "single_correct":
        return _to_number(answer) is not None and int(_to_number(answer)) == int(correct)

    if qtype == "multiple_correct":
        if not isinstance(answer, (list, tuple)):
            return False
        try:
            chosen = {int(x) for x in answer}
        except (TypeError, ValueError):
            return False
        return chosen == {int(x) for x in correct}

    if qtype == "integer":
        a = _to_number(answer)
        return a is not None and int(a) == int(correct)

    if qtype == "numerical":
        a = _to_number(answer)
        if a is None:
            return False
        tol = question.tolerance if question.tolerance is not None else 0.01
        return abs(a - float(correct)) <= tol

    return False


def grade_questions(
    questions: list[Question], answers: dict[str, Any]
) -> dict[str, Any]:
    """Grade a set of questions against a {question_id: answer} map.

    Returns score (%), accuracy (% of attempted), per-question breakdown,
    and the concepts the student got wrong (weak-topic detection).
    """
    graded: list[dict[str, Any]] = []
    correct_count = 0
    attempted = 0
    weak: dict[str, int] = {}

    for q in questions:
        ans = answers.get(q.id)
        if ans is not None and ans != "" and ans != []:
            attempted += 1
        ok = is_correct(q, ans)
        if ok:
            correct_count += 1
        else:
            weak[q.concept] = weak.get(q.concept, 0) + 1
        graded.append(
            {
                "question_id": q.id,
                "concept": q.concept,
                "chapter": q.chapter,
                "correct": ok,
                "your_answer": ans,
                "correct_answer": q.correct_answer,
                "solution": q.solution,
            }
        )

    total = len(questions) or 1
    score = round(100.0 * correct_count / total, 1)
    accuracy = round(100.0 * correct_count / attempted, 1) if attempted else 0.0
    weak_concepts = [c for c, _ in sorted(weak.items(), key=lambda kv: -kv[1])]

    return {
        "score": score,
        "accuracy": accuracy,
        "total_questions": len(questions),
        "correct_count": correct_count,
        "weak_concepts": weak_concepts,
        "graded": graded,
    }
