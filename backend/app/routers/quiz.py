"""Chapter practice quizzes: adaptive engine retires misses and spawns replacements."""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..models import Chapter, Question, QuizAttempt, User
from ..schemas import AdaptiveSummary, QuestionOut, QuizResult, QuizSubmission
from ..services import learning_path as lp
from ..services.adaptive import process_after_quiz
from ..services.grading import grade_questions
from ..services.mastery import mark_chapter_mastered, update_concept_mastery, upsert_mastery
from ..services.pilot import assert_pilot_chapter_access
from ..services.questions import question_to_out
from ..services.quiz_rules import accept_quiz_questions, clamp_quiz_request
from ..services.selection import chapter_questions

router = APIRouter(prefix="/quiz", tags=["quiz"])
logger = logging.getLogger(__name__)


def _quiz_mode(mode: str | None) -> str:
    """practice | final (legacy 'adaptive' maps to final)."""
    if mode == "practice":
        return "practice"
    return "final"


@router.get("/{chapter_id}/questions", response_model=list[QuestionOut])
def get_quiz(
    chapter_id: str,
    count: int = 6,
    mode: str = "final",
    is_pyq: bool | None = None,
    pyq_year: int | None = None,
    pyq_exam: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chapter = db.get(Chapter, chapter_id)
    if chapter is None:
        raise HTTPException(404, "Chapter not found")
    assert_pilot_chapter_access(db, chapter_id)
    
    if is_pyq or pyq_year or pyq_exam:
        question_count = count
        quiz_mode = "practice"
    else:
        quiz_mode = _quiz_mode(mode)
        pool_size = settings.practice_pool_size if quiz_mode == "practice" else count
        question_count = clamp_quiz_request(pool_size if quiz_mode == "practice" else count)

    questions = accept_quiz_questions(
        chapter_questions(
            db,
            chapter_id,
            user.id,
            count=question_count,
            mode=quiz_mode,
            is_pyq=is_pyq,
            pyq_year=pyq_year,
            pyq_exam=pyq_exam,
        )
    )
    if not questions:
        if is_pyq or pyq_year or pyq_exam:
            raise HTTPException(404, "No matching Previous Year Questions (PYQs) found for this chapter.")
        total = db.query(Question).filter(Question.chapter_id == chapter_id).count()
        if quiz_mode == "practice":
            raise HTTPException(
                404,
                "No practice questions available yet. Run: python -m app.seed --pregenerate-backups",
            )
        logger.warning(
            "Quiz unavailable: chapter=%s user=%s (seeded_questions=%d)",
            chapter_id,
            user.id,
            total,
        )
        raise HTTPException(404, "No questions available for this chapter yet.")
    db.commit()
    logger.info(
        "Quiz loaded: mode=%s chapter=%s user=%s questions=%d",
        quiz_mode,
        chapter_id,
        user.id,
        len(questions),
    )
    return [question_to_out(q) for q in questions]


@router.post("/{chapter_id}/submit", response_model=QuizResult)
def submit_quiz(
    chapter_id: str,
    body: QuizSubmission,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chapter = db.get(Chapter, chapter_id)
    if chapter is None:
        raise HTTPException(404, "Chapter not found")
    assert_pilot_chapter_access(db, chapter_id)

    answer_map = {a.question_id: a.answer for a in body.answers}
    questions = db.query(Question).filter(Question.id.in_(answer_map.keys())).all()
    if not questions:
        raise HTTPException(400, "No valid questions submitted.")
    if len(questions) < settings.min_quiz_questions:
        raise HTTPException(
            400,
            f"A quiz must include at least {settings.min_quiz_questions} questions.",
        )

    result = grade_questions(questions, answer_map)

    quiz_mode = _quiz_mode(body.mode)
    attempt: QuizAttempt | None = None

    if quiz_mode == "final":
        attempt = QuizAttempt(
            user_id=user.id,
            chapter_id=chapter.id,
            chapter_name=chapter.chapter_name,
            mode="final",
            score=result["score"],
            accuracy=result["accuracy"],
            time_taken=body.time_taken,
            total_questions=result["total_questions"],
            correct_count=result["correct_count"],
            weak_concepts=result["weak_concepts"],
            report=None,
        )
        db.add(attempt)

    perfect_final = (
        quiz_mode == "final"
        and result["total_questions"] > 0
        and result["correct_count"] == result["total_questions"]
    )
    chapter_mastered = False
    if perfect_final:
        mark_chapter_mastered(db, user.id, chapter)
        chapter_mastered = True
    elif quiz_mode == "final":
        upsert_mastery(db, user.id, chapter, result["score"])

    correct_by_qid = {g["question_id"]: g["correct"] for g in result["graded"]}
    update_concept_mastery(db, user.id, questions, correct_by_qid)

    adaptive = process_after_quiz(
        db, user.id, chapter.id, questions, result["graded"], mode=quiz_mode
    )
    lp.generate(db, user.id)

    quiz_response = QuizResult(
        score=result["score"],
        accuracy=result["accuracy"],
        total_questions=result["total_questions"],
        correct_count=result["correct_count"],
        time_taken=body.time_taken,
        weak_concepts=result["weak_concepts"],
        graded=result["graded"],
        adaptive=AdaptiveSummary(**adaptive),
        chapter_mastered=chapter_mastered,
    )

    if quiz_mode == "final" and attempt is not None:
        attempt.report = {
            "result": quiz_response.model_dump(),
            "questions": [question_to_out(q).model_dump() for q in questions],
        }

    db.commit()

    return quiz_response
