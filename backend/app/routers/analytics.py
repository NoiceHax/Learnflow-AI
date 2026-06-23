"""Analytics endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import ExamHistoryItem, ExamReportOut
from ..services.exam_history import build_exam_history, get_exam_report

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/exam-history", response_model=list[ExamHistoryItem])
def exam_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [ExamHistoryItem(**row) for row in build_exam_history(db, user.id)]


@router.get("/exam-history/{kind}/{record_id}", response_model=ExamReportOut)
def exam_report(
    kind: str,
    record_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if kind not in ("assessment", "final_quiz"):
        raise HTTPException(400, "Invalid exam kind.")
    payload = get_exam_report(db, user.id, kind, record_id)
    if payload is None:
        raise HTTPException(404, "Exam report not found.")
    return ExamReportOut(**payload)
