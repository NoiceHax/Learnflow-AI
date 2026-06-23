"""Initial assessment: uses the same Quiz Engine, then builds the knowledge
map, seeds mastery and generates the personalised learning path."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Assessment, Chapter, Question, Subject, User
from ..schemas import AssessmentResult, AssessmentSubmission, QuestionOut
from ..services.adaptive import record_attempts
from ..services import learning_path as lp
from ..services.grading import is_correct
from ..services.mastery import seed_mastery_from_assessment, update_concept_mastery
from ..services.questions import question_to_out
from ..services.selection import assessment_questions

router = APIRouter(prefix="/assessment", tags=["assessment"])


@router.get("/questions", response_model=list[QuestionOut])
def get_assessment(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.onboarded:
        raise HTTPException(403, "Assessment already completed.")
    questions = assessment_questions(db, user_id=user.id)
    if not questions:
        raise HTTPException(404, "Assessment not available. Seed the database first.")
    return [question_to_out(q) for q in questions]


@router.post("/submit", response_model=AssessmentResult)
def submit_assessment(
    body: AssessmentSubmission,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.onboarded:
        raise HTTPException(403, "Assessment already completed.")
    answer_map = {a.question_id: a.answer for a in body.answers}
    questions = db.query(Question).filter(Question.id.in_(answer_map.keys())).all()
    if not questions:
        raise HTTPException(400, "No valid answers submitted.")

    chapters = {c.id: c for c in db.query(Chapter).all()}
    subjects = {s.id: s for s in db.query(Subject).all()}

    # Per-chapter correctness -> chapter mastery percentage.
    chapter_scores: dict[str, float] = {}
    subject_correct: dict[str, list[int]] = {}
    correct_by_qid: dict[str, bool] = {}
    correct_count = 0
    for q in questions:
        ok = is_correct(q, answer_map.get(q.id))
        correct_by_qid[q.id] = ok
        correct_count += int(ok)
        chapter = chapters.get(q.chapter_id)
        if chapter is None:
            continue
        chapter_scores[chapter.slug] = 100.0 if ok else 0.0
        bucket = subject_correct.setdefault(chapter.subject_id, [])
        bucket.append(int(ok))

    subject_scores = {
        subjects[sid].slug: round(100.0 * sum(vals) / len(vals), 1)
        for sid, vals in subject_correct.items()
        if vals
    }
    overall = round(100.0 * correct_count / len(questions), 1)

    knowledge_map = []
    for q in questions:
        chapter = chapters.get(q.chapter_id)
        if chapter is None:
            continue
        knowledge_map.append(
            {
                "chapter": chapter.chapter_name,
                "slug": chapter.slug,
                "subject": subjects[chapter.subject_id].name if chapter.subject_id in subjects else "",
                "score": chapter_scores.get(chapter.slug, 0.0),
            }
        )

    report_payload = {
        "score": overall,
        "chapter_scores": chapter_scores,
        "subject_scores": subject_scores,
        "knowledge_map": knowledge_map,
        "total_questions": len(questions),
        "correct_count": correct_count,
    }

    assessment = Assessment(
        user_id=user.id,
        score=overall,
        chapter_scores=chapter_scores,
        subject_scores=subject_scores,
        total_questions=len(questions),
        correct_count=correct_count,
        report=report_payload,
    )
    db.add(assessment)

    seed_mastery_from_assessment(db, user.id, chapter_scores)
    update_concept_mastery(db, user.id, questions, correct_by_qid)
    correct_by_qid_map = {q.id: correct_by_qid[q.id] for q in questions}
    record_attempts(db, user.id, questions, correct_by_qid_map)
    user.onboarded = True
    db.commit()

    lp.generate(db, user.id)

    return AssessmentResult(
        id=assessment.id,
        score=overall,
        chapter_scores=chapter_scores,
        subject_scores=subject_scores,
        knowledge_map=knowledge_map,
        total_questions=len(questions),
        correct_count=correct_count,
    )
