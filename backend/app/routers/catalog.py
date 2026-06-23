"""Subjects + chapters catalog."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Chapter, Subject
from ..schemas import ChapterOut, SubjectOut
from ..services.pilot import pilot_chapter_ids, pilot_mode_enabled

router = APIRouter(prefix="/catalog", tags=["catalog"])


def _chapter_out(ch: Chapter, pilot_ids: set[str] | None) -> ChapterOut:
    base = ChapterOut.model_validate(ch)
    if pilot_ids is None:
        return base
    return base.model_copy(update={"unlocked": ch.id in pilot_ids})


@router.get("/subjects", response_model=list[SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    pilot_ids = pilot_chapter_ids(db) if pilot_mode_enabled() else None
    subjects = db.query(Subject).order_by(Subject.order_index).all()
    out: list[SubjectOut] = []
    for subj in subjects:
        row = SubjectOut.model_validate(subj)
        chapters = [_chapter_out(c, pilot_ids) for c in subj.chapters]
        out.append(row.model_copy(update={"chapters": chapters}))
    return out


@router.get("/chapters", response_model=list[ChapterOut])
def list_chapters(db: Session = Depends(get_db)):
    pilot_ids = pilot_chapter_ids(db) if pilot_mode_enabled() else None
    chapters = db.query(Chapter).order_by(Chapter.order_index).all()
    return [_chapter_out(c, pilot_ids) for c in chapters]


@router.get("/chapters/{slug}", response_model=ChapterOut)
def get_chapter(slug: str, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.slug == slug).first()
    if chapter is None:
        raise HTTPException(404, "Chapter not found")
    pilot_ids = pilot_chapter_ids(db) if pilot_mode_enabled() else None
    return _chapter_out(chapter, pilot_ids)
