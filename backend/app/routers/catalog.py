"""Subjects + chapters catalog."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Chapter, Subject
from ..schemas import ChapterOut, SubjectOut

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/subjects", response_model=list[SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).order_by(Subject.order_index).all()
    return [SubjectOut.model_validate(s) for s in subjects]


@router.get("/chapters", response_model=list[ChapterOut])
def list_chapters(db: Session = Depends(get_db)):
    chapters = db.query(Chapter).order_by(Chapter.order_index).all()
    return [ChapterOut.model_validate(c) for c in chapters]


@router.get("/chapters/{slug}", response_model=ChapterOut)
def get_chapter(slug: str, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.slug == slug).first()
    if chapter is None:
        raise HTTPException(404, "Chapter not found")
    return ChapterOut.model_validate(chapter)
