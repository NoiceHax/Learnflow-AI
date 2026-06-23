"""Lesson engine: serves premium, structured chapter lessons."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Chapter, Lesson, User
from ..schemas import LessonOut
from ..services.pilot import assert_pilot_chapter_access

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/{chapter_id}", response_model=LessonOut)
def get_lesson(
    chapter_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chapter = db.get(Chapter, chapter_id)
    if chapter is None:
        raise HTTPException(404, "Chapter not found")
    assert_pilot_chapter_access(db, chapter_id)
    lesson = db.query(Lesson).filter(Lesson.chapter_id == chapter_id).first()
    if lesson is None:
        raise HTTPException(404, "Lesson not available for this chapter yet.")
    return LessonOut.model_validate(lesson)
