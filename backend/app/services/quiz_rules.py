"""Hard rules for chapter practice/final quizzes."""
from __future__ import annotations

from ..config import settings

MAX_QUIZ_QUESTIONS = 12


def clamp_quiz_request(count: int) -> int:
    """Requested quiz size, never below ``min_quiz_questions``."""
    lo = settings.min_quiz_questions
    return max(lo, min(count, MAX_QUIZ_QUESTIONS))


def accept_quiz_questions(questions: list) -> list:
    """Reject sets smaller than ``min_quiz_questions`` (never serve a 1-question quiz)."""
    if len(questions) < settings.min_quiz_questions:
        return []
    return questions
