"""Completed exam history: initial assessment + final chapter quizzes only."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from ..models import Assessment, Chapter, QuizAttempt, Subject


def build_exam_history(db: Session, user_id: str) -> list[dict[str, Any]]:
    subjects = {s.id: s for s in db.query(Subject).all()}
    chapters = {c.id: c for c in db.query(Chapter).all()}

    items: list[dict[str, Any]] = []

    for row in (
        db.query(Assessment)
        .filter(Assessment.user_id == user_id)
        .order_by(Assessment.created_at.desc())
        .all()
    ):
        items.append(
            {
                "kind": "assessment",
                "id": row.id,
                "title": "Initial Assessment",
                "chapter": None,
                "chapter_id": None,
                "subject": None,
                "score": round(row.score, 1),
                "accuracy": round(
                    100.0 * row.correct_count / row.total_questions, 1
                )
                if row.total_questions
                else 0.0,
                "correct_count": row.correct_count,
                "total_questions": row.total_questions,
                "time_taken": None,
                "passed": None,
                "timestamp": row.created_at,
            }
        )

    for row in (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id, QuizAttempt.mode == "final")
        .order_by(QuizAttempt.created_at.desc())
        .all()
    ):
        ch = chapters.get(row.chapter_id)
        subj = subjects.get(ch.subject_id) if ch else None
        items.append(
            {
                "kind": "final_quiz",
                "id": row.id,
                "title": f"Final Quiz · {row.chapter_name}",
                "chapter": row.chapter_name,
                "chapter_id": row.chapter_id,
                "subject": subj.name if subj else "",
                "score": round(row.score, 1),
                "accuracy": round(row.accuracy, 1),
                "correct_count": row.correct_count,
                "total_questions": row.total_questions,
                "time_taken": row.time_taken,
                "passed": row.correct_count == row.total_questions and row.total_questions > 0,
                "timestamp": row.created_at,
            }
        )

    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return items


def _assessment_result_from_row(row: Assessment, db: Session) -> dict[str, Any]:
    payload = row.report if isinstance(row.report, dict) else {}
    knowledge_map = payload.get("knowledge_map")
    if not knowledge_map:
        chapters = {c.slug: c for c in db.query(Chapter).all()}
        subjects = {s.id: s for s in db.query(Subject).all()}
        knowledge_map = []
        for slug, score in (row.chapter_scores or {}).items():
            ch = chapters.get(slug)
            if ch is None:
                continue
            subj = subjects.get(ch.subject_id)
            knowledge_map.append(
                {
                    "chapter": ch.chapter_name,
                    "slug": ch.slug,
                    "subject": subj.name if subj else "",
                    "score": score,
                }
            )
    return {
        "id": row.id,
        "score": row.score,
        "chapter_scores": row.chapter_scores or {},
        "subject_scores": row.subject_scores or {},
        "knowledge_map": knowledge_map,
        "total_questions": row.total_questions,
        "correct_count": row.correct_count,
    }


def get_exam_report(db: Session, user_id: str, kind: str, record_id: str) -> dict[str, Any] | None:
    if kind == "assessment":
        row = db.get(Assessment, record_id)
        if row is None or row.user_id != user_id:
            return None
        return {
            "kind": "assessment",
            "assessment": _assessment_result_from_row(row, db),
            "quiz_result": None,
            "questions": None,
            "detail_available": bool(row.report or row.chapter_scores),
        }

    if kind == "final_quiz":
        row = db.get(QuizAttempt, record_id)
        if row is None or row.user_id != user_id or row.mode != "final":
            return None
        payload = row.report if isinstance(row.report, dict) else {}
        result = payload.get("result")
        questions = payload.get("questions")
        if not result:
            passed = row.correct_count == row.total_questions and row.total_questions > 0
            result = {
                "score": row.score,
                "accuracy": row.accuracy,
                "total_questions": row.total_questions,
                "correct_count": row.correct_count,
                "time_taken": row.time_taken,
                "weak_concepts": row.weak_concepts or [],
                "graded": [],
                "adaptive": None,
                "chapter_mastered": passed,
            }
            questions = []
        return {
            "kind": "final_quiz",
            "assessment": None,
            "quiz_result": result,
            "questions": questions or [],
            "detail_available": bool(payload.get("result")),
        }

    return None
